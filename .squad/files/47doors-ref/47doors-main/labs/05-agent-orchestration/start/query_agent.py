"""
Query Agent Module

This agent is responsible for analyzing incoming user queries,
classifying intent, and extracting relevant entities.
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class Intent(str, Enum):
    """Enumeration of possible query intents."""

    KNOWLEDGE_QUERY = "knowledge_query"
    PASSWORD_RESET = "password_reset"
    TICKET_STATUS = "ticket_status"
    GENERAL_CHAT = "general_chat"
    ESCALATION = "escalation"
    COURSE_INFO = "course_info"
    UNKNOWN = "unknown"


@dataclass
class Entity:
    """Represents an extracted entity from the query."""

    name: str
    value: str
    entity_type: str
    confidence: float


@dataclass
class QueryResult:
    """Structured result from query analysis."""

    original_query: str
    intent: Intent
    entities: list[Entity]
    confidence: float
    requires_clarification: bool = False
    clarification_question: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_entities_dict(self) -> dict[str, Any]:
        """Return entities as a dictionary for easy access."""
        return {entity.name: entity.value for entity in self.entities}


class QueryAgent:
    """
    Agent responsible for analyzing user queries.

    This agent classifies the intent of incoming queries and extracts
    relevant entities for downstream processing by other agents.

    Attributes:
        client: The Azure OpenAI client for LLM calls.
        model: The model deployment name to use.
    """

    SYSTEM_PROMPT = """You are a query understanding agent for a student support system.
Your job is to analyze user messages and extract structured information.

## Intent Categories

Classify the user's message into exactly ONE of these intents:

1. **knowledge_query**: Questions about policies, procedures, how-to guides, FAQs
   - Example: "How do I reset my password?"
   - Example: "What is the refund policy?"

2. **password_reset**: Specifically about password or account access issues
   - Example: "I forgot my password"
   - Example: "I can't log into my account"

3. **ticket_status**: Checking on existing support tickets
   - Example: "What's the status of my ticket?"
   - Example: "Can you check TKT-12345?"

4. **general_chat**: Casual conversation, greetings, thanks, small talk
   - Example: "Hello!"
   - Example: "Thanks for your help"

5. **escalation**: User wants human support, is frustrated, or has complex needs
   - Example: "I need to speak to a human"
   - Example: "This is urgent!"

6. **course_info**: Questions about courses, schedules, registration
   - Example: "When does CS101 start?"
   - Example: "How do I register for classes?"

7. **unknown**: Cannot determine intent from the message
   - Use when the message is unclear or off-topic
   - Set confidence below 0.5 for unknown

## Entity Extraction

Extract these entities when present:
- **ticket_id**: Support ticket IDs (format: TKT-XXXXX or similar)
- **user_name**: If user identifies themselves by name
- **date**: Dates mentioned (format: YYYY-MM-DD if possible)
- **topic**: Main subject of the query
- **urgency**: low, medium, or high based on language

## Output Format

Respond with ONLY valid JSON in this exact format:
{
    "intent": "<one of: knowledge_query, password_reset, ticket_status, general_chat, escalation, course_info, unknown>",
    "confidence": <0.0 to 1.0>,
    "entities": {
        "entity_name": "entity_value",
        ...
    },
    "entity_confidences": {
        "entity_name": <0.0 to 1.0>,
        ...
    },
    "requires_clarification": <true or false>,
    "clarification_question": "<question to ask if clarification needed, null otherwise>",
    "urgency": "<low, medium, or high>"
}

## Guidelines

- Be conservative with confidence scores
- If multiple intents could apply, choose the most specific one
- Set requires_clarification=true if the message is ambiguous
- Always provide a clarification_question when requires_clarification is true
- Detect urgency from language: "ASAP", "urgent", "immediately" = high
"""

    def __init__(self, client: Any, model: str = "gpt-4o") -> None:
        """
        Initialize the QueryAgent.

        Args:
            client: Azure OpenAI client instance.
            model: The model deployment name to use for analysis.
        """
        self.client = client
        self.model = model

    async def analyze(
        self, query: str, conversation_context: str | None = None
    ) -> QueryResult:
        """
        Analyze a user query to classify intent and extract entities.

        This method processes the incoming query using an LLM to:
        1. Classify the user's intent (question, complaint, request, etc.)
        2. Extract relevant entities (product names, dates, amounts, etc.)
        3. Calculate a confidence score for the classification

        Args:
            query: The raw user query string to analyze.
            conversation_context: Optional context from previous turns.

        Returns:
            QueryResult containing intent, entities, and confidence score.

        Raises:
            ValueError: If the query is empty or invalid.
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        # Build user prompt
        user_prompt = self._build_classification_prompt(query)

        # Call Azure OpenAI chat completions API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
            max_tokens=500,
        )

        # Parse the JSON response
        result_json = json.loads(response.choices[0].message.content)

        # Map intent string to Intent enum
        intent_str = result_json.get("intent", "unknown")
        try:
            intent = Intent(intent_str)
        except ValueError:
            intent = Intent.UNKNOWN

        # Parse entities
        entities = self._parse_entities(
            result_json.get("entities", {}), result_json.get("entity_confidences", {})
        )

        # Extract confidence
        confidence = float(result_json.get("confidence", 0.0))

        # Return QueryResult
        return QueryResult(
            original_query=query,
            intent=intent,
            entities=entities,
            confidence=confidence,
            requires_clarification=result_json.get("requires_clarification", False),
            clarification_question=result_json.get("clarification_question"),
            metadata={
                "urgency": result_json.get("urgency", "low"),
            },
        )

    def _build_classification_prompt(
        self, query: str, conversation_context: str | None = None
    ) -> str:
        """
        Build the prompt for intent classification.

        Args:
            query: The user query to classify.
            conversation_context: Optional summary of previous conversation
                                 (helps with follow-up questions like "tell me more").

        Returns:
            Formatted prompt string for the LLM.
        """
        parts = []
        if conversation_context:
            parts.append(f"## Conversation Context\n{conversation_context}\n")
        parts.append(f"## Current User Message\n{query}\n")
        parts.append("Analyze this message and respond with JSON.")
        return "\n".join(parts)

    def _parse_entities(
        self,
        entities_dict: dict[str, str],
        confidences_dict: dict[str, float] | None = None,
    ) -> list[Entity]:
        """
        Parse entity data from LLM response into Entity objects.

        Args:
            entities_dict: Dictionary mapping entity names to their values
                          (e.g., {"ticket_id": "TKT-12345", "topic": "password"})
            confidences_dict: Optional dictionary mapping entity names to confidence
                             scores (e.g., {"ticket_id": 0.95, "topic": 0.8})

        Returns:
            List of Entity objects extracted from the response.
        """
        type_mapping = {
            "ticket_id": "identifier",
            "user_name": "name",
            "date": "date",
            "topic": "topic",
            "urgency": "attribute",
        }

        entities = []
        for name, value in entities_dict.items():
            if value is None:
                continue

            confidence = confidences_dict.get(name, 0.8) if confidences_dict else 0.8
            entity_type = type_mapping.get(name, "unknown")

            entities.append(
                Entity(
                    name=name,
                    value=str(value),
                    entity_type=entity_type,
                    confidence=float(confidence),
                )
            )

        return entities

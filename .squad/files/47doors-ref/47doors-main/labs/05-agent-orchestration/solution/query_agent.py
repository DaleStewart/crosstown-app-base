"""
Query Agent Module - Lab 05 Solution

This agent is the first stage of the three-agent orchestration pipeline.
Its job is to transform raw user input into structured, actionable data
that downstream agents can process.

Key Responsibilities:
1. Parse natural language queries
2. Classify user intent into predefined categories
3. Extract relevant entities (names, IDs, dates, topics)
4. Enrich queries with conversation context
5. Determine if clarification is needed before proceeding

The QueryAgent uses Azure OpenAI to perform intent classification and
entity extraction in a single call, returning structured JSON output.
"""

import json
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from openai import AzureOpenAI


class Intent(str, Enum):
    """
    Enumeration of all supported query intents.

    Each intent maps to a specific ActionAgent in the routing table.
    The UNKNOWN intent is used when classification confidence is very low.

    Note: Using str, Enum allows direct JSON serialization and comparison.
    """
    KNOWLEDGE_QUERY = "knowledge_query"     # Questions about policies, procedures, how-to
    PASSWORD_RESET = "password_reset"       # Account access and password issues
    TICKET_STATUS = "ticket_status"         # Checking existing support ticket status
    GENERAL_CHAT = "general_chat"           # Casual conversation, greetings, chitchat
    ESCALATION = "escalation"               # User wants human agent, frustrated, complex issue
    COURSE_INFO = "course_info"             # Questions about courses, schedules, enrollment
    UNKNOWN = "unknown"                     # Cannot determine intent with confidence


@dataclass
class Entity:
    """
    Represents a single extracted entity from the user query.

    Entities are key pieces of information that agents need to fulfill requests.
    For example, a ticket ID, user name, course number, or date.

    Attributes:
        name: The entity type identifier (e.g., "ticket_id", "course_number")
        value: The actual extracted value (e.g., "TKT-12345", "CS101")
        entity_type: Category of the entity (e.g., "identifier", "date", "name")
        confidence: How confident the model is in this extraction (0.0-1.0)
    """
    name: str
    value: str
    entity_type: str
    confidence: float


@dataclass
class QueryResult:
    """
    Structured output from the QueryAgent.

    This dataclass serves as the contract between QueryAgent and RouterAgent.
    It contains all information needed to make routing decisions and execute actions.

    Attributes:
        original_query: The raw user message (preserved for logging/debugging)
        intent: The classified intent enum value
        entities: List of extracted Entity objects
        confidence: Overall confidence in the classification (0.0-1.0)
        requires_clarification: Whether the agent should ask for more info
        clarification_question: The specific question to ask if clarification needed
        metadata: Additional context (urgency, sentiment, etc.)
    """
    original_query: str
    intent: Intent
    entities: list[Entity]
    confidence: float
    requires_clarification: bool = False
    clarification_question: Optional[str] = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        """Initialize metadata if not provided."""
        if self.metadata is None:
            self.metadata = {}

    def get_entity(self, name: str) -> Optional[Entity]:
        """
        Retrieve an entity by name.

        Args:
            name: The entity name to look up

        Returns:
            The Entity if found, None otherwise
        """
        for entity in self.entities:
            if entity.name == name:
                return entity
        return None

    def get_entities_dict(self) -> dict[str, str]:
        """
        Convert entities to a simple dictionary for passing to downstream agents.

        Returns:
            Dictionary mapping entity names to their values
        """
        return {e.name: e.value for e in self.entities}


class QueryAgent:
    """
    Agent responsible for understanding and structuring user queries.

    The QueryAgent is the entry point of the orchestration pipeline. It takes
    raw user input and produces a structured QueryResult that downstream
    agents can process. This is a critical component because poor query
    understanding leads to poor routing and responses.

    Design Decisions:
    - Uses Azure OpenAI with JSON mode for reliable structured output
    - Low temperature (0.1) for deterministic, consistent classification
    - Includes conversation context to handle follow-up questions
    - Returns confidence scores so RouterAgent can request clarification

    Attributes:
        client: Azure OpenAI client for LLM calls
        model: The deployment name of the chat model (e.g., "gpt-4o")
    """

    # System prompt defines the agent's behavior and expected output format.
    # Key elements:
    # 1. Clear list of intent categories with descriptions
    # 2. Entity types to extract
    # 3. Exact JSON schema for the response
    # 4. Instructions for handling ambiguous cases
    SYSTEM_PROMPT = """You are a query understanding agent for a student support system.
Your job is to analyze user messages and extract structured information.

## Intent Categories

Classify the user's message into exactly ONE of these intents:

1. **knowledge_query**: Questions about policies, procedures, how-to guides, FAQs
   - Example: "How do I reset my password?"
   - Example: "What is the refund policy?"
   - Example: "Where can I find the handbook?"

2. **password_reset**: Specifically about password or account access issues
   - Example: "I forgot my password"
   - Example: "I can't log into my account"
   - Example: "My account is locked"

3. **ticket_status**: Checking on existing support tickets
   - Example: "What's the status of my ticket?"
   - Example: "Can you check TKT-12345?"
   - Example: "I submitted a request last week"

4. **general_chat**: Casual conversation, greetings, thanks, small talk
   - Example: "Hello!"
   - Example: "Thanks for your help"
   - Example: "How are you?"

5. **escalation**: User wants human support, is frustrated, or has complex needs
   - Example: "I need to speak to a human"
   - Example: "This is urgent!"
   - Example: "I want to file a complaint"
   - Trigger words: lawyer, complaint, supervisor, manager, urgent, frustrated

6. **course_info**: Questions about courses, schedules, registration, enrollment
   - Example: "When does CS101 start?"
   - Example: "How do I register for classes?"
   - Example: "What are the prerequisites for the course?"

7. **unknown**: Cannot determine intent from the message
   - Use this when the message is unclear, gibberish, or off-topic
   - Set confidence below 0.5 for unknown

## Entity Extraction

Extract these entities when present:
- **ticket_id**: Support ticket IDs (format: TKT-XXXXX or similar)
- **course_number**: Course codes (e.g., CS101, MATH200)
- **user_name**: If user identifies themselves by name
- **date**: Dates mentioned (format: YYYY-MM-DD if possible)
- **topic**: Main subject of the query
- **urgency**: low, medium, or high based on language

## Output Format

Respond with ONLY valid JSON in this exact format:
{
    "intent": "<one of the intent values>",
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

    def __init__(
        self,
        client: Optional[AzureOpenAI] = None,
        model: str = "gpt-4o",
        openai_endpoint: Optional[str] = None,
        openai_key: Optional[str] = None,
    ) -> None:
        """
        Initialize the QueryAgent.

        The agent can be initialized with an existing client or will create
        one from environment variables. This flexibility supports both
        dependency injection (for testing) and standalone usage.

        Args:
            client: Pre-configured Azure OpenAI client (optional)
            model: The model deployment name to use for analysis
            openai_endpoint: Azure OpenAI endpoint URL (optional, uses env var)
            openai_key: Azure OpenAI API key (optional, uses env var)
        """
        # Use provided client or create new one from environment/parameters
        if client:
            self.client = client
        else:
            # Load configuration from parameters or environment variables
            endpoint = openai_endpoint or os.environ.get("AZURE_OPENAI_ENDPOINT")
            key = openai_key or os.environ.get("AZURE_OPENAI_KEY")

            if not endpoint or not key:
                raise ValueError(
                    "Azure OpenAI credentials required. Provide client, parameters, "
                    "or set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY environment variables."
                )

            self.client = AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=key,
                api_version="2025-01-01-preview",
            )

        self.model = model

    async def analyze(
        self,
        query: str,
        conversation_context: Optional[str] = None,
    ) -> QueryResult:
        """
        Analyze a user query to classify intent and extract entities.

        This is the main entry point for the QueryAgent. It processes the
        incoming query using Azure OpenAI to:
        1. Classify the user's intent
        2. Extract relevant entities
        3. Calculate confidence scores
        4. Determine if clarification is needed

        The async pattern allows for non-blocking I/O when integrated into
        an async web framework like FastAPI.

        Args:
            query: The raw user query string to analyze
            conversation_context: Optional summary of previous conversation
                                 (helps with follow-up questions like "tell me more")

        Returns:
            QueryResult containing intent, entities, and confidence scores

        Raises:
            ValueError: If the query is empty or invalid

        Example:
            result = await agent.analyze(
                query="Can you check ticket TKT-12345?",
                conversation_context="User previously asked about password reset"
            )
            print(f"Intent: {result.intent}, Ticket: {result.get_entity('ticket_id')}")
        """
        # Validate input - empty queries would waste API calls
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        # Build the user prompt, optionally including conversation context
        # Context helps handle follow-up questions and anaphora ("it", "that", "more")
        user_prompt = self._build_user_prompt(query, conversation_context)

        # Call Azure OpenAI with JSON mode for structured output
        # Using low temperature (0.1) for deterministic, consistent results
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,  # Low temp for consistent classification
            response_format={"type": "json_object"},  # Ensure valid JSON output
            max_tokens=500,  # Classification doesn't need many tokens
        )

        # Parse the JSON response from the LLM
        # The response_format ensures we get valid JSON, but we still
        # need to handle potential missing fields gracefully
        result_json = json.loads(response.choices[0].message.content)

        # Convert raw JSON into our structured QueryResult
        return self._parse_response(query, result_json)

    def _build_user_prompt(
        self,
        query: str,
        conversation_context: Optional[str] = None,
    ) -> str:
        """
        Build the user prompt for intent classification.

        The prompt structure is important:
        1. Include conversation context first (if available) so the model
           understands the broader conversation
        2. Clearly mark the current user message
        3. Request analysis

        Args:
            query: The current user query
            conversation_context: Summary of previous conversation

        Returns:
            Formatted prompt string for the LLM
        """
        parts = []

        # Include context if available - helps with follow-up questions
        if conversation_context:
            parts.append(f"## Conversation Context\n{conversation_context}\n")

        # Add the current query with clear marking
        parts.append(f"## Current User Message\n{query}\n")

        # Request analysis
        parts.append("Analyze this message and respond with JSON.")

        return "\n".join(parts)

    def _parse_response(
        self,
        original_query: str,
        llm_response: dict[str, Any],
    ) -> QueryResult:
        """
        Parse the LLM's JSON response into a QueryResult object.

        This method handles:
        - Mapping string intent to Intent enum
        - Creating Entity objects from the entities dict
        - Setting defaults for missing fields
        - Validating the response structure

        Args:
            original_query: The original user query (preserved for reference)
            llm_response: The parsed JSON dict from the LLM

        Returns:
            QueryResult with all extracted information
        """
        # Extract intent, defaulting to UNKNOWN if invalid
        intent_str = llm_response.get("intent", "unknown")
        try:
            intent = Intent(intent_str)
        except ValueError:
            # If LLM returns an invalid intent, default to unknown
            intent = Intent.UNKNOWN

        # Parse entities from the response
        entities = self._parse_entities(
            llm_response.get("entities", {}),
            llm_response.get("entity_confidences", {}),
        )

        # Extract other fields with sensible defaults
        confidence = float(llm_response.get("confidence", 0.5))
        requires_clarification = llm_response.get("requires_clarification", False)
        clarification_question = llm_response.get("clarification_question")

        # Build metadata from additional fields
        metadata = {
            "urgency": llm_response.get("urgency", "low"),
        }

        return QueryResult(
            original_query=original_query,
            intent=intent,
            entities=entities,
            confidence=confidence,
            requires_clarification=requires_clarification,
            clarification_question=clarification_question,
            metadata=metadata,
        )

    def _parse_entities(
        self,
        entities_dict: dict[str, str],
        confidences_dict: dict[str, float],
    ) -> list[Entity]:
        """
        Parse entity data from LLM response into Entity objects.

        Transforms the flat dictionaries from the LLM into proper Entity
        objects with type information derived from the entity name.

        Args:
            entities_dict: Map of entity names to values
            confidences_dict: Map of entity names to confidence scores

        Returns:
            List of Entity objects
        """
        entities = []

        # Map entity names to their types for downstream processing
        type_mapping = {
            "ticket_id": "identifier",
            "course_number": "identifier",
            "user_name": "name",
            "date": "date",
            "topic": "topic",
            "urgency": "attribute",
        }

        for name, value in entities_dict.items():
            if value is None:
                continue  # Skip null values

            # Get confidence, defaulting to 0.8 if not provided
            confidence = confidences_dict.get(name, 0.8)

            # Determine entity type from the mapping
            entity_type = type_mapping.get(name, "unknown")

            entities.append(Entity(
                name=name,
                value=str(value),  # Ensure string type
                entity_type=entity_type,
                confidence=float(confidence),
            ))

        return entities


# Synchronous wrapper for environments that don't support async
def analyze_query_sync(
    query: str,
    client: Optional[AzureOpenAI] = None,
    model: str = "gpt-4o",
    conversation_context: Optional[str] = None,
) -> QueryResult:
    """
    Synchronous wrapper for query analysis.

    Use this in non-async environments. For async environments,
    use QueryAgent.analyze() directly.

    Args:
        query: The user query to analyze
        client: Azure OpenAI client (optional)
        model: Model deployment name
        conversation_context: Previous conversation summary

    Returns:
        QueryResult with classified intent and entities
    """
    import asyncio

    agent = QueryAgent(client=client, model=model)

    # Run the async method in an event loop
    return asyncio.run(agent.analyze(query, conversation_context))


# Example usage and testing
if __name__ == "__main__":
    import asyncio

    async def main():
        """Demonstrate QueryAgent usage."""
        # Initialize agent (uses environment variables)
        agent = QueryAgent()

        # Test queries covering different intents
        test_queries = [
            "Hello, how are you?",
            "How do I reset my password?",
            "What's the status of ticket TKT-12345?",
            "I need to speak to a human right now!",
            "When does CS101 start next semester?",
            "asdfghjkl",  # Gibberish - should be unknown
        ]

        for query in test_queries:
            print(f"\n{'='*50}")
            print(f"Query: {query}")

            result = await agent.analyze(query)

            print(f"Intent: {result.intent.value}")
            print(f"Confidence: {result.confidence:.2f}")
            print(f"Entities: {result.get_entities_dict()}")
            print(f"Requires clarification: {result.requires_clarification}")
            if result.clarification_question:
                print(f"Clarification: {result.clarification_question}")

    asyncio.run(main())

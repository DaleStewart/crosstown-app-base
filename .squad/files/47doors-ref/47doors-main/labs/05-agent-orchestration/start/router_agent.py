"""
Router Agent Module

This agent is responsible for routing analyzed queries to the
appropriate department or action handler based on intent and entities.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from query_agent import QueryResult, Intent


class Priority(str, Enum):
    """Priority levels for routed requests."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class RoutingDecision:
    """Structured routing decision for a query."""

    target_agent: str
    parameters: dict = field(default_factory=dict)
    fallback_agent: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    reasoning: str = ""
    requires_escalation: bool = False
    escalation_reason: Optional[str] = None


class RouterAgent:
    """
    Agent responsible for routing queries to appropriate departments.

    This agent analyzes the QueryResult from the QueryAgent and determines
    the best department, priority level, and any escalation requirements.

    Attributes:
        client: The Azure OpenAI client for LLM calls.
        model: The model deployment name to use.
        escalation_keywords: Keywords that trigger automatic escalation.
    """

    def __init__(
        self,
        client: Any,
        model: str = "gpt-4o",
        escalation_keywords: list[str] | None = None,
    ) -> None:
        """
        Initialize the RouterAgent.

        Args:
            client: Azure OpenAI client instance.
            model: The model deployment name to use for routing decisions.
            escalation_keywords: List of keywords that trigger escalation.
        """
        self.client = client
        self.model = model
        self.escalation_keywords = escalation_keywords or [
            "urgent",
            "emergency",
            "lawsuit",
            "legal",
            "executive",
        ]

    async def route(self, query_result: QueryResult) -> RoutingDecision:
        """
        Route a query to the appropriate department.

        This method analyzes the QueryResult and determines:
        1. Which department should handle the query
        2. The priority level of the request
        3. Whether escalation to a human is required
        4. Suggested actions for the handling agent

        Args:
            query_result: The analyzed query from QueryAgent.

        Returns:
            RoutingDecision with target_agent, priority, and reasoning.

        Raises:
            ValueError: If query_result is invalid.
        """
        if query_result is None:
            raise ValueError("Query result cannot be None")

        # Check for automatic escalation triggers FIRST
        escalation_result = self._check_escalation_triggers(query_result)
        if escalation_result:
            return escalation_result

        # Handle clarification requests from QueryAgent
        if query_result.requires_clarification:
            return RoutingDecision(
                target_agent="clarification_agent",
                parameters={
                    "question": query_result.clarification_question,
                    "original_query": query_result.original_query,
                },
                fallback_agent="general_agent",
                priority=Priority.MEDIUM,
                reasoning="Query requires clarification before proceeding",
                requires_escalation=False,
                escalation_reason=None,
            )

        # Check confidence level - low confidence needs clarification
        if query_result.confidence < 0.6:
            return RoutingDecision(
                target_agent="clarification_agent",
                parameters={
                    "intent_guess": query_result.intent.value,
                    "confidence": query_result.confidence,
                },
                fallback_agent="general_agent",
                priority=Priority.MEDIUM,
                reasoning=f"Low confidence ({query_result.confidence:.2f}) - requesting clarification",
                requires_escalation=False,
                escalation_reason=None,
            )

        # Look up route in routing table based on intent
        ROUTING_TABLE = {
            Intent.KNOWLEDGE_QUERY: ("retrieve_agent", "general_agent"),
            Intent.PASSWORD_RESET: ("password_agent", "escalation_agent"),
            Intent.TICKET_STATUS: ("ticket_agent", "general_agent"),
            Intent.GENERAL_CHAT: ("general_agent", None),
            Intent.ESCALATION: ("escalation_agent", None),
            Intent.COURSE_INFO: ("retrieve_agent", "general_agent"),
            Intent.UNKNOWN: ("clarification_agent", "general_agent"),
        }
        primary, fallback = ROUTING_TABLE.get(
            query_result.intent, ("general_agent", None)
        )

        # Determine priority
        priority = self._determine_priority(query_result)

        # Build parameters based on intent
        parameters = {
            "query": query_result.original_query,
            "entities": {e.name: e.value for e in query_result.entities},
        }

        return RoutingDecision(
            target_agent=primary,
            parameters=parameters,
            fallback_agent=fallback,
            priority=priority,
            reasoning=f"Intent '{query_result.intent.value}' with confidence {query_result.confidence:.2f}",
            requires_escalation=False,
            escalation_reason=None,
        )

    def _check_escalation_triggers(
        self, query_result: QueryResult
    ) -> RoutingDecision | None:
        """
        Check if the query requires automatic escalation.

        Escalation triggers indicate situations that require human intervention
        regardless of the classified intent. These include:
        - Legal concerns (lawyer, sue, attorney)
        - Safety concerns (suicide, harm, hurt myself)
        - Strong frustration (complaint, manager, supervisor)
        - Explicit human requests (human, real person)

        Args:
            query_result: The analyzed query to check.

        Returns:
            RoutingDecision for escalation if triggers found, None otherwise.
        """
        ESCALATION_TRIGGERS = [
            # Legal
            "lawyer",
            "attorney",
            "legal",
            "sue",
            "lawsuit",
            # Safety (URGENT priority)
            "suicide",
            "harm",
            "hurt myself",
            "kill",
            "die",
            # Frustration
            "supervisor",
            "manager",
            "complaint",
            "incompetent",
            # Urgency
            "emergency",
            "urgent",
            "immediately",
            "right now",
            # Explicit requests
            "human",
            "real person",
            "speak to someone",
        ]

        SAFETY_TRIGGERS = ["suicide", "harm", "hurt myself", "kill", "die"]
        LEGAL_TRIGGERS = ["lawyer", "attorney", "legal", "sue", "lawsuit"]

        query_lower = query_result.original_query.lower()
        triggered = [kw for kw in ESCALATION_TRIGGERS if kw in query_lower]

        if not triggered:
            return None

        # Determine priority based on trigger type
        if any(kw in query_lower for kw in SAFETY_TRIGGERS):
            priority = Priority.URGENT
            reason = "Safety concern detected"
        elif any(kw in query_lower for kw in LEGAL_TRIGGERS):
            priority = Priority.HIGH
            reason = "Legal concern detected"
        else:
            priority = Priority.HIGH
            reason = f"Escalation triggered by: {', '.join(triggered)}"

        return RoutingDecision(
            target_agent="escalation_agent",
            parameters={
                "query": query_result.original_query,
                "triggered_keywords": triggered,
            },
            fallback_agent=None,
            priority=priority,
            reasoning=reason,
            requires_escalation=True,
            escalation_reason=reason,
        )

    def _determine_priority(self, query_result: QueryResult) -> Priority:
        """
        Determine the priority level for a routed query.

        Priority is derived from:
        1. Intent type (ESCALATION is highest priority)
        2. Specific entity values (e.g., "ASAP" in topic)
        3. Urgency keywords in original query

        Args:
            query_result: The analyzed query with metadata.

        Returns:
            Priority enum value.
        """
        # High priority intents
        if query_result.intent == Intent.ESCALATION:
            return Priority.HIGH

        # Check for urgency keywords in original query
        if any(
            kw in query_result.original_query.lower()
            for kw in ["urgent", "asap", "immediately", "emergency"]
        ):
            return Priority.HIGH

        # Password reset gets medium priority by default
        if query_result.intent == Intent.PASSWORD_RESET:
            return Priority.MEDIUM

        # Default to low priority
        return Priority.LOW

    def _build_routing_prompt(self, query_result: QueryResult) -> str:
        """
        Build the prompt for routing decision (optional LLM-based routing).

        Note: The solution uses rule-based routing via a static ROUTING_TABLE
        for most cases. This method is provided for complex routing scenarios
        that require LLM reasoning.

        Args:
            query_result: The query to route.

        Returns:
            Formatted prompt string for the LLM.
        """
        # Use rule-based routing via ROUTING_TABLE for most cases
        # LLM-based routing is optional for complex scenarios
        return f"""Query: {query_result.original_query}
Intent: {query_result.intent.value}
Confidence: {query_result.confidence}"""

"""
Router Agent Module - Lab 05 Solution

This agent is the second stage of the three-agent orchestration pipeline.
It receives structured queries from QueryAgent and decides which ActionAgent
should handle the request.

Key Responsibilities:
1. Map intents to appropriate ActionAgents
2. Apply business rules and escalation logic
3. Set priority levels based on urgency
4. Handle edge cases (low confidence, ambiguous queries)
5. Provide fallback options for error handling

The RouterAgent uses a combination of rule-based routing (routing table)
and optional LLM-based reasoning for complex cases.
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from openai import AzureOpenAI

# Import from our query_agent module (same package)
from query_agent import Intent, QueryResult


class Priority(str, Enum):
    """
    Priority levels for request handling.

    Priority affects:
    - Response time expectations
    - Agent selection (high priority may go to specialized agents)
    - Logging and monitoring alerts
    """
    LOW = "low"           # Standard requests, no time pressure
    MEDIUM = "medium"     # Important but not urgent
    HIGH = "high"         # Time-sensitive, needs quick response
    URGENT = "urgent"     # Immediate attention, possible escalation


@dataclass
class RoutingDecision:
    """
    Output from the RouterAgent specifying how to handle a query.

    This dataclass serves as the contract between RouterAgent and ActionAgents.
    It contains all information needed to execute the appropriate action.

    Attributes:
        target_agent: Name of the ActionAgent to invoke (e.g., "retrieve_agent")
        parameters: Dict of parameters to pass to the target agent
        fallback_agent: Backup agent if primary fails (enables graceful degradation)
        priority: Request priority level
        reasoning: Human-readable explanation of routing decision (for logging)
        requires_escalation: Flag if this should go to human support
        escalation_reason: Why escalation is needed
    """
    target_agent: str
    parameters: dict = field(default_factory=dict)
    fallback_agent: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    reasoning: str = ""
    requires_escalation: bool = False
    escalation_reason: Optional[str] = None


class RouterAgent:
    """
    Determines the best action path for a given structured query.

    The RouterAgent acts as a traffic controller, directing queries to the
    appropriate ActionAgent based on intent, confidence, and business rules.
    It also detects escalation triggers and sets priority levels.

    Design Decisions:
    - Uses a static routing table for fast, deterministic routing
    - Escalation triggers are checked before normal routing
    - Low confidence queries are sent to clarification agent
    - Each route includes a fallback for graceful error handling

    Routing Flow:
    1. Check for escalation triggers (keywords, sentiment)
    2. Check query confidence (low confidence -> clarification)
    3. Look up route in routing table based on intent
    4. Build parameters for the target agent
    5. Return RoutingDecision with all context

    Attributes:
        client: Azure OpenAI client (for complex routing decisions)
        model: The deployment name for LLM calls
    """

    # Static routing table: maps Intent -> (primary_agent, fallback_agent)
    # This provides fast, deterministic routing for known intents
    ROUTING_TABLE = {
        Intent.KNOWLEDGE_QUERY: ("retrieve_agent", "general_agent"),
        Intent.PASSWORD_RESET: ("retrieve_agent", "escalation_agent"),
        Intent.TICKET_STATUS: ("ticket_agent", "general_agent"),
        Intent.GENERAL_CHAT: ("general_agent", None),
        Intent.ESCALATION: ("escalation_agent", None),
        Intent.COURSE_INFO: ("retrieve_agent", "general_agent"),
        Intent.UNKNOWN: ("clarification_agent", "general_agent"),
    }

    # Keywords that trigger immediate escalation regardless of intent
    # These indicate situations requiring human intervention
    ESCALATION_TRIGGERS = [
        # Legal/serious situations
        "lawyer", "attorney", "legal", "sue", "lawsuit",
        # Safety concerns
        "suicide", "harm", "hurt myself", "kill", "die",
        # Strong frustration
        "supervisor", "manager", "complaint", "incompetent",
        # Urgency
        "emergency", "urgent", "immediately", "right now", "asap",
        # Explicit requests
        "human", "real person", "speak to someone", "talk to someone",
    ]

    # Confidence threshold below which we request clarification
    CONFIDENCE_THRESHOLD = 0.6

    def __init__(
        self,
        client: Optional[AzureOpenAI] = None,
        model: str = "gpt-4o",
        openai_endpoint: Optional[str] = None,
        openai_key: Optional[str] = None,
    ) -> None:
        """
        Initialize the RouterAgent.

        The client is optional for basic routing (uses static rules).
        It's needed for complex routing decisions that require LLM reasoning.

        Args:
            client: Pre-configured Azure OpenAI client (optional)
            model: The model deployment name for LLM calls
            openai_endpoint: Azure OpenAI endpoint URL (optional)
            openai_key: Azure OpenAI API key (optional)
        """
        # Store client for potential LLM-based routing decisions
        if client:
            self.client = client
        elif openai_endpoint and openai_key:
            self.client = AzureOpenAI(
                azure_endpoint=openai_endpoint,
                api_key=openai_key,
                api_version="2025-01-01-preview",
            )
        else:
            # Try environment variables, but don't fail if not present
            # (routing can work without LLM for basic cases)
            endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
            key = os.environ.get("AZURE_OPENAI_KEY")
            if endpoint and key:
                self.client = AzureOpenAI(
                    azure_endpoint=endpoint,
                    api_key=key,
                    api_version="2025-01-01-preview",
                )
            else:
                self.client = None

        self.model = model

    async def route(self, query: QueryResult) -> RoutingDecision:
        """
        Route a structured query to the appropriate ActionAgent.

        This is the main entry point for the RouterAgent. It applies
        routing logic in the following order:
        1. Check for escalation triggers (highest priority)
        2. Check if QueryAgent already requested clarification
        3. Check confidence level (low -> clarification)
        4. Look up route in routing table
        5. Set priority based on urgency

        Args:
            query: StructuredQuery from QueryAgent

        Returns:
            RoutingDecision specifying which agent to invoke

        Example:
            decision = await router.route(query_result)
            print(f"Routing to: {decision.target_agent}")
            print(f"Priority: {decision.priority}")
        """
        # Step 1: Check for escalation triggers
        # These take precedence over normal routing because they indicate
        # situations requiring human attention
        escalation_result = self._check_escalation_triggers(query)
        if escalation_result:
            return escalation_result

        # Step 2: Handle clarification requests from QueryAgent
        # If the QueryAgent determined it needs more information,
        # route to clarification agent
        if query.requires_clarification:
            return RoutingDecision(
                target_agent="clarification_agent",
                parameters={
                    "question": query.clarification_question,
                    "original_query": query.original_query,
                    "intent_guess": query.intent.value,
                },
                fallback_agent="general_agent",
                priority=Priority.MEDIUM,
                reasoning="QueryAgent requested clarification before proceeding",
            )

        # Step 3: Check confidence level
        # Low confidence means the intent classification is unreliable
        if query.confidence < self.CONFIDENCE_THRESHOLD:
            return RoutingDecision(
                target_agent="clarification_agent",
                parameters={
                    "intent_guess": query.intent.value,
                    "confidence": query.confidence,
                    "original_query": query.original_query,
                },
                fallback_agent="general_agent",
                priority=Priority.MEDIUM,
                reasoning=f"Low confidence ({query.confidence:.2f}) - requesting clarification",
            )

        # Step 4: Look up route in routing table
        primary_agent, fallback_agent = self.ROUTING_TABLE.get(
            query.intent,
            ("general_agent", None)  # Default fallback
        )

        # Step 5: Build parameters for the target agent
        parameters = self._build_parameters(query)

        # Step 6: Determine priority based on urgency metadata
        priority = self._determine_priority(query)

        return RoutingDecision(
            target_agent=primary_agent,
            parameters=parameters,
            fallback_agent=fallback_agent,
            priority=priority,
            reasoning=f"Intent '{query.intent.value}' with confidence {query.confidence:.2f}",
        )

    def _check_escalation_triggers(
        self,
        query: QueryResult,
    ) -> Optional[RoutingDecision]:
        """
        Check if the query contains escalation trigger words.

        Escalation triggers indicate situations that require human
        intervention regardless of the classified intent. These include:
        - Legal concerns (lawyer, sue)
        - Safety concerns (suicide, harm)
        - Strong frustration (complaint, manager)
        - Explicit human requests

        Args:
            query: The QueryResult to check

        Returns:
            RoutingDecision for escalation, or None if no triggers found
        """
        # Convert query to lowercase for case-insensitive matching
        query_lower = query.original_query.lower()

        # Check each trigger word
        triggered_keywords = []
        for trigger in self.ESCALATION_TRIGGERS:
            if trigger in query_lower:
                triggered_keywords.append(trigger)

        # If any triggers found, route to escalation
        if triggered_keywords:
            # Determine priority based on trigger type
            # Safety concerns get urgent priority
            safety_triggers = {"suicide", "harm", "hurt myself", "kill", "die"}
            if any(t in safety_triggers for t in triggered_keywords):
                priority = Priority.URGENT
                escalation_reason = "Safety concern detected - immediate attention required"
            # Legal triggers get high priority
            elif any(t in {"lawyer", "attorney", "legal", "sue"} for t in triggered_keywords):
                priority = Priority.HIGH
                escalation_reason = "Legal concern detected - requires human review"
            else:
                priority = Priority.HIGH
                escalation_reason = f"Escalation trigger detected: {', '.join(triggered_keywords)}"

            return RoutingDecision(
                target_agent="escalation_agent",
                parameters={
                    "original_query": query.original_query,
                    "triggered_keywords": triggered_keywords,
                    "entities": query.get_entities_dict(),
                },
                fallback_agent=None,  # Escalation has no fallback
                priority=priority,
                reasoning=f"Escalation triggers detected: {triggered_keywords}",
                requires_escalation=True,
                escalation_reason=escalation_reason,
            )

        return None

    def _build_parameters(self, query: QueryResult) -> dict:
        """
        Build parameters specific to the target agent based on intent.

        Different agents need different information. This method extracts
        relevant data from the query and packages it appropriately.

        Args:
            query: The QueryResult containing extracted information

        Returns:
            Dictionary of parameters for the target agent
        """
        # Base parameters that all agents need
        params = {
            "query": query.original_query,
            "entities": query.get_entities_dict(),
            "intent": query.intent.value,
            "confidence": query.confidence,
        }

        # Add intent-specific parameters
        if query.intent == Intent.TICKET_STATUS:
            # Ticket agent needs the ticket ID prominently
            ticket_entity = query.get_entity("ticket_id")
            params["ticket_id"] = ticket_entity.value if ticket_entity else None

        elif query.intent == Intent.KNOWLEDGE_QUERY:
            # Retrieve agent needs search-optimized query
            topic_entity = query.get_entity("topic")
            params["topic"] = topic_entity.value if topic_entity else None
            params["search_query"] = query.original_query

        elif query.intent == Intent.PASSWORD_RESET:
            # Password agent needs user identification
            user_entity = query.get_entity("user_name")
            params["user_name"] = user_entity.value if user_entity else None

        elif query.intent == Intent.COURSE_INFO:
            # Course agent needs course identifier
            course_entity = query.get_entity("course_number")
            params["course_number"] = course_entity.value if course_entity else None
            params["search_query"] = query.original_query

        return params

    def _determine_priority(self, query: QueryResult) -> Priority:
        """
        Determine request priority based on query metadata.

        Priority is derived from:
        1. Urgency metadata from QueryAgent
        2. Specific entity values
        3. Intent type

        Args:
            query: The QueryResult with metadata

        Returns:
            Priority enum value
        """
        # Check urgency from metadata
        urgency = query.metadata.get("urgency", "low")

        # Map urgency to priority
        urgency_to_priority = {
            "high": Priority.HIGH,
            "medium": Priority.MEDIUM,
            "low": Priority.LOW,
        }

        priority = urgency_to_priority.get(urgency, Priority.MEDIUM)

        # Escalation intent always gets high priority
        if query.intent == Intent.ESCALATION:
            priority = Priority.HIGH

        return priority

    def get_available_agents(self) -> list[str]:
        """
        Get list of all available action agents.

        Useful for debugging and displaying system capabilities.

        Returns:
            List of agent names that can be routed to
        """
        agents = set()
        for primary, fallback in self.ROUTING_TABLE.values():
            agents.add(primary)
            if fallback:
                agents.add(fallback)
        return sorted(agents)

    def update_routing(
        self,
        intent: Intent,
        primary_agent: str,
        fallback_agent: Optional[str] = None,
    ) -> None:
        """
        Update the routing table dynamically.

        Allows runtime configuration of routing rules without
        code changes.

        Args:
            intent: The Intent to update routing for
            primary_agent: The new primary agent name
            fallback_agent: The new fallback agent name (optional)
        """
        self.ROUTING_TABLE[intent] = (primary_agent, fallback_agent)

    def add_escalation_trigger(self, trigger: str) -> None:
        """
        Add a new escalation trigger keyword.

        Args:
            trigger: The keyword to trigger escalation
        """
        if trigger.lower() not in self.ESCALATION_TRIGGERS:
            self.ESCALATION_TRIGGERS.append(trigger.lower())


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    from query_agent import QueryAgent

    async def main():
        """Demonstrate RouterAgent usage."""
        # Initialize both agents
        query_agent = QueryAgent()
        router_agent = RouterAgent()

        # Test queries
        test_queries = [
            "Hello, how are you?",
            "How do I reset my password?",
            "What's the status of ticket TKT-12345?",
            "I need to speak to a human right now!",
            "I want to talk to a lawyer about this issue",
            "I'm feeling really down, I might hurt myself",  # Safety trigger
            "asdfghjkl",  # Gibberish - low confidence
        ]

        for query_text in test_queries:
            print(f"\n{'='*60}")
            print(f"Query: {query_text}")

            # Stage 1: QueryAgent
            query_result = await query_agent.analyze(query_text)
            print(f"  Intent: {query_result.intent.value}")
            print(f"  Confidence: {query_result.confidence:.2f}")

            # Stage 2: RouterAgent
            decision = await router_agent.route(query_result)
            print(f"  -> Route to: {decision.target_agent}")
            print(f"  -> Priority: {decision.priority.value}")
            print(f"  -> Reasoning: {decision.reasoning}")
            if decision.requires_escalation:
                print(f"  -> ESCALATION: {decision.escalation_reason}")
            if decision.fallback_agent:
                print(f"  -> Fallback: {decision.fallback_agent}")

    asyncio.run(main())

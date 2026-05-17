"""
Action Agent Module - Lab 05 Solution

This module contains the ActionAgents - the third and final stage of the
three-agent orchestration pipeline. ActionAgents execute specific tasks
and generate the final response to the user.

Key Responsibilities:
1. Execute specialized tasks based on routing decisions
2. Use RAG (RetrieveAgent from Lab 04) for knowledge queries
3. Generate user-friendly responses with citations
4. Handle errors gracefully
5. Support escalation and clarification flows

Design Pattern:
All ActionAgents inherit from BaseActionAgent and implement the execute()
method. This allows the pipeline to treat all agents uniformly while
each agent provides specialized behavior.
"""

import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

from openai import AzureOpenAI

# Import routing types from our router module
from router_agent import RoutingDecision, Priority


@dataclass
class ActionResult:
    """
    Output from an ActionAgent - the final response to the user.

    This dataclass represents the complete response including content,
    metadata, and any follow-up actions needed.

    Attributes:
        content: The response text to show the user
        sources: List of citations/sources if RAG was used
        confidence: How confident the agent is in the response (0.0-1.0)
        requires_followup: Whether the conversation needs continuation
        suggested_actions: Buttons/quick replies to suggest to user
        metadata: Additional context for logging/analytics
    """
    content: str
    sources: list[dict] = field(default_factory=list)
    confidence: float = 0.8
    requires_followup: bool = False
    suggested_actions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseActionAgent(ABC):
    """
    Abstract base class for all ActionAgents.

    Provides common initialization and defines the interface that all
    action agents must implement. The execute() method is the main
    entry point called by the pipeline.

    Attributes:
        client: Azure OpenAI client for LLM calls
        model: The deployment name for chat completions
    """

    def __init__(
        self,
        client: Optional[AzureOpenAI] = None,
        model: str = "gpt-4o",
        openai_endpoint: Optional[str] = None,
        openai_key: Optional[str] = None,
    ) -> None:
        """
        Initialize the ActionAgent with Azure OpenAI client.

        Args:
            client: Pre-configured Azure OpenAI client (optional)
            model: The model deployment name
            openai_endpoint: Azure OpenAI endpoint URL (optional)
            openai_key: Azure OpenAI API key (optional)
        """
        if client:
            self.client = client
        else:
            endpoint = openai_endpoint or os.environ.get("AZURE_OPENAI_ENDPOINT")
            key = openai_key or os.environ.get("AZURE_OPENAI_KEY")

            if endpoint and key:
                self.client = AzureOpenAI(
                    azure_endpoint=endpoint,
                    api_key=key,
                    api_version="2025-01-01-preview",
                )
            else:
                raise ValueError(
                    "Azure OpenAI credentials required. Provide client, parameters, "
                    "or set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY environment variables."
                )

        self.model = model

    @abstractmethod
    async def execute(
        self,
        decision: RoutingDecision,
        conversation_history: Optional[list[dict]] = None,
    ) -> ActionResult:
        """
        Execute the agent's task and return a response.

        This is the main entry point called by the pipeline. Each
        concrete agent implementation must provide this method.

        Args:
            decision: RoutingDecision from RouterAgent with parameters
            conversation_history: Previous turns for context (optional)

        Returns:
            ActionResult with the response and metadata
        """
        pass


class RetrieveActionAgent(BaseActionAgent):
    """
    RAG Agent that searches a knowledge base and generates cited responses.

    This agent integrates with the RetrieveAgent from Lab 04 to provide
    grounded answers from a document index. It:
    1. Searches the knowledge base using hybrid search
    2. Builds context from retrieved documents
    3. Generates a response using the context
    4. Includes citations for verifiability

    This is the primary agent for answering knowledge queries, policy
    questions, and how-to requests.
    """

    # System prompt for RAG response generation
    # Key elements:
    # 1. Only use provided context
    # 2. Always cite sources
    # 3. Admit when information isn't available
    RAG_SYSTEM_PROMPT = """You are a helpful assistant answering questions based on a knowledge base.

IMPORTANT RULES:
1. ONLY answer based on the provided context - do not make up information
2. ALWAYS cite your sources using [1], [2], [3], etc. corresponding to the context sections
3. If the context doesn't contain enough information, say "I don't have enough information about that in my knowledge base"
4. Be concise but thorough - provide complete answers without unnecessary verbosity
5. If multiple sources support a point, cite all of them (e.g., "according to [1] and [2]")
6. Format responses clearly with bullet points or numbered lists when appropriate

When you cannot answer from the context:
- Acknowledge the limitation
- Suggest what information might help
- Offer to escalate to human support if needed"""

    def __init__(
        self,
        client: Optional[AzureOpenAI] = None,
        model: str = "gpt-4o",
        retrieve_agent: Optional[Any] = None,
        search_endpoint: Optional[str] = None,
        search_key: Optional[str] = None,
        search_index: Optional[str] = None,
        openai_endpoint: Optional[str] = None,
        openai_key: Optional[str] = None,
    ) -> None:
        """
        Initialize the RetrieveActionAgent.

        Can use an existing RetrieveAgent from Lab 04 or create one
        from search service configuration.

        Args:
            client: Azure OpenAI client
            model: Model deployment name
            retrieve_agent: Pre-configured RetrieveAgent from Lab 04
            search_endpoint: Azure AI Search endpoint
            search_key: Azure AI Search API key
            search_index: Name of the search index
            openai_endpoint: Azure OpenAI endpoint
            openai_key: Azure OpenAI API key
        """
        super().__init__(client, model, openai_endpoint, openai_key)

        # Store retrieve agent if provided, or create later
        self.retrieve_agent = retrieve_agent

        # Store search configuration for creating SearchTool if needed
        self.search_endpoint = search_endpoint or os.environ.get("AZURE_SEARCH_ENDPOINT")
        self.search_key = search_key or os.environ.get("AZURE_SEARCH_KEY")
        self.search_index = search_index or os.environ.get("AZURE_SEARCH_INDEX", "documents")

    def _get_retrieve_agent(self):
        """
        Get or lazily create the RetrieveAgent.

        This allows the agent to be used even if Lab 04's RetrieveAgent
        isn't available - it will fall back to a simpler implementation.
        """
        if self.retrieve_agent:
            return self.retrieve_agent

        # Try to import Lab 04's RetrieveAgent
        try:
            # Add Lab 04 solution to path
            lab04_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "04-build-rag-pipeline",
                "solution"
            )
            if lab04_path not in sys.path:
                sys.path.insert(0, lab04_path)

            from retrieve_agent import RetrieveAgent
            self.retrieve_agent = RetrieveAgent()
            return self.retrieve_agent
        except ImportError:
            # Lab 04 not available - will use fallback
            return None

    async def execute(
        self,
        decision: RoutingDecision,
        conversation_history: Optional[list[dict]] = None,
    ) -> ActionResult:
        """
        Search the knowledge base and generate a cited response.

        Flow:
        1. Extract search query from parameters
        2. Perform hybrid search on knowledge base
        3. Build context from retrieved documents
        4. Generate response with citations
        5. Return result with sources

        Args:
            decision: RoutingDecision with search parameters
            conversation_history: Previous conversation turns

        Returns:
            ActionResult with cited response and sources
        """
        # Extract the search query from parameters
        search_query = decision.parameters.get(
            "search_query",
            decision.parameters.get("query", "")
        )

        # Try to use Lab 04's RetrieveAgent for the search
        retrieve_agent = self._get_retrieve_agent()

        if retrieve_agent:
            # Use the full RAG pipeline from Lab 04
            try:
                rag_response = retrieve_agent.query(
                    question=search_query,
                    top_k=5,
                    temperature=0.3,
                )

                # Convert Lab 04 response to ActionResult
                sources = []
                for i, source in enumerate(rag_response.sources, 1):
                    sources.append({
                        "id": i,
                        "title": source.metadata.get("source", f"Source {i}"),
                        "content_preview": source.content[:200] + "..." if len(source.content) > 200 else source.content,
                        "score": source.score,
                    })

                return ActionResult(
                    content=rag_response.answer,
                    sources=sources,
                    confidence=0.85 if sources else 0.5,
                    requires_followup=len(sources) == 0,
                    suggested_actions=["Ask a follow-up question", "Need more help?"],
                    metadata={
                        "token_usage": rag_response.token_usage,
                        "search_results_count": len(rag_response.sources),
                    }
                )
            except Exception as e:
                # If Lab 04 fails, fall back to direct generation
                print(f"RetrieveAgent error: {e}, falling back to direct generation")

        # Fallback: Generate response without RAG
        # This is used when Lab 04 isn't available or fails
        return await self._generate_fallback_response(
            search_query,
            conversation_history,
        )

    async def _generate_fallback_response(
        self,
        query: str,
        conversation_history: Optional[list[dict]] = None,
    ) -> ActionResult:
        """
        Generate a response without RAG (fallback mode).

        Used when the knowledge base isn't available. The agent
        acknowledges the limitation and offers alternatives.

        Args:
            query: The user's query
            conversation_history: Previous turns

        Returns:
            ActionResult with fallback response
        """
        system_prompt = """You are a helpful assistant. The knowledge base search is temporarily unavailable.

Please:
1. Acknowledge that you cannot search the knowledge base right now
2. Offer general guidance if appropriate (but note it's not from official sources)
3. Suggest the user try again later or speak with human support
4. Be helpful and apologetic about the limitation"""

        messages = [{"role": "system", "content": system_prompt}]

        if conversation_history:
            messages.extend(conversation_history[-6:])  # Last 3 turns

        messages.append({"role": "user", "content": query})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.5,
            max_tokens=500,
        )

        return ActionResult(
            content=response.choices[0].message.content,
            sources=[],
            confidence=0.4,  # Lower confidence without KB
            requires_followup=True,
            suggested_actions=["Try again", "Speak to human support"],
            metadata={"fallback_mode": True},
        )

    def _build_context(self, documents: list[dict]) -> str:
        """
        Build a context string from retrieved documents with numbered citations.

        Args:
            documents: List of document dicts with 'title' and 'content'

        Returns:
            Formatted context string for the LLM
        """
        if not documents:
            return "No relevant documents found in the knowledge base."

        parts = []
        for i, doc in enumerate(documents, 1):
            title = doc.get("title", f"Document {i}")
            content = doc.get("content", "")
            parts.append(f"[{i}] **{title}**\n{content}")

        return "\n\n---\n\n".join(parts)


class GeneralChatAgent(BaseActionAgent):
    """
    Handles general conversation and chitchat.

    This agent responds to greetings, thanks, small talk, and other
    non-specific queries. It maintains a friendly, helpful tone while
    guiding users toward actionable requests.
    """

    SYSTEM_PROMPT = """You are a friendly and helpful support assistant.

For general conversation:
- Be warm and personable
- Acknowledge what the user said
- If they seem to need help, offer to assist with specific tasks
- Keep responses concise (2-3 sentences for greetings)

Things you can help with:
- Answering questions from the knowledge base
- Checking ticket status
- Password reset guidance
- Course information
- Connecting with human support

End responses by gently guiding toward these capabilities when appropriate."""

    async def execute(
        self,
        decision: RoutingDecision,
        conversation_history: Optional[list[dict]] = None,
    ) -> ActionResult:
        """
        Generate a friendly conversational response.

        Args:
            decision: RoutingDecision with query
            conversation_history: Previous turns

        Returns:
            ActionResult with conversational response
        """
        query = decision.parameters.get("query", "")

        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        # Include recent conversation history for context
        if conversation_history:
            messages.extend(conversation_history[-6:])

        messages.append({"role": "user", "content": query})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,  # Higher temp for more natural conversation
            max_tokens=300,
        )

        return ActionResult(
            content=response.choices[0].message.content,
            confidence=0.8,
            suggested_actions=[
                "Ask a question",
                "Check ticket status",
                "Get help with password",
            ],
        )


class ClarificationAgent(BaseActionAgent):
    """
    Asks clarifying questions when intent is unclear or ambiguous.

    This agent is invoked when:
    - QueryAgent has low confidence
    - The query is ambiguous
    - Essential information is missing

    It generates helpful clarification questions to get the conversation
    back on track.
    """

    SYSTEM_PROMPT = """You are a helpful assistant asking for clarification.

The user's message was unclear or ambiguous. Your job is to:
1. Acknowledge what you understood (if anything)
2. Ask a specific, helpful clarification question
3. Provide examples of what you can help with

Keep your response friendly and brief. Don't make the user feel bad
for being unclear - just guide them toward a clearer request.

Format: Start with what you understood, then ask ONE clear question."""

    async def execute(
        self,
        decision: RoutingDecision,
        conversation_history: Optional[list[dict]] = None,
    ) -> ActionResult:
        """
        Generate a clarification request.

        Args:
            decision: RoutingDecision with original query and context
            conversation_history: Previous turns

        Returns:
            ActionResult asking for clarification
        """
        params = decision.parameters

        # Check if a specific clarification question was provided
        if "question" in params and params["question"]:
            return ActionResult(
                content=params["question"],
                confidence=0.6,
                requires_followup=True,
            )

        # Generate a clarification question based on context
        original_query = params.get("original_query", "")
        intent_guess = params.get("intent_guess", "unknown")
        confidence = params.get("confidence", 0.0)

        # Build prompt for generating clarification
        user_prompt = f"""The user said: "{original_query}"

My best guess at their intent: {intent_guess} (confidence: {confidence:.0%})

Generate a brief, friendly clarification question to understand what they need."""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.5,
            max_tokens=200,
        )

        return ActionResult(
            content=response.choices[0].message.content,
            confidence=0.5,
            requires_followup=True,
            suggested_actions=[
                "Ask about policies",
                "Check ticket status",
                "Reset password",
                "Talk to human",
            ],
        )


class EscalationAgent(BaseActionAgent):
    """
    Handles escalation to human support.

    This agent is invoked when:
    - User explicitly requests human support
    - Escalation triggers are detected (legal, safety, etc.)
    - Complex issues that require human judgment

    It acknowledges the need for human support, collects relevant
    information, and provides next steps.
    """

    # Different templates for different escalation reasons
    ESCALATION_TEMPLATES = {
        "safety": """I'm concerned about what you've shared. Your wellbeing is our top priority.

Please know that help is available:
- National Suicide Prevention Lifeline: 988
- Crisis Text Line: Text HOME to 741741
- Campus Counseling Services: [Contact your campus counseling center]

A support team member will reach out to you within 1 hour. In the meantime, please reach out to one of these resources if you need immediate support.

Is there anything else I can help with right now?""",

        "legal": """I understand this involves a legal matter. I'm connecting you with our support team who can properly address your concerns.

A team member will contact you within 2 business hours. Please have any relevant documentation ready.

Your reference number is: {ref_number}

Is there any other information you'd like to provide?""",

        "default": """I understand you'd like to speak with a human support agent.

I'm creating a support ticket for you now. A member of our team will reach out within 2 business hours during business days.

Your reference number is: {ref_number}

In the meantime, is there anything specific you'd like me to document for the support team?""",
    }

    async def execute(
        self,
        decision: RoutingDecision,
        conversation_history: Optional[list[dict]] = None,
    ) -> ActionResult:
        """
        Handle escalation to human support.

        Args:
            decision: RoutingDecision with escalation context
            conversation_history: Previous turns

        Returns:
            ActionResult with escalation acknowledgment
        """
        import uuid

        # Generate a reference number for tracking
        ref_number = f"ESC-{uuid.uuid4().hex[:8].upper()}"

        # Determine escalation type from decision
        triggered_keywords = decision.parameters.get("triggered_keywords", [])
        escalation_reason = decision.escalation_reason or ""

        # Select appropriate template
        if "safety" in escalation_reason.lower() or any(
            kw in ["suicide", "harm", "hurt", "kill", "die"]
            for kw in triggered_keywords
        ):
            template = self.ESCALATION_TEMPLATES["safety"]
            priority_note = "URGENT - Safety Concern"
        elif "legal" in escalation_reason.lower() or any(
            kw in ["lawyer", "attorney", "legal", "sue"]
            for kw in triggered_keywords
        ):
            template = self.ESCALATION_TEMPLATES["legal"]
            priority_note = "HIGH - Legal Matter"
        else:
            template = self.ESCALATION_TEMPLATES["default"]
            priority_note = "Standard Escalation"

        # Format the template
        content = template.format(ref_number=ref_number)

        return ActionResult(
            content=content,
            confidence=1.0,  # High confidence for escalation
            requires_followup=True,
            suggested_actions=[
                "Provide more details",
                "Confirm contact info",
            ],
            metadata={
                "reference_number": ref_number,
                "escalation_reason": escalation_reason,
                "priority": priority_note,
                "triggered_keywords": triggered_keywords,
            },
        )


class TicketStatusAgent(BaseActionAgent):
    """
    Handles ticket status inquiries.

    This agent looks up support tickets and provides status updates.
    In a real implementation, this would integrate with a ticketing
    system API. For the lab, it provides a mock implementation.
    """

    async def execute(
        self,
        decision: RoutingDecision,
        conversation_history: Optional[list[dict]] = None,
    ) -> ActionResult:
        """
        Look up ticket status and return information.

        Args:
            decision: RoutingDecision with ticket_id
            conversation_history: Previous turns

        Returns:
            ActionResult with ticket status
        """
        ticket_id = decision.parameters.get("ticket_id")

        if not ticket_id:
            # No ticket ID provided - ask for it
            return ActionResult(
                content="I'd be happy to check your ticket status. Could you please provide your ticket number? It usually starts with 'TKT-' followed by numbers.",
                confidence=0.8,
                requires_followup=True,
            )

        # Mock ticket lookup - in production, this would call a ticketing API
        # This simulates different ticket states for demonstration
        mock_statuses = {
            "TKT-12345": {
                "status": "In Progress",
                "assigned_to": "Support Team",
                "last_update": "2024-01-15",
                "summary": "Password reset request",
            },
            "TKT-67890": {
                "status": "Resolved",
                "assigned_to": "IT Department",
                "last_update": "2024-01-10",
                "summary": "VPN access issue",
            },
        }

        # Normalize ticket ID format
        ticket_id_upper = ticket_id.upper()
        if not ticket_id_upper.startswith("TKT-"):
            ticket_id_upper = f"TKT-{ticket_id_upper}"

        if ticket_id_upper in mock_statuses:
            ticket = mock_statuses[ticket_id_upper]
            content = f"""Here's the status of your ticket **{ticket_id_upper}**:

- **Status:** {ticket['status']}
- **Assigned to:** {ticket['assigned_to']}
- **Last Updated:** {ticket['last_update']}
- **Summary:** {ticket['summary']}

Is there anything else you'd like to know about this ticket?"""

            return ActionResult(
                content=content,
                confidence=0.95,
                suggested_actions=["Add a comment", "Escalate ticket", "Check another ticket"],
                metadata={"ticket_id": ticket_id_upper, "ticket_data": ticket},
            )
        else:
            # Ticket not found
            content = f"""I couldn't find a ticket with ID **{ticket_id}** in our system.

This could mean:
- The ticket number might be different (check your confirmation email)
- The ticket may have been closed and archived
- There might be a typo in the ticket number

Could you double-check the ticket number? It should look like TKT-12345."""

            return ActionResult(
                content=content,
                confidence=0.7,
                requires_followup=True,
                suggested_actions=["Try another ticket number", "Create new ticket", "Talk to support"],
            )


# Factory function to create all action agents
def create_action_agents(
    client: Optional[AzureOpenAI] = None,
    model: str = "gpt-4o",
    retrieve_agent: Optional[Any] = None,
) -> dict[str, BaseActionAgent]:
    """
    Create all action agents with shared configuration.

    This factory function creates all the ActionAgents used by the pipeline
    with consistent configuration. It's the recommended way to initialize
    the action agent registry.

    Args:
        client: Azure OpenAI client to share across agents
        model: Model deployment name
        retrieve_agent: Optional pre-configured RetrieveAgent from Lab 04

    Returns:
        Dictionary mapping agent names to agent instances
    """
    return {
        "retrieve_agent": RetrieveActionAgent(
            client=client,
            model=model,
            retrieve_agent=retrieve_agent,
        ),
        "general_agent": GeneralChatAgent(client=client, model=model),
        "clarification_agent": ClarificationAgent(client=client, model=model),
        "escalation_agent": EscalationAgent(client=client, model=model),
        "ticket_agent": TicketStatusAgent(client=client, model=model),
        # Password agent uses retrieve agent for KB lookup
        "password_agent": RetrieveActionAgent(
            client=client,
            model=model,
            retrieve_agent=retrieve_agent,
        ),
    }


# Example usage
if __name__ == "__main__":
    import asyncio
    from router_agent import RoutingDecision, Priority

    async def main():
        """Demonstrate ActionAgent usage."""
        # Create agents
        agents = create_action_agents()

        # Test scenarios
        test_cases = [
            (
                "general_agent",
                RoutingDecision(
                    target_agent="general_agent",
                    parameters={"query": "Hello there!"},
                    priority=Priority.LOW,
                    reasoning="General greeting",
                ),
            ),
            (
                "clarification_agent",
                RoutingDecision(
                    target_agent="clarification_agent",
                    parameters={
                        "original_query": "xyz foo bar",
                        "intent_guess": "unknown",
                        "confidence": 0.3,
                    },
                    priority=Priority.MEDIUM,
                    reasoning="Low confidence query",
                ),
            ),
            (
                "ticket_agent",
                RoutingDecision(
                    target_agent="ticket_agent",
                    parameters={"ticket_id": "TKT-12345"},
                    priority=Priority.MEDIUM,
                    reasoning="Ticket status request",
                ),
            ),
            (
                "escalation_agent",
                RoutingDecision(
                    target_agent="escalation_agent",
                    parameters={
                        "original_query": "I need to speak to a human",
                        "triggered_keywords": ["human"],
                    },
                    priority=Priority.HIGH,
                    reasoning="Escalation requested",
                    requires_escalation=True,
                    escalation_reason="User requested human support",
                ),
            ),
        ]

        for agent_name, decision in test_cases:
            print(f"\n{'='*60}")
            print(f"Testing: {agent_name}")
            print(f"Query: {decision.parameters.get('query', decision.parameters)}")

            agent = agents[agent_name]
            result = await agent.execute(decision)

            print(f"\nResponse:\n{result.content}")
            print(f"\nConfidence: {result.confidence}")
            if result.sources:
                print(f"Sources: {[s['title'] for s in result.sources]}")
            if result.suggested_actions:
                print(f"Suggested: {result.suggested_actions}")

    asyncio.run(main())

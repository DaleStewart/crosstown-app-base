"""
Pipeline Orchestrator Module - Lab 05 Solution

This module implements the complete three-agent orchestration pipeline.
It wires together QueryAgent, RouterAgent, and ActionAgents into a
cohesive system that processes user queries end-to-end.

Pipeline Flow:
    User Message --> QueryAgent --> RouterAgent --> ActionAgent --> Response
                          ^                                            |
                          |                                            |
                          +---------- Session Context -----------------+

Key Responsibilities:
1. Initialize and manage all agents
2. Coordinate the three-stage pipeline execution
3. Maintain session context for multi-turn conversations
4. Handle errors gracefully with fallback agents
5. Track metrics and logging for observability

The pipeline is designed for:
- Async/await support for non-blocking I/O
- Dependency injection for testability
- Graceful degradation when components fail
- Multi-turn conversation support
"""

import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from openai import AzureOpenAI

# Import our agent modules
from query_agent import QueryAgent, QueryResult, Intent
from router_agent import RouterAgent, RoutingDecision, Priority
from action_agent import (
    BaseActionAgent,
    ActionResult,
    create_action_agents,
)


# Configure logging for the pipeline
# In production, you'd configure this more robustly
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ConversationTurn:
    """
    Represents a single turn in the conversation.

    A turn consists of a user message and the agent's response,
    along with metadata about how the message was processed.

    Attributes:
        turn_id: Unique identifier for this turn
        timestamp: When the turn occurred
        user_message: The raw user input
        agent_response: The agent's response content
        intent: The classified intent
        entities: Extracted entities from the query
        routing: Where the query was routed
        confidence: Overall confidence in the response
    """
    turn_id: str
    timestamp: datetime
    user_message: str
    agent_response: str
    intent: str
    entities: dict
    routing: str
    confidence: float


@dataclass
class Session:
    """
    Maintains conversation state across multiple turns.

    The session stores:
    - Conversation history for context
    - Extracted entities for reference
    - Arbitrary context data
    - Timing information

    Attributes:
        session_id: Unique identifier for the session
        created_at: When the session was created
        turns: List of conversation turns
        context: Arbitrary key-value storage
        last_activity: Timestamp of last interaction
    """
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    turns: list[ConversationTurn] = field(default_factory=list)
    context: dict = field(default_factory=dict)
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_turn(
        self,
        user_message: str,
        agent_response: str,
        intent: str,
        entities: dict,
        routing: str,
        confidence: float,
    ) -> ConversationTurn:
        """
        Record a new conversation turn.

        Args:
            user_message: What the user said
            agent_response: What the agent responded
            intent: Classified intent
            entities: Extracted entities
            routing: Which agent handled it
            confidence: Response confidence

        Returns:
            The created ConversationTurn
        """
        turn = ConversationTurn(
            turn_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            user_message=user_message,
            agent_response=agent_response,
            intent=intent,
            entities=entities,
            routing=routing,
            confidence=confidence,
        )
        self.turns.append(turn)
        self.last_activity = turn.timestamp

        # Accumulate entities across turns for reference
        self.context.setdefault("all_entities", {}).update(entities)

        return turn

    def get_history(self, max_turns: int = 5) -> list[dict]:
        """
        Get recent conversation history in chat format.

        Returns alternating user/assistant messages suitable for
        including in LLM prompts.

        Args:
            max_turns: Maximum number of turns to include

        Returns:
            List of message dicts with 'role' and 'content'
        """
        recent = self.turns[-max_turns:] if len(self.turns) > max_turns else self.turns
        history = []

        for turn in recent:
            history.append({"role": "user", "content": turn.user_message})
            history.append({"role": "assistant", "content": turn.agent_response})

        return history

    def get_context_summary(self) -> str:
        """
        Generate a summary of the conversation context.

        This summary is included in prompts to help agents understand
        the broader conversation context.

        Returns:
            Human-readable context summary string
        """
        if not self.turns:
            return "This is the start of a new conversation."

        # Collect recent intents and all entities
        recent_intents = [t.intent for t in self.turns[-3:]]
        all_entities = self.context.get("all_entities", {})

        # Build summary parts
        parts = []

        if recent_intents:
            unique_intents = list(set(recent_intents))
            parts.append(f"Recent topics: {', '.join(unique_intents)}")

        if all_entities:
            entity_strs = [f"{k}={v}" for k, v in all_entities.items()]
            parts.append(f"Known information: {', '.join(entity_strs)}")

        parts.append(f"Conversation length: {len(self.turns)} turns")

        return "\n".join(parts)


class SessionManager:
    """
    Manages multiple concurrent conversation sessions.

    Provides CRUD operations for sessions and handles session
    lifecycle (creation, retrieval, cleanup).

    In production, you'd want to:
    - Persist sessions to a database
    - Implement session expiration
    - Add distributed session support
    """

    def __init__(self):
        """Initialize the session manager with empty session store."""
        self._sessions: dict[str, Session] = {}

    def get_or_create(self, session_id: Optional[str] = None) -> Session:
        """
        Get an existing session or create a new one.

        If session_id is provided and exists, returns that session.
        If session_id is provided but doesn't exist, creates with that ID.
        If no session_id, creates a new session with generated ID.

        Args:
            session_id: Optional session ID to look up or use

        Returns:
            Session instance
        """
        # Return existing session if found
        if session_id and session_id in self._sessions:
            session = self._sessions[session_id]
            session.last_activity = datetime.now(timezone.utc)
            return session

        # Create new session
        session = Session(session_id=session_id) if session_id else Session()
        self._sessions[session.session_id] = session
        return session

    def get(self, session_id: str) -> Optional[Session]:
        """
        Get a session by ID.

        Args:
            session_id: The session ID to look up

        Returns:
            Session if found, None otherwise
        """
        return self._sessions.get(session_id)

    def delete(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: The session ID to delete

        Returns:
            True if deleted, False if not found
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def cleanup_old_sessions(self, max_age_minutes: int = 60) -> int:
        """
        Remove sessions older than max_age_minutes.

        Should be called periodically to prevent memory leaks.

        Args:
            max_age_minutes: Maximum session age in minutes

        Returns:
            Number of sessions removed
        """
        from datetime import timedelta

        cutoff = datetime.now(timezone.utc) - timedelta(minutes=max_age_minutes)
        old_sessions = [
            sid for sid, session in self._sessions.items()
            if session.last_activity < cutoff
        ]

        for sid in old_sessions:
            del self._sessions[sid]

        return len(old_sessions)


class AgentPipeline:
    """
    Orchestrates the three-agent pipeline for processing user queries.

    This is the main entry point for the agent system. It coordinates:
    1. QueryAgent - Understanding and structuring the query
    2. RouterAgent - Deciding which action to take
    3. ActionAgent - Executing the action and generating response

    The pipeline maintains session state for multi-turn conversations
    and handles errors gracefully with fallback mechanisms.

    Example usage:
        pipeline = AgentPipeline()

        # First turn
        response, session_id = await pipeline.process("Hello!")

        # Follow-up turn (same session)
        response, _ = await pipeline.process("How do I reset my password?", session_id)

        # Check session
        session = pipeline.session_manager.get(session_id)
        print(f"Turns: {len(session.turns)}")

    Attributes:
        session_manager: Manages conversation sessions
        query_agent: Processes raw queries into structured form
        router_agent: Routes queries to appropriate action agents
        action_agents: Registry of available action agents
    """

    def __init__(
        self,
        openai_client: Optional[AzureOpenAI] = None,
        model_deployment: str = "gpt-4o",
        retrieve_agent: Optional[Any] = None,
        openai_endpoint: Optional[str] = None,
        openai_key: Optional[str] = None,
    ):
        """
        Initialize the pipeline with all agents.

        The pipeline can be initialized with explicit configuration or
        will use environment variables as fallback.

        Args:
            openai_client: Pre-configured Azure OpenAI client
            model_deployment: Model deployment name (e.g., "gpt-4o")
            retrieve_agent: Pre-configured RetrieveAgent from Lab 04
            openai_endpoint: Azure OpenAI endpoint URL
            openai_key: Azure OpenAI API key
        """
        # Create OpenAI client if not provided
        if openai_client:
            self.openai_client = openai_client
        else:
            endpoint = openai_endpoint or os.environ.get("AZURE_OPENAI_ENDPOINT")
            key = openai_key or os.environ.get("AZURE_OPENAI_KEY")

            if not endpoint or not key:
                raise ValueError(
                    "Azure OpenAI credentials required. Provide openai_client, "
                    "explicit parameters, or set environment variables."
                )

            self.openai_client = AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=key,
                api_version="2025-01-01-preview",
            )

        self.model_deployment = model_deployment

        # Initialize session manager
        # This handles multi-turn conversation state
        self.session_manager = SessionManager()

        # Initialize the three agents
        # QueryAgent: Understands and structures user input
        logger.info("Initializing QueryAgent...")
        self.query_agent = QueryAgent(
            client=self.openai_client,
            model=model_deployment,
        )

        # RouterAgent: Decides where to route the query
        logger.info("Initializing RouterAgent...")
        self.router_agent = RouterAgent(
            client=self.openai_client,
            model=model_deployment,
        )

        # ActionAgents: Execute specific tasks
        # Using factory function to create all agents with shared config
        logger.info("Initializing ActionAgents...")
        self.action_agents: dict[str, BaseActionAgent] = create_action_agents(
            client=self.openai_client,
            model=model_deployment,
            retrieve_agent=retrieve_agent,
        )

        logger.info(f"Pipeline initialized with agents: {list(self.action_agents.keys())}")

    async def process(
        self,
        user_message: str,
        session_id: Optional[str] = None,
    ) -> tuple[ActionResult, str]:
        """
        Process a user message through the full pipeline.

        This is the main entry point. It executes the three-stage pipeline:
        1. QueryAgent processes the raw message
        2. RouterAgent determines which agent should handle it
        3. The selected ActionAgent generates the response

        Session state is maintained across calls to support multi-turn
        conversations. Pass the session_id from a previous call to
        continue the same conversation.

        Args:
            user_message: The raw user input to process
            session_id: Optional session ID for continuing a conversation

        Returns:
            Tuple of (ActionResult, session_id)
            - ActionResult contains the response and metadata
            - session_id can be used for follow-up messages

        Raises:
            ValueError: If user_message is empty

        Example:
            # Start a new conversation
            response, session_id = await pipeline.process("Hello!")
            print(response.content)

            # Continue the conversation
            response, _ = await pipeline.process(
                "What's my ticket status?",
                session_id=session_id
            )
        """
        # Validate input
        if not user_message or not user_message.strip():
            return ActionResult(
                content="I didn't receive a message. Could you please try again?",
                confidence=0.0,
                requires_followup=True,
            ), session_id or str(uuid.uuid4())

        # Get or create session for this conversation
        session = self.session_manager.get_or_create(session_id)
        logger.info(f"Processing message in session {session.session_id}")
        logger.debug(f"Session has {len(session.turns)} previous turns")

        try:
            # ============================================
            # STAGE 1: QueryAgent - Understand the query
            # ============================================
            # The QueryAgent transforms raw user input into structured data.
            # It classifies intent, extracts entities, and determines if
            # clarification is needed.
            logger.info("Stage 1: QueryAgent - analyzing query")

            # Provide conversation context to help with follow-up questions
            context_summary = session.get_context_summary()
            structured_query = await self.query_agent.analyze(
                query=user_message,
                conversation_context=context_summary,
            )

            logger.info(
                f"QueryAgent result: intent={structured_query.intent.value}, "
                f"confidence={structured_query.confidence:.2f}, "
                f"entities={structured_query.get_entities_dict()}"
            )

            # ============================================
            # STAGE 2: RouterAgent - Decide the route
            # ============================================
            # The RouterAgent uses the structured query to determine
            # which ActionAgent should handle the request. It also
            # checks for escalation triggers and sets priority.
            logger.info("Stage 2: RouterAgent - determining route")

            routing_decision = await self.router_agent.route(structured_query)

            logger.info(
                f"RouterAgent decision: target={routing_decision.target_agent}, "
                f"priority={routing_decision.priority.value}, "
                f"reasoning={routing_decision.reasoning}"
            )

            if routing_decision.requires_escalation:
                logger.warning(f"ESCALATION: {routing_decision.escalation_reason}")

            # ============================================
            # STAGE 3: ActionAgent - Execute and respond
            # ============================================
            # The selected ActionAgent executes its specialized task
            # and generates the final response to the user.
            logger.info(f"Stage 3: ActionAgent ({routing_decision.target_agent})")

            # Get conversation history for context
            conversation_history = session.get_history(max_turns=5)

            # Execute the action with fallback handling
            response = await self._execute_action(
                decision=routing_decision,
                conversation_history=conversation_history,
            )

            logger.info(
                f"ActionAgent response: confidence={response.confidence:.2f}, "
                f"requires_followup={response.requires_followup}"
            )

            # ============================================
            # Record the turn in session history
            # ============================================
            # This enables multi-turn context for future queries
            session.add_turn(
                user_message=user_message,
                agent_response=response.content,
                intent=structured_query.intent.value,
                entities=structured_query.get_entities_dict(),
                routing=routing_decision.target_agent,
                confidence=response.confidence,
            )

            return response, session.session_id

        except Exception as e:
            # ============================================
            # Error handling - graceful degradation
            # ============================================
            # If anything fails, return a helpful error response
            # rather than crashing. Log the error for debugging.
            logger.exception(f"Pipeline error: {e}")

            error_response = ActionResult(
                content=(
                    "I apologize, but I encountered an issue processing your request. "
                    "Please try again, or let me know if you'd like to speak with "
                    "a human support agent."
                ),
                confidence=0.0,
                requires_followup=True,
                suggested_actions=["Try again", "Speak to human"],
                metadata={"error": str(e)},
            )

            return error_response, session.session_id

    async def _execute_action(
        self,
        decision: RoutingDecision,
        conversation_history: list[dict],
    ) -> ActionResult:
        """
        Execute the selected ActionAgent with fallback handling.

        This method:
        1. Looks up the target agent
        2. Executes it
        3. Falls back to fallback_agent if execution fails
        4. Falls back to general_agent as last resort

        Args:
            decision: RoutingDecision specifying the target agent
            conversation_history: Previous turns for context

        Returns:
            ActionResult from the agent (or fallback)
        """
        # Get the target agent
        agent = self.action_agents.get(decision.target_agent)

        if not agent:
            # Unknown agent - log warning and use general agent
            logger.warning(f"Unknown agent requested: {decision.target_agent}")
            agent = self.action_agents.get("general_agent")

            if not agent:
                # This should never happen, but handle it gracefully
                raise RuntimeError("No agents available")

        try:
            # Execute the primary agent
            return await agent.execute(decision, conversation_history)

        except Exception as e:
            logger.error(f"Agent {decision.target_agent} failed: {e}")

            # Try the fallback agent if specified
            if decision.fallback_agent:
                fallback = self.action_agents.get(decision.fallback_agent)
                if fallback:
                    logger.info(f"Falling back to {decision.fallback_agent}")
                    try:
                        return await fallback.execute(decision, conversation_history)
                    except Exception as fallback_error:
                        logger.error(f"Fallback agent also failed: {fallback_error}")

            # Last resort: try general agent
            general = self.action_agents.get("general_agent")
            if general and decision.target_agent != "general_agent":
                logger.info("Falling back to general_agent as last resort")
                try:
                    return await general.execute(decision, conversation_history)
                except Exception:
                    pass

            # If all else fails, return an error response
            raise RuntimeError(f"All agents failed for decision: {decision}")

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get a session by ID.

        Convenience method for accessing session data.

        Args:
            session_id: The session ID to look up

        Returns:
            Session if found, None otherwise
        """
        return self.session_manager.get(session_id)

    def clear_session(self, session_id: str) -> bool:
        """
        Clear/delete a session.

        Use when conversation is complete or user wants to start fresh.

        Args:
            session_id: The session ID to delete

        Returns:
            True if deleted, False if not found
        """
        return self.session_manager.delete(session_id)


# ============================================
# Example usage and testing
# ============================================
async def demo_pipeline():
    """
    Demonstrate the pipeline with sample conversations.

    This function shows how to use the pipeline for:
    - Single-turn queries
    - Multi-turn conversations
    - Different intent types
    - Escalation handling
    """
    print("=" * 60)
    print("Agent Pipeline Demo")
    print("=" * 60)

    # Initialize the pipeline
    pipeline = AgentPipeline()

    # Demo conversation
    conversation = [
        "Hello!",
        "How do I reset my password?",
        "What if I don't have access to my email?",
        "Can you check ticket TKT-12345?",
        "I need to speak to a human please",
    ]

    session_id = None

    for turn_num, message in enumerate(conversation, 1):
        print(f"\n{'='*60}")
        print(f"Turn {turn_num}")
        print(f"User: {message}")
        print("-" * 60)

        response, session_id = await pipeline.process(message, session_id)

        print(f"Agent: {response.content}")
        print(f"\nConfidence: {response.confidence:.2f}")

        if response.sources:
            print(f"Sources: {[s.get('title', s) for s in response.sources]}")

        if response.suggested_actions:
            print(f"Suggestions: {response.suggested_actions}")

    # Show session summary
    print(f"\n{'='*60}")
    print("Session Summary")
    print("=" * 60)

    session = pipeline.get_session(session_id)
    if session:
        print(f"Session ID: {session.session_id}")
        print(f"Total turns: {len(session.turns)}")
        print(f"Entities collected: {session.context.get('all_entities', {})}")

        print("\nTurn history:")
        for turn in session.turns:
            print(f"  [{turn.intent}] {turn.user_message[:50]}...")


if __name__ == "__main__":
    import asyncio

    # Run the demo
    asyncio.run(demo_pipeline())

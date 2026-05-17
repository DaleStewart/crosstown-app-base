"""
ActionAgent: Ticket creation and knowledge retrieval.

Bounded Authority:
- CAN: Create tickets, search knowledge base, format responses
- CANNOT: Approve refunds, modify records, bypass human review
"""

from typing import Optional

from app.models.enums import ActionStatus, Department, Priority
from app.models.schemas import ActionResult, KnowledgeArticle, RoutingDecision, QueryResult
from app.services.interfaces import (
    KnowledgeServiceInterface,
    LLMServiceInterface,
    TicketServiceInterface,
)


# System prompt for response generation with citations
ACTION_AGENT_SYSTEM_PROMPT = """You are the ActionAgent for University Student Support, responsible for generating helpful responses using knowledge base articles.

Your role is to:
1. Understand the student's specific question or issue
2. Search the provided knowledge base context for relevant information
3. Craft a clear, actionable response that directly addresses their needs
4. Cite all sources used

## Context Format

You will receive knowledge base articles in this format:
<knowledge_base>
[Document ID: KB-XXX]
Title: Article Title
Content: Article content...

[Document ID: KB-YYY]
Title: Another Article
Content: More content...
</knowledge_base>

## Examples

Example 1:
Context:
[Document ID: KB-101]
Title: Password Reset Procedures
Content: To reset your university password: 1) Go to password.university.edu 2) Click "Forgot Password" 3) Enter your student email 4) Check your email for reset link (valid 24 hours) 5) Create new password meeting requirements: 8+ characters, uppercase, number, symbol.

User: "How do I reset my password?"
Response:
"Here's how to reset your university password:

1. Go to password.university.edu
2. Click 'Forgot Password'
3. Enter your student email address
4. Check your email for the reset link (valid for 24 hours)
5. Create a new password with at least 8 characters, including uppercase, number, and symbol

[Source: KB-101]

Is there anything else I can help you with?"

Example 2:
Context:
[Document ID: KB-205]
Title: Transcript Requests
Content: Official transcripts: $10 each, processed within 3-5 business days. Order at registrar.university.edu/transcripts. Rush processing ($25): 24-hour turnaround.

User: "I need a transcript for a job application. How long will it take?"
Response:
"For your job application, you have two options for official transcripts:

**Standard Processing**: $10 per transcript, delivered within 3-5 business days
**Rush Processing**: $25 per transcript, 24-hour turnaround

You can place your order at registrar.university.edu/transcripts [Source: KB-205]

Given this is for a job application, would you like me to note if rush processing might be helpful?"

Example 3:
Context:
[Document ID: KB-312]
Title: Financial Aid Disbursement
Content: Financial aid disburses to student accounts 10 days before classes start. Excess funds are refunded via BankMobile within 3-5 days after disbursement.

User: "Why hasn't my refund check arrived yet? Classes started 2 weeks ago."
Response:
"Let me help you track down your refund. According to our records, financial aid typically disburses 10 days before classes start, with excess funds refunded via BankMobile within 3-5 business days after that. [Source: KB-312]

Since you should have received your refund by now, I recommend:
1. Check your BankMobile account status at bankmobile.com/refundchoices
2. Verify your refund preference is set up correctly

If everything looks correct there but you still haven't received funds, I've created a ticket for our Financial Aid team to investigate. Is there anything else you need?"

## Constraints

1. ONLY use information from the provided knowledge base context - never invent facts
2. Every factual statement MUST include a citation: [Source: KB-XXX]
3. If the context doesn't contain the answer, respond: "I don't have specific information about that in my knowledge base. Let me connect you with a specialist who can help."
4. Do not cite a source if you're not using information from it
5. Maintain a professional, empathetic, student-friendly tone
6. Provide step-by-step instructions when applicable
7. Keep responses concise but complete (aim for 50-150 words unless more detail needed)
8. Include relevant links, deadlines, costs, or contact info from the KB articles
9. End with an offer to help further or a clear next step
10. If a ticket was created, mention the reference number

## Tone Guidelines

- Use "you" and "your" to speak directly to the student
- Acknowledge frustration when sentiment indicates it
- Be solution-focused, not explanation-heavy
- Use formatting (bullets, bold) for scannable responses

## Citation Format

[Source: KB-XXX]

Respond naturally. No JSON required for this agent."""


class ActionAgent:
    """
    Agent responsible for executing actions.

    Takes RoutingDecision and executes:
    - Ticket creation in ticketing system
    - Knowledge base search for relevant articles
    - Response message generation
    """

    # SLA hours to human-readable format
    SLA_DESCRIPTIONS: dict[int, str] = {
        1: "within 1 hour",
        4: "within 4 hours",
        24: "within 1 business day",
        48: "within 2 business days",
        72: "within 3 business days",
    }

    # Minimum relevance score to consider KB as sufficient for self-service
    # If top article has relevance >= this threshold, no ticket is created for low/medium priority
    KB_SELF_SERVICE_THRESHOLD: float = 0.5

    def __init__(
        self,
        ticket_service: TicketServiceInterface,
        knowledge_service: KnowledgeServiceInterface,
        llm_service: LLMServiceInterface,
    ) -> None:
        """
        Initialize ActionAgent with required services.

        Args:
            ticket_service: Service for ticket operations.
            knowledge_service: Service for KB search.
            llm_service: Service for message generation.
        """
        self._tickets = ticket_service
        self._knowledge = knowledge_service
        self._llm = llm_service

    async def execute(
        self,
        query_result: QueryResult,
        routing_decision: RoutingDecision,
        student_id_hash: str,
        original_message: str,
    ) -> ActionResult:
        """
        Execute actions based on routing decision.

        Args:
            query_result: Intent analysis from QueryAgent.
            routing_decision: Routing decision from RouterAgent.
            student_id_hash: Hashed student identifier.
            original_message: The user's original message (for ticket description).

        Returns:
            ActionResult with ticket info, KB articles, and response message.
        """
        ticket_id: Optional[str] = None
        ticket_url: Optional[str] = None
        status: ActionStatus

        # Search knowledge base FIRST to determine if self-service is possible
        knowledge_articles, kb_article_contents = await self._search_knowledge_with_content(
            query_result=query_result,
            department=routing_decision.department,
            original_message=original_message,
        )

        # Determine if we should create a ticket (considering KB results)
        should_create_ticket = self._should_create_ticket(
            routing_decision=routing_decision,
            knowledge_articles=knowledge_articles,
        )

        if should_create_ticket:
            # Generate ticket summary and description
            summary = self._generate_ticket_summary(query_result)
            description = self._generate_ticket_description(
                query_result=query_result,
                original_message=original_message,
            )

            # Create the ticket
            ticket_id, ticket_url = await self._tickets.create_ticket(
                department=routing_decision.department,
                priority=routing_decision.priority,
                summary=summary,
                description=description,
                student_id_hash=student_id_hash,
                entities=query_result.entities,
            )

            if routing_decision.escalate_to_human:
                status = ActionStatus.ESCALATED
            else:
                status = ActionStatus.CREATED
        else:
            status = ActionStatus.KB_ONLY

        # Generate human-readable response time
        estimated_response_time = self._format_sla(routing_decision.suggested_sla_hours)

        # Generate user-friendly response message with KB content for self-service
        user_message = await self._llm.generate_response_message(
            intent=query_result.intent,
            department=routing_decision.department,
            ticket_id=ticket_id,
            escalated=routing_decision.escalate_to_human,
            estimated_response_time=estimated_response_time,
            original_message=original_message,
            knowledge_articles=knowledge_articles,
            kb_article_contents=kb_article_contents,
            system_prompt=ACTION_AGENT_SYSTEM_PROMPT,
        )

        return ActionResult(
            ticket_id=ticket_id,
            ticket_url=ticket_url,
            department=routing_decision.department,
            status=status,
            knowledge_articles=knowledge_articles,
            estimated_response_time=estimated_response_time,
            escalated=routing_decision.escalate_to_human,
            user_message=user_message,
        )

    async def create_clarification_response(
        self,
        clarification_question: str,
    ) -> ActionResult:
        """
        Create a response requesting clarification.

        Args:
            clarification_question: The question to ask the user.

        Returns:
            ActionResult with pending_clarification status.
        """
        return ActionResult(
            ticket_id=None,
            ticket_url=None,
            department=Department.IT,  # Placeholder
            status=ActionStatus.PENDING_CLARIFICATION,
            knowledge_articles=[],
            estimated_response_time="pending",
            escalated=False,
            user_message=clarification_question,
        )

    def _should_create_ticket(
        self,
        routing_decision: RoutingDecision,
        knowledge_articles: list[KnowledgeArticle],
    ) -> bool:
        """
        Determine if a ticket should be created.

        First-contact resolution (no ticket) is preferred when:
        - No escalation required
        - Low/medium priority
        - KB has a highly relevant article that can answer the question

        Args:
            routing_decision: The routing decision from RouterAgent.
            knowledge_articles: KB articles found for this query.

        Returns:
            True if a ticket should be created, False for KB-only self-service.
        """
        # Always create ticket for escalations (human review required)
        if routing_decision.escalate_to_human:
            return True

        # Always create ticket for high priority/urgent requests
        if routing_decision.priority in (Priority.HIGH, Priority.URGENT):
            return True

        # For low/medium priority: check if KB can handle it
        # If we have a highly relevant KB article, skip ticket creation
        if knowledge_articles:
            top_article = knowledge_articles[0]
            if top_article.relevance_score >= self.KB_SELF_SERVICE_THRESHOLD:
                # KB can answer this - no ticket needed (first-contact resolution)
                return False

        # No good KB match - create ticket for human follow-up
        return True

    def _generate_ticket_summary(self, query_result: QueryResult) -> str:
        """Generate a brief summary for the ticket."""
        intent_display = query_result.intent.replace("_", " ").title()
        return f"{intent_display} request"

    def _generate_ticket_description(
        self,
        query_result: QueryResult,
        original_message: str,
    ) -> str:
        """Generate ticket description without exposing raw PII."""
        lines = [
            f"Intent: {query_result.intent}",
            f"Category: {query_result.intent_category.value}",
            f"Confidence: {query_result.confidence:.2f}",
            f"Sentiment: {query_result.sentiment.value}",
        ]

        if query_result.entities:
            entities_str = ", ".join(
                f"{k}: {v}" for k, v in query_result.entities.items()
            )
            lines.append(f"Entities: {entities_str}")

        if query_result.urgency_indicators:
            lines.append(f"Urgency: {', '.join(query_result.urgency_indicators)}")

        if query_result.pii_detected:
            lines.append("Note: PII detected in original message (not included)")
        else:
            # Include sanitized version of message if no PII
            lines.append(f"User message: {original_message[:500]}")

        return "\n".join(lines)

    async def _search_knowledge_with_content(
        self,
        query_result: QueryResult,
        department: Department,
        original_message: str = "",
    ) -> tuple[list[KnowledgeArticle], list[dict]]:
        """Search knowledge base for relevant articles with full content.

        Uses the student's original message as the primary search query for best
        vector and keyword relevance, falling back to intent/entity terms when
        the original message is unavailable.
        """
        # Use the student's original message for search — it contains the most
        # natural language for both embedding similarity and BM25 keyword matching.
        # Intent labels (e.g. "financial_aid_inquiry") and entity slugs
        # (e.g. "financial_aid_disbursement") are classification artifacts that
        # perform poorly as search queries.
        if original_message.strip():
            search_query = original_message.strip()
        else:
            # Fallback: reconstruct from intent + entities (legacy behavior)
            search_terms = [query_result.intent.replace("_", " ")]
            for value in query_result.entities.values():
                if isinstance(value, str):
                    search_terms.append(value.replace("_", " "))
            search_query = " ".join(search_terms)

        # Don't filter by department for escalated requests
        dept_filter = None if department == Department.ESCALATE_TO_HUMAN else department

        articles, contents = await self._knowledge.search_with_content(
            query=search_query,
            department=dept_filter,
            limit=3,
        )

        return articles, contents

    async def _search_knowledge(
        self,
        query_result: QueryResult,
        department: Department,
        original_message: str = "",
    ) -> list[KnowledgeArticle]:
        """Search knowledge base for relevant articles (legacy method)."""
        articles, _ = await self._search_knowledge_with_content(
            query_result, department, original_message
        )
        return articles

    def _format_sla(self, hours: int) -> str:
        """Format SLA hours as human-readable string."""
        if hours in self.SLA_DESCRIPTIONS:
            return self.SLA_DESCRIPTIONS[hours]

        if hours < 24:
            return f"within {hours} hours"
        else:
            days = hours // 24
            return f"within {days} business day{'s' if days > 1 else ''}"

"""
QueryAgent: Intent detection and entity extraction.

Bounded Authority:
- CAN: Analyze text, detect intent, extract entities, detect PII, assess sentiment
- CANNOT: Create tickets, access knowledge base, make routing decisions
"""
# ruff: noqa: E501, I001

from app.models.schemas import ConversationTurn, QueryResult
from app.services.interfaces import LLMServiceInterface


# System prompt for intent classification
QUERY_AGENT_SYSTEM_PROMPT = """You are the QueryAgent for University Student Support, responsible for classifying incoming student inquiries.

Your task is to analyze each student message and return a structured JSON classification with intent, department routing, entities, sentiment, and escalation flags.

Analyze the student's message and return a JSON object with:
{
    "intent": "string - specific intent like password_reset, login_issues, transcript_request, financial_aid_inquiry, facilities_issue, grade_appeal, course_enrollment, parking_permit, general_question, request_human",
    "intent_category": "one of: ACCOUNT_ACCESS, ACADEMIC_RECORDS, FINANCIAL, FACILITIES, ENROLLMENT, STUDENT_SERVICES, POLICY_EXCEPTION, GENERAL_INQUIRY, STATUS_CHECK, HUMAN_REQUEST",
    "department": "one of: IT, HR, REGISTRAR, FINANCIAL_AID, FACILITIES, STUDENT_AFFAIRS, CAMPUS_SAFETY, ESCALATE_TO_HUMAN",
    "confidence": "float 0.0-1.0 indicating how confident you are",
    "entities": {
        "building": "extracted building name if mentioned",
        "course_code": "extracted course code if mentioned",
        "system": "IT system mentioned like Canvas, Outlook, etc.",
        "date": "any date or deadline mentioned"
    },
    "requires_escalation": "boolean - true if: mentions appeal/waiver/refund, Title IX, mental health, threats, or explicitly asks for human",
    "escalation_reason": "if escalation needed: policy_keyword_detected, sensitive_topic, user_requested_human, or null",
    "pii_detected": "boolean - true if SSN, credit card, or other sensitive personal data found",
    "pii_types": ["list of PII types found: ssn, credit_card, phone, email, dob"],
    "sentiment": "one of: NEUTRAL, FRUSTRATED, URGENT, SATISFIED",
    "urgency_indicators": ["list of urgency words found: urgent, asap, emergency, deadline, today, tonight"]
}

## Department Routing Guide

- IT: password, login, email, WiFi, software, computer issues, Canvas, Blackboard, LMS
- REGISTRAR: transcripts, enrollment verification, grades, graduation, degree audit, course history
- FINANCIAL_AID: scholarships, grants, loans, tuition payment, financial aid disbursement, account balance
- FACILITIES: building issues, maintenance, room booking, elevators
- STUDENT_AFFAIRS: housing, dining, student organizations, parking, student ID, address changes
- CAMPUS_SAFETY: safety concerns, lost items, emergencies
- HR: employment, work-study, payroll
- ESCALATE_TO_HUMAN: appeals, refunds, waivers, Title IX, mental health, threats, explicit human request

## Examples

Example 1:
User: "I can't log into Canvas to submit my assignment that's due tonight."
Response:
{
  "intent": "login_issues",
  "intent_category": "ACCOUNT_ACCESS",
  "department": "IT",
  "confidence": 0.95,
  "entities": {"system": "Canvas", "date": "tonight"},
  "requires_escalation": false,
  "escalation_reason": null,
  "pii_detected": false,
  "pii_types": [],
  "sentiment": "FRUSTRATED",
  "urgency_indicators": ["tonight"]
}

Example 2:
User: "My financial aid was supposed to be disbursed last week but my account still shows a balance."
Response:
{
  "intent": "financial_aid_inquiry",
  "intent_category": "FINANCIAL",
  "department": "FINANCIAL_AID",
  "confidence": 0.92,
  "entities": {"topic": "financial_aid_disbursement"},
  "requires_escalation": false,
  "escalation_reason": null,
  "pii_detected": false,
  "pii_types": [],
  "sentiment": "FRUSTRATED",
  "urgency_indicators": []
}

Example 3:
User: "How do I request an official transcript for my grad school application?"
Response:
{
  "intent": "transcript_request",
  "intent_category": "ACADEMIC_RECORDS",
  "department": "REGISTRAR",
  "confidence": 0.97,
  "entities": {"document_type": "official_transcript", "purpose": "grad_school"},
  "requires_escalation": false,
  "escalation_reason": null,
  "pii_detected": false,
  "pii_types": [],
  "sentiment": "NEUTRAL",
  "urgency_indicators": []
}

Example 4:
User: "I want to speak with a real person about my situation."
Response:
{
  "intent": "request_human",
  "intent_category": "HUMAN_REQUEST",
  "department": "ESCALATE_TO_HUMAN",
  "confidence": 0.95,
  "entities": {},
  "requires_escalation": true,
  "escalation_reason": "user_requested_human",
  "pii_detected": false,
  "pii_types": [],
  "sentiment": "FRUSTRATED",
  "urgency_indicators": []
}

Example 5:
User: "I need to appeal my grade in CS 201. This is unfair."
Response:
{
  "intent": "grade_appeal",
  "intent_category": "POLICY_EXCEPTION",
  "department": "ESCALATE_TO_HUMAN",
  "confidence": 0.93,
  "entities": {"course_code": "CS201"},
  "requires_escalation": true,
  "escalation_reason": "policy_keyword_detected",
  "pii_detected": false,
  "pii_types": [],
  "sentiment": "FRUSTRATED",
  "urgency_indicators": []
}

Example 6:
User: "Hi there!"
Response:
{
  "intent": "general_question",
  "intent_category": "GENERAL_INQUIRY",
  "department": "IT",
  "confidence": 0.85,
  "entities": {},
  "requires_escalation": false,
  "escalation_reason": null,
  "pii_detected": false,
  "pii_types": [],
  "sentiment": "NEUTRAL",
  "urgency_indicators": []
}

## Constraints

1. Always return valid JSON in the exact format specified above — all fields are required
2. If a query could fit multiple categories, select the MOST SPECIFIC one
3. Set confidence below 0.7 when the intent is ambiguous or unclear
4. Extract relevant entities: system names, deadlines, document types, dates, course codes
5. Never attempt to resolve the issue — classification only
6. Set requires_escalation to true for: appeals, refunds, waivers, Title IX, mental health concerns, threats, or explicit requests for a human agent
7. Flag PII if detected (SSN patterns, credit card numbers) but do not echo them back
8. Detect urgency indicators: "urgent", "ASAP", "deadline", "today", "tonight", "emergency"

Respond with valid JSON only. No additional text."""

# System prompt for clarification questions
CLARIFICATION_SYSTEM_PROMPT = """You are a helpful university support assistant.

When a student's query is ambiguous, generate a friendly, concise clarification question.
- Keep it brief (1-2 sentences)
- Offer clear options when possible
- Be warm and student-friendly

Example:
Student: "I need help with my account"
You: "I'd be happy to help! Are you having trouble logging in, or do you need to update your account information like your address or email?"
"""


class QueryAgent:
    """
    Agent responsible for understanding user queries.

    Takes raw user input and produces structured QueryResult with:
    - Detected intent and category
    - Extracted entities (buildings, courses, systems, etc.)
    - Confidence score
    - PII detection flags
    - Sentiment analysis
    - Urgency indicators
    """

    def __init__(self, llm_service: LLMServiceInterface) -> None:
        """
        Initialize QueryAgent with LLM service.

        Args:
            llm_service: LLM service for intent classification.
        """
        self._llm = llm_service

    async def analyze(
        self,
        message: str,
        conversation_history: list[ConversationTurn] | None = None,
    ) -> QueryResult:
        """
        Analyze a user message to detect intent and extract information.

        Args:
            message: The user's support query.
            conversation_history: Previous conversation turns for context.

        Returns:
            QueryResult with intent, entities, confidence, and metadata.
        """
        # Convert conversation history to OpenAI message format
        # ConversationTurn contains metadata (intent, turn_number) — not raw messages.
        # Pack prior turns as a single context message so the LLM can see the conversation arc.
        history_dicts = None
        if conversation_history:
            history_summary = "; ".join(
                f"Turn {turn.turn_number}: intent={turn.intent}"
                + (f", ticket={turn.ticket_id}" if turn.ticket_id else "")
                + (", escalated" if turn.escalated else "")
                for turn in conversation_history[-5:]
            )
            history_dicts = [
                {
                    "role": "user",
                    "content": f"[Conversation context — prior turns: {history_summary}]",
                }
            ]

        # Use LLM service for classification with our system prompt
        result = await self._llm.classify_intent(
            message=message,
            conversation_history=history_dicts,
            system_prompt=QUERY_AGENT_SYSTEM_PROMPT,
        )

        return result

    async def generate_clarification(
        self,
        message: str,
        possible_intents: list[str],
    ) -> str:
        """
        Generate a clarification question when intent is ambiguous.

        Args:
            message: The ambiguous user message.
            possible_intents: List of possible intent classifications.

        Returns:
            A user-friendly clarification question.
        """
        return await self._llm.generate_clarification_question(
            message=message,
            possible_intents=possible_intents,
            system_prompt=CLARIFICATION_SYSTEM_PROMPT,
        )

"""
Intent classifier for university student support queries.

Classifies student queries into 7 domain-specific intent categories:
- financial_aid: FAFSA, scholarships, grants, loans, tuition assistance
- registration: Course enrollment, transcripts, graduation, add/drop
- housing: Dormitories, roommates, move-in/move-out, residence halls
- it_support: Password resets, email, Canvas/LMS, WiFi, login issues
- academic_advising: Major/minor selection, degree planning, course advice
- student_accounts: Bills, refunds, payment plans, account holds, bursar
- general: Ambiguous queries or those requiring human escalation
"""

from dataclasses import dataclass
from typing import Literal

# Intent type - 7 domain-specific categories only
IntentType = Literal[
    "financial_aid",
    "registration",
    "housing",
    "it_support",
    "academic_advising",
    "student_accounts",
    "general",
]


@dataclass
class ClassificationResult:
    """Result of intent classification with confidence score."""

    intent: IntentType
    confidence: float


# Negation words that reduce keyword weights when they precede keywords
NEGATION_WORDS = {
    "not",
    "no",
    "don't",
    "doesn't",
    "didn't",
    "won't",
    "can't",
    "cannot",
    "couldn't",
    "never",
    "neither",
    "nor",
    "isn't",
    "aren't",
    "wasn't",
    "weren't",
}

# Negation discount factor: multiply keyword weight by this when negated
NEGATION_DISCOUNT = 0.2


# Weighted keyword patterns for each intent category
# Higher weights = stronger signals
INTENT_PATTERNS: dict[IntentType, dict[str, float]] = {
    "financial_aid": {
        # Strong indicators (3.0)
        "fafsa": 3.0,
        "financial aid": 3.0,
        "scholarship": 3.0,
        "pell grant": 3.0,
        "satisfactory academic progress": 3.0,
        "aid appeal": 2.5,
        # Medium indicators (2.0)
        "grant": 2.0,
        "student loan": 2.0,
        "work study": 2.0,
        "work-study": 2.0,
        "aid package": 2.0,
        "tuition assistance": 2.0,
        "sap": 2.0,
        "outside scholarship": 2.0,
        "loan": 1.5,
        "income change": 1.5,
        "professional judgment": 1.5,
        # Weak indicators (1.0)
        "aid": 1.0,
    },
    "registration": {
        # Strong indicators (3.0)
        "register for class": 3.0,
        "add/drop": 3.0,
        "official transcript": 3.0,
        "transcript": 3.0,
        "degree audit": 3.0,
        "transfer credit": 3.0,
        "transfer credits": 3.0,
        "course catalog": 3.0,
        "waitlist": 3.0,
        # Medium indicators (2.0)
        "registration": 2.0,
        "enroll": 2.0,
        "drop a class": 2.0,
        "add a class": 2.0,
        "graduation requirement": 2.0,
        "apply to graduate": 2.0,
        "retroactive withdrawal": 2.0,
        "permission number": 2.0,
        "registration hold": 2.0,
        "articulation": 2.0,
        # Weak indicators (1.0)
        "graduate": 1.0,
        "class schedule": 1.0,
        "schedule": 0.5,
    },
    "housing": {
        # Strong indicators (3.0)
        "housing": 3.0,
        "dorm": 3.0,
        "dormitory": 3.0,
        "residence hall": 3.0,
        "roommate": 3.0,
        "room assignment": 3.0,
        "housing application": 3.0,
        "housing contract": 3.0,
        "room swap": 3.0,
        # Medium indicators (2.0)
        "move-in": 2.0,
        "move-out": 2.0,
        "housing deposit": 2.0,
        "on-campus housing": 2.0,
        "break my housing contract": 2.0,
        "swap request": 2.0,
        "room switch": 2.0,
        # Weak indicators (1.0)
        "room": 1.0,
        "living": 0.5,
        "apartment": 1.0,
        "residence": 1.0,
    },
    "it_support": {
        # Strong indicators (3.0)
        "password": 3.0,
        "reset password": 3.0,
        "forgot password": 3.0,
        "can't log in": 3.0,
        "cannot log in": 3.0,
        "wifi": 3.0,
        "wi-fi": 3.0,
        "canvas": 3.0,
        "office 365": 3.0,
        "o365": 3.0,
        "teams": 3.0,
        "phishing": 3.0,
        "hacked": 3.0,
        # Medium indicators (2.0)
        "login": 2.0,
        "log in": 2.0,
        "student portal": 2.0,
        "email": 2.0,
        "student email": 2.0,
        "lms": 2.0,
        "vpn": 2.0,
        "two-factor": 2.0,
        "2fa": 2.0,
        "mfa": 2.0,
        "sso": 2.0,
        "internet": 2.0,
        "data recovery": 2.0,
        "shared drive": 2.0,
        # Weak indicators (1.0)
        "access": 1.0,
        "account": 1.0,
        "network": 1.0,
        "not working": 1.0,
    },
    "academic_advising": {
        # Strong indicators (3.0)
        "academic advisor": 3.0,
        "declare major": 3.0,
        "change major": 3.0,
        "degree plan": 3.0,
        "what classes should": 3.0,
        "academic probation": 3.0,
        # Medium indicators (2.0)
        "advisor": 2.0,
        "advising": 2.0,
        "switch major": 2.0,
        "double major": 2.0,
        "minor": 2.0,
        "add a minor": 2.0,
        "after graduation": 2.0,
        "do after graduation": 2.0,
        "5th year": 2.0,
        "career planning": 2.0,
        "course planning": 2.0,
        # Weak indicators (1.0)
        "career": 1.0,
        "degree": 1.0,
        "major": 1.0,
        "taking time off": 1.0,
    },
    "student_accounts": {
        # Strong indicators (3.0)
        "tuition bill": 3.0,
        "pay my tuition": 3.0,
        "pay tuition": 3.0,
        "payment plan": 3.0,
        "tuition payment": 3.0,
        "bursar": 3.0,
        "student accounts": 3.0,
        "refund": 3.0,
        "got a bill": 3.0,
        # Medium indicators (2.0)
        "payment deadline": 2.0,
        "refund deadline": 2.0,
        "charge on my account": 2.0,
        "unrecognized charge": 2.0,
        "collections": 2.0,
        "sent to collections": 2.0,
        "account hold": 2.0,
        "financial hold": 2.0,
        "billing": 2.0,
        # Weak indicators (1.0)
        "balance": 1.0,
        "balance due": 1.0,
        "bill": 1.0,
        "owe": 1.0,
        "payment": 1.0,
        "fee": 1.0,
        "charge": 1.0,
    },
    "general": {
        # Catch-all indicators for ambiguous queries
        "library": 2.0,
        "dining": 2.0,
        "cafeteria": 2.0,
        "club": 1.5,
        "student id": 2.0,
        "id card": 2.0,
        "file a complaint": 2.5,
        "accessibility": 2.0,
        "international student": 1.5,
        "don't know where to turn": 2.0,
        "don't know what kind of help": 2.0,
        "i need help but": 1.5,
        "talk to someone": 1.5,
    },
}


class IntentClassifier:
    """
    Intent classifier for student support queries.

    Uses weighted keyword matching to classify queries into 7 intent categories.
    """

    def __init__(self, confidence_threshold: float = 0.5):
        """
        Initialize the classifier.

        Args:
            confidence_threshold: Minimum score difference to avoid 'general'
        """
        self.confidence_threshold = confidence_threshold
        self.patterns = INTENT_PATTERNS

    def classify(self, text: str) -> ClassificationResult:
        """
        Classify a student query into an intent category.

        Args:
            text: The student's question or request

        Returns:
            ClassificationResult with intent and confidence score
        """
        # Handle null/empty input
        if text is None or not isinstance(text, str):
            return ClassificationResult(intent="general", confidence=0.3)

        normalized = text.strip().lower()
        if not normalized:
            return ClassificationResult(intent="general", confidence=0.3)

        # Calculate scores for each intent
        scores: dict[IntentType, float] = {}
        for intent, patterns in self.patterns.items():
            scores[intent] = self._calculate_score(normalized, patterns)

        # Find the top two intents
        sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_intent, top_score = sorted_intents[0]
        second_intent, second_score = sorted_intents[1] if len(sorted_intents) > 1 else (None, 0)

        # If top score is too low, default to general
        if top_score < 1.5:
            return ClassificationResult(intent="general", confidence=0.4)

        # If scores are too close (ambiguous), fall back to general
        score_gap = top_score - second_score
        if score_gap < self.confidence_threshold and top_score < 3.0:
            if top_intent != "general":
                return ClassificationResult(intent="general", confidence=0.5)

        # Calculate confidence based on score magnitude and gap
        confidence = min(0.95, 0.5 + (top_score / 10) + (score_gap / 5))

        return ClassificationResult(intent=top_intent, confidence=confidence)

    def _calculate_score(self, text: str, patterns: dict[str, float]) -> float:
        """Calculate weighted score for a set of patterns, with negation handling."""
        score = 0.0
        for pattern, weight in patterns.items():
            if pattern in text:
                # Check if this keyword is negated
                if self._is_negated(text, pattern):
                    # Apply negation discount
                    score += weight * NEGATION_DISCOUNT
                else:
                    score += weight
        return score

    def _is_negated(self, text: str, keyword: str) -> bool:
        """
        Check if a keyword appears in a negation context.
        
        Returns True if keyword is preceded by a negation word within 5 words.
        """
        # Find position of keyword in text
        keyword_pos = text.find(keyword)
        if keyword_pos == -1:
            return False
        
        # Extract text before keyword (up to 20 chars to cover ~5 words)
        start_pos = max(0, keyword_pos - 20)
        context_before = text[start_pos:keyword_pos]
        
        # Check for negation words in context
        words_before = context_before.split()
        for word in words_before[-5:]:  # Check last 5 words before keyword
            if word in NEGATION_WORDS:
                return True
        
        return False


# Convenience function for simple usage
def classify_intent(query: str) -> IntentType:
    """
    Classify a student query into one of 7 intent categories.

    Args:
        query: The student's question or request

    Returns:
        The classified intent category
    """
    classifier = IntentClassifier()
    result = classifier.classify(query)
    return result.intent

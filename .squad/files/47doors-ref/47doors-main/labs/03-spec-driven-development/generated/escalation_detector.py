"""
Escalation Detector - Generated from your-spec.md and your-constitution.md

Feature: Escalation Trigger and Triage Assistant
Spec: labs/03-spec-driven-development/your-spec.md
Constitution: labs/03-spec-driven-development/your-constitution.md

This module implements deterministic escalation detection per the specification.
"""

from dataclasses import dataclass, field
from typing import Optional
import json
from pathlib import Path


# FR-006: Support configurable keyword list without code changes
# Keywords can be loaded from external JSON config
DEFAULT_SAFETY_TERMS = {
    "harm", "hurt", "danger", "attack", "suicide", "threat",
    "crisis", "emergency", "violence", "self-harm",
}

DEFAULT_POLICY_TERMS = {
    "appeal", "waiver", "exception", "refund", "override",
    "complaint", "grievance", "dispute",
}

# Constitution: Governance Notes - escalate legal/medical/Title IX/safety
GOVERNANCE_TERMS = {
    "title ix", "legal", "lawyer", "attorney", "lawsuit",
    "medical", "disability", "accommodation", "ferpa",
    "discrimination", "harassment",
}


def load_keywords_from_config(config_path: Optional[Path] = None) -> tuple[set, set, set]:
    """FR-006: Load configurable keywords from external JSON file."""
    if config_path and config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
        return (
            set(config.get("safety_terms", DEFAULT_SAFETY_TERMS)),
            set(config.get("policy_terms", DEFAULT_POLICY_TERMS)),
            set(config.get("governance_terms", GOVERNANCE_TERMS)),
        )
    return DEFAULT_SAFETY_TERMS, DEFAULT_POLICY_TERMS, GOVERNANCE_TERMS


@dataclass
class EscalationDecision:
    """
    FR-003: Structured output with escalate, priority, and reasons fields.
    FR-005: Include confidence score and rule hits in decision metadata.
    """
    escalate: bool
    priority: str  # "urgent", "high", "normal"
    reasons: list[str] = field(default_factory=list)
    confidence: float = 0.0
    # FR-004: Preserve original user text for human reviewers
    original_text: str = ""
    rule_hits: list[str] = field(default_factory=list)


def detect_escalation(
    user_text: str,
    config_path: Optional[Path] = None,
) -> EscalationDecision:
    """
    Detect escalation triggers in user text.
    
    FR-001: Detect crisis/safety keywords → urgent escalation priority.
    FR-002: Detect policy keywords (appeal, waiver, exception, refund).
    FR-007: Provide fallback response when confidence is low.
    
    Constitution Principle 1: Safety first - prioritize user wellbeing.
    Constitution Principle 2: Deterministic behavior - explicit rules.
    Constitution Principle 3: Transparent outputs - reason codes included.
    Constitution Principle 4: Human collaboration - escalate on low confidence.
    
    Constitution Prohibited: Never suppress crisis indicators.
    """
    # Load configurable keywords (FR-006)
    safety_terms, policy_terms, governance_terms = load_keywords_from_config(config_path)
    
    text = (user_text or "").lower()
    reasons: list[str] = []
    rule_hits: list[str] = []
    
    # FR-001: Detect crisis and safety keywords
    matched_safety = [term for term in safety_terms if term in text]
    if matched_safety:
        reasons.append("safety_signal")
        rule_hits.extend([f"safety:{term}" for term in matched_safety])
    
    # FR-002: Detect policy keywords
    matched_policy = [term for term in policy_terms if term in text]
    if matched_policy:
        reasons.append("policy_signal")
        rule_hits.extend([f"policy:{term}" for term in matched_policy])
    
    # Constitution Governance: Escalate legal/medical/Title IX/safety topics
    matched_governance = [term for term in governance_terms if term in text]
    if matched_governance:
        reasons.append("governance_escalation")
        rule_hits.extend([f"governance:{term}" for term in matched_governance])
    
    # Determine priority and confidence
    if reasons:
        # FR-001: Safety signals get urgent priority
        if "safety_signal" in reasons:
            priority = "urgent"
            confidence = 0.95
        elif "governance_escalation" in reasons:
            priority = "urgent"  # Constitution requires immediate escalation
            confidence = 0.90
        else:
            priority = "high"
            confidence = 0.85
        
        # FR-003, FR-004, FR-005: Return structured decision with all metadata
        return EscalationDecision(
            escalate=True,
            priority=priority,
            reasons=reasons,
            confidence=confidence,
            original_text=user_text,  # FR-004: Preserve original text
            rule_hits=rule_hits,  # FR-005: Include rule hits
        )
    
    # FR-007: Fallback when no triggers detected
    # Constitution Principle 4: Escalate when confidence is low
    return EscalationDecision(
        escalate=False,
        priority="normal",
        reasons=[],
        confidence=0.4,
        original_text=user_text,
        rule_hits=[],
    )

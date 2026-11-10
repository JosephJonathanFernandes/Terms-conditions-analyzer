"""Risk assessment engine.

Hybrid approach: rule-based detection assigns risk levels with rationale
linked to supporting source text. LLM can refine later.
"""

from typing import List, Dict, Any

# Category -> base risk level and rationale template.
BASE_RISK: Dict[str, dict] = {
    "data_collection": {"level": "MEDIUM", "rationale": "The document describes collection of personal data."},
    "personal_information_usage": {"level": "MEDIUM", "rationale": "Personal information may be used for purposes beyond core service delivery."},
    "third_party_data_sharing": {"level": "HIGH", "rationale": "Data may be shared with third parties; scope and recipients should be reviewed."},
    "cookies_and_tracking": {"level": "LOW", "rationale": "Standard cookie/tracking practices disclosed."},
    "data_retention": {"level": "MEDIUM", "rationale": "Data retention period affects how long your information is stored."},
    "account_deletion": {"level": "MEDIUM", "rationale": "Account deletion process may be difficult or unclear."},
    "user_rights": {"level": "LOW", "rationale": "User rights are addressed."},
    "payment_terms": {"level": "MEDIUM", "rationale": "Financial commitments are described."},
    "automatic_subscription_renewal": {"level": "HIGH", "rationale": "Automatic renewal may continue charges unless cancelled."},
    "cancellation_and_refunds": {"level": "MEDIUM", "rationale": "Refund and cancellation terms affect your financial exposure."},
    "intellectual_property_rights": {"level": "LOW", "rationale": "Intellectual property terms disclosed."},
    "content_ownership": {"level": "MEDIUM", "rationale": "Clarifies who owns user-generated content."},
    "license_granted_to_platform": {"level": "HIGH", "rationale": "You grant the platform broad rights to your content."},
    "account_suspension": {"level": "MEDIUM", "rationale": "Account may be suspended under stated conditions."},
    "termination_without_notice": {"level": "HIGH", "rationale": "Account may be terminated without prior warning."},
    "liability_limitations": {"level": "HIGH", "rationale": "The platform limits its liability, reducing your recourse."},
    "indemnification": {"level": "HIGH", "rationale": "You may be required to indemnify the platform."},
    "arbitration": {"level": "MEDIUM", "rationale": "Disputes may be resolved via arbitration rather than court."},
    "jurisdiction": {"level": "LOW", "rationale": "Governing law and venue specified."},
    "dispute_resolution": {"level": "MEDIUM", "rationale": "Dispute resolution process may limit legal options (e.g., class-action waiver)."},
    "unilateral_modification_of_terms": {"level": "HIGH", "rationale": "Terms may be changed unilaterally, potentially without notice."},
}

# Keywords that escalate risk within a category.
ESCALATE_KEYWORDS = {
    "third_party_data_sharing": ["sell", "broker", "unlimited", "any third party"],
    "automatic_subscription_renewal": ["without notice", "difficult to cancel", "no cancellation"],
    "termination_without_notice": ["immediate", "at any time", "sole discretion"],
    "indemnification": ["all claims", "unlimited", "including legal fees"],
    "liability_limitations": ["all liability", "no liability whatsoever", "consequential"],
    "unilateral_modification_of_terms": ["without notice", "at any time", "continued use constitutes acceptance"],
    "data_retention": ["indefinitely", "permanently", "no deletion"],
    "account_deletion": ["cannot delete", "no deletion", "impossible"],
}

# Keywords that de-escalate risk.
DEESCALATE_KEYWORDS = {
    "third_party_data_sharing": ["only with your consent", "you may opt out", "no sale of data"],
    "automatic_subscription_renewal": ["easy to cancel", "clear cancellation", "reminder before renewal"],
    "termination_without_notice": ["notice will be provided", "reasonable notice"],
    "indemnification": ["except for our negligence", "reasonable"],
    "liability_limitations": ["except for gross negligence", "willful misconduct"],
    "unilateral_modification_of_terms": ["notice will be provided", "material changes require consent"],
}

RISK_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}


def assess_risk(clause: dict, full_text: str = "") -> dict:
    """Assign a risk level and rationale to a detected clause.

    Considers wording, scope, conditions, exceptions, and context — not
    merely the presence of a clause.
    """
    category = clause.get("category", "")
    text = clause.get("original_text", "").lower()
    base = BASE_RISK.get(category, {"level": "LOW", "rationale": "General clause."})
    level = base["level"]
    rationale = base["rationale"]

    # Escalate based on escalation keywords found in the clause text.
    for kw in ESCALATE_KEYWORDS.get(category, []):
        if kw in text:
            level = _escalate(level)
            rationale += f" Contains escalating language: '{kw}'."

    # De-escalate based on mitigating language.
    mitigated = False
    for kw in DEESCALATE_KEYWORDS.get(category, []):
        if kw in text:
            mitigated = True
            rationale += f" Mitigating language: '{kw}'."

    if mitigated and level != "LOW":
        level = _deescalate(level)

    return {
        "risk_level": level,
        "risk_rationale": rationale,
        "confidence": clause.get("confidence", 0.7),
    }


def _escalate(level: str) -> str:
    order = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    idx = order.index(level) if level in order else 0
    return order[min(idx + 1, 3)]


def _deescalate(level: str) -> str:
    order = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    idx = order.index(level) if level in order else 3
    return order[max(idx - 1, 0)]


def compute_distribution(clauses: List[dict]) -> Dict[str, int]:
    dist = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for c in clauses:
        lvl = c.get("risk_level", "LOW")
        dist[lvl] = dist.get(lvl, 0) + 1
    return dist

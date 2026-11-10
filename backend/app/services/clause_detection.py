"""Rule-based clause detection into 21 legal categories.

Deterministic keyword/pattern matching serves as the baseline classifier.
Results are explainable: each match is linked to its source text.
"""

import re
from typing import List, Tuple

# 21 clause categories -> list of (keywords, weight) patterns.
# Higher weight = stronger signal. Order matters for first-match preference.
CLAUSE_PATTERNS = [
    ("data_collection", [
        (r"collect(?:s|ed|ing)?\s+(?:personal\s+)?(?:data|information)", 3),
        (r"we\s+collect", 2),
        (r"information\s+we\s+collect", 2),
        (r"gather\s+(?:personal\s+)?(?:data|information)", 2),
    ]),
    ("personal_information_usage", [
        (r"use\s+(?:your|personal|user)\s+(?:data|information)", 3),
        (r"personal\s+information\s+is\s+used", 2),
        (r"we\s+use\s+your\s+information", 2),
        (r"for\s+(?:marketing|advertising|promotional)\s+purposes", 2),
    ]),
    ("third_party_data_sharing", [
        (r"share\s+(?:your|personal|user)\s+(?:data|information)\s+with", 3),
        (r"third.?part", 2),
        (r"sell\s+(?:your|personal|user)\s+(?:data|information)", 3),
        (r"disclose\s+(?:your|personal|user)\s+(?:data|information)", 2),
        (r"data\s+(?:brokers|partners|vendors)", 2),
    ]),
    ("cookies_and_tracking", [
        (r"cookie", 2),
        (r"tracking\s+(?:technology|pixel|beacon)", 2),
        (r"web\s+beacon", 2),
        (r"similar\s+technologies", 1),
        (r"do\s+not\s+track", 1),
    ]),
    ("data_retention", [
        (r"retain\s+(?:your|personal|user)\s+(?:data|information)", 3),
        (r"keep\s+(?:your|personal|user)\s+(?:data|information)", 2),
        (r"storage\s+period", 2),
        (r"how\s+long\s+we\s+keep", 2),
        (r"retention\s+period", 2),
    ]),
    ("account_deletion", [
        (r"delete\s+your\s+account", 3),
        (r"deactivate\s+(?:your|the)\s+account", 2),
        (r"close\s+your\s+account", 2),
        (r"account\s+(?:cancellation|termination)\s+request", 2),
        (r"right\s+to\s+(?:be\s+forgotten|erasure)", 2),
    ]),
    ("user_rights", [
        (r"your\s+rights", 2),
        (r"right\s+to\s+access", 2),
        (r"right\s+to\s+correct", 2),
        (r"right\s+to\s+object", 2),
        (r"data\s+(?:subject|access)\s+request", 2),
    ]),
    ("payment_terms", [
        (r"payment", 2),
        (r"billing", 2),
        (r"subscription\s+fee", 2),
        (r"charge\s+(?:your|the)\s+(?:card|account)", 2),
        (r"recurring\s+(?:payment|charge)", 2),
        (r"invoice", 1),
    ]),
    ("automatic_subscription_renewal", [
        (r"automatic\s+renew", 3),
        (r"auto.?renew", 3),
        (r"renew\s+automatically", 3),
        (r"renewal\s+will\s+occur", 2),
        (r"continues\s+until\s+you\s+cancel", 2),
    ]),
    ("cancellation_and_refunds", [
        (r"cancel", 2),
        (r"refund", 2),
        (r"money.back", 2),
        (r"cancel\s+(?:at\s+any\s+time|anytime)", 2),
        (r"refund\s+policy", 2),
    ]),
    ("intellectual_property_rights", [
        (r"intellectual\s+property", 3),
        (r"copyright", 2),
        (r"trademark", 2),
        (r"ip\s+rights", 2),
        (r"proprietary\s+rights", 2),
    ]),
    ("content_ownership", [
        (r"you\s+(?:retain|keep)\s+(?:ownership|title)", 2),
        (r"you\s+own\s+(?:your|the)\s+content", 2),
        (r"content\s+you\s+(?:upload|post|submit)", 2),
        (r"user-generated\s+content", 2),
        (r"ownership\s+of\s+content", 2),
    ]),
    ("license_granted_to_platform", [
        (r"grant\s+us\s+a\s+license", 3),
        (r"license\s+(?:to\s+)?(?:use|host|store|reproduce)", 2),
        (r"non-exclusive\s+license", 2),
        (r"worldwide\s+license", 2),
        (r"royalty.free\s+license", 2),
    ]),
    ("account_suspension", [
        (r"suspend\s+(?:your|the)\s+account", 3),
        (r"account\s+suspension", 2),
        (r"disable\s+(?:your|the)\s+account", 2),
        (r"we\s+may\s+suspend", 2),
    ]),
    ("termination_without_notice", [
        (r"terminate\s+(?:your|the)\s+account\s+(?:at\s+any\s+time|without\s+notice)", 3),
        (r"terminate\s+without\s+notice", 3),
        (r"immediate\s+termination", 2),
        (r"we\s+may\s+terminate", 2),
        (r"at\s+our\s+(?:sole|discretion)", 1),
    ]),
    ("liability_limitations", [
        (r"limit.*liability", 3),
        (r"liability\s+is\s+limited", 3),
        (r"not\s+liable\s+for", 2),
        (r"disclaim.*liability", 2),
        (r"no\s+liability", 2),
        (r"consequential\s+damages", 2),
    ]),
    ("indemnification", [
        (r"indemnif", 3),
        (r"hold\s+harmless", 2),
        (r"defend\s+and\s+indemnify", 2),
        (r"you\s+agree\s+to\s+indemnify", 3),
    ]),
    ("arbitration", [
        (r"arbitrat", 3),
        (r"binding\s+arbitration", 3),
        (r"arbitration\s+agreement", 2),
        (r"dispute\s+resolution\s+via\s+arbitration", 2),
    ]),
    ("jurisdiction", [
        (r"jurisdiction", 2),
        (r"governing\s+law", 2),
        (r"laws\s+of\s+(?:the\s+)?state\s+of", 2),
        (r"laws\s+of\s+[A-Z][a-z]+", 2),
        (r"courts\s+of", 2),
        (r"venue", 1),
    ]),
    ("dispute_resolution", [
        (r"dispute\s+resolution", 3),
        (r"resolve\s+disputes", 2),
        (r"class\s+action\s+waiver", 3),
        (r"waive\s+(?:your|the)\s+right\s+to\s+(?:a\s+)?(?:jury|class)", 2),
    ]),
    ("unilateral_modification_of_terms", [
        (r"modify\s+these\s+terms", 3),
        (r"change\s+these\s+terms", 3),
        (r"update\s+these\s+terms", 2),
        (r"we\s+may\s+change\s+(?:the\s+)?terms", 3),
        (r"terms\s+may\s+change", 2),
        (r"at\s+any\s+time\s+without\s+notice", 1),
    ]),
]


def detect_clauses(text: str) -> List[dict]:
    """Segment text into paragraphs and classify each into categories.

    Returns a list of dicts with: category, original_text, paragraph_index,
    matched_patterns, confidence.
    """
    paragraphs = [p.strip() for p in re.split(r"\n{2,}|(?<=[.!?])\s+(?=[A-Z])", text) if p.strip()]
    results = []

    for idx, para in enumerate(paragraphs):
        matches = _match_category(para)
        if not matches:
            continue
        # Pick the best category by total weight; tie-break by first occurrence.
        best = max(matches, key=lambda m: m["weight"])
        results.append({
            "category": best["category"],
            "original_text": para,
            "paragraph_index": idx,
            "matched_patterns": [p for m in matches for p in m.get("patterns", [])],
            "confidence": min(0.95, 0.5 + 0.1 * best["weight"]),
        })

    return results


def _match_category(text: str) -> List[dict]:
    lower = text.lower()
    matches = []
    for category, patterns in CLAUSE_PATTERNS:
        total_weight = 0
        matched_patterns = []
        for pattern, weight in patterns:
            if re.search(pattern, lower, re.IGNORECASE):
                total_weight += weight
                matched_patterns.append(pattern)
        if total_weight > 0:
            matches.append({
                "category": category,
                "weight": total_weight,
                "patterns": matched_patterns,
            })
    return matches

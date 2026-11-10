"""Plain-language simplification service.

Uses an LLM provider when available; falls back to rule-based simplification.
Never changes the original meaning of the legal text.
"""

from typing import Optional

from app.services.llm_provider import get_provider


def simplify(
    original_text: str,
    category: str,
    level: str = "standard",
    context: str = "",
) -> dict:
    """Return {simplified_text, rationale, confidence} for a clause."""
    provider = get_provider()
    if provider.is_available():
        return provider.simplify(original_text, category, level, context)
    return _rule_based_simplify(original_text, category, level)


def _rule_based_simplify(original_text: str, category: str, level: str) -> dict:
    """Deterministic fallback simplification. Preserves meaning."""
    text = original_text.strip()
    if level == "simple":
        simplified = (
            f"In plain terms: this section covers {category.replace('_', ' ')}. "
            f"It says: {text[:400]}"
        )
    elif level == "detailed":
        simplified = (
            f"Detailed explanation ({category.replace('_', ' ')}): "
            f"This clause describes obligations and rights related to "
            f"{category.replace('_', ' ')}. In the document it states: "
            f"{text}. "
            "Note: This is an informational simplification, not legal advice."
        )
    else:  # standard
        simplified = (
            f"This section is about {category.replace('_', ' ')}. "
            f"In simpler language: {text[:500]}"
        )

    return {
        "simplified_text": simplified,
        "rationale": "Rule-based simplification (no LLM configured).",
        "confidence": 0.6,
    }

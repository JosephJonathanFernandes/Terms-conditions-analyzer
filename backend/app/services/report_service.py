"""Report generation service.

Produces a structured report dict (used for PDF export downstream).
"""

from typing import Dict, Any


def build_report(analysis: dict, document: dict) -> Dict[str, Any]:
    clauses = analysis.get("clauses", [])
    risk_dist = analysis.get("risk_distribution") or {}
    categories: Dict[str, int] = {}
    for c in clauses:
        cat = c.get("category", "uncategorized")
        categories[cat] = categories.get(cat, 0) + 1

    concerning = [c for c in clauses if c.get("risk_level") in ("HIGH", "CRITICAL")]

    return {
        "document": {
            "filename": document.get("filename"),
            "source_type": document.get("source_type"),
            "source_url": document.get("source_url"),
            "uploaded_at": document.get("uploaded_at"),
        },
        "analysis": {
            "id": analysis.get("id"),
            "summary": analysis.get("summary"),
            "explanation_level": analysis.get("explanation_level"),
            "llm_mode": analysis.get("llm_mode"),
            "created_at": analysis.get("created_at"),
        },
        "risk_distribution": risk_dist,
        "category_distribution": categories,
        "total_clauses": len(clauses),
        "concerning_clauses": concerning,
        "clauses": clauses,
        "disclaimer": (
            "ClauseClear provides informational explanations only. "
            "This is not legal advice. Consult a qualified attorney for "
            "legal interpretation of terms and conditions."
        ),
    }

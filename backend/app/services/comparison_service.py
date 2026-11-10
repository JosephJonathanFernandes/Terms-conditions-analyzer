"""Document comparison service.

Compares two analyses and identifies added, removed, and modified clauses,
plus impact on user obligations, data collection, payments, liability, etc.
"""

from typing import List, Dict, Any


def compare(analysis_a: dict, analysis_b: dict) -> dict:
    clauses_a = {c["id"]: c for c in analysis_a.get("clauses", [])}
    clauses_b = {c["id"]: c for c in analysis_b.get("clauses", [])}

    # Match clauses by category + text similarity (simple approach).
    added = []
    removed = []
    modified = []

    ids_a = set(clauses_a.keys())
    ids_b = set(clauses_b.keys())

    for cid in ids_b - ids_a:
        added.append(_diff_entry(clauses_b[cid], "added", clauses_a))
    for cid in ids_a - ids_b:
        removed.append(_diff_entry(clauses_a[cid], "removed", clauses_b))

    # Modified: same category, different text.
    for cid in ids_a & ids_b:
        ca, cb = clauses_a[cid], clauses_b[cid]
        if ca.get("original_text") != cb.get("original_text"):
            modified.append({
                "clause_id": cid,
                "category": ca.get("category"),
                "change_type": "modified",
                "text_a": ca.get("original_text"),
                "text_b": cb.get("original_text"),
                "impact": _impact(ca.get("category"), ca.get("original_text"), cb.get("original_text")),
            })

    impact_summary = _summarize_impact(added, removed, modified)

    return {
        "analysis_id_a": analysis_a.get("id"),
        "analysis_id_b": analysis_b.get("id"),
        "added": added,
        "removed": removed,
        "modified": modified,
        "impact_summary": impact_summary,
    }


def _diff_entry(clause: dict, change_type: str, other: dict) -> dict:
    return {
        "clause_id": clause.get("id"),
        "category": clause.get("category"),
        "change_type": change_type,
        "text_a": clause.get("original_text") if change_type != "added" else None,
        "text_b": clause.get("original_text") if change_type != "removed" else None,
        "impact": _impact(clause.get("category"), clause.get("original_text"), None),
    }


def _impact(category: str, text_a: str, text_b: str) -> str:
    cat = (category or "").lower()
    if "automatic_subscription_renewal" in cat or "payment" in cat:
        return "May affect billing and renewal obligations."
    if "third_party_data_sharing" in cat:
        return "May change how your data is shared."
    if "termination" in cat or "account_suspension" in cat:
        return "May affect account access."
    if "liability" in cat or "indemnification" in cat:
        return "May affect your legal exposure."
    if "unilateral_modification" in cat:
        return "Terms may change more freely."
    return "Review the change for practical impact."


def _summarize_impact(added: List[dict], removed: List[dict], modified: List[dict]) -> str:
    total = len(added) + len(removed) + len(modified)
    if total == 0:
        return "No significant clause differences detected."
    parts = []
    if added:
        parts.append(f"{len(added)} new clause(s) added")
    if removed:
        parts.append(f"{len(removed)} clause(s) removed")
    if modified:
        parts.append(f"{len(modified)} clause(s) modified")
    return "; ".join(parts) + ". Review for impact on your rights and obligations."

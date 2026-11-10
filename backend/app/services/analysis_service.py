"""Analysis service: orchestration of detection, risk, simplification, storage."""

import json
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.database.base import SessionLocal, session_scope
from app.models.analysis import Analysis, AnalysisStatus
from app.models.clause import Clause
from app.models.document import Document, DocumentStatus
from app.services.clause_detection import detect_clauses
from app.services.risk_engine import assess_risk, compute_distribution
from app.services.simplification_service import simplify
from app.services.rag_service import answer_question as rag_answer
from app.services.comparison_service import compare as svc_compare
from app.services.report_service import build_report


def _llm_available() -> bool:
    from app.services.llm_provider import get_provider
    return get_provider().is_available()


def _suggested_questions(category: str) -> list:
    mapping = {
        "third_party_data_sharing": ["Can they share my data with third parties?", "Who do they share data with?"],
        "automatic_subscription_renewal": ["Will my subscription renew automatically?", "How do I cancel?"],
        "cancellation_and_refunds": ["Can I get a refund?", "What is the cancellation policy?"],
        "account_deletion": ["Can I delete my account?", "How do I deactivate my account?"],
        "termination_without_notice": ["Can they terminate my account without notice?"],
        "liability_limitations": ["What is their liability if something goes wrong?"],
        "indemnification": ["Do I have to indemnify them?"],
        "unilateral_modification_of_terms": ["Can they change the terms at any time?"],
        "content_ownership": ["Who owns the content I upload?"],
    }
    return mapping.get(category, ["What does this clause mean for me?"])


def _build_summary(document_title: str, clauses: list, distribution: dict) -> str:
    high = distribution.get("HIGH", 0) + distribution.get("CRITICAL", 0)
    total = len(clauses)
    if high == 0:
        return f"This document contains {total} classified clauses with no high-risk findings. Review the clause explorer for details."
    return (
        f"This document contains {total} classified clauses, {high} of which are "
        f"flagged as HIGH or CRITICAL risk. Pay close attention to concerning clauses "
        f"in the explorer."
    )


def _serialize(analysis: Analysis, clauses: list) -> dict:
    return {
        "id": analysis.id,
        "document_id": analysis.document_id,
        "status": analysis.status,
        "summary": analysis.summary,
        "risk_distribution": json.loads(analysis.risk_distribution_json) if analysis.risk_distribution_json else {},
        "explanation_level": analysis.explanation_level,
        "llm_mode": analysis.llm_mode,
        "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
        "clauses": [
            {
                "id": c.id,
                "analysis_id": c.analysis_id,
                "category": c.category,
                "original_text": c.original_text,
                "simplified_text": c.simplified_text,
                "risk_level": c.risk_level,
                "risk_rationale": c.risk_rationale,
                "confidence": c.confidence,
                "source_location": c.source_location,
                "paragraph_index": c.paragraph_index,
                "evidence": json.loads(c.evidence_json) if c.evidence_json else None,
                "suggested_questions": json.loads(c.suggested_questions_json) if c.suggested_questions_json else None,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in clauses
        ],
    }


def run_analysis(document_id: int, explanation_level: str = "standard") -> dict:
    """Run full analysis pipeline on a document."""
    with session_scope() as db:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")

        text = document.extracted_text or ""
        if not text:
            raise ValueError("Document has no extracted text")

        # Create analysis record.
        analysis = Analysis(
            document_id=document_id,
            status=AnalysisStatus.pending.value,
            explanation_level=explanation_level,
            llm_mode="ai" if _llm_available() else "rule-based",
        )
        db.add(analysis)
        db.flush()  # get analysis.id within the transaction

        try:
            # Detect clauses.
            detected = detect_clauses(text)

            clauses_out = []
            for det in detected:
                risk = assess_risk(det, full_text=text)
                simplified = simplify(
                    det["original_text"],
                    det["category"],
                    level=explanation_level,
                    context=risk["risk_rationale"],
                )
                clause = Clause(
                    analysis_id=analysis.id,
                    category=det["category"],
                    original_text=det["original_text"],
                    simplified_text=simplified.get("simplified_text"),
                    risk_level=risk["risk_level"],
                    risk_rationale=risk["risk_rationale"],
                    confidence=risk["confidence"],
                    source_location=f"Paragraph {det.get('paragraph_index', 0) + 1}",
                    paragraph_index=det.get("paragraph_index"),
                    evidence_json=json.dumps({"matched_patterns": det.get("matched_patterns", [])}),
                    suggested_questions_json=json.dumps(_suggested_questions(det["category"])),
                )
                db.add(clause)
                clauses_out.append(clause)

            distribution = compute_distribution([{"risk_level": c.risk_level} for c in clauses_out])

            # Generate summary.
            summary = _build_summary(document.filename, clauses_out, distribution)

            analysis.status = AnalysisStatus.completed.value
            analysis.summary = summary
            analysis.risk_distribution_json = json.dumps(distribution)
            db.flush()

            return _serialize(analysis, clauses_out)

        except Exception as exc:
            analysis.status = AnalysisStatus.failed.value
            db.flush()
            raise RuntimeError(f"Analysis pipeline failed: {exc}") from exc


def get_analysis(analysis_id: int) -> Optional[dict]:
    with SessionLocal() as db:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            return None
        clauses = db.query(Clause).filter(Clause.analysis_id == analysis_id).all()
        return _serialize(analysis, clauses)


def list_history() -> list:
    with SessionLocal() as db:
        analyses = (
            db.query(Analysis)
            .join(Document, Analysis.document_id == Document.id)
            .order_by(Analysis.created_at.desc())
            .all()
        )
        result = []
        for a in analyses:
            doc = a.document
            result.append({
                "id": a.id,
                "document_id": a.document_id,
                "filename": doc.filename if doc else "Unknown",
                "source_type": doc.source_type if doc else "unknown",
                "status": a.status,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            })
        return result


def delete_analysis(analysis_id: int) -> bool:
    with SessionLocal() as db:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            return False
        db.delete(analysis)
        db.commit()
        return True


def chat(analysis_id: int, question: str) -> dict:
    with SessionLocal() as db:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            raise ValueError("Analysis not found")
        clauses = db.query(Clause).filter(Clause.analysis_id == analysis_id).all()
        clause_dicts = [
            {
                "id": c.id,
                "category": c.category,
                "original_text": c.original_text,
                "source_location": c.source_location,
            }
            for c in clauses
        ]
        return rag_answer(question, clause_dicts)


def compare_analyses(analysis_id_a: int, analysis_id_b: int) -> dict:
    with SessionLocal() as db:
        a = db.query(Analysis).filter(Analysis.id == analysis_id_a).first()
        b = db.query(Analysis).filter(Analysis.id == analysis_id_b).first()
        if not a or not b:
            raise ValueError("One or both analyses not found")
        a_data = _serialize(a, db.query(Clause).filter(Clause.analysis_id == a.id).all())
        b_data = _serialize(b, db.query(Clause).filter(Clause.analysis_id == b.id).all())
        return svc_compare(a_data, b_data)


def get_report(analysis_id: int) -> dict:
    with SessionLocal() as db:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            raise ValueError("Analysis not found")
        document = db.query(Document).filter(Document.id == analysis.document_id).first()
        a_data = _serialize(analysis, db.query(Clause).filter(Clause.analysis_id == analysis.id).all())
        return build_report(a_data, {
            "filename": document.filename if document else "Unknown",
            "source_type": document.source_type if document else "unknown",
            "source_url": document.source_url if document else None,
            "uploaded_at": document.uploaded_at.isoformat() if document and document.uploaded_at else None,
        })

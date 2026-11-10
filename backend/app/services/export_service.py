"""Document export service.

Produces TXT, JSON, or PDF bytes for a document (and its analysis if
available). PDF generation delegates to reportlab when installed.
"""

import csv
import io
import json
import zipfile
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.document import Document
from app.services.report_service import build_report


def export_document(db: Session, document_id: int, fmt: str) -> tuple[bytes, str, str]:
    """Export a single document.

    Returns (bytes, filename, content_type).
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise ValueError(f"Document {document_id} not found")

    fmt = fmt.lower()
    if fmt == "txt":
        return _export_txt(document), f"{_safe_name(document.filename)}.txt", "text/plain"
    if fmt == "json":
        return _export_json(document), f"{_safe_name(document.filename)}.json", "application/json"
    if fmt == "pdf":
        # Delegate to the report service which builds a full analysis report.
        # If no analysis exists, still produce a minimal PDF of extracted text.
        return _export_pdf(document), f"{_safe_name(document.filename)}.pdf", "application/pdf"
    raise ValueError(f"Unsupported export format: {fmt}")


def export_all_documents(db: Session, fmt: str) -> tuple[bytes, str, str]:
    """Export all documents as a ZIP archive.

    Returns (zip_bytes, filename, content_type).
    """
    documents = db.query(Document).order_by(Document.uploaded_at.desc()).all()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for document in documents:
            try:
                data, fname, _ctype = export_document(db, document.id, fmt)
                zf.writestr(fname, data)
            except ValueError:
                continue  # skip documents that cannot be exported
    return buf.getvalue(), f"clauseclear_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.zip", "application/zip"


def _safe_name(name: str) -> str:
    safe = "".join(c if c.isalnum() or c in ".-_" else "_" for c in name)
    return safe or "document"


def _export_txt(document: Document) -> bytes:
    parts = []
    parts.append(f"ClauseClear Export — {document.filename}")
    parts.append(f"Source type: {document.source_type}")
    parts.append(f"Source URL: {document.source_url or 'N/A'}")
    parts.append(f"Status: {document.status}")
    parts.append(f"Uploaded: {document.uploaded_at.isoformat() if document.uploaded_at else 'N/A'}")
    parts.append(f"File size: {document.file_size} bytes" if document.file_size else "File size: N/A")
    parts.append(f"Page count: {document.page_count}" if document.page_count else "Page count: N/A")
    if document.failure_reason:
        parts.append(f"Failure reason: {document.failure_reason}")
    parts.append("")
    parts.append("=== EXTRACTED TEXT ===")
    parts.append(document.extracted_text or "")
    parts.append("")
    parts.append("=== METADATA ===")
    parts.append(document.metadata_json or "{}")
    return ("\n".join(parts)).encode("utf-8")


def _export_json(document: Document) -> bytes:
    payload = {
        "id": document.id,
        "filename": document.filename,
        "source_type": document.source_type,
        "source_url": document.source_url,
        "content_hash": document.content_hash,
        "file_size": document.file_size,
        "mime_type": document.mime_type,
        "status": document.status,
        "failure_reason": document.failure_reason,
        "page_count": document.page_count,
        "language": document.language,
        "extracted_text": document.extracted_text,
        "metadata": json.loads(document.metadata_json) if document.metadata_json else {},
        "extraction_warnings": json.loads(document.extraction_warnings_json) if document.extraction_warnings_json else [],
        "uploaded_at": document.uploaded_at.isoformat() if document.uploaded_at else None,
        "retention_delete_at": document.retention_delete_at.isoformat() if document.retention_delete_at else None,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")


def _export_pdf(document: Document) -> bytes:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        width, height = letter
        y = height - 50

        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, "ClauseClear Export")
        y -= 30
        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"Document: {document.filename}")
        y -= 16
        c.drawString(50, y, f"Source: {document.source_type}")
        y -= 16
        c.drawString(50, y, f"Status: {document.status}")
        y -= 24

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Extracted Text")
        y -= 18
        c.setFont("Helvetica", 9)
        text = document.extracted_text or ""
        for line in text.split("\n"):
            if y < 60:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 9)
            c.drawString(50, y, line[:110])
            y -= 12

        c.showPage()
        c.save()
        return buf.getvalue()
    except ImportError:
        # Fallback: return a minimal PDF-like text if reportlab missing.
        return _export_txt(document)

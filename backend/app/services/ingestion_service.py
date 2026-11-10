"""Ingestion service: orchestrates validation, extraction, and storage."""

import io
import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.database.base import SessionLocal
from app.models.document import Document, DocumentStatus, SourceType
from app.services.extraction_service import (
    ExtractionResult,
    ExtractionError,
    extract_file,
    extract_url,
)
from app.security.files import (
    validate_extension,
    verify_content_type,
    save_temp_file,
    remove_temp_file,
)
from app.config import settings


def compute_content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _retention_delete_at() -> Optional[datetime]:
    if settings.document_retention_days > 0:
        return datetime.utcnow() + timedelta(days=settings.document_retention_days)
    return None


def _create_document_record(
    db: Session,
    *,
    filename: str,
    source_type: str,
    source_url: Optional[str],
    content_hash: str,
    file_size: Optional[int],
    mime_type: Optional[str],
    extracted_text: str,
    metadata: dict,
    page_count: Optional[int] = None,
    language: Optional[str] = None,
    extraction_warnings: Optional[list] = None,
    status: str = DocumentStatus.extracted.value,
    failure_reason: Optional[str] = None,
) -> Document:
    document = Document(
        filename=filename,
        source_type=source_type,
        source_url=source_url,
        content_hash=content_hash,
        file_size=file_size,
        mime_type=mime_type,
        extracted_text=extracted_text,
        metadata_json=json.dumps(metadata),
        status=status,
        failure_reason=failure_reason,
        page_count=page_count,
        language=language,
        extraction_warnings_json=json.dumps(extraction_warnings or []),
        downloaded_at=datetime.utcnow() if status == DocumentStatus.extracted.value else None,
        retention_delete_at=_retention_delete_at(),
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def _ingest_result_to_dict(result: dict) -> dict:
    return {
        "document_id": result["document_id"],
        "status": result["status"],
        "extracted_length": result["extracted_length"],
        "source_type": result["source_type"],
        "discovered_documents": result.get("discovered_documents"),
        "message": result["message"],
    }


def ingest_url(url: str, db: Session) -> dict:
    """Ingest a website URL: validate, extract, store document."""
    result: ExtractionResult = extract_url(url)
    if not result.text or not result.text.strip():
        raise ExtractionError("No text could be extracted from the URL.")

    content_hash = compute_content_hash(result.text)

    # Short-circuit: return existing document if content hash matches.
    existing = db.query(Document).filter(Document.content_hash == content_hash).first()
    if existing:
        return _ingest_result_to_dict({
            "document_id": existing.id,
            "status": existing.status,
            "extracted_length": len(existing.extracted_text or ""),
            "source_type": existing.source_type,
            "discovered_documents": result.discovered_documents,
            "message": "Document already exists (duplicate content).",
        })

    warnings = []
    if len(result.text) < 100:
        warnings.append("Limited text extracted; page may be JavaScript-rendered or image-based")

    document = _create_document_record(
        db,
        filename=result.source_url or "website",
        source_type=SourceType.url.value,
        source_url=result.source_url,
        content_hash=content_hash,
        file_size=None,
        mime_type="text/html",
        extracted_text=result.text,
        metadata=result.metadata,
        page_count=None,
        language=result.metadata.get("language") if result.metadata else None,
        extraction_warnings=warnings,
    )

    return _ingest_result_to_dict({
        "document_id": document.id,
        "status": document.status,
        "extracted_length": len(result.text),
        "source_type": document.source_type,
        "discovered_documents": result.discovered_documents,
        "message": "URL extracted successfully.",
    })


def ingest_file(file_bytes: bytes, filename: str, db: Session) -> dict:
    """Ingest an uploaded file: validate, extract, store document."""
    ok, error = validate_extension(filename)
    if not ok:
        raise ExtractionError(error)

    ext = os.path.splitext(filename)[1].lower()
    ok, error = verify_content_type(file_bytes, ext)
    if not ok:
        raise ExtractionError(error)

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise ExtractionError(
            f"File exceeds maximum upload size of {settings.max_upload_size_mb} MB."
        )

    temp_path, error = save_temp_file(file_bytes, filename)
    if error:
        raise ExtractionError(error)
    try:
        with open(temp_path, "rb") as f:
            temp_bytes = f.read()
        result: ExtractionResult = extract_file(temp_bytes, filename)
    finally:
        remove_temp_file(temp_path)

    if not result.text or not result.text.strip():
        # Record as failed rather than raising unhandled.
        document = _create_document_record(
            db,
            filename=filename,
            source_type=SourceType.file.value,
            source_url=None,
            content_hash=compute_content_hash(b""),
            file_size=len(file_bytes),
            mime_type=result.mime_type,
            extracted_text="",
            metadata={},
            status=DocumentStatus.failed.value,
            failure_reason="No text could be extracted from the file.",
        )
        return _ingest_result_to_dict({
            "document_id": document.id,
            "status": document.status,
            "extracted_length": 0,
            "source_type": document.source_type,
            "discovered_documents": [],
            "message": "No text could be extracted from the file.",
        })

    content_hash = compute_content_hash(result.text)

    existing = db.query(Document).filter(Document.content_hash == content_hash).first()
    if existing:
        return _ingest_result_to_dict({
            "document_id": existing.id,
            "status": existing.status,
            "extracted_length": len(existing.extracted_text or ""),
            "source_type": existing.source_type,
            "discovered_documents": [],
            "message": "Document already exists (duplicate content).",
        })

    warnings = []
    if len(result.text) < 100:
        warnings.append("Limited text extracted; document may be scanned or image-based")

    document = _create_document_record(
        db,
        filename=result.filename or filename,
        source_type=SourceType.file.value,
        source_url=None,
        content_hash=content_hash,
        file_size=result.file_size,
        mime_type=result.mime_type,
        extracted_text=result.text,
        metadata=result.metadata,
        page_count=result.page_count,
        extraction_warnings=warnings,
    )

    return _ingest_result_to_dict({
        "document_id": document.id,
        "status": document.status,
        "extracted_length": len(result.text),
        "source_type": document.source_type,
        "discovered_documents": [],
        "message": "File extracted successfully.",
    })


def ingest_text(text: str, db: Session, filename: str = "pasted_text.txt") -> dict:
    """Ingest pasted raw text."""
    from app.utils.text import truncate

    if not text or not text.strip():
        raise ExtractionError("Text input is empty.")

    cleaned = truncate(text.strip(), settings.max_extracted_chars)
    content_hash = compute_content_hash(cleaned)

    existing = db.query(Document).filter(Document.content_hash == content_hash).first()
    if existing:
        return _ingest_result_to_dict({
            "document_id": existing.id,
            "status": existing.status,
            "extracted_length": len(existing.extracted_text or ""),
            "source_type": existing.source_type,
            "discovered_documents": [],
            "message": "Document already exists (duplicate content).",
        })

    document = _create_document_record(
        db,
        filename=filename,
        source_type=SourceType.text.value,
        source_url=None,
        content_hash=content_hash,
        file_size=len(cleaned.encode("utf-8")),
        mime_type="text/plain",
        extracted_text=cleaned,
        metadata={},
    )

    return _ingest_result_to_dict({
        "document_id": document.id,
        "status": document.status,
        "extracted_length": len(cleaned),
        "source_type": document.source_type,
        "discovered_documents": [],
        "message": "Text ingested successfully.",
    })


def ingest_upload_file_streaming(upload_file, db: Session) -> dict:
    """Ingest an UploadFile by streaming to disk (enforces size while streaming).

    This avoids reading very large files entirely into memory.
    """
    import tempfile
    import os as _os

    filename = upload_file.filename or "uploaded"
    ok, error = validate_extension(filename)
    if not ok:
        raise ExtractionError(error)

    ext = _os.path.splitext(filename)[1].lower()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    temp_fd, temp_path = tempfile.mkstemp(prefix="clauseclear_upload_", suffix=f"_{filename}")
    total = 0
    try:
        with _os.fdopen(temp_fd, "wb") as f:
            while True:
                chunk = upload_file.file.read(1024 * 1024)  # 1 MB chunks
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise ExtractionError(
                        f"File exceeds maximum upload size of {settings.max_upload_size_mb} MB."
                    )
                f.write(chunk)
        with open(temp_path, "rb") as f:
            file_bytes = f.read()
        return ingest_file(file_bytes, filename, db)
    finally:
        remove_temp_file(temp_path)

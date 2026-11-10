"""Document management endpoints (list, get, delete, export, reingest)."""

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.models.document import Document
from app.services.export_service import export_document, export_all_documents

router = APIRouter()


def _doc_summary(document: Document) -> dict:
    return {
        "id": document.id,
        "filename": document.filename,
        "source_type": document.source_type,
        "source_url": document.source_url,
        "file_size": document.file_size,
        "mime_type": document.mime_type,
        "status": document.status,
        "failure_reason": document.failure_reason,
        "page_count": document.page_count,
        "uploaded_at": document.uploaded_at.isoformat() if document.uploaded_at else None,
        "retention_delete_at": document.retention_delete_at.isoformat() if document.retention_delete_at else None,
        "has_analysis": document.analysis is not None,
    }


@router.get("/documents", tags=["documents"])
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    source_type: str | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Document)
    if status:
        query = query.filter(Document.status == status)
    if source_type:
        query = query.filter(Document.source_type == source_type)
    total = query.count()
    documents = (
        query.order_by(Document.uploaded_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "items": [_doc_summary(d) for d in documents],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size if total else 0,
    }


@router.get("/documents/{document_id}", tags=["documents"])
async def get_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return _doc_summary(document)


@router.delete("/documents/{document_id}", tags=["documents"], response_model=None)
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(document)
    db.commit()
    return Response(status_code=204)


@router.get("/documents/{document_id}/export", tags=["documents"], response_model=None)
async def export_document_endpoint(
    document_id: int,
    format: str = Query("json", pattern="^(txt|json|pdf)$"),
    db: Session = Depends(get_db),
):
    try:
        data, filename, content_type = export_document(db, document_id, format)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return Response(
        content=data,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/documents/export/all", tags=["documents"], response_model=None)
async def export_all_endpoint(
    format: str = Query("json", pattern="^(txt|json|pdf)$"),
    db: Session = Depends(get_db),
):
    data, filename, content_type = export_all_documents(db, format)
    return Response(
        content=data,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

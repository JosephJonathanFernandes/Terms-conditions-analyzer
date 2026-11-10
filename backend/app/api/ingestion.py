"""Document ingestion endpoints (Phase 2)."""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.services.ingestion_service import (
    ingest_url,
    ingest_file,
    ingest_text,
    ingest_upload_file_streaming,
)
from app.services.extraction_service import ExtractionError

router = APIRouter()


class UrlIngestRequest(BaseModel):
    url: str


class UrlIngestResponse(BaseModel):
    document_id: Optional[int] = None
    status: str
    extracted_length: int = 0
    source_type: str = "url"
    discovered_documents: Optional[List[dict]] = None
    message: str


@router.post("/ingest/url", response_model=UrlIngestResponse, tags=["ingestion"])
async def ingest_url_endpoint(payload: UrlIngestRequest, db: Session = Depends(get_db)):
    try:
        return ingest_url(payload.url, db)
    except ExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}")


@router.post("/ingest/file", tags=["ingestion"])
async def ingest_file_endpoint(
    file: UploadFile = File(...), db: Session = Depends(get_db)
):
    try:
        return ingest_upload_file_streaming(file, db)
    except ExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=f"File ingestion failed: {exc}")


@router.post("/ingest/text", tags=["ingestion"])
async def ingest_text_endpoint(
    text: str = Form(...), db: Session = Depends(get_db)
):
    try:
        return ingest_text(text, db)
    except ExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=f"Text ingestion failed: {exc}")

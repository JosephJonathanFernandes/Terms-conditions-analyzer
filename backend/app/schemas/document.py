"""Pydantic schemas for documents."""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Any
from datetime import datetime


class DocumentIngestRequest(BaseModel):
    url: Optional[HttpUrl] = None
    text: Optional[str] = None


class DocumentIngestResponse(BaseModel):
    document_id: int
    status: str
    extracted_length: int
    source_type: str
    discovered_documents: Optional[List[dict]] = None


class DocumentOut(BaseModel):
    id: int
    filename: str
    source_type: str
    source_url: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    status: str
    uploaded_at: datetime

    model_config = {"from_attributes": True}

"""Pydantic schemas for document Q&A."""

from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any


class ChatRequest(BaseModel):
    analysis_id: int
    question: str


class CitationOut(BaseModel):
    clause_id: int
    category: str
    source_location: Optional[str] = None
    quote: str


class ChatResponse(BaseModel):
    answer: str
    citations: List[CitationOut] = []
    document_does_not_specify: bool = False

    model_config = ConfigDict(from_attributes=True)

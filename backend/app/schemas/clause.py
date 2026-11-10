"""Pydantic schemas for clauses."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any
from datetime import datetime


class ClauseBase(BaseModel):
    category: str
    original_text: str
    simplified_text: Optional[str] = None
    risk_level: str
    risk_rationale: Optional[str] = None
    confidence: Optional[float] = None
    source_location: Optional[str] = None
    paragraph_index: Optional[int] = None
    evidence: Optional[dict] = None
    suggested_questions: Optional[List[str]] = None


class ClauseOut(ClauseBase):
    id: int
    analysis_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClauseCreate(ClauseBase):
    analysis_id: int

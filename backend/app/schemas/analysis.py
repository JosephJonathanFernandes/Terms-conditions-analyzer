"""Pydantic schemas for analyses."""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.schemas.clause import ClauseOut


class AnalyzeRequest(BaseModel):
    document_id: int
    explanation_level: str = Field(default="standard", pattern="^(simple|standard|detailed)$")


class AnalysisOut(BaseModel):
    id: int
    document_id: int
    status: str
    summary: Optional[str] = None
    risk_distribution: Optional[dict] = None
    explanation_level: str
    llm_mode: str
    created_at: datetime
    clauses: List[ClauseOut] = []

    model_config = ConfigDict(from_attributes=True)


class HistoryItem(BaseModel):
    id: int
    document_id: int
    filename: str
    source_type: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

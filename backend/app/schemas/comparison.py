"""Pydantic schemas for document comparison."""

from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any


class ClauseDiff(BaseModel):
    clause_id: int
    category: str
    change_type: str  # added | removed | modified
    text_a: Optional[str] = None
    text_b: Optional[str] = None
    impact: Optional[str] = None


class ComparisonResponse(BaseModel):
    analysis_id_a: int
    analysis_id_b: int
    added: List[ClauseDiff] = []
    removed: List[ClauseDiff] = []
    modified: List[ClauseDiff] = []
    impact_summary: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

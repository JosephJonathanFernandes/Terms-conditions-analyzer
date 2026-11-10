"""Comparison endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services import analysis_service

router = APIRouter()


class CompareRequest(BaseModel):
    analysis_id_a: int
    analysis_id_b: int


@router.post("/compare", tags=["comparison"])
async def compare(payload: CompareRequest):
    try:
        return analysis_service.compare_analyses(payload.analysis_id_a, payload.analysis_id_b)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Comparison failed: {exc}")

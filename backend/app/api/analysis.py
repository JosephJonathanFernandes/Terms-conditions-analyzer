"""Analysis endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.services import analysis_service

router = APIRouter()


class AnalyzeRequest(BaseModel):
    document_id: int
    explanation_level: str = Field(default="standard", pattern="^(simple|standard|detailed)$")


@router.post("/analyze", tags=["analysis"])
async def analyze(payload: AnalyzeRequest, db: Session = Depends(get_db)):
    try:
        return analysis_service.run_analysis(payload.document_id, payload.explanation_level)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")


@router.get("/analysis/{analysis_id}", tags=["analysis"])
async def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    result = analysis_service.get_analysis(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result

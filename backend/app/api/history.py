"""History endpoints."""

from fastapi import APIRouter, HTTPException
from app.services import analysis_service

router = APIRouter()


@router.get("/history", tags=["history"])
async def history():
    return analysis_service.list_history()


@router.delete("/history/{analysis_id}", tags=["history"])
async def delete_history(analysis_id: int):
    ok = analysis_service.delete_analysis(analysis_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {"ok": True}

"""Chat / Q&A endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services import analysis_service

router = APIRouter()


class ChatRequest(BaseModel):
    analysis_id: int
    question: str


@router.post("/chat", tags=["chat"])
async def chat(payload: ChatRequest):
    if not payload.question or not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question is required")
    try:
        return analysis_service.chat(payload.analysis_id, payload.question)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Chat failed: {exc}")

"""Health check endpoints."""

from fastapi import APIRouter
from app.config import settings

router = APIRouter()


@router.get("/health", tags=["health"])
async def health():
    return {
        "status": "ok",
        "service": settings.app_name,
        "env": settings.app_env,
        "llm_mode": "ai" if settings.llm_provider != "none" else "rule-based",
    }

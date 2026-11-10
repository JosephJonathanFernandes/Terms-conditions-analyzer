"""ClauseClear FastAPI application entry point."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from app.config import settings, validate_production_settings
from app.api import health, ingestion, analysis, chat, comparison, history, report, documents
from app.middleware.errors import ErrorHandlingMiddleware
from app.middleware.rate_limiting import RateLimitingMiddleware
from app.database.base import dispose_engine

app = FastAPI(
    title="ClauseClear",
    description="AI-Powered Terms & Conditions Analyzer",
    version="1.0.0",
)

# CORS (restricted to configured origins).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Rate limiting (after CORS).
app.add_middleware(RateLimitingMiddleware)

# Global error handling (outermost business-logic wrapper).
app.add_middleware(ErrorHandlingMiddleware)

# Routers.
app.include_router(health.router)
app.include_router(ingestion.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(comparison.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(report.router, prefix="/api")
app.include_router(documents.router, prefix="/api")


def _error_shape(status_code: int, code: str, message: str, headers: dict | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
        headers=headers or {},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return _error_shape(exc.status_code, _code_for_status(exc.status_code), str(exc.detail))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return _error_shape(
        HTTP_422_UNPROCESSABLE_ENTITY,
        "validation_error",
        "Request validation failed",
    )


@app.exception_handler(500)
async def internal_exception_handler(request: Request, exc: Exception):
    return _error_shape(HTTP_500_INTERNAL_SERVER_ERROR, "internal_error", "An internal error occurred")


def _code_for_status(status_code: int) -> str:
    return {
        HTTP_400_BAD_REQUEST: "bad_request",
        HTTP_404_NOT_FOUND: "not_found",
        HTTP_409_CONFLICT: "conflict",
        HTTP_422_UNPROCESSABLE_ENTITY: "validation_error",
        HTTP_429_TOO_MANY_REQUESTS: "rate_limited",
        HTTP_500_INTERNAL_SERVER_ERROR: "internal_error",
    }.get(status_code, "error")


@app.on_event("startup")
def on_startup():
    from app.database.base import Base, engine

    # Idempotent table creation; indexes/tables may already exist in test
    # environments where pytest_configure pre-creates them.
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:  # pragma: no cover - best-effort; Alembic manages prod schema
        pass

    # Log production configuration warnings.
    for warning in validate_production_settings(settings):
        print(f"[ClauseClear CONFIG WARNING] {warning}")


@app.on_event("shutdown")
def on_shutdown():
    dispose_engine()


@app.get("/", tags=["root"])
def root():
    return {
        "service": settings.app_name,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }

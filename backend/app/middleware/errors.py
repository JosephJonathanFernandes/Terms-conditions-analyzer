"""Global error handling middleware.

Returns a consistent JSON error shape for truly unhandled exceptions and
never leaks stack traces to the client. Adds X-Request-ID to every response.

Note: HTTPException and RequestValidationError are handled by FastAPI's own
exception handlers (registered in main.py) so they keep their proper status
codes. This middleware catches everything else.
"""

import logging
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.config import settings
from app.services.extraction_service import ExtractionError

logger = logging.getLogger("clauseclear")


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Callable):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Content-Type-Options"] = "nosniff"
            return response
        except ExtractionError as exc:
            return _json_response(
                request_id,
                400,
                "extraction_error",
                str(exc),
            )
        except Exception as exc:  # noqa: BLE001 - catch-all for unhandled errors
            logger.exception(
                "Unhandled error (request_id=%s): %s", request_id, exc
            )
            if settings.is_production:
                message = "An internal error occurred"
            else:
                message = f"Internal error: {exc}"
            return _json_response(
                request_id,
                HTTP_500_INTERNAL_SERVER_ERROR,
                "internal_error",
                message,
            )


def _json_response(
    request_id: str,
    status_code: int,
    code: str,
    message: str,
    details: list | dict | None = None,
) -> JSONResponse:
    from fastapi.responses import JSONResponse

    body: dict = {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
        }
    }
    if details is not None:
        body["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=body, headers={
        "X-Request-ID": request_id,
        "X-Content-Type-Options": "nosniff",
    })

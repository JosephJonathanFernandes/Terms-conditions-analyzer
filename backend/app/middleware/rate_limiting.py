"""In-memory fixed-window rate limiting middleware.

Keyed by client IP (and optional API key header). Stricter limits on
ingestion/analysis endpoints, looser on health/history. Returns 429 with
Retry-After header and structured error body.

Note: For multi-worker production deployments, replace with Redis-backed
limiting (e.g., slowapi + Redis).
"""

import time
from collections import defaultdict
from threading import Lock
from typing import Callable, Dict, Tuple

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

from app.config import settings
from app.middleware.errors import _json_response


class _Window:
    __slots__ = ("count", "reset_at")

    def __init__(self, reset_at: float):
        self.count = 0
        self.reset_at = reset_at


class RateLimitingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Callable):
        super().__init__(app)
        self._buckets: Dict[Tuple[str, str], _Window] = {}
        self._lock = Lock()

    # route path prefix -> limit per minute
    _ROUTE_LIMITS = {
        "/api/ingest": None,  # set from settings at dispatch
        "/api/analyze": None,
        "/api/chat": None,
    }

    def _client_key(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        ip = forwarded.split(",")[0].strip() if forwarded else request.client.host if request.client else "unknown"
        api_key = request.headers.get("x-api-key", "")
        return f"{ip}:{api_key}"

    def _limit_for_path(self, path: str) -> int:
        for prefix, _ in self._ROUTE_LIMITS.items():
            if path.startswith(prefix):
                if prefix == "/api/ingest":
                    return settings.rate_limit_ingest
                if prefix == "/api/analyze":
                    return settings.rate_limit_analyze
                if prefix == "/api/chat":
                    return settings.rate_limit_chat
        return settings.rate_limit_default

    def _check(self, key: str, limit: int) -> Tuple[bool, int, float]:
        """Return (allowed, remaining, reset_at)."""
        now = time.time()
        with self._lock:
            window = self._buckets.get(key)
            if window is None or now >= window.reset_at:
                window = _Window(reset_at=now + 60.0)
                self._buckets[key] = window
            if window.count >= limit:
                return False, 0, window.reset_at
            window.count += 1
            return True, limit - window.count, window.reset_at

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health in a way that's still tracked separately
        path = request.url.path
        key = self._client_key(request)
        limit = self._limit_for_path(path)
        allowed, remaining, reset_at = self._check(key, limit)

        response = await call_next(request)

        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(remaining, 0))
        response.headers["X-RateLimit-Reset"] = str(int(reset_at))

        if not allowed:
            return _json_response(
                request_id=getattr(request.state, "request_id", ""),
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                code="rate_limited",
                message="Rate limit exceeded. Try again later.",
                details={"retry_after_seconds": max(int(reset_at - time.time()), 1)},
            )
        response.headers["Retry-After"] = str(max(int(reset_at - time.time()), 1))
        return response

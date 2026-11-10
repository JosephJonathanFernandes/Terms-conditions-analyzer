"""Rate limiting tests - test the middleware logic directly."""

import time

from app.middleware.rate_limiting import RateLimitingMiddleware


def test_window_allows_under_limit():
    mw = RateLimitingMiddleware(None)
    key = "test:user"
    limit = 5
    for i in range(limit):
        allowed, remaining, reset = mw._check(key, limit)
        assert allowed is True
        assert remaining == limit - i - 1


def test_window_blocks_at_limit():
    mw = RateLimitingMiddleware(None)
    key = "test:user2"
    limit = 3
    for i in range(limit):
        allowed, _, _ = mw._check(key, limit)
        assert allowed is True
    allowed, remaining, reset = mw._check(key, limit)
    assert allowed is False
    assert remaining == 0
    assert reset > time.time()


def test_window_resets_after_expiry():
    mw = RateLimitingMiddleware(None)
    key = "test:user3"
    limit = 1
    allowed, _, _ = mw._check(key, limit)
    assert allowed is True
    # Manually expire the window.
    with mw._lock:
        mw._buckets[key].reset_at = time.time() - 1
    allowed, _, _ = mw._check(key, limit)
    assert allowed is True


def test_rate_limit_headers_present(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert "X-RateLimit-Limit" in res.headers
    assert "X-RateLimit-Remaining" in res.headers

# backend/tests/unit/test_ratelimit.py
# Unit tests for the sliding-window rate limiter and its helpers.

import time

import pytest
from starlette.requests import Request

from app.core.ratelimit import RateLimiter, client_ip, parse_rate_limit


def _request(
    headers: dict[str, str] | None = None,
    client: tuple[str, int] | None = ("1.2.3.4", 1234),
) -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "query_string": b"",
        "headers": [
            (k.lower().encode(), v.encode())
            for k, v in (headers or {}).items()
        ],
        "client": client,
    }
    return Request(scope)


class TestParseRateLimit:
    def test_valid(self) -> None:
        assert parse_rate_limit("30/minute") == (30, 60.0)
        assert parse_rate_limit("2/second") == (2, 1.0)
        assert parse_rate_limit("100/hours") == (100, 3600.0)

    def test_disabled(self) -> None:
        assert parse_rate_limit("") is None
        assert parse_rate_limit("0") is None

    @pytest.mark.parametrize(
        "value", ["banana", "30/fortnight", "x/minute", "30", "/minute"]
    )
    def test_invalid(self, value: str) -> None:
        with pytest.raises(ValueError):
            parse_rate_limit(value)


class TestRateLimiter:
    def test_allows_up_to_limit(self) -> None:
        limiter = RateLimiter(limit=2, window_seconds=60.0)
        assert limiter.is_limited("a") is False
        assert limiter.is_limited("a") is False
        assert limiter.is_limited("a") is True

    def test_keys_are_isolated(self) -> None:
        limiter = RateLimiter(limit=1, window_seconds=60.0)
        assert limiter.is_limited("a") is False
        assert limiter.is_limited("b") is False
        assert limiter.is_limited("a") is True
        assert limiter.is_limited("b") is True

    def test_window_expiry(self) -> None:
        limiter = RateLimiter(limit=1, window_seconds=0.05)
        assert limiter.is_limited("a") is False
        assert limiter.is_limited("a") is True
        time.sleep(0.06)
        assert limiter.is_limited("a") is False

    def test_lru_eviction_bounds_memory(self) -> None:
        limiter = RateLimiter(limit=5, window_seconds=60.0, max_keys=2)
        limiter.is_limited("a")
        limiter.is_limited("b")
        limiter.is_limited("c")  # evicts least-recently-seen ("a")
        assert "a" not in limiter._hits
        assert len(limiter._hits) <= 2


class TestClientIp:
    def test_direct_client(self) -> None:
        assert client_ip(_request(), trust_proxy=False) == "1.2.3.4"

    def test_forwarded_when_trusted(self) -> None:
        request = _request(
            headers={"x-forwarded-for": "9.9.9.9, 10.0.0.1"}
        )
        assert client_ip(request, trust_proxy=True) == "9.9.9.9"

    def test_forwarded_ignored_when_untrusted(self) -> None:
        request = _request(headers={"x-forwarded-for": "9.9.9.9"})
        assert client_ip(request, trust_proxy=False) == "1.2.3.4"

    def test_real_ip_fallback(self) -> None:
        request = _request(headers={"x-real-ip": "8.8.8.8"})
        assert client_ip(request, trust_proxy=True) == "8.8.8.8"

    def test_missing_client(self) -> None:
        assert client_ip(_request(client=None), trust_proxy=False) == (
            "unknown"
        )

# backend/tests/api/test_errors.py
# API error paths: domain errors use the envelope, unexpected errors
# are sanitized and never leak internals.

from __future__ import annotations

import httpx

from app.api import routes
from app.core.errors import TextTooLongError


class _RaisingService:
    """Dependency stand-in whose endpoints raise on every call."""

    def __init__(self, exc: Exception) -> None:
        self.exc = exc

    def analyze(self, text: str, include_sentences: bool = False):  # type: ignore[no-untyped-def]
        raise self.exc

    def analyze_sentences(self, text: str):  # type: ignore[no-untyped-def]
        raise self.exc


def _client(app) -> httpx.AsyncClient:  # type: ignore[no-untyped-def]
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


async def test_domain_error_uses_envelope(app) -> None:  # type: ignore[no-untyped-def]
    app.dependency_overrides[routes.get_analysis_service] = lambda: (
        _RaisingService(TextTooLongError(max_chars=2000, actual=2500))
    )
    async with _client(app) as client:
        resp = await client.post("/api/analyze", json={"text": "hi"})
    assert resp.status_code == 422
    body = resp.json()
    assert body["error"]["code"] == "text_too_long"
    assert "2500" in body["error"]["message"]


async def test_unhandled_exception_is_sanitized(app) -> None:  # type: ignore[no-untyped-def]
    secret = "secret-internal-detail"
    app.dependency_overrides[routes.get_analysis_service] = lambda: (
        _RaisingService(RuntimeError(secret))
    )
    async with _client(app) as client:
        resp = await client.post("/api/analyze", json={"text": "hi"})
    assert resp.status_code == 500
    body = resp.json()
    assert body["error"]["code"] == "internal_error"
    assert secret not in resp.text

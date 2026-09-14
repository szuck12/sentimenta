# backend/tests/api/test_routes.py
# API endpoint tests exercising HTTP request/response round-trips
# with the stub analysis service.

import httpx
import pytest

from app.core.config import Settings


async def test_health(client: httpx.AsyncClient) -> None:
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "version" in body
    assert isinstance(body["model_loaded"], bool)


async def test_emotions(client: httpx.AsyncClient) -> None:
    resp = await client.get("/api/emotions")
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 28
    first = body["emotions"][0]
    assert first["label"] == "admiration"
    assert "emoji" in first
    assert first["group"] == "positive"


async def test_analyze_success(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/api/analyze", json={"text": "I love this!"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "primary_emotion" in body
    assert body["primary_emotion"]["label"] == "joy"
    assert 0.0 <= body["primary_emotion"]["score"] <= 1.0
    assert isinstance(body["emotions"], list)
    assert isinstance(body["explanation"], dict)


async def test_analyze_empty_text(client: httpx.AsyncClient) -> None:
    resp = await client.post("/api/analyze", json={"text": ""})
    assert resp.status_code == 422
    body = resp.json()
    assert "error" in body


async def test_analyze_long_text(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/api/analyze", json={"text": "word " * 1000}
    )
    assert resp.status_code == 422


async def test_analyze_malformed_json(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/api/analyze", content=b"{bad json", headers={"content-type": "application/json"}
    )
    assert resp.status_code == 422
    assert "error" in resp.json()


async def test_analyze_missing_text(client: httpx.AsyncClient) -> None:
    resp = await client.post("/api/analyze", json={"other": "value"})
    assert resp.status_code == 422


async def test_analyze_wrong_type(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/api/analyze", json={"text": 12345}
    )
    assert resp.status_code == 422


async def test_analyze_sentences(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/api/analyze/sentences",
        json={"text": "Hello world"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["sentences"], list)
    assert body["sentences"][0]["index"] == 0


async def test_analyze_include_sentences(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/api/analyze",
        json={"text": "Hello.", "include_sentences": True},
    )
    assert resp.status_code == 200
    assert "sentences" in resp.json()


async def test_analyze_returns_all_28_emotions(
    client: httpx.AsyncClient,
) -> None:
    body = (await client.post("/api/analyze", json={"text": "I love this!"})).json()
    assert len(body["all_emotions"]) == 28
    scores = [e["score"] for e in body["all_emotions"]]
    assert scores == sorted(scores, reverse=True)
    assert body["primary_emotion"] == body["all_emotions"][0]


async def test_analyze_metadata_shape(client: httpx.AsyncClient) -> None:
    body = (
        await client.post("/api/analyze", json={"text": "Hello there"})
    ).json()
    metadata = body["metadata"]
    for key in (
        "model_id",
        "char_count",
        "word_count",
        "sentence_count",
        "threshold",
        "attribution_used",
        "truncated_tokens",
        "latency_ms",
    ):
        assert key in metadata
    assert metadata["word_count"] == 2


async def test_analyze_without_sentences_returns_empty_list(
    client: httpx.AsyncClient,
) -> None:
    body = (
        await client.post(
            "/api/analyze", json={"text": "Hello.", "include_sentences": False}
        )
    ).json()
    assert body["sentences"] == []


async def test_sentences_empty_text(client: httpx.AsyncClient) -> None:
    resp = await client.post("/api/analyze/sentences", json={"text": ""})
    assert resp.status_code == 422
    assert "error" in resp.json()


async def test_sentences_over_limit(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/api/analyze/sentences", json={"text": "word " * 1000}
    )
    assert resp.status_code == 422


async def test_unknown_route_returns_404(client: httpx.AsyncClient) -> None:
    resp = await client.get("/api/does-not-exist")
    assert resp.status_code == 404


async def test_emotions_response_shape(client: httpx.AsyncClient) -> None:
    body = (await client.get("/api/emotions")).json()
    assert set(body["groups"]) == {
        "positive",
        "negative",
        "cognitive",
        "neutral",
    }
    assert all("description" in e for e in body["emotions"])


async def test_cors_preflight_allows_localhost(
    client: httpx.AsyncClient,
) -> None:
    resp = await client.options(
        "/api/analyze",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert resp.status_code == 200
    assert (
        resp.headers.get("access-control-allow-origin")
        == "http://localhost:5173"
    )


async def test_cors_header_present_on_post(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/api/analyze",
        json={"text": "hello"},
        headers={"Origin": "http://localhost:5173"},
    )
    assert (
        resp.headers.get("access-control-allow-origin")
        == "http://localhost:5173"
    )


async def test_security_headers_present(client: httpx.AsyncClient) -> None:
    resp = await client.get("/api/health")
    assert resp.headers.get("x-content-type-options") == "nosniff"
    assert resp.headers.get("referrer-policy") == "no-referrer"
    assert resp.headers.get("x-frame-options") == "DENY"


async def test_docs_disabled_by_default(client: httpx.AsyncClient) -> None:
    assert (await client.get("/openapi.json")).status_code == 404
    assert (await client.get("/docs")).status_code == 404


async def test_docs_can_be_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.main import create_app

    monkeypatch.setattr(
        "app.main.get_settings", lambda: Settings(enable_docs=True)
    )
    application = create_app()
    transport = httpx.ASGITransport(app=application)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://test"
    ) as ac:
        assert (await ac.get("/openapi.json")).status_code == 200
        assert (await ac.get("/docs")).status_code == 200


async def test_rate_limiter_blocks_after_limit() -> None:
    """Test the rate limiter logic directly."""
    from app.main import _RateLimiter

    limiter = _RateLimiter(limit=1, window_seconds=60.0)
    assert limiter.is_limited("1.2.3.4") is False  # 0 prior ≤ 1 → allowed
    assert limiter.is_limited("1.2.3.4") is False  # 1 prior ≤ 1 → allowed
    assert limiter.is_limited("1.2.3.4") is True   # 2 prior > 1 → blocked
    # Different IPs are independent
    assert limiter.is_limited("5.6.7.8") is False

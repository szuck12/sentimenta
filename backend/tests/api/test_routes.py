# backend/tests/api/test_routes.py
# API endpoint tests exercising HTTP request/response round-trips
# with the stub analysis service.

import httpx


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

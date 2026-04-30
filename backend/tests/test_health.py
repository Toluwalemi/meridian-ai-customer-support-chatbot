import pytest


@pytest.mark.asyncio
async def test_healthz_returns_ok(client):
    resp = await client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_chat_requires_auth(client):
    resp = await client.post(
        "/api/v1/chat",
        json={"messages": [{"role": "user", "content": "hi"}]},
    )
    assert resp.status_code in (401, 403)

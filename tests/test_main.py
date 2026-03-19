import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_register_and_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 회원가입
        resp = await client.post(
            "/api/users/register",
            json={"email": "test@example.com", "password": "testpass123", "full_name": "테스트"},
        )
        assert resp.status_code == 201
        assert resp.json()["email"] == "test@example.com"

        # 로그인
        resp = await client.post(
            "/api/users/login",
            data={"username": "test@example.com", "password": "testpass123"},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()

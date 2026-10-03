import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient):
    payload = {
        "email": "newuser@example.com",
        "password": "Password123!",
        "full_name": "New User",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["user"]["email"] == "newuser@example.com"
    assert "token" in data["data"]
    assert "access_token" in data["data"]["token"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user):
    payload = {
        "email": test_user.email,
        "password": "Password123!",
        "full_name": "Duplicate User",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    data = response.json()
    assert data["success"] is False
    assert "already exists" in data["error"]["message"].lower()


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    payload = {
        "email": test_user.email,
        "password": "StrongPassword123!",
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]["token"]


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, test_user):
    payload = {
        "email": test_user.email,
        "password": "WrongPassword!",
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False


@pytest.mark.asyncio
async def test_get_current_user_me(client: AsyncClient, auth_headers: dict, test_user):
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == test_user.email
    assert data["data"]["id"] == test_user.id


@pytest.mark.asyncio
async def test_get_me_unauthorized(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401

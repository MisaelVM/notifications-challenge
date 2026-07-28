import pytest
from httpx import AsyncClient

from tests.conftest import create_test_user

BASE_URL = "/api/v1/auth"


@pytest.mark.anyio
async def test_register_user_validation_error(client: AsyncClient):
    response = await client.post(BASE_URL, json={"name": "testuser"})

    assert response.status_code == 422
    assert "email" in response.text
    assert "password" in response.text


@pytest.mark.anyio
async def test_register_user_duplicate_email(client: AsyncClient):
    existing_user = await create_test_user(client)
    response = await client.post(
        BASE_URL,
        json={
            "name": "different_user",
            "email": existing_user["email"],
            "password": "password1234",
        },
    )

    assert response.status_code == 409
    assert response.json()["error_code"] == "EMAIL_ALREADY_REGISTERED"


@pytest.mark.anyio
async def test_register_user_success(client: AsyncClient):
    new_user = {
        "name": "new user",
        "email": "new.user@example.com",
        "password": "UltR4SecR3t-P@$$w0rd!",
    }
    response = await client.post(BASE_URL, json=new_user)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == new_user["name"]
    assert data["email"] == new_user["email"]
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.anyio
async def test_login_for_access_token_incorrect_email(client: AsyncClient):
    response = await client.post(
        f"{BASE_URL}/token",
        data={
            "username": "this.email.does.not.exist@example.com",
            "password": "testpassword123",
        },
    )
    assert response.status_code == 401
    data = response.json()
    assert data["error_code"] == "INVALID_CREDENTIALS"
    assert data["detail"] == "Incorrect email or password"


@pytest.mark.anyio
async def test_login_for_access_token_wrong_password(client: AsyncClient):
    existing_user = await create_test_user(client)
    response = await client.post(
        f"{BASE_URL}/token",
        data={"username": existing_user["email"], "password": "wrong-password"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["error_code"] == "INVALID_CREDENTIALS"
    assert data["detail"] == "Incorrect email or password"


@pytest.mark.anyio
async def test_login_for_access_token_success(client: AsyncClient):
    test_user = {
        "name": "new user",
        "email": "new.user@example.com",
        "password": "UltR4SecR3t-P@$$w0rd!",
    }
    _ = await create_test_user(
        client,
        name=test_user["name"],
        email=test_user["email"],
        password=test_user["password"],
    )
    response = await client.post(
        f"{BASE_URL}/token",
        data={"username": test_user["email"], "password": test_user["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"  # noqa: S105
    assert "access_token" in data
    assert isinstance(data["access_token"], str)

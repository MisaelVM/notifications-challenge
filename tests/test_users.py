import pytest
from httpx import AsyncClient

from tests.conftest import auth_header, create_test_user, login_user

BASE_URL = "/api/v1/users"


@pytest.mark.anyio
async def test_get_current_user_success(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)
    response = await client.get(f"{BASE_URL}/me", headers=auth_header(token))

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user["id"]
    assert data["name"] == user["name"]
    assert data["email"] == user["email"]
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.anyio
async def test_get_user_success(client: AsyncClient):
    existing_user = await create_test_user(client)
    response = await client.get(f"{BASE_URL}/{existing_user['id']}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == existing_user["id"]
    assert data["name"] == existing_user["name"]
    assert "email" not in data
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.anyio
async def test_get_user_validation_error(client: AsyncClient):
    response = await client.get(f"{BASE_URL}/invalid-id")

    assert response.status_code == 422
    assert "uuid_parsing" in response.text


@pytest.mark.anyio
async def test_get_user_not_found(client: AsyncClient):
    non_existing_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"{BASE_URL}/{non_existing_id}")

    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "USER_NOT_FOUND"
    assert non_existing_id in data["detail"]


@pytest.mark.anyio
async def test_update_user_success(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)

    response = await client.patch(
        f"{BASE_URL}/{user['id']}",
        json={"name": "Updated Name"},
        headers=auth_header(token),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user["id"]
    assert data["name"] == "Updated Name"
    assert data["email"] == user["email"]
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.anyio
async def test_update_user_not_found(client: AsyncClient):
    _ = await create_test_user(client)
    token = await login_user(client)

    non_existing_id = "00000000-0000-0000-0000-000000000000"
    response = await client.patch(
        f"{BASE_URL}/{non_existing_id}",
        json={"name": "Non-existing user"},
        headers=auth_header(token),
    )

    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "USER_NOT_FOUND"
    assert non_existing_id in data["detail"]


@pytest.mark.anyio
async def test_update_user_forbidden(client: AsyncClient):
    existing_user = await create_test_user(
        client, name="user1", email="user1@example.com"
    )

    _ = await create_test_user(client, name="user2", email="user2@example.com")
    token = await login_user(client, email="user2@example.com")
    response = await client.patch(
        f"{BASE_URL}/{existing_user['id']}",
        json={"name": "Hacked Name"},
        headers=auth_header(token),
    )

    assert response.status_code == 403
    assert response.json()["error_code"] == "PERMISSION_DENIED"


@pytest.mark.anyio
async def test_delete_user_success(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)

    response = await client.delete(
        f"{BASE_URL}/{user['id']}", headers=auth_header(token)
    )

    assert response.status_code == 204
    assert not response.content

    response = await client.get(f"/api/v1/users/{user['id']}")

    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "USER_NOT_FOUND"
    assert user["id"] in data["detail"]


@pytest.mark.anyio
async def test_delete_user_not_found(client: AsyncClient):
    _ = await create_test_user(client)
    token = await login_user(client)

    non_existing_id = "00000000-0000-0000-0000-000000000000"
    response = await client.delete(
        f"{BASE_URL}/{non_existing_id}", headers=auth_header(token)
    )

    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "USER_NOT_FOUND"
    assert non_existing_id in data["detail"]


@pytest.mark.anyio
async def test_delete_user_forbidden(client: AsyncClient):
    existing_user = await create_test_user(
        client, name="user1", email="user1@example.com"
    )

    _ = await create_test_user(client, name="user2", email="user2@example.com")
    token = await login_user(client, email="user2@example.com")
    response = await client.delete(
        f"{BASE_URL}/{existing_user['id']}", headers=auth_header(token)
    )

    assert response.status_code == 403
    assert response.json()["error_code"] == "PERMISSION_DENIED"

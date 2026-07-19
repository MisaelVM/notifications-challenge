import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_get_users_empty(client: AsyncClient):
    response = await client.get("/api/v1/users")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data == []
    assert len(list(data)) == 0


@pytest.mark.anyio
async def test_get_user_not_found(client: AsyncClient):
    response = await client.get("/api/v1/users/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404


@pytest.mark.anyio
async def test_create_user_success(client: AsyncClient):
    response = await client.post(
        "/api/v1/users",
        json={
            "name": "John Doe",
            "email": "jdoe@example.com",
            "password": "passwordpassword",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "jdoe@example.com"
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.anyio
async def test_update_user_success(client: AsyncClient):
    response = await client.post(
        "/api/v1/users",
        json={
            "name": "John Doe",
            "email": "jdoe@example.com",
            "password": "passwordpassword",
        },
    )
    user_id = response.json()["id"]

    response = await client.patch(
        f"/api/v1/users/{user_id}", json={"name": "Updated Name"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["email"] == "jdoe@example.com"


@pytest.mark.anyio
async def test_update_user_not_found(client: AsyncClient):
    response = await client.patch(
        "/api/v1/users/00000000-0000-0000-0000-000000000000",
        json={"name": "Non-existing user"},
    )

    assert response.status_code == 404


@pytest.mark.anyio
async def test_delete_user_success(client: AsyncClient):
    response = await client.post(
        "/api/v1/users",
        json={
            "name": "John Doe",
            "email": "jdoe@example.com",
            "password": "passwordpassword",
        },
    )
    user_id = response.json()["id"]

    response = await client.delete(f"/api/v1/users/{user_id}")

    assert response.status_code == 204

    response = await client.get(f"/api/v1/users/{user_id}")

    assert response.status_code == 404


@pytest.mark.anyio
async def test_delete_user_not_found(client: AsyncClient):
    response = await client.delete("/api/v1/users/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404

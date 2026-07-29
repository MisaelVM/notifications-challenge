import pytest
from httpx import AsyncClient

from tests.conftest import auth_header, create_test_user, login_user

BASE_URL = "/api/v1/notifications"


@pytest.mark.anyio
async def test_get_notifications_for_current_user_empty(client: AsyncClient):
    _ = await create_test_user(client)
    token = await login_user(client)
    response = await client.get(BASE_URL, headers=auth_header(token))

    assert response.status_code == 200
    data = response.json()
    assert data["notifications"] == []
    assert data["total"] == 0
    assert data["has_more"] is False


@pytest.mark.anyio
async def test_create_notification_success(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)

    new_notification = {
        "title": "Test Notification",
        "content": "Test notification content",
        "channel": "email",
    }
    response = await client.post(
        BASE_URL,
        json=new_notification,
        headers=auth_header(token),
    )

    assert response.status_code == 201
    data = response.json()
    assert response.headers["Location"] == f"{BASE_URL}/{data['id']}"
    assert data["title"] == new_notification["title"]
    assert data["content"] == new_notification["content"]
    assert data["channel"] == new_notification["channel"]
    assert data["user_id"] == user["id"]
    assert "id" in data
    assert "created_at" in data


@pytest.mark.anyio
async def test_create_notification_unauthorized(client: AsyncClient):
    response = await client.post(
        BASE_URL,
        json={
            "title": "Failed Notification",
            "content": "Unauthorized content",
            "channel": "email",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.anyio
async def test_get_notification_success(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)
    response = await client.post(
        BASE_URL,
        json={
            "title": "Notification Title",
            "content": "Content for notification",
            "channel": "email",
        },
        headers=headers,
    )
    notification = response.json()
    notification_id = notification["id"]

    response = await client.get(f"{BASE_URL}/{notification_id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == notification["title"]
    assert data["content"] == notification["content"]
    assert data["channel"] == notification["channel"]
    assert data["user_id"] == user["id"]
    assert "id" in data
    assert "created_at" in data


@pytest.mark.anyio
async def test_get_notification_not_found(client: AsyncClient):
    _ = await create_test_user(client)
    token = await login_user(client)

    non_existing_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(
        f"{BASE_URL}/{non_existing_id}", headers=auth_header(token)
    )

    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "NOTIFICATION_NOT_FOUND"
    assert non_existing_id in data["detail"]


@pytest.mark.anyio
async def test_get_notification_forbidden(client: AsyncClient):
    _ = await create_test_user(client, name="user1", email="user1@example.com")
    token1 = await login_user(client, email="user1@example.com")

    response = await client.post(
        BASE_URL,
        json={
            "title": "User 1's notification",
            "content": "Content for user 1's notification'",
            "channel": "email",
        },
        headers=auth_header(token1),
    )
    notification_id = response.json()["id"]

    _ = await create_test_user(client, name="user2", email="user2@example.com")
    token2 = await login_user(client, email="user2@example.com")
    response = await client.get(
        f"{BASE_URL}/{notification_id}", headers=auth_header(token2)
    )

    assert response.status_code == 403
    assert response.json()["error_code"] == "PERMISSION_DENIED"


@pytest.mark.anyio
async def test_update_notification_success(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    response = await client.post(
        BASE_URL,
        json={
            "title": "Original Notification",
            "content": "Original content",
            "channel": "email",
        },
        headers=headers,
    )
    notification_id = response.json()["id"]

    response = await client.patch(
        f"{BASE_URL}/{notification_id}",
        json={"title": "Updated Title"},
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Original content"
    assert data["channel"] == "email"
    assert data["user_id"] == user["id"]
    assert "id" in data
    assert "created_at" in data


@pytest.mark.anyio
async def test_update_notification_wrong_user(client: AsyncClient):
    _ = await create_test_user(client, name="user1", email="user1@example.com")
    token1 = await login_user(client, email="user1@example.com")
    response = await client.post(
        BASE_URL,
        json={
            "title": "User's 1 Notification",
            "content": "Only user 1 should edit this!",
            "channel": "email",
        },
        headers=auth_header(token1),
    )
    notification_id = response.json()["id"]

    _ = await create_test_user(client, name="user2", email="user2@example.com")
    token2 = await login_user(client, email="user2@example.com")
    response = await client.patch(
        f"{BASE_URL}/{notification_id}",
        json={"title": "Hacked Title"},
        headers=auth_header(token2),
    )

    assert response.status_code == 403
    assert response.json()["error_code"] == "PERMISSION_DENIED"


@pytest.mark.anyio
async def test_update_notification_not_found(client: AsyncClient):
    _ = await create_test_user(client)
    token = await login_user(client)

    non_existing_id = "00000000-0000-0000-0000-000000000000"
    response = await client.patch(
        f"{BASE_URL}/{non_existing_id}",
        json={"title": "This Notification does not exist"},
        headers=auth_header(token),
    )

    assert response.status_code == 404
    assert response.json()["error_code"] == "NOTIFICATION_NOT_FOUND"


@pytest.mark.anyio
async def test_delete_notification_success(client: AsyncClient):
    _ = await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)
    response = await client.post(
        BASE_URL,
        json={
            "title": "Notification Title",
            "content": "Content for notification",
            "channel": "email",
        },
        headers=headers,
    )
    notification_id = response.json()["id"]
    response = await client.delete(
        f"{BASE_URL}/{notification_id}", headers=auth_header(token)
    )

    assert response.status_code == 204
    assert not response.content

    response = await client.get(f"{BASE_URL}/{notification_id}", headers=headers)

    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "NOTIFICATION_NOT_FOUND"
    assert notification_id in data["detail"]


@pytest.mark.anyio
async def test_delete_notification_wrong_user(client: AsyncClient):
    _ = await create_test_user(client, name="user1", email="user1@example.com")
    token1 = await login_user(client, email="user1@example.com")
    response = await client.post(
        BASE_URL,
        json={
            "title": "User's 1 Notification",
            "content": "Only user 1 should delete this!",
            "channel": "email",
        },
        headers=auth_header(token1),
    )
    notification_id = response.json()["id"]

    _ = await create_test_user(client, name="user2", email="user2@example.com")
    token2 = await login_user(client, email="user2@example.com")
    response = await client.delete(
        f"{BASE_URL}/{notification_id}",
        headers=auth_header(token2),
    )

    assert response.status_code == 403
    assert response.json()["error_code"] == "PERMISSION_DENIED"


@pytest.mark.anyio
async def test_delete_notification_not_found(client: AsyncClient):
    _ = await create_test_user(client)
    token = await login_user(client)

    non_existing_id = "00000000-0000-0000-0000-000000000000"
    response = await client.delete(
        f"{BASE_URL}/{non_existing_id}",
        headers=auth_header(token),
    )

    assert response.status_code == 404
    assert response.json()["error_code"] == "NOTIFICATION_NOT_FOUND"


@pytest.mark.anyio
async def test_get_notifications_for_current_user_with_pagination(client: AsyncClient):
    _ = await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    for i in range(5):
        response = await client.post(
            BASE_URL,
            json={
                "title": f"Notification {i}",
                "content": f"Content for notification {i}",
                "channel": "email",
            },
            headers=headers,
        )
        assert response.status_code == 201

    response = await client.get(BASE_URL, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["notifications"]) == 5
    assert data["has_more"] is False

    response = await client.get(f"{BASE_URL}?limit=2", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["notifications"]) == 2
    assert data["has_more"] is True

    response = await client.get(f"{BASE_URL}?skip=2&limit=2", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["notifications"]) == 2
    assert data["skip"] == 2
    assert data["limit"] == 2
    assert data["has_more"] is True

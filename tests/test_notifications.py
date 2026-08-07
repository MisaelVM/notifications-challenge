import pytest
from httpx import AsyncClient
from pytest_mock import AsyncMockType

from tests.conftest import (
    NotificationChannel,
    auth_header,
    create_simple_notification,
    create_test_user,
    login_user,
    update_test_user_recipient,
)

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
async def test_create_email_notification_success(
    client: AsyncClient,
    notification_strategy_mocks: dict[NotificationChannel, AsyncMockType],
):
    user = await create_test_user(client)
    token = await login_user(client)

    new_notification = {
        "title": "Test Notification",
        "content": "Test notification content",
        "channel": "EMAIL",
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
    assert data["status"] == "PENDING"
    assert data["user_id"] == user["id"]
    assert "id" in data
    assert "created_at" in data

    for channel, notification_send_mock in notification_strategy_mocks.items():
        if channel == "EMAIL":
            notification_send_mock.assert_awaited_once()
            args, kwargs = notification_send_mock.call_args
            payload = args[0] if args else kwargs.get("payload")

            assert payload.recipient == user["email"]
            assert payload.title == new_notification["title"]
            assert payload.content == new_notification["content"]
        else:
            notification_send_mock.assert_not_awaited()


@pytest.mark.anyio
async def test_create_sms_notification_success(
    client: AsyncClient,
    notification_strategy_mocks: dict[NotificationChannel, AsyncMockType],
):
    user = await create_test_user(client)
    token = await login_user(client)

    new_notification = {
        "title": "Test Notification",
        "content": "Test notification content",
        "channel": "SMS",
    }
    await update_test_user_recipient(client, "phone_number", "+14155550123", token)
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
    assert data["status"] == "PENDING"
    assert data["user_id"] == user["id"]
    assert "id" in data
    assert "created_at" in data

    for channel, notification_send_mock in notification_strategy_mocks.items():
        if channel == "SMS":
            notification_send_mock.assert_awaited_once()
            args, kwargs = notification_send_mock.call_args
            payload = args[0] if args else kwargs.get("payload")

            assert payload.recipient == "+14155550123"
            assert payload.title == new_notification["title"]
            assert payload.content == new_notification["content"]
        else:
            notification_send_mock.assert_not_awaited()


@pytest.mark.anyio
async def test_create_push_notification_success(
    client: AsyncClient,
    notification_strategy_mocks: dict[NotificationChannel, AsyncMockType],
):
    user = await create_test_user(client)
    token = await login_user(client)

    new_notification = {
        "title": "Test Notification",
        "content": "Test notification content",
        "channel": "PUSH_NOTIFICATION",
    }
    await update_test_user_recipient(client, "push_token", "test_push", token)
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
    assert data["status"] == "PENDING"
    assert data["user_id"] == user["id"]
    assert "id" in data
    assert "created_at" in data

    for channel, notification_send_mock in notification_strategy_mocks.items():
        if channel == "PUSH_NOTIFICATION":
            notification_send_mock.assert_awaited_once()
            args, kwargs = notification_send_mock.call_args
            payload = args[0] if args else kwargs.get("payload")

            assert payload.recipient == "test_push"
            assert payload.title == new_notification["title"]
            assert payload.content == new_notification["content"]
        else:
            notification_send_mock.assert_not_awaited()


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
async def test_get_notification_success(
    client: AsyncClient,
    notification_strategy_mocks: dict[NotificationChannel, AsyncMockType],
):
    user = await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)
    notification = await create_simple_notification(
        client,
        notification_strategy_mocks,
        token,
        title="Notification Title",
        content="Content for notification",
    )
    notification_id = notification["id"]

    response = await client.get(f"{BASE_URL}/{notification_id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == notification["title"]
    assert data["content"] == notification["content"]
    assert data["channel"] == notification["channel"]
    assert data["user_id"] == user["id"]
    assert "id" in data
    assert "status" in data
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
async def test_get_notification_forbidden(
    client: AsyncClient,
    notification_strategy_mocks: dict[NotificationChannel, AsyncMockType],
):
    _ = await create_test_user(client, name="user1", email="user1@example.com")
    token1 = await login_user(client, email="user1@example.com")

    notification = await create_simple_notification(
        client,
        notification_strategy_mocks,
        token1,
        title="User 1's notification",
        content="Content for user 1's notification'",
    )
    notification_id = notification["id"]

    _ = await create_test_user(client, name="user2", email="user2@example.com")
    token2 = await login_user(client, email="user2@example.com")
    response = await client.get(
        f"{BASE_URL}/{notification_id}", headers=auth_header(token2)
    )

    assert response.status_code == 403
    assert response.json()["error_code"] == "PERMISSION_DENIED"


@pytest.mark.anyio
async def test_update_notification_success(
    client: AsyncClient,
    notification_strategy_mocks: dict[NotificationChannel, AsyncMockType],
):
    user = await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    notification = await create_simple_notification(
        client,
        notification_strategy_mocks,
        token,
        title="Original Notification",
        content="Original content",
    )
    notification_id = notification["id"]

    response = await client.patch(
        f"{BASE_URL}/{notification_id}",
        json={"title": "Updated Title"},
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Original content"
    assert data["channel"] == "EMAIL"
    assert data["user_id"] == user["id"]
    assert "status" in data
    assert "id" in data
    assert "created_at" in data


@pytest.mark.anyio
async def test_update_notification_wrong_user(
    client: AsyncClient,
    notification_strategy_mocks: dict[NotificationChannel, AsyncMockType],
):
    _ = await create_test_user(client, name="user1", email="user1@example.com")
    token1 = await login_user(client, email="user1@example.com")
    notification = await create_simple_notification(
        client,
        notification_strategy_mocks,
        token1,
        title="User's 1 Notification",
        content="Only user 1 should edit this!",
    )
    notification_id = notification["id"]

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
async def test_delete_notification_success(
    client: AsyncClient,
    notification_strategy_mocks: dict[NotificationChannel, AsyncMockType],
):
    _ = await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)
    notification = await create_simple_notification(
        client,
        notification_strategy_mocks,
        token,
        title="Notification Title",
        content="Content for notification",
    )
    notification_id = notification["id"]
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
async def test_delete_notification_wrong_user(
    client: AsyncClient,
    notification_strategy_mocks: dict[NotificationChannel, AsyncMockType],
):
    _ = await create_test_user(client, name="user1", email="user1@example.com")
    token1 = await login_user(client, email="user1@example.com")
    notification = await create_simple_notification(
        client,
        notification_strategy_mocks,
        token1,
        title="User's 1 Notification",
        content="Only user 1 should delete this!",
    )
    notification_id = notification["id"]

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
async def test_get_notifications_for_current_user_with_pagination(
    client: AsyncClient,
    notification_strategy_mocks: dict[NotificationChannel, AsyncMockType],
):
    _ = await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    for i in range(5):
        _ = await create_simple_notification(
            client,
            notification_strategy_mocks,
            token,
            title=f"Notification {i}",
            content=f"Content for notification {i}",
        )

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

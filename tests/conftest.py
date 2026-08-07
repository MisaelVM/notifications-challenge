from collections.abc import AsyncGenerator
from typing import Any, Literal

import pytest
from httpx import ASGITransport, AsyncClient
from pytest_mock import AsyncMockType, MockerFixture, MockType
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import Settings
from app.core.database import Base, get_db_session
from app.core.push.fcm_client import FCMClient
from app.core.rate_limiter import limiter
from app.main import app
from app.notifications.strategies.dependencies import get_strategies
from app.notifications.strategies.email_dispatcher_strategy import (
    EmailDispatcherStrategy,
)
from app.notifications.strategies.push_dispatcher_strategy import PushDispatcherStrategy

type NotificationChannel = Literal["EMAIL", "PUSH_NOTIFICATION"]

test_settings = Settings(_env_file=".env.test")  # pyright: ignore[reportCallIssue]
limiter.enabled = False

pytest_plugins = ["anyio"]


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def test_engine():
    return create_async_engine(
        test_settings.database_connection_url.get_secret_value(),
        poolclass=NullPool,
    )


@pytest.fixture(scope="session")
async def setup_database(test_engine: AsyncEngine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


@pytest.fixture
async def db_session(
    test_engine: AsyncEngine, setup_database
) -> AsyncGenerator[AsyncSession]:
    conn = await test_engine.connect()
    trans = await conn.begin()

    test_async_session = async_sessionmaker(
        bind=conn,
        class_=AsyncSession,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    async with test_async_session() as session:
        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()
            await conn.close()


@pytest.fixture
def fcm_client_mock(mocker: MockerFixture) -> MockType:
    return mocker.MagicMock(spec=FCMClient)


@pytest.fixture
def notification_strategy_mocks(
    mocker: MockerFixture,
) -> dict[NotificationChannel, AsyncMockType]:
    return {
        "EMAIL": mocker.AsyncMock(return_value=True),
        "PUSH_NOTIFICATION": mocker.AsyncMock(return_value=True),
    }


@pytest.fixture
async def client(
    db_session: AsyncSession,
    notification_strategy_mocks: dict[NotificationChannel, AsyncMockType],
    fcm_client_mock: MockType,
) -> AsyncGenerator[AsyncClient]:
    async def override_get_db_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session

    def override_get_strategies() -> dict[NotificationChannel, Any]:
        email_inst = EmailDispatcherStrategy()
        email_inst.send = notification_strategy_mocks["EMAIL"]

        push_inst = PushDispatcherStrategy(fcm_client_mock)
        push_inst.send = notification_strategy_mocks["PUSH_NOTIFICATION"]

        return {"EMAIL": email_inst, "PUSH_NOTIFICATION": push_inst}

    app.dependency_overrides[get_strategies] = override_get_strategies

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


async def create_test_user(
    client: AsyncClient,
    name: str = "testuser",
    email: str = "test@example.com",
    password: str = "testpassword123",  # noqa: S107
) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth", json={"name": name, "email": email, "password": password}
    )
    assert response.status_code == 201, f"Failed to create user: {response.text}"
    return response.json()


async def login_user(
    client: AsyncClient,
    email: str = "test@example.com",
    password: str = "testpassword123",  # noqa: S107
) -> str:
    response = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": password}
    )
    assert response.status_code == 200, f"Failed to login: {response.text}"
    return response.json()["access_token"]


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def update_test_user_recipient(
    client: AsyncClient, recipient_type: str, recipient: str, auth_token: str
) -> dict[str, str]:
    response = await client.get("/api/v1/users/me", headers=auth_header(auth_token))
    assert response.status_code == 200, f"Failed to get current user: {response.text}"

    user = response.json()
    response = await client.patch(
        f"/api/v1/users/{user['id']}",
        json={recipient_type: recipient},
        headers=auth_header(auth_token),
    )
    assert response.status_code == 200, f"Failed to update user: {response.text}"
    data = response.json()
    assert data[recipient_type] == recipient, "Recipient was not properly updated"

    return data


async def create_simple_notification(
    client: AsyncClient,
    notification_strategy_mocks: dict[NotificationChannel, AsyncMockType],
    auth_token: str,
    title: str = "Test Notification",
    content: str = "Test notification content",
    channel: NotificationChannel = "EMAIL",
) -> dict[str, str]:
    notification_strategy_send_mock = notification_strategy_mocks[channel]
    notification_strategy_send_mock.reset_mock()

    new_notification = {
        "title": title,
        "content": content,
        "channel": channel.upper(),
    }
    response = await client.post(
        "/api/v1/notifications", json=new_notification, headers=auth_header(auth_token)
    )

    assert response.status_code == 201, (
        f"Failed to create notification: {response.text}"
    )
    data = response.json()
    assert response.headers["Location"] == f"/api/v1/notifications/{data['id']}"

    notification_strategy_send_mock.assert_awaited_once()

    return data

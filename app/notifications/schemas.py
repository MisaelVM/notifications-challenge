from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from app.notifications.models import NotificationChannels, NotificationStatus


def uppercase_channel[T](value: T) -> T | str:
    return value.upper() if isinstance(value, str) else value


class NotificationBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    channel: Annotated[NotificationChannels, BeforeValidator(uppercase_channel)] = (
        Field(default=NotificationChannels.EMAIL)
    )


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    content: str | None = Field(default=None, min_length=1)
    channel: Annotated[
        NotificationChannels | None, BeforeValidator(uppercase_channel)
    ] = Field(default=None)


class NotificationResponse(NotificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    status: NotificationStatus
    user_id: UUID


class PaginatedNotificationResponse(BaseModel):
    notifications: list[NotificationResponse]
    total: int
    skip: int
    limit: int
    has_more: bool

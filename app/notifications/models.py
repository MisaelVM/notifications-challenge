from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.users.models import User


class NotificationChannels(enum.StrEnum):
    EMAIL = "email"
    SMS = "sms"
    PUSH_NOTIFICATION = "push_notification"


class Notification(Base):
    __tablename__: str = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID, default=uuid.uuid4, primary_key=True, index=True
    )
    title: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    content: Mapped[str] = mapped_column(sa.Text, nullable=False)
    channel: Mapped[NotificationChannels] = mapped_column(
        sa.Enum(NotificationChannels, name="notification_channels"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), default=sa.func.now(), server_default=sa.func.now()
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id"), nullable=False, index=True
    )

    user: Mapped[User] = relationship(back_populates="notifications")

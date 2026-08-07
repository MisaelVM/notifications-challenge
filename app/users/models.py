from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.notifications.models import Notification


class User(Base):
    __tablename__: str = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID, default=uuid.uuid4, primary_key=True, index=True
    )
    name: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    email: Mapped[str] = mapped_column(
        sa.String(120), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(sa.String(200), nullable=False)

    push_token: Mapped[str | None] = mapped_column(
        sa.String(200), nullable=True, default=None
    )

    notifications: Mapped[list[Notification]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

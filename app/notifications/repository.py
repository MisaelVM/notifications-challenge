from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.notifications.models import Notification, NotificationStatus
from app.notifications.schemas import NotificationCreate, NotificationUpdate


class NotificationRepository:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db_session)]) -> None:
        self._db: AsyncSession = db

    async def get_total_count_by_user_id(self, user_id: UUID) -> int:
        count_result = await self._db.execute(
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id)
        )
        return count_result.scalar() or 0

    async def find_all_by_user_id(
        self, user_id: UUID, skip: int, limit: int
    ) -> Sequence[Notification]:
        result = await self._db.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def find_by_id(self, notification_id: UUID) -> Notification | None:
        result = await self._db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar()

    async def create(
        self, create_data: NotificationCreate, user_id: UUID
    ) -> Notification:
        new_notification = Notification(
            title=create_data.title,
            content=create_data.content,
            channel=create_data.channel,
            user_id=user_id,
        )
        self._db.add(new_notification)
        await self._db.commit()
        await self._db.refresh(new_notification, attribute_names=["user"])

        return new_notification

    async def update(
        self, notification: Notification, update_data: NotificationUpdate
    ) -> None:
        data_to_update = update_data.model_dump(exclude_unset=True, exclude_none=True)
        for field, value in data_to_update.items():
            setattr(notification, field, value)
        await self._db.commit()
        await self._db.refresh(notification, attribute_names=["user"])

    async def update_status(
        self, notification: Notification, status: NotificationStatus
    ) -> None:
        notification.status = status
        await self._db.commit()
        await self._db.refresh(notification, attribute_names=["user"])

    async def delete(self, notification: Notification) -> None:
        await self._db.delete(notification)
        await self._db.commit()

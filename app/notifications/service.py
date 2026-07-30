from typing import Annotated
from uuid import UUID

from fastapi import Depends

from app.auth.exceptions import PermissionDeniedException
from app.notifications.exceptions import NotificationNotFoundException
from app.notifications.repository import NotificationRepository
from app.notifications.schemas import (
    NotificationCreate,
    NotificationResponse,
    NotificationUpdate,
    PaginatedNotificationResponse,
)


class NotificationService:
    def __init__(
        self, notification_repository: Annotated[NotificationRepository, Depends()]
    ) -> None:
        self._notification_repository: NotificationRepository = notification_repository

    async def get_notifications_by_user_id(
        self, user_id: UUID, skip: int, limit: int
    ) -> PaginatedNotificationResponse:
        total = await self._notification_repository.get_total_count_by_user_id(user_id)
        notifications = await self._notification_repository.find_all_by_user_id(
            user_id, skip, limit
        )
        has_more = skip + len(notifications) < total

        return PaginatedNotificationResponse(
            notifications=[
                NotificationResponse.model_validate(notification)
                for notification in notifications
            ],
            total=total,
            skip=skip,
            limit=limit,
            has_more=has_more,
        )

    async def get_notification_by_id(
        self, notification_id: UUID, user_id: UUID
    ) -> NotificationResponse:
        notification = await self._notification_repository.find_by_id(notification_id)
        if not notification:
            raise NotificationNotFoundException(str(notification_id))

        if notification.user_id != user_id:
            raise PermissionDeniedException(
                action_description="Read someone else's notifications"
            )

        return NotificationResponse.model_validate(notification)

    async def create_notification(
        self, create_data: NotificationCreate, user_id: UUID
    ) -> NotificationResponse:
        notification = await self._notification_repository.create(create_data, user_id)
        return NotificationResponse.model_validate(notification)

    async def update_notification(
        self, notification_id: UUID, update_data: NotificationUpdate, user_id: UUID
    ) -> NotificationResponse:
        notification = await self._notification_repository.find_by_id(notification_id)
        if not notification:
            raise NotificationNotFoundException(str(notification_id))

        if notification.user_id != user_id:
            raise PermissionDeniedException(
                action_description="Modify someone else's notifications"
            )

        await self._notification_repository.update(notification, update_data)
        return NotificationResponse.model_validate(notification)

    async def delete_notification(self, notification_id: UUID, user_id: UUID) -> None:
        notification = await self._notification_repository.find_by_id(notification_id)
        if not notification:
            raise NotificationNotFoundException(str(notification_id))

        if notification.user_id != user_id:
            raise PermissionDeniedException(
                action_description="Delete someone else's notifications"
            )

        await self._notification_repository.delete(notification)


type NotificationServiceDependency = Annotated[NotificationService, Depends()]

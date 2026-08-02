from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Query, Response, status

from app.auth.service import CurrentUser
from app.notifications.schemas import (
    NotificationCreate,
    NotificationResponse,
    NotificationUpdate,
    PaginatedNotificationResponse,
)
from app.notifications.service import NotificationServiceDependency

router = APIRouter(prefix="/notifications")


@router.get("", response_model=PaginatedNotificationResponse)
async def get_notifications_for_current_user(
    current_user: CurrentUser,
    service: NotificationServiceDependency,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    return await service.get_notifications_by_user_id(current_user.id, skip, limit)


@router.post(
    "", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED
)
async def create_notification(
    notification_create_data: NotificationCreate,
    current_user: CurrentUser,
    background_tasks: BackgroundTasks,
    service: NotificationServiceDependency,
    response: Response,
):
    new_notification = await service.create_notification(
        notification_create_data, current_user, background_tasks
    )
    response.headers["Location"] = f"/api/v1/notifications/{new_notification.id}"
    return new_notification


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: UUID,
    current_user: CurrentUser,
    service: NotificationServiceDependency,
):
    return await service.get_notification_by_id(notification_id, current_user.id)


@router.patch("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: UUID,
    notification_update_data: NotificationUpdate,
    current_user: CurrentUser,
    service: NotificationServiceDependency,
):
    return await service.update_notification(
        notification_id, notification_update_data, current_user.id
    )


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: UUID,
    current_user: CurrentUser,
    service: NotificationServiceDependency,
):
    await service.delete_notification(notification_id, current_user.id)

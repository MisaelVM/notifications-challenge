from fastapi import status

from app.core.exception_handlers import CustomException


class NotificationsException(CustomException):
    """Base exception for notification-related errors."""


class NotificationNotFoundException(NotificationsException):
    def __init__(self, notification_id: str) -> None:
        super().__init__(
            error_code="NOTIFICATION_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with id '{notification_id}' not found",
        )

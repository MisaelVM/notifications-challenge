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


class InvalidChannelException(NotificationsException):
    def __init__(self, supported_channels: list[str]) -> None:
        super().__init__(
            error_code="INVALID_CHANNEL",
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Invalid or unsupported channel. Only the following channels are supported at the moment: {supported_channels}",
        )


class InvalidRecipientException(NotificationsException):
    def __init__(self, channel: str, recipient_type: str) -> None:
        super().__init__(
            error_code="INVALID_RECIPIENT",
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"{channel} channel requires a valid '{recipient_type}' in your profile. Update your profile to include one.",
        )

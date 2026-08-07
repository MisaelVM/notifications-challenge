import logging
from typing import TYPE_CHECKING, override

from app.core.push.fcm_client import FCMClient, FCMClientDependency
from app.notifications.exceptions import InvalidRecipientException

from .notification_dispatcher_strategy import (
    NotificationDeliveryPayload,
    NotificationDispatcherStrategy,
)

if TYPE_CHECKING:
    from app.users.models import User

logger = logging.getLogger(__name__)


class PushDeliveryPayload(NotificationDeliveryPayload):
    pass


class PushDispatcherStrategy(NotificationDispatcherStrategy):
    def __init__(self, fcm_client: FCMClientDependency) -> None:
        self._fcm_client: FCMClient = fcm_client

    @override
    def validate_requirements(
        self, title: str, content: str, user: User
    ) -> NotificationDeliveryPayload:
        if not user.push_token:
            raise InvalidRecipientException(
                channel="PUSH_NOTIFICATION", recipient_type="push_token"
            )

        return PushDeliveryPayload(
            recipient=user.push_token,
            title=title,
            content=content,
        )

    @override
    async def send(self, payload: NotificationDeliveryPayload) -> bool:
        try:
            response = await self._fcm_client.send_notification(
                title=payload.title,
                body=payload.content,
                fid=payload.recipient,
            )
        except Exception:
            logger.exception("Push Notification Delivery failed")
            return False
        else:
            return response.success

import logging
from typing import TYPE_CHECKING, override

from pydantic import Field

from app.core.sms.twilio_client import TwilioClient, TwilioClientDependency
from app.notifications.exceptions import InvalidRecipientException
from app.users.schemas import E164NumberType

from .notification_dispatcher_strategy import (
    NotificationDeliveryPayload,
    NotificationDispatcherStrategy,
)

if TYPE_CHECKING:
    from app.users.models import User


logger = logging.getLogger(__name__)


class SMSDeliveryPayload(NotificationDeliveryPayload):
    recipient: E164NumberType
    content: str = Field(min_length=1, max_length=160)


class SMSDispatcherStrategy(NotificationDispatcherStrategy):
    def __init__(self, twilio_client: TwilioClientDependency) -> None:
        self._twilio_client: TwilioClient = twilio_client

    @override
    def validate_requirements(
        self, title: str, content: str, user: User
    ) -> NotificationDeliveryPayload:
        if user.phone_number is None:
            raise InvalidRecipientException(
                channel="SMS", recipient_type="phone_number"
            )

        return SMSDeliveryPayload(
            recipient=user.phone_number, title=title, content=content
        )

    @override
    async def send(self, payload: NotificationDeliveryPayload) -> bool:
        try:
            await self._twilio_client.send_sms(
                to_number=payload.recipient, body=payload.content
            )
        except Exception:
            logger.exception("SMS Dispatch failed")
            return False
        else:
            return True

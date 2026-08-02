from typing import TYPE_CHECKING, override

from fastapi.templating import Jinja2Templates
from pydantic import EmailStr

from app.core.email import send_email

from .notification_dispatcher_strategy import (
    NotificationDeliveryPayload,
    NotificationDispatcherStrategy,
)

if TYPE_CHECKING:
    from app.users.models import User


class EmailDeliveryPayload(NotificationDeliveryPayload):
    recipient: EmailStr


class EmailDispatcherStrategy(NotificationDispatcherStrategy):
    @override
    def validate_requirements(
        self, title: str, content: str, user: User
    ) -> NotificationDeliveryPayload:
        return EmailDeliveryPayload(recipient=user.email, title=title, content=content)

    @override
    async def send(self, payload: NotificationDeliveryPayload) -> bool:
        templates = Jinja2Templates(directory="templates")

        template = templates.env.get_template("email_notification.html")
        html_content = template.render(title=payload.title, content=payload.content)

        errors, _ = await send_email(
            to_email=payload.recipient,
            subject=payload.title,
            plain_text=payload.content,
            html_content=html_content,
        )
        return not errors

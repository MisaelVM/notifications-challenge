from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.users.models import User


class NotificationDeliveryPayload(BaseModel):
    recipient: str
    title: str
    content: str


class NotificationDispatcherStrategy(ABC):
    @abstractmethod
    def validate_requirements(
        self, title: str, content: str, user: User
    ) -> NotificationDeliveryPayload: ...

    @abstractmethod
    async def send(self, payload: NotificationDeliveryPayload) -> bool: ...

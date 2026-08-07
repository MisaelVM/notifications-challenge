from app.core.push.fcm_client import FCMClient
from app.notifications.models import NotificationChannels
from app.notifications.strategies.email_dispatcher_strategy import (
    EmailDispatcherStrategy,
)
from app.notifications.strategies.notification_dispatcher_strategy import (
    NotificationDispatcherStrategy,
)
from app.notifications.strategies.push_dispatcher_strategy import PushDispatcherStrategy

type NotificationStrategiesTable = dict[
    NotificationChannels, NotificationDispatcherStrategy
]


def get_strategies() -> NotificationStrategiesTable:
    return {
        NotificationChannels.EMAIL: EmailDispatcherStrategy(),
        NotificationChannels.PUSH_NOTIFICATION: PushDispatcherStrategy(FCMClient()),
    }

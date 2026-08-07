from typing import Annotated

import firebase_admin
from fastapi import Depends
from firebase_admin import credentials, messaging

from app.core.config import settings


class FCMClient:
    def __init__(self) -> None:
        if not firebase_admin._apps:
            self.__initialize_firebase()

    def __initialize_firebase(self) -> None:
        firebase_cred = credentials.Certificate(settings.fcm_service_key_file)
        firebase_admin.initialize_app(firebase_cred)

    async def send_notification(
        self, title: str, body: str, fid: str
    ) -> messaging.SendResponse:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            fid=fid,
        )
        result = await messaging.send_each_async([message])
        response = result.responses[0]
        if not response.success:
            raise response.exception

        return response


type FCMClientDependency = Annotated[FCMClient, Depends()]

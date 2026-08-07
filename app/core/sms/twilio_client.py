from typing import TYPE_CHECKING, Annotated

from fastapi import Depends
from twilio.http.async_http_client import AsyncTwilioHttpClient
from twilio.rest import Client

if TYPE_CHECKING:
    from twilio.rest.api.v2010.account.message import MessageInstance

from app.core.config import settings


class TwilioClient:
    def __init__(self) -> None:
        self.__initialize_twilio()

    def __initialize_twilio(self) -> None:
        self.__client: Client = Client(
            settings.twilio_api_key,
            settings.twilio_api_secret.get_secret_value(),
            account_sid=settings.twilio_account_sid,
            http_client=AsyncTwilioHttpClient(),
        )

    async def send_sms(self, to_number: str, body: str) -> MessageInstance:
        return await self.__client.messages.create_async(
            body=body,
            from_=settings.twilio_phone_number,
            to=to_number,
        )


type TwilioClientDependency = Annotated[TwilioClient, Depends()]

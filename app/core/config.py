from pathlib import Path

from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_protocol_driver: str
    database_host: str
    database_port: int
    database_user: str
    database_password: SecretStr
    database_name: str

    @computed_field
    @property
    def database_connection_url(self) -> SecretStr:
        connection_url = (
            f"{self.database_protocol_driver}://"
            f"{self.database_user}:{self.database_password.get_secret_value()}@"
            f"{self.database_host}:{self.database_port}/"
            f"{self.database_name}"
        )
        return SecretStr(connection_url)

    jwt_secret_key: SecretStr
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    mail_server: str = "localhost"
    mail_port: int = 587
    mail_username: str = ""
    mail_password: SecretStr = SecretStr("")
    mail_from: str = "noreply@example.com"
    mail_use_tls: bool = True

    fcm_service_key_file: Path = Path()

    twilio_account_sid: str
    twilio_api_key: str
    twilio_api_secret: SecretStr
    twilio_phone_number: str


settings = Settings()  # pyright: ignore[reportCallIssue]

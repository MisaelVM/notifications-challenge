from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_user: str
    database_password: SecretStr
    database_name: str

    database_connection_url: SecretStr


settings = Settings()  # pyright: ignore[reportCallIssue]

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


settings = Settings()  # pyright: ignore[reportCallIssue]

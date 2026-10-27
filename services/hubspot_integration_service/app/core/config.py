from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    app_env: str = "development"
    log_level: str = "INFO"

    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "hubspot_sync"
    db_username: str = "postgres"
    db_password: str = Field(min_length=1)

    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_sync_topic: str = "hubspot.sync.requested"
    kafka_consumer_group: str = "hubspot-integration-group"

    hubspot_access_token: str = Field(min_length=1)
    hubspot_api_base_url: str = "https://api.hubapi.com"

    @property
    def database_url(self) -> str:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.db_username,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        ).render_as_string(hide_password=False)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

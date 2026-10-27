from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    log_level: str = "INFO"

    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_sync_topic: str = "hubspot.sync.requested"

    sync_cron_expression: str = "*/30 * * * *"
    sync_timezone: str = "Asia/Kolkata"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import create_async_engine


class Settings(BaseSettings):
    DATABASE_URL: str
    TEST_DATABASE_URL: str | None = None
    API_URL: str = "http://localhost:8000"

    model_config = SettingsConfigDict(
        env_file=".env",
    )


settings = Settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    connect_args={"server_settings": {"application_name": "service"}},
)

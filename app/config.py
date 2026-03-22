from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    APP_ENV: str = "development"

    DATABASE_URL: str
    TEST_DATABASE_URL: str = ""

    REDIS_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    RESET_TOKEN_EXPIRE_MINUTES: int = 15

    GMAIL_USER: str = ""
    GMAIL_APP_PASSWORD: str = ""

    model_config = SettingsConfigDict(
        env_file=".env", 
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
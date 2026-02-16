"""
Bot configuration.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Bot settings loaded from environment variables."""
    
    BOT_TOKEN: str
    BACKEND_URL: str
    WEB_APP_URL: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


settings = Settings()

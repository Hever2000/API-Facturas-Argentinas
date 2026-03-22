import os
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    APP_NAME: str = "FacturaAI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"

    # API
    API_V1_PREFIX: str = "/v1"
    SECRET_KEY: str = Field(default="changeme-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/facturaai"
    )
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    FREE_TIER_MONTHLY_LIMIT: int = 100
    PRO_TIER_MONTHLY_LIMIT: int = 1000
    ENTERPRISE_TIER_MONTHLY_LIMIT: int = 10000

    # OCR & LLM
    GROQ_API_KEY: str = Field(default="")
    PADDLE_VL_API_URL: str = Field(
        default="https://c6vceb62c4n8zfaf.aistudio-app.com/layout-parsing"
    )
    PADDLE_VL_TOKEN: str = Field(default="")

    # Mercado Pago
    MERCADO_PAGO_ACCESS_TOKEN: str = Field(default="")
    MERCADO_PAGO_WEBHOOK_SECRET: str = Field(default="")
    MERCADO_PAGO_ENABLED: bool = False

    # Storage
    STORAGE_PATH: str = Field(default="./storage")
    MAX_FILE_SIZE_MB: int = 10

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "https://facturaai.com"]

    # Paths
    TEMP_PATH: str = "./temp"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        os.makedirs(self.STORAGE_PATH, exist_ok=True)
        os.makedirs(self.TEMP_PATH, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()

"""Application settings and configuration."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database Configuration
    database_url: str = "postgresql://user:password@localhost:5432/dbname"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    redis_password: Optional[str] = None

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False

    # Logging
    log_level: str = "INFO"

    # Model Path
    models_path: str = "./models"

    # Cache Configuration
    cache_enabled: bool = True
    cache_type: str = "memory"  # memory or redis
    cache_ttl: int = 3600  # 1 hour in seconds

    # Authentication Configuration
    auth_enabled: bool = False
    auth_type: str = "jwt"  # jwt or api_key
    jwt_secret: str = "secret-key-change-in-production"
    jwt_algorithm: str = "HS256"

    # Pre-aggregations Configuration
    pre_aggregations_enabled: bool = True

    @property
    def database_url_async(self) -> str:
        """Get async database URL."""
        # Convert postgresql:// to postgresql+asyncpg://
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.database_url


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


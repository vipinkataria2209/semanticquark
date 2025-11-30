"""Application settings and configuration."""

from functools import lru_cache
from typing import Optional
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database Configuration
    # Option 1: Full URL (takes precedence if provided)
    database_url: Optional[str] = None
    
    # Option 2: Individual components (used if database_url is not provided)
    # Defaults match docker-compose.yml configuration
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "semanticquark_db"
    database_user: str = "semanticquark"
    database_password: str = "semanticquark123"
    
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Redis Configuration
    # Option 1: Full URL (takes precedence if provided)
    redis_url: Optional[str] = None
    
    # Option 2: Individual components (used if redis_url is not provided)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False

    # Logging
    log_level: str = "INFO"

    # Model Path
    models_path: str = "/Users/vkataria/vipin_github/community_contribution/semantic_quark/semanticquark/models"

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

    @computed_field
    def effective_database_url(self) -> str:
        """Get database URL from individual components or full URL."""
        # If full URL is provided, use it
        if self.database_url:
            return self.database_url
        
        # Otherwise, construct from individual components
        # URL encode password in case it contains special characters
        encoded_password = quote_plus(self.database_password)
        return f"postgresql://{self.database_user}:{encoded_password}@{self.database_host}:{self.database_port}/{self.database_name}"
    
    @computed_field
    def effective_redis_url(self) -> str:
        """Get Redis URL from individual components or full URL."""
        # If full URL is provided, use it
        if self.redis_url:
            return self.redis_url
        
        # Otherwise, construct from individual components
        password_part = f":{quote_plus(self.redis_password)}@" if self.redis_password else ""
        return f"redis://{password_part}{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def database_url_async(self) -> str:
        """Get async database URL."""
        url = self.effective_database_url
        # Convert postgresql:// to postgresql+asyncpg://
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


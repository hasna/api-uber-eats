"""
Configuration settings for Uber Eats API
"""
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, PostgresDsn, field_validator, validator
from pydantic_settings import BaseSettings
import secrets


class Settings(BaseSettings):
    # Project info
    PROJECT_NAME: str = "Uber Eats API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_USER: str = "uber_eats_user"
    POSTGRES_PASSWORD: str = "uber_eats_pass"
    POSTGRES_DB: str = "uber_eats_db"
    DATABASE_URL: Optional[PostgresDsn] = None
    
    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[str], info) -> Any:
        if isinstance(v, str):
            return v
        postgres_server = info.data.get("POSTGRES_SERVER")
        postgres_user = info.data.get("POSTGRES_USER")
        postgres_password = info.data.get("POSTGRES_PASSWORD")
        postgres_db = info.data.get("POSTGRES_DB")
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=postgres_user,
            password=postgres_password,
            host=postgres_server,
            path=f"{postgres_db or ''}",
        )
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Uber Eats API Configuration
    UBER_EATS_BASE_URL: str = "https://api.uber.com"
    UBER_EATS_AUTH_URL: str = "https://auth.uber.com/oauth/v2/token"
    UBER_EATS_CLIENT_ID: str = ""
    UBER_EATS_CLIENT_SECRET: str = ""
    UBER_EATS_WEBHOOK_SECRET: str = ""
    UBER_EATS_SANDBOX_MODE: bool = True
    
    # API Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 3600
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Webhook Configuration
    WEBHOOK_ENDPOINT: str = "/api/v1/webhooks/uber-eats"
    WEBHOOK_VERIFY_SIGNATURE: bool = True
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Cache TTL (in seconds)
    CACHE_TTL_SHORT: int = 300  # 5 minutes
    CACHE_TTL_MEDIUM: int = 3600  # 1 hour
    CACHE_TTL_LONG: int = 86400  # 24 hours
    
    # Background Tasks
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"
    
    # Sentry
    SENTRY_DSN: Optional[str] = None
    
    # Feature Flags
    ENABLE_METRICS: bool = True
    ENABLE_RATE_LIMITING: bool = True
    ENABLE_WEBHOOK_VERIFICATION: bool = True
    ENABLE_CACHE: bool = True
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
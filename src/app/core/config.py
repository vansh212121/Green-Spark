from pydantic import PostgresDsn, EmailStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Project Metadata ---
    PROJECT_NAME: str = "GreenSpark API"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Backend service for extracting structured data from electricity bills."
    ENVIRONMENT: str = "development"  # E.g., development, staging, production

    # --- API Configuration ---
    API_V1_STR: str = "/api/v1"
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    # --- Core Infrastructure Credentials ---
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_SERVER: str = "postgres"  # The Docker service name
    POSTGRES_PORT: int = 5432

    REDIS_URL: str  # For Celery Broker and caching

    @computed_field
    @property
    def DATABASE_URL(self) -> PostgresDsn:
        """Assemble the async database URL for the application."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @computed_field
    @property
    def DATABASE_URL_SYNC(self) -> str:
        """Assemble the sync database URL for Alembic migrations."""
        # Note: Uses localhost:5433 to connect from host to container
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@localhost:5433/{self.POSTGRES_DB}"
        )

    # --- Database Pool Settings ---
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # --- Security & JWT Settings ---
    JWT_SECRET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"

    # --- Email Settings (for fastapi-mail) ---
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int = 587
    MAIL_SERVER: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    # --- File Storage (S3/Minio) ---
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    S3_ENDPOINT_URL: str = "http://minio:9000"
    S3_ACCESS_KEY_ID: str
    S3_SECRET_ACCESS_KEY: str
    S3_BUCKET_NAME: str = "greenspark-bills"

    # --- Model Configuration ---
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
"""
Application configuration and settings
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional
from pathlib import Path

# Get the base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    # Application Settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Database Configuration
    DB_USER: str = "wealthadvisor"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "wealthdb"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432

    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL"""
        return (
            f"postgresql+asyncpg://"
            f"{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None

    # API Keys - Multiple Provider Support
    # Free/Affordable Providers
    GROQ_API_KEY: Optional[str] = None
    TOGETHER_API_KEY: Optional[str] = None
    ANYSCALE_API_KEY: Optional[str] = None
    REPLICATE_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None

    # Premium Providers (Optional)
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # Market Data APIs (Free Options)
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    TWELVE_DATA_API_KEY: Optional[str] = None
    FINNHUB_API_KEY: Optional[str] = None
    FMP_API_KEY: Optional[str] = None
    POLYGON_API_KEY: Optional[str] = None

    # JWT Configuration
    JWT_SECRET: str = "change-this-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:3000,https://www.walletwealth.co.in"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # LLM Configuration
    LLM_PROVIDER: str = "groq"
    LLM_MODEL: str = "mixtral-8x7b-32768"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2000

    # Email Configuration
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # Wallet Wealth API Integration
    WALLET_WEALTH_API_URL: str = "https://api.walletwealth.co.in"
    WALLET_WEALTH_API_KEY: Optional[str] = None

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_PORT: int = 9090

    # AWS Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "ap-south-1"
    S3_BUCKET_NAME: Optional[str] = None

    # Encryption
    ENCRYPTION_KEY: Optional[str] = None

    @field_validator("LLM_TEMPERATURE")
    @classmethod
    def validate_temperature(cls, v):
        """Validate LLM temperature is within valid range"""
        if not 0 <= v <= 2:
            raise ValueError("LLM_TEMPERATURE must be between 0 and 2")
        return v

    @field_validator("JWT_SECRET")
    @classmethod
    def validate_jwt_secret(cls, v, info):
        """Ensure JWT secret is changed in production"""
        # Access other field values through info.data
        environment = info.data.get("ENVIRONMENT", "development")
        if environment == "production" and v == "change-this-secret-key":
            raise ValueError(
                "JWT_SECRET must be changed for production environment"
            )
        return v

    class Config:
        env_file = str(BASE_DIR / ".env")
        case_sensitive = True
        extra = "allow"


# Create settings instance
settings = Settings()


# Validate critical settings
def validate_settings():
    """Validate that all critical settings are configured"""
    errors = []

    if settings.ENVIRONMENT == "production":
        # At least one LLM provider must be configured
        llm_providers = [
            settings.GROQ_API_KEY,
            settings.TOGETHER_API_KEY,
            settings.ANYSCALE_API_KEY,
            settings.REPLICATE_API_KEY,
            settings.HUGGINGFACE_API_KEY,
            settings.OPENAI_API_KEY,
            settings.ANTHROPIC_API_KEY
        ]

        if not any(llm_providers):
            errors.append("At least one LLM API key must be configured")

        if not settings.ENCRYPTION_KEY:
            errors.append("ENCRYPTION_KEY must be set in production")

        if settings.DEBUG:
            errors.append("DEBUG must be False in production")

    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")


# Run validation on import
if settings.ENVIRONMENT == "production":
    validate_settings()
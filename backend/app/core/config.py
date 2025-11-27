"""
Application configuration and settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional
from pathlib import Path

# Get the base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    # Application Settings
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # Database Configuration
    DB_USER: str = Field(default="wealthadvisor", env="DB_USER")
    DB_PASSWORD: str = Field(default="password", env="DB_PASSWORD")
    DB_NAME: str = Field(default="wealthdb", env="DB_NAME")
    DB_HOST: str = Field(default="localhost", env="DB_HOST")
    DB_PORT: int = Field(default=5432, env="DB_PORT")

    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL"""
        return f"postgresql+asyncpg://{
            self.DB_USER}:{
            self.DB_PASSWORD}@{
            self.DB_HOST}:{
                self.DB_PORT}/{
                    self.DB_NAME}"

    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")

    # API Keys - Multiple Provider Support
    # Free/Affordable Providers
    GROQ_API_KEY: Optional[str] = Field(default=None, env="GROQ_API_KEY")
    TOGETHER_API_KEY: Optional[str] = Field(
        default=None, env="TOGETHER_API_KEY")
    ANYSCALE_API_KEY: Optional[str] = Field(
        default=None, env="ANYSCALE_API_KEY")
    REPLICATE_API_KEY: Optional[str] = Field(
        default=None, env="REPLICATE_API_KEY")
    HUGGINGFACE_API_KEY: Optional[str] = Field(
        default=None, env="HUGGINGFACE_API_KEY")

    # Premium Providers (Optional)
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(
        default=None, env="ANTHROPIC_API_KEY")

    # Market Data APIs (Free Options)
    ALPHA_VANTAGE_API_KEY: Optional[str] = Field(
        default=None, env="ALPHA_VANTAGE_API_KEY")
    TWELVE_DATA_API_KEY: Optional[str] = Field(
        default=None, env="TWELVE_DATA_API_KEY")
    FINNHUB_API_KEY: Optional[str] = Field(default=None, env="FINNHUB_API_KEY")
    FMP_API_KEY: Optional[str] = Field(default=None, env="FMP_API_KEY")
    POLYGON_API_KEY: Optional[str] = Field(default=None, env="POLYGON_API_KEY")

    # JWT Configuration
    JWT_SECRET: str = Field(default="change-this-secret-key", env="JWT_SECRET")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_EXPIRATION_HOURS: int = Field(default=24, env="JWT_EXPIRATION_HOURS")

    # CORS Configuration
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,https://www.walletwealth.co.in",
        env="CORS_ORIGINS"
    )

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")

    # LLM Configuration
    LLM_PROVIDER: str = Field(default="groq", env="LLM_PROVIDER")
    LLM_MODEL: str = Field(default="mixtral-8x7b-32768", env="LLM_MODEL")
    LLM_TEMPERATURE: float = Field(default=0.7, env="LLM_TEMPERATURE")
    LLM_MAX_TOKENS: int = Field(default=2000, env="LLM_MAX_TOKENS")

    # Email Configuration
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")

    # Wallet Wealth API Integration
    WALLET_WEALTH_API_URL: str = Field(
        default="https://api.walletwealth.co.in",
        env="WALLET_WEALTH_API_URL"
    )
    WALLET_WEALTH_API_KEY: Optional[str] = Field(
        default=None, env="WALLET_WEALTH_API_KEY")

    # Monitoring
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    PROMETHEUS_PORT: int = Field(default=9090, env="PROMETHEUS_PORT")

    # AWS Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = Field(
        default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(
        default=None, env="AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = Field(default="ap-south-1", env="AWS_REGION")
    S3_BUCKET_NAME: Optional[str] = Field(default=None, env="S3_BUCKET_NAME")

    # Encryption
    ENCRYPTION_KEY: Optional[str] = Field(default=None, env="ENCRYPTION_KEY")

    @validator("LLM_TEMPERATURE")
    def validate_temperature(cls, v):
        """Validate LLM temperature is within valid range"""
        if not 0 <= v <= 2:
            raise ValueError("LLM_TEMPERATURE must be between 0 and 2")
        return v

    @validator("JWT_SECRET")
    def validate_jwt_secret(cls, v, values):
        """Ensure JWT secret is changed in production"""
        if values.get(
                "ENVIRONMENT") == "production" and v == "change-this-secret-key":
            raise ValueError(
                "JWT_SECRET must be changed for production environment")
        return v

    class Config:
        env_file = BASE_DIR / ".env"
        case_sensitive = True


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

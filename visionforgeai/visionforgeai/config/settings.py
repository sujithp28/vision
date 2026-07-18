"""Application Configuration Management.

This module handles loading and managing application configuration from
environment variables, .env files, and default values. It provides a
centralized, type-safe way to access configuration throughout the application.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Settings
    app_name: str = Field(default="VisionForge AI", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Enable debug mode")
    environment: str = Field(default="development", description="Environment (development, staging, production)")

    # API Settings
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_reload: bool = Field(default=False, description="Enable auto-reload (development only)")
    api_workers: int = Field(default=1, description="Number of API workers")

    # LLM Settings
    llm_provider: str = Field(default="openai", description="LLM provider (openai, anthropic, ollama, etc.)")
    llm_api_key: Optional[str] = Field(default=None, description="API key for the LLM provider")
    llm_model: str = Field(default="gpt-4o-mini", description="Default LLM model")
    llm_max_tokens: int = Field(default=2000, description="Maximum tokens for LLM responses")
    llm_temperature: float = Field(default=0.7, description="Default temperature for LLM sampling")
    llm_extra_config: dict = Field(default_factory=dict, description="Additional provider-specific configuration")

    # Database Settings
    database_url: str = Field(default="sqlite:///./visionforge.db", description="Database connection URL")
    database_echo: bool = Field(default=False, description="Enable SQL query logging")

    # Cache Settings
    redis_url: Optional[str] = Field(default=None, description="Redis URL for caching (optional)")
    cache_ttl: int = Field(default=3600, description="Default cache TTL in seconds")

    # Storage Settings
    storage_type: str = Field(default="local", description="Storage type (local, s3, gcs, azure)")
    storage_path: str = Field(default="./storage", description="Local storage path or bucket name")
    storage_bucket: Optional[str] = Field(default=None, description="Cloud storage bucket name")

    # Security Settings
    secret_key: str = Field(default="your-secret-key-here", description="Secret key for encryption and signing")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration time in minutes")

    # File Upload Settings
    max_upload_size: int = Field(default=100 * 1024 * 1024, description="Maximum file upload size in bytes")
    allowed_file_types: list[str] = Field(
        default=["image/jpeg", "image/png", "image/gif", "video/mp4", "video/quicktime", "text/plain", "application/pdf"],
        description="Allowed MIME types for file uploads"
    )
    upload_directory: str = Field(default="./uploads", description="Directory for uploaded files")

    # Output Settings
    output_directory: str = Field(default="./output", description="Directory for generated output files")
    temp_directory: str = Field(default="./tmp", description="Directory for temporary files")

    # Logging Settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="Log format")

    # External Service APIs
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    elevenlabs_api_key: Optional[str] = Field(default=None, description="ElevenLabs API key")
    runway_api_key: Optional[str] = Field(default=None, description="Runway ML API key")
    suno_api_key: Optional[str] = Field(default=None, description="Suno AI API key")

    # Feature Flags
    enable_usage_tracking: bool = Field(default=True, description="Enable API usage tracking and cost calculation")
    enable_content_moderation: bool = Field(default=False, description="Enable content moderation for generated content")
    enable_caching: bool = Field(default=True, description="Enable response caching")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        allowed = ["development", "staging", "production", "test"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v.upper()

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"


@lru_cache()
def get_settings() -> Settings:
    """Get the application settings (cached).

    Returns:
        Settings: The application settings instance
    """
    return Settings()


def validate_required_settings() -> list[str]:
    """Validate that all required settings are present.

    Returns:
        list[str]: List of missing required settings (empty if all present)
    """
    settings = get_settings()
    missing = []

    # Check for required API keys based on provider
    provider = settings.llm_provider.lower()
    if provider == "openai" and not settings.openai_api_key and not settings.llm_api_key:
        missing.append("OPENAI_API_KEY or LLM_API_KEY")
    elif provider == "anthropic" and not settings.anthropic_api_key and not settings.llm_api_key:
        missing.append("ANTHROPIC_API_KEY or LLM_API_KEY")
    # Add more provider-specific checks as needed

    # Always check for secret key in production
    if settings.is_production and settings.secret_key == "your-secret-key-here":
        missing.append("SECRET_KEY (must be changed in production)")

    return missing
"""Application settings and configuration."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""
    # Database configuration
    # Prefer DATABASE_URL if provided (common with Alembic/SQLAlchemy), fallback to database_url
    database_url: str = Field(default="sqlite:///./connector_framework.db", alias="DATABASE_URL")

    # Application settings
    app_name: str = "Connector Framework Manager"
    debug: bool = False

    # URL configuration
    backend_base_url: str = Field(default="http://localhost:3001", alias="BACKEND_BASE_URL")
    frontend_base_url: str = Field(default="http://localhost:3000", alias="FRONTEND_BASE_URL")

    # JWT configuration
    jwt_secret: str = Field(default="your-secret-key-here", alias="JWT_SECRET")  # Should be overridden in .env

    # OAuth configuration
    oauth_redirect_base: str = Field(default="http://localhost:3001", alias="OAUTH_REDIRECT_BASE")

    # Connector OAuth credentials
    jira_client_id: str = Field(default="", alias="JIRA_CLIENT_ID")
    jira_client_secret: str = Field(default="", alias="JIRA_CLIENT_SECRET")
    confluence_client_id: str = Field(default="", alias="CONFLUENCE_CLIENT_ID")
    confluence_client_secret: str = Field(default="", alias="CONFLUENCE_CLIENT_SECRET")
    slack_client_id: str = Field(default="", alias="SLACK_CLIENT_ID")
    slack_client_secret: str = Field(default="", alias="SLACK_CLIENT_SECRET")
    notion_client_id: str = Field(default="", alias="NOTION_CLIENT_ID")
    notion_client_secret: str = Field(default="", alias="NOTION_CLIENT_SECRET")
    figma_client_id: str = Field(default="", alias="FIGMA_CLIENT_ID")
    figma_client_secret: str = Field(default="", alias="FIGMA_CLIENT_SECRET")
    datadog_client_id: str = Field(default="", alias="DATADOG_CLIENT_ID")
    datadog_client_secret: str = Field(default="", alias="DATADOG_CLIENT_SECRET")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


# Global settings instance
settings = Settings()

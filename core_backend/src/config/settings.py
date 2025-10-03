"""Application settings and configuration."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database configuration
    database_url: str = "sqlite:///./connector_framework.db"
    
    # Application settings
    app_name: str = "Connector Framework Manager"
    debug: bool = False
    
    # URL configuration
    backend_base_url: str = "http://localhost:3001"
    frontend_base_url: str = "http://localhost:3000"
    
    # JWT configuration
    jwt_secret: str = "your-secret-key-here"  # Should be overridden in .env
    
    # OAuth configuration
    oauth_redirect_base: str = "http://localhost:3001"
    
    # Connector OAuth credentials
    jira_client_id: str = ""
    jira_client_secret: str = ""
    confluence_client_id: str = ""
    confluence_client_secret: str = ""
    slack_client_id: str = ""
    slack_client_secret: str = ""
    notion_client_id: str = ""
    notion_client_secret: str = ""
    figma_client_id: str = ""
    figma_client_secret: str = ""
    datadog_client_id: str = ""
    datadog_client_secret: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()

"""Application settings and configuration."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database configuration
    database_url: str = "sqlite:///./connector_framework.db"
    
    # Application settings
    app_name: str = "Connector Framework Manager"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()

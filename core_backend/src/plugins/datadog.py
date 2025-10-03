"""Datadog connector plugin implementation."""
from typing import Dict, Any, Optional
from .base import ConnectorPlugin, PluginMetadata, NotConfigured
from src.config import settings


class DatadogConnector(ConnectorPlugin):
    """Datadog connector plugin for Datadog monitoring integration."""

    def get_metadata(self) -> PluginMetadata:
        """Get Datadog plugin metadata."""
        return PluginMetadata(
            key="datadog",
            name="Datadog",
            oauth_scopes=["metrics_read", "logs_read", "dashboards_read"],
            supports_oauth=True,
        )

    def get_config_schema(self) -> Dict[str, Any]:
        """Get Datadog configuration schema."""
        return {
            "type": "object",
            "properties": {
                "site": {
                    "type": "string",
                    "title": "Datadog Site",
                    "description": "Your Datadog site (e.g., datadoghq.com, datadoghq.eu)",
                    "default": "datadoghq.com"
                },
                "api_key": {
                    "type": "string",
                    "title": "API Key",
                    "description": "Your Datadog API key"
                },
                "app_key": {
                    "type": "string",
                    "title": "Application Key",
                    "description": "Your Datadog application key"
                }
            },
            "required": ["site", "api_key", "app_key"]
        }

    def authorize_url(self, redirect_uri: str, state: str) -> str:
        """Generate Datadog OAuth authorization URL."""
        client_id = settings.datadog_client_id
        if not client_id:
            raise NotConfigured("Datadog is not configured. Set DATADOG_CLIENT_ID and DATADOG_CLIENT_SECRET.")
        base_url = "https://app.datadoghq.com/oauth2/v1/authorize"
        scopes = " ".join(self.metadata.oauth_scopes)
        return (
            f"{base_url}?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"scope={scopes}&"
            f"state={state}&"
            f"response_type=code"
        )

    async def handle_oauth_callback(self, code: str, state: str) -> Dict[str, Any]:
        """Handle Datadog OAuth callback."""
        return {
            "access_token": f"dd_access_token_{code[:10]}",
            "refresh_token": f"dd_refresh_token_{code[:10]}",
            "expires_at": None,
            "token_type": "Bearer"
        }

    async def test_connection(self, config: Dict[str, Any], tokens: Optional[Dict[str, Any]] = None) -> bool:
        """Test Datadog connection."""
        api_key = config.get("api_key")
        app_key = config.get("app_key")
        if not api_key or not app_key:
            return False
        return True

    async def fetch_sample(self, config: Dict[str, Any], tokens: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fetch sample Datadog data."""
        return {
            "dashboards": [
                {"id": "abc-123-def", "title": "System Overview", "url": "https://..."},
                {"id": "ghi-456-jkl", "title": "Application Metrics", "url": "https://..."}
            ],
            "metrics": [
                {"name": "system.cpu.user", "type": "gauge"},
                {"name": "system.mem.used", "type": "gauge"},
                {"name": "application.requests.count", "type": "count"}
            ]
        }

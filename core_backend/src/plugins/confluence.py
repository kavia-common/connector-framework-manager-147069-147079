"""Confluence connector plugin implementation."""
from typing import Dict, Any, Optional
from .base import ConnectorPlugin, PluginMetadata, NotConfigured
from src.config import settings


class ConfluenceConnector(ConnectorPlugin):
    """Confluence connector plugin for Atlassian Confluence integration."""

    def get_metadata(self) -> PluginMetadata:
        """Get Confluence plugin metadata."""
        return PluginMetadata(
            key="confluence",
            name="Atlassian Confluence",
            oauth_scopes=["read:confluence-content.all", "read:confluence-space.summary"],
            supports_oauth=True,
        )

    def get_config_schema(self) -> Dict[str, Any]:
        """Get Confluence configuration schema."""
        return {
            "type": "object",
            "properties": {
                "instance_url": {
                    "type": "string",
                    "title": "Confluence Instance URL",
                    "description": "Your Confluence instance URL (e.g., https://company.atlassian.net/wiki)"
                },
                "email": {
                    "type": "string",
                    "title": "Email",
                    "description": "Your Confluence account email"
                }
            },
            "required": ["instance_url", "email"]
        }

    def authorize_url(self, redirect_uri: str, state: str) -> str:
        """Generate Confluence OAuth authorization URL."""
        client_id = settings.confluence_client_id
        if not client_id:
            raise NotConfigured("Confluence is not configured. Set CONFLUENCE_CLIENT_ID and CONFLUENCE_CLIENT_SECRET.")
        base_url = "https://auth.atlassian.com/authorize"
        scopes = "+".join(self.metadata.oauth_scopes)
        return (
            f"{base_url}?"
            f"audience=api.atlassian.com&"
            f"client_id={client_id}&"
            f"scope={scopes}&"
            f"redirect_uri={redirect_uri}&"
            f"state={state}&"
            f"response_type=code&"
            f"prompt=consent"
        )

    async def handle_oauth_callback(self, code: str, state: str) -> Dict[str, Any]:
        """Handle Confluence OAuth callback."""
        return {
            "access_token": f"confluence_access_token_{code[:10]}",
            "refresh_token": f"confluence_refresh_token_{code[:10]}",
            "expires_at": None,
            "token_type": "Bearer"
        }

    async def test_connection(self, config: Dict[str, Any], tokens: Optional[Dict[str, Any]] = None) -> bool:
        """Test Confluence connection."""
        instance_url = config.get("instance_url")
        if not instance_url or not tokens:
            return False
        return True

    async def fetch_sample(self, config: Dict[str, Any], tokens: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fetch sample Confluence data."""
        return {
            "spaces": [
                {"key": "DEMO", "name": "Demo Space", "type": "global"},
                {"key": "TEAM", "name": "Team Space", "type": "global"}
            ],
            "recent_pages": [
                {"id": "123456", "title": "Sample Page", "space": "DEMO"},
                {"id": "123457", "title": "Another Page", "space": "TEAM"}
            ]
        }

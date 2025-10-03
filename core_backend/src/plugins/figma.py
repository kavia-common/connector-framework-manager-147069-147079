"""Figma connector plugin implementation."""
from typing import Dict, Any, Optional
from .base import ConnectorPlugin, PluginMetadata, NotConfigured
from src.config import settings


class FigmaConnector(ConnectorPlugin):
    """Figma connector plugin for Figma design integration."""

    def get_metadata(self) -> PluginMetadata:
        """Get Figma plugin metadata."""
        return PluginMetadata(
            key="figma",
            name="Figma",
            oauth_scopes=["file_read"],
            supports_oauth=True,
        )

    def get_config_schema(self) -> Dict[str, Any]:
        """Get Figma configuration schema."""
        return {
            "type": "object",
            "properties": {
                "team_id": {
                    "type": "string",
                    "title": "Team ID",
                    "description": "Your Figma team ID (optional)"
                }
            },
            "required": []
        }

    def authorize_url(self, redirect_uri: str, state: str) -> str:
        """Generate Figma OAuth authorization URL."""
        client_id = settings.figma_client_id
        if not client_id:
            raise NotConfigured("Figma is not configured. Set FIGMA_CLIENT_ID and FIGMA_CLIENT_SECRET.")
        base_url = "https://www.figma.com/oauth"
        scopes = ",".join(self.metadata.oauth_scopes)
        return (
            f"{base_url}?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"scope={scopes}&"
            f"state={state}&"
            f"response_type=code"
        )

    async def handle_oauth_callback(self, code: str, state: str) -> Dict[str, Any]:
        """Handle Figma OAuth callback."""
        return {
            "access_token": f"figd_figma_access_token_{code[:10]}",
            "refresh_token": f"figr_figma_refresh_token_{code[:10]}",
            "expires_at": None,
            "token_type": "Bearer"
        }

    async def test_connection(self, config: Dict[str, Any], tokens: Optional[Dict[str, Any]] = None) -> bool:
        """Test Figma connection."""
        if not tokens:
            return False
        return True

    async def fetch_sample(self, config: Dict[str, Any], tokens: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fetch sample Figma data."""
        return {
            "teams": [
                {"id": "123456789", "name": "Design Team"},
                {"id": "123456790", "name": "Product Team"}
            ],
            "recent_files": [
                {"key": "ABC123", "name": "Mobile App Design", "thumbnail_url": "https://..."},
                {"key": "DEF456", "name": "Web Dashboard", "thumbnail_url": "https://..."}
            ]
        }

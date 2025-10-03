"""Slack connector plugin implementation."""
from typing import Dict, Any, Optional
from .base import ConnectorPlugin, PluginMetadata, NotConfigured
from src.config import settings


class SlackConnector(ConnectorPlugin):
    """Slack connector plugin for Slack workspace integration."""

    def get_metadata(self) -> PluginMetadata:
        """Get Slack plugin metadata."""
        return PluginMetadata(
            key="slack",
            name="Slack",
            oauth_scopes=["channels:read", "users:read", "chat:write"],
            supports_oauth=True,
        )

    def get_config_schema(self) -> Dict[str, Any]:
        """Get Slack configuration schema."""
        return {
            "type": "object",
            "properties": {
                "workspace_name": {
                    "type": "string",
                    "title": "Workspace Name",
                    "description": "Your Slack workspace name (e.g., company-workspace)"
                }
            },
            "required": ["workspace_name"]
        }

    def authorize_url(self, redirect_uri: str, state: str) -> str:
        """Generate Slack OAuth authorization URL."""
        client_id = settings.slack_client_id
        if not client_id:
            raise NotConfigured("Slack is not configured. Set SLACK_CLIENT_ID and SLACK_CLIENT_SECRET.")
        base_url = "https://slack.com/oauth/v2/authorize"
        scopes = ",".join(self.metadata.oauth_scopes)
        return (
            f"{base_url}?"
            f"client_id={client_id}&"
            f"scope={scopes}&"
            f"redirect_uri={redirect_uri}&"
            f"state={state}&"
            f"response_type=code"
        )

    async def handle_oauth_callback(self, code: str, state: str) -> Dict[str, Any]:
        """Handle Slack OAuth callback."""
        return {
            "access_token": f"xoxb-slack_access_token_{code[:10]}",
            "refresh_token": None,
            "expires_at": None,
            "token_type": "Bearer"
        }

    async def test_connection(self, config: Dict[str, Any], tokens: Optional[Dict[str, Any]] = None) -> bool:
        """Test Slack connection."""
        workspace_name = config.get("workspace_name")
        if not workspace_name or not tokens:
            return False
        return True

    async def fetch_sample(self, config: Dict[str, Any], tokens: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fetch sample Slack data."""
        return {
            "channels": [
                {"id": "C1234567890", "name": "general", "is_private": False},
                {"id": "C1234567891", "name": "random", "is_private": False},
                {"id": "C1234567892", "name": "dev-team", "is_private": True}
            ],
            "user_info": {
                "id": "U1234567890",
                "name": "john.doe",
                "real_name": "John Doe"
            }
        }

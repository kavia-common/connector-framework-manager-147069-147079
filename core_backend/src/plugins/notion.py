"""Notion connector plugin implementation."""
import os
from typing import Dict, Any, Optional
from .base import ConnectorPlugin, PluginMetadata


class NotionConnector(ConnectorPlugin):
    """Notion connector plugin for Notion workspace integration."""
    
    def get_metadata(self) -> PluginMetadata:
        """Get Notion plugin metadata."""
        return PluginMetadata(
            key="notion",
            name="Notion",
            oauth_scopes=["read", "write"]
        )
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get Notion configuration schema."""
        return {
            "type": "object",
            "properties": {
                "workspace_name": {
                    "type": "string",
                    "title": "Workspace Name",
                    "description": "Your Notion workspace name"
                }
            },
            "required": ["workspace_name"]
        }
    
    def authorize_url(self, redirect_uri: str, state: str) -> str:
        """Generate Notion OAuth authorization URL."""
        client_id = os.getenv("NOTION_CLIENT_ID")
        if not client_id:
            raise ValueError("NOTION_CLIENT_ID not configured")
        
        # Placeholder implementation - would use actual Notion OAuth URLs
        base_url = "https://api.notion.com/v1/oauth/authorize"
        
        return (
            f"{base_url}?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"owner=user&"
            f"state={state}"
        )
    
    async def handle_oauth_callback(self, code: str, state: str) -> Dict[str, Any]:
        """Handle Notion OAuth callback."""
        # Placeholder implementation - would exchange code for tokens
        return {
            "access_token": f"secret_notion_access_token_{code[:10]}",
            "refresh_token": None,  # Notion doesn't use refresh tokens
            "expires_at": None,
            "token_type": "Bearer"
        }
    
    async def test_connection(self, config: Dict[str, Any], tokens: Optional[Dict[str, Any]] = None) -> bool:
        """Test Notion connection."""
        # Placeholder implementation - would make actual API call
        workspace_name = config.get("workspace_name")
        if not workspace_name or not tokens:
            return False
        
        # Would make GET request to https://api.notion.com/v1/users/me
        return True
    
    async def fetch_sample(self, config: Dict[str, Any], tokens: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fetch sample Notion data."""
        # Placeholder implementation - would fetch actual databases/pages
        return {
            "databases": [
                {"id": "12345678-1234-1234-1234-123456789012", "title": "Tasks", "object": "database"},
                {"id": "12345678-1234-1234-1234-123456789013", "title": "Notes", "object": "database"}
            ],
            "pages": [
                {"id": "12345678-1234-1234-1234-123456789014", "title": "Sample Page", "object": "page"},
                {"id": "12345678-1234-1234-1234-123456789015", "title": "Another Page", "object": "page"}
            ]
        }

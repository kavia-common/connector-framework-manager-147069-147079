"""Jira connector plugin implementation."""
import os
from typing import Dict, Any, Optional
from .base import ConnectorPlugin, PluginMetadata


class JiraConnector(ConnectorPlugin):
    """Jira connector plugin for Atlassian Jira integration."""
    
    def get_metadata(self) -> PluginMetadata:
        """Get Jira plugin metadata."""
        return PluginMetadata(
            key="jira",
            name="Atlassian Jira",
            oauth_scopes=["read:jira-work", "read:jira-user"]
        )
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get Jira configuration schema."""
        return {
            "type": "object",
            "properties": {
                "instance_url": {
                    "type": "string",
                    "title": "Jira Instance URL",
                    "description": "Your Jira instance URL (e.g., https://company.atlassian.net)"
                },
                "email": {
                    "type": "string",
                    "title": "Email",
                    "description": "Your Jira account email"
                }
            },
            "required": ["instance_url", "email"]
        }
    
    def authorize_url(self, redirect_uri: str, state: str) -> str:
        """Generate Jira OAuth authorization URL."""
        client_id = os.getenv("JIRA_CLIENT_ID")
        if not client_id:
            raise ValueError("JIRA_CLIENT_ID not configured")
        
        # Placeholder implementation - would use actual Jira OAuth URLs
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
        """Handle Jira OAuth callback."""
        # Placeholder implementation - would exchange code for tokens
        return {
            "access_token": f"jira_access_token_{code[:10]}",
            "refresh_token": f"jira_refresh_token_{code[:10]}",
            "expires_at": None,  # Jira tokens don't typically expire
            "token_type": "Bearer"
        }
    
    async def test_connection(self, config: Dict[str, Any], tokens: Optional[Dict[str, Any]] = None) -> bool:
        """Test Jira connection."""
        # Placeholder implementation - would make actual API call
        instance_url = config.get("instance_url")
        if not instance_url or not tokens:
            return False
        
        # Would make GET request to /rest/api/3/myself
        return True
    
    async def fetch_sample(self, config: Dict[str, Any], tokens: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fetch sample Jira data."""
        # Placeholder implementation - would fetch actual projects/issues
        return {
            "projects": [
                {"key": "DEMO", "name": "Demo Project", "id": "10000"},
                {"key": "TEST", "name": "Test Project", "id": "10001"}
            ],
            "recent_issues": [
                {"key": "DEMO-1", "summary": "Sample issue", "status": "Open"},
                {"key": "DEMO-2", "summary": "Another issue", "status": "In Progress"}
            ]
        }

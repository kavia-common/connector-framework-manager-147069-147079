"""Base plugin class for connector implementations."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class NotConfigured(Exception):
    """Raised when a plugin is missing required configuration (e.g., client id/secret)."""


class PluginMetadata(BaseModel):
    """Metadata for a connector plugin."""
    key: str
    name: str
    oauth_scopes: List[str]
    supports_oauth: bool = True


class ConnectorPlugin(ABC):
    """
    Abstract base class for all connector plugins.

    All connector implementations must inherit from this class and implement
    the required methods to provide a consistent interface for the plugin system.
    """

    def __init__(self):
        """Initialize the connector plugin."""
        self._metadata = self.get_metadata()

    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return self._metadata

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """
        Get plugin metadata including key, name, and OAuth scopes.

        Returns:
            PluginMetadata: Plugin metadata object
        """
        raise NotImplementedError

    @abstractmethod
    def get_config_schema(self) -> Dict[str, Any]:
        """
        Get the configuration schema for this connector.

        Returns:
            Dict: JSON schema defining required configuration parameters
        """
        raise NotImplementedError

    @abstractmethod
    def authorize_url(self, redirect_uri: str, state: str) -> str:
        """
        Generate OAuth authorization URL for this connector.

        Args:
            redirect_uri: OAuth redirect URI
            state: OAuth state parameter for security

        Returns:
            str: Authorization URL to redirect user to
        """
        raise NotImplementedError

    @abstractmethod
    async def handle_oauth_callback(self, code: str, state: str) -> Dict[str, Any]:
        """
        Handle OAuth callback and exchange code for tokens.

        Args:
            code: OAuth authorization code
            state: OAuth state parameter

        Returns:
            Dict: Token data including access_token, refresh_token, expires_at
        """
        raise NotImplementedError

    @abstractmethod
    async def test_connection(self, config: Dict[str, Any], tokens: Optional[Dict[str, Any]] = None) -> bool:
        """
        Test the connection to the service with given configuration and tokens.

        Args:
            config: Connector configuration data
            tokens: OAuth token data (if applicable)

        Returns:
            bool: True if connection is successful, False otherwise
        """
        raise NotImplementedError

    @abstractmethod
    async def fetch_sample(self, config: Dict[str, Any], tokens: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Fetch sample data from the service to verify connection.

        Args:
            config: Connector configuration data
            tokens: OAuth token data (if applicable)

        Returns:
            Dict: Sample data from the service
        """
        raise NotImplementedError

    async def execute_action(self, action: str, config: Dict[str, Any], tokens: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """
        Execute a connector-specific action (optional implementation).

        Args:
            action: Action name to execute
            config: Connector configuration data
            tokens: OAuth token data (if applicable)
            **kwargs: Additional action parameters

        Returns:
            Dict: Action result data
        """
        raise NotImplementedError(f"Action '{action}' not implemented for {self.metadata.key}")

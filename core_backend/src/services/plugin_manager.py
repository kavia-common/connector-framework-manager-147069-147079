"""Plugin manager service for registering and managing connector plugins."""
from typing import Dict, List, Optional, Any
from src.plugins.base import ConnectorPlugin, NotConfigured
from src.plugins.jira import JiraConnector
from src.plugins.confluence import ConfluenceConnector
from src.plugins.slack import SlackConnector
from src.plugins.notion import NotionConnector
from src.plugins.figma import FigmaConnector
from src.plugins.datadog import DatadogConnector


class PluginManager:
    """
    Plugin manager for registering and managing connector plugins.

    This class maintains a registry of all available connector plugins
    and provides methods to retrieve them by key.
    """

    def __init__(self):
        """Initialize the plugin manager with available plugins."""
        self._plugins: Dict[str, ConnectorPlugin] = {}
        self._register_builtin_plugins()

    def _register_builtin_plugins(self) -> None:
        """Register all built-in connector plugins."""
        builtin_plugins = [
            JiraConnector(),
            ConfluenceConnector(),
            SlackConnector(),
            NotionConnector(),
            FigmaConnector(),
            DatadogConnector(),
        ]
        for plugin in builtin_plugins:
            self.register_plugin(plugin)

    def register_plugin(self, plugin: ConnectorPlugin) -> None:
        """
        Register a connector plugin.

        Args:
            plugin: ConnectorPlugin instance to register
        """
        key = plugin.metadata.key
        self._plugins[key] = plugin

    # PUBLIC_INTERFACE
    def get_all_plugins(self) -> List[ConnectorPlugin]:
        """
        Get all registered connector plugins.

        Returns:
            List[ConnectorPlugin]: List of all registered plugins
        """
        return list(self._plugins.values())

    # PUBLIC_INTERFACE
    def get_plugin(self, key: str) -> Optional[ConnectorPlugin]:
        """
        Get a specific connector plugin by its key.

        Args:
            key: Plugin key identifier

        Returns:
            ConnectorPlugin: The requested plugin, or None if not found
        """
        return self._plugins.get(key)

    # PUBLIC_INTERFACE
    def get_plugin_keys(self) -> List[str]:
        """
        Get all registered plugin keys.

        Returns:
            List[str]: List of all plugin keys
        """
        return list(self._plugins.keys())

    # PUBLIC_INTERFACE
    def is_plugin_available(self, key: str) -> bool:
        """
        Check if a plugin is available.

        Args:
            key: Plugin key identifier

        Returns:
            bool: True if plugin is available, False otherwise
        """
        return key in self._plugins

    # PUBLIC_INTERFACE
    def get_plugin_availability(self) -> List[Dict[str, Any]]:
        """
        Get listing of plugins with availability and configuration requirements.

        Returns:
            List[Dict[str, Any]]: Items include key, name, supports_oauth,
            configured (bool), and requirements (list of missing/notes).
        """
        items: List[Dict[str, Any]] = []
        for key, plugin in self._plugins.items():
            configured = True
            missing: List[str] = []
            if plugin.metadata.supports_oauth:
                # Try to generate an authorize URL with dummy values to detect missing config
                try:
                    plugin.authorize_url("http://localhost/example", "state")
                except NotConfigured as e:
                    configured = False
                    missing.append(str(e))
                except Exception:
                    # Ignore other errors during probing
                    pass
            items.append(
                {
                    "key": plugin.metadata.key,
                    "name": plugin.metadata.name,
                    "supports_oauth": plugin.metadata.supports_oauth,
                    "configured": configured,
                    "requirements": missing,
                }
            )
        return items


# Global plugin manager instance
plugin_manager = PluginManager()

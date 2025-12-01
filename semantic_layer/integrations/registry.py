"""Integration registry."""

from typing import Dict, Optional, Any
from semantic_layer.integrations.base import Integration
from semantic_layer.plugins.registry import get_plugin_registry


class IntegrationRegistry:
    """Registry for integrations (wrapper around PluginRegistry)."""
    
    def __init__(self):
        """Initialize integration registry."""
        self._plugin_registry = get_plugin_registry()
    
    def get_integration(self, name: str) -> Optional[Integration]:
        """Get a loaded integration instance.
        
        Args:
            name: Integration name (e.g., 'datahub', 'langchain')
            
        Returns:
            Optional[Integration]: Integration instance or None
        """
        plugin = self._plugin_registry.get_plugin("integration", name)
        return plugin if isinstance(plugin, Integration) else None
    
    def load_integration(
        self,
        name: str,
        config: Dict[str, Any]
    ) -> Integration:
        """Load and initialize an integration.
        
        Args:
            name: Integration name
            config: Configuration dictionary
            
        Returns:
            Integration: Initialized integration
            
        Raises:
            ValueError: If integration not found
        """
        plugin = self._plugin_registry.load_plugin("integration", name, config)
        if not isinstance(plugin, Integration):
            raise ValueError(f"Plugin {name} is not an Integration")
        return plugin
    
    def list_integrations(self) -> list[Dict[str, Any]]:
        """List available integrations.
        
        Returns:
            list[Dict[str, Any]]: List of integration metadata
        """
        plugins = self._plugin_registry.list_plugins("integration")
        return plugins.get("integration", [])


# Global registry instance
_global_integration_registry: Optional[IntegrationRegistry] = None


def get_integration_registry() -> IntegrationRegistry:
    """Get the global integration registry instance.
    
    Returns:
        IntegrationRegistry: Global integration registry
    """
    global _global_integration_registry
    if _global_integration_registry is None:
        _global_integration_registry = IntegrationRegistry()
    return _global_integration_registry


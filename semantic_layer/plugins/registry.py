"""Unified plugin registry for discovering and loading plugins."""

from typing import Dict, Type, Optional, Any, List
from semantic_layer.plugins.base import PluginInterface


class PluginRegistry:
    """Registry for discovering and loading plugins."""
    
    def __init__(self):
        """Initialize the plugin registry."""
        self._plugins: Dict[str, PluginInterface] = {}
        self._plugin_classes: Dict[str, Type[PluginInterface]] = {}
    
    def register(self, plugin_class: Type[PluginInterface]) -> None:
        """Register a plugin class.
        
        Args:
            plugin_class: Plugin class that extends PluginInterface
            
        Raises:
            ValueError: If plugin class is invalid
        """
        try:
            instance = plugin_class()
            plugin_id = f"{instance.plugin_type}:{instance.name}"
            self._plugin_classes[plugin_id] = plugin_class
        except Exception as e:
            raise ValueError(f"Failed to register plugin class: {e}") from e
    
    def get_plugin(self, plugin_type: str, name: str) -> Optional[PluginInterface]:
        """Get a loaded plugin instance.
        
        Args:
            plugin_type: Type of plugin (e.g., 'driver', 'llm')
            name: Name of the plugin (e.g., 'postgres', 'openai')
            
        Returns:
            Optional[PluginInterface]: Loaded plugin instance or None if not found
        """
        plugin_id = f"{plugin_type}:{name}"
        return self._plugins.get(plugin_id)
    
    def load_plugin(
        self,
        plugin_type: str,
        name: str,
        config: Dict[str, Any]
    ) -> PluginInterface:
        """Load and initialize a plugin.
        
        Args:
            plugin_type: Type of plugin (e.g., 'driver', 'llm')
            name: Name of the plugin (e.g., 'postgres', 'openai')
            config: Configuration dictionary for the plugin
            
        Returns:
            PluginInterface: Initialized plugin instance
            
        Raises:
            ValueError: If plugin is not found or initialization fails
        """
        plugin_id = f"{plugin_type}:{name}"
        
        # Check if already loaded
        if plugin_id in self._plugins:
            return self._plugins[plugin_id]
        
        # Check if class is registered
        if plugin_id not in self._plugin_classes:
            available = self.list_plugins(plugin_type)
            raise ValueError(
                f"Plugin not found: {plugin_id}. "
                f"Available {plugin_type} plugins: {[p['name'] for p in available.get(plugin_type, [])]}"
            )
        
        # Instantiate and initialize
        try:
            plugin_class = self._plugin_classes[plugin_id]
            plugin = plugin_class()
            
            # Validate config if plugin supports it
            if hasattr(plugin, 'validate_config'):
                if not plugin.validate_config(config):
                    raise ValueError(f"Invalid configuration for plugin {plugin_id}")
            
            plugin.initialize(config)
            self._plugins[plugin_id] = plugin
            return plugin
        except Exception as e:
            raise ValueError(f"Failed to load plugin {plugin_id}: {e}") from e
    
    def list_plugins(self, plugin_type: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """List available plugins.
        
        Args:
            plugin_type: Optional filter by plugin type
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Dictionary mapping plugin types to lists of plugin metadata
        """
        result: Dict[str, List[Dict[str, Any]]] = {}
        
        for plugin_id, plugin_class in self._plugin_classes.items():
            ptype, pname = plugin_id.split(":", 1)
            
            if plugin_type and ptype != plugin_type:
                continue
            
            try:
                instance = plugin_class()
                metadata = instance.get_metadata()
                
                if ptype not in result:
                    result[ptype] = []
                result[ptype].append(metadata)
            except Exception:
                # Skip plugins that can't be instantiated
                continue
        
        return result
    
    def unload_plugin(self, plugin_type: str, name: str) -> None:
        """Unload a plugin instance.
        
        Args:
            plugin_type: Type of plugin
            name: Name of the plugin
        """
        plugin_id = f"{plugin_type}:{name}"
        if plugin_id in self._plugins:
            plugin = self._plugins[plugin_id]
            try:
                plugin.shutdown()
            except Exception:
                pass  # Ignore shutdown errors
            del self._plugins[plugin_id]
    
    def clear(self) -> None:
        """Clear all loaded plugins."""
        for plugin in list(self._plugins.values()):
            try:
                plugin.shutdown()
            except Exception:
                pass
        self._plugins.clear()


# Global registry instance
_global_registry: Optional[PluginRegistry] = None


def get_plugin_registry() -> PluginRegistry:
    """Get the global plugin registry instance.
    
    Returns:
        PluginRegistry: Global plugin registry
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = PluginRegistry()
    return _global_registry


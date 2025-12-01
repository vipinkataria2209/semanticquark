"""LLM provider registry."""

from typing import Dict, Optional, Any
from semantic_layer.llm.base import LLMProvider
from semantic_layer.plugins.registry import get_plugin_registry


class LLMRegistry:
    """Registry for LLM providers (wrapper around PluginRegistry)."""
    
    def __init__(self):
        """Initialize LLM registry."""
        self._plugin_registry = get_plugin_registry()
    
    def get_provider(self, name: str) -> Optional[LLMProvider]:
        """Get a loaded LLM provider instance.
        
        Args:
            name: Provider name (e.g., 'openai', 'anthropic')
            
        Returns:
            Optional[LLMProvider]: Provider instance or None
        """
        plugin = self._plugin_registry.get_plugin("llm", name)
        return plugin if isinstance(plugin, LLMProvider) else None
    
    def load_provider(
        self,
        name: str,
        config: Dict[str, Any]
    ) -> LLMProvider:
        """Load and initialize an LLM provider.
        
        Args:
            name: Provider name
            config: Configuration dictionary
            
        Returns:
            LLMProvider: Initialized provider
            
        Raises:
            ValueError: If provider not found
        """
        plugin = self._plugin_registry.load_plugin("llm", name, config)
        if not isinstance(plugin, LLMProvider):
            raise ValueError(f"Plugin {name} is not an LLMProvider")
        return plugin
    
    def list_providers(self) -> list[Dict[str, Any]]:
        """List available LLM providers.
        
        Returns:
            list[Dict[str, Any]]: List of provider metadata
        """
        plugins = self._plugin_registry.list_plugins("llm")
        return plugins.get("llm", [])


# Global registry instance
_global_llm_registry: Optional[LLMRegistry] = None


def get_llm_registry() -> LLMRegistry:
    """Get the global LLM registry instance.
    
    Returns:
        LLMRegistry: Global LLM registry
    """
    global _global_llm_registry
    if _global_llm_registry is None:
        _global_llm_registry = LLMRegistry()
    return _global_llm_registry


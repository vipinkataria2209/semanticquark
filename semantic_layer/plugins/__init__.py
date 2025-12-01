"""Plugin system for SemanticQuark."""

from semantic_layer.plugins.base import PluginInterface
from semantic_layer.plugins.registry import PluginRegistry, get_plugin_registry
from semantic_layer.plugins.loader import PluginLoader

__all__ = [
    "PluginInterface",
    "PluginRegistry",
    "get_plugin_registry",
    "PluginLoader",
]


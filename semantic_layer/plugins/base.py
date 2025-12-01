"""Plugin interface for SemanticQuark plugins."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class PluginInterface(ABC):
    """Base interface for all plugins."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name (e.g., 'postgres', 'openai', 'redis').
        
        Returns:
            str: Plugin name identifier
        """
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version (e.g., '1.0.0').
        
        Returns:
            str: Plugin version string
        """
        pass
    
    @property
    @abstractmethod
    def plugin_type(self) -> str:
        """Plugin type identifier.
        
        Returns:
            str: Plugin type (e.g., 'driver', 'llm', 'integration', 'cache', 'auth')
        """
        pass
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Return JSON schema for this plugin's configuration.
        
        Returns:
            Dict[str, Any]: Configuration schema definition
        """
        return {}
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            bool: True if configuration is valid
        """
        return True
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration.
        
        Args:
            config: Configuration dictionary for the plugin
        """
        pass
    
    def shutdown(self) -> None:
        """Cleanup when plugin is being unloaded."""
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return plugin metadata.
        
        Returns:
            Dict[str, Any]: Plugin metadata including name, version, type, etc.
        """
        return {
            "name": self.name,
            "version": self.version,
            "type": self.plugin_type,
            "author": "Unknown",
            "description": "",
            "documentation": "",
            "requires": [],  # Plugin dependencies
        }


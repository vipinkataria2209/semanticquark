"""Base integration interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from semantic_layer.plugins.base import PluginInterface


class Integration(PluginInterface):
    """Abstract base for external integrations."""
    
    @property
    def plugin_type(self) -> str:
        """Plugin type identifier."""
        return "integration"
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Return configuration schema for this integration.
        
        Returns:
            Dict[str, Any]: Configuration schema
        """
        return {}
    
    @abstractmethod
    async def connect(self) -> None:
        """Connect to the external service."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the external service."""
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return integration metadata.
        
        Returns:
            Dict[str, Any]: Integration metadata
        """
        metadata = super().get_metadata()
        metadata.update({
            "integration_type": self.name,  # e.g., 'datahub', 'langchain'
        })
        return metadata


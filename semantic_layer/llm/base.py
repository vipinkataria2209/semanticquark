"""Base LLM provider interface."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from semantic_layer.plugins.base import PluginInterface


class LLMProvider(PluginInterface):
    """Abstract base for LLM providers."""
    
    @property
    def plugin_type(self) -> str:
        """Plugin type identifier."""
        return "llm"
    
    @abstractmethod
    async def complete(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Complete a prompt using the LLM.
        
        Args:
            prompt: Input prompt text
            temperature: Sampling temperature (0.0 = deterministic)
            max_tokens: Maximum tokens to generate
            
        Returns:
            str: Generated text completion
        """
        pass
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],  # [{"role": "user/assistant/system", "content": "..."}]
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Chat with the LLM using message history.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            str: Generated response
        """
        pass
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Return configuration schema for this LLM provider.
        
        Returns:
            Dict[str, Any]: Configuration schema
        """
        return {
            "api_key": {
                "type": "string",
                "description": "API key for LLM provider",
                "required": True
            },
            "model": {
                "type": "string",
                "description": "Model name/version",
                "default": self.model_name if hasattr(self, 'model_name') else ""
            },
            "temperature": {
                "type": "number",
                "description": "Default temperature",
                "default": 0.0
            },
        }
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Currently active model name.
        
        Returns:
            str: Model identifier
        """
        pass


"""External integrations framework for SemanticQuark."""

from semantic_layer.integrations.base import Integration
from semantic_layer.integrations.registry import IntegrationRegistry, get_integration_registry

__all__ = [
    "Integration",
    "IntegrationRegistry",
    "get_integration_registry",
]


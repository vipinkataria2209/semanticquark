"""Database connectors (backward compatibility layer)."""

# Backward compatibility: redirect old imports to new location
import warnings

warnings.warn(
    "semantic_layer.connectors is deprecated. Use semantic_layer.drivers instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import from new location
from semantic_layer.drivers import (
    BaseDriver as BaseConnector,
    ConnectionConfig,
    PostgresDriver as PostgreSQLConnector,
    MySQLDriver as MySQLConnector,
    DriverFactory,
)

__all__ = [
    "BaseConnector",
    "ConnectionConfig",
    "PostgreSQLConnector",
    "MySQLConnector",
    "DriverFactory",
]

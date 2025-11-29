"""Database connectors."""

from semantic_layer.connectors.base import BaseConnector, ConnectionConfig
from semantic_layer.connectors.postgresql import PostgreSQLConnector

# Import MySQL connector conditionally
try:
    from semantic_layer.connectors.mysql import MySQLConnector
except ImportError:
    MySQLConnector = None

__all__ = ["BaseConnector", "ConnectionConfig", "PostgreSQLConnector", "MySQLConnector"]

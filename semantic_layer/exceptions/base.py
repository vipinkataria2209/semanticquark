"""Base exception classes."""


class SemanticLayerError(Exception):
    """Base exception for all semantic layer errors."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(SemanticLayerError):
    """Configuration-related errors."""

    pass


class ModelError(SemanticLayerError):
    """Model definition errors."""

    pass


class QueryError(SemanticLayerError):
    """Query parsing or validation errors."""

    pass


class ValidationError(SemanticLayerError):
    """Data validation errors."""

    pass


class ExecutionError(SemanticLayerError):
    """Query execution errors."""

    pass


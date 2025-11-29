"""Storage backends for pre-aggregations and data."""

from semantic_layer.storage.base_storage import BaseStorage
from semantic_layer.storage.postgres_storage import DatabasePreAggregation
from semantic_layer.storage.cloud_storage import CloudStorage, S3Storage, GCSStorage

# ParquetStorage is optional (requires pyarrow)
try:
    from semantic_layer.storage.parquet_storage import ParquetStorage
    PARQUET_AVAILABLE = True
except ImportError:
    PARQUET_AVAILABLE = False
    ParquetStorage = None  # type: ignore

__all__ = [
    "BaseStorage",
    "DatabasePreAggregation",
    "CloudStorage",
    "S3Storage",
    "GCSStorage",
]

if PARQUET_AVAILABLE:
    __all__.append("ParquetStorage")


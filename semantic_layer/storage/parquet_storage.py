"""Parquet file storage backend."""

from typing import Any, Dict, Optional
from pathlib import Path

try:
    import pyarrow.parquet as pq
    import pyarrow as pa
    PYARROW_AVAILABLE = True
except ImportError:
    PYARROW_AVAILABLE = False
    pq = None
    pa = None


class ParquetStorage:
    """Parquet file storage."""
    
    def __init__(self, base_path: str = "./storage/parquet"):
        """Initialize Parquet storage."""
        if not PYARROW_AVAILABLE:
            raise ImportError(
                "pyarrow is required for ParquetStorage. "
                "Install it with: pip install pyarrow"
            )
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    async def store(self, key: str, data: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Store data as Parquet file."""
        # Convert data to PyArrow table
        table = pa.Table.from_pylist(data)
        
        # Write to Parquet file
        file_path = self.base_path / f"{key}.parquet"
        pq.write_table(table, file_path)
    
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from Parquet file."""
        file_path = self.base_path / f"{key}.parquet"
        if not file_path.exists():
            return None
        
        # Read Parquet file
        table = pq.read_table(file_path)
        return table.to_pylist()
    
    async def delete(self, key: str) -> None:
        """Delete Parquet file."""
        file_path = self.base_path / f"{key}.parquet"
        if file_path.exists():
            file_path.unlink()
    
    async def exists(self, key: str) -> bool:
        """Check if Parquet file exists."""
        file_path = self.base_path / f"{key}.parquet"
        return file_path.exists()


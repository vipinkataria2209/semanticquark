"""Data catalog management."""

from typing import Dict, List, Any, Optional
from datetime import datetime


class DataCatalog:
    """Maintains a data catalog of available tables and columns."""
    
    def __init__(self):
        """Initialize data catalog."""
        self.catalog: Dict[str, Any] = {}
        self.last_updated: Optional[datetime] = None
    
    def add_table(self, table_name: str, metadata: Dict[str, Any]) -> None:
        """Add table to catalog."""
        self.catalog[table_name] = {
            **metadata,
            "added_at": datetime.utcnow().isoformat(),
        }
        self.last_updated = datetime.utcnow()
    
    def get_table(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Get table metadata from catalog."""
        return self.catalog.get(table_name)
    
    def list_tables(self) -> List[str]:
        """List all tables in catalog."""
        return list(self.catalog.keys())
    
    def search(self, query: str) -> List[str]:
        """Search catalog for tables matching query."""
        query_lower = query.lower()
        return [
            table_name
            for table_name, metadata in self.catalog.items()
            if query_lower in table_name.lower() or 
               query_lower in metadata.get("description", "").lower()
        ]


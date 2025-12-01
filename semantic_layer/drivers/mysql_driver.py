"""MySQL connector implementation."""

from typing import Any, Dict, List, Optional

try:
    import aiomysql
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    aiomysql = None

from typing import Optional, Dict, Any
from semantic_layer.drivers.base_driver import BaseDriver, ConnectionConfig
from semantic_layer.exceptions import ExecutionError


class MySQLDriver(BaseDriver):
    """MySQL database driver."""
    
    @property
    def name(self) -> str:
        """Plugin name."""
        return "mysql"
    
    @property
    def version(self) -> str:
        """Plugin version."""
        return "1.0.0"

    def __init__(self, config: Optional[ConnectionConfig] = None):
        """Initialize MySQL connector.
        
        Args:
            config: Connection configuration (optional for plugin initialization)
        """
        if not MYSQL_AVAILABLE:
            raise ExecutionError(
                "MySQL connector not available. Install with: pip install semanticquark[mysql]"
            )
        super().__init__(config)
        self._pool: Optional[Any] = None
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize driver from config dict (PluginInterface method).
        
        Args:
            config: Configuration dictionary
        """
        super().initialize(config)
        self._pool = None

    async def connect(self) -> None:
        """Connect to MySQL database."""
        # Parse connection URL
        url = self.config.url.replace("mysql://", "").replace("mysql+aiomysql://", "")
        # Format: user:password@host:port/database
        parts = url.split("@")
        if len(parts) != 2:
            raise ExecutionError("Invalid MySQL connection URL")
        
        user_pass = parts[0].split(":")
        user = user_pass[0]
        password = user_pass[1] if len(user_pass) > 1 else ""
        
        host_db = parts[1].split("/")
        if len(host_db) != 2:
            raise ExecutionError("Invalid MySQL connection URL")
        
        host_port = host_db[0].split(":")
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 3306
        database = host_db[1]

        self._pool = await aiomysql.create_pool(
            host=host,
            port=port,
            user=user,
            password=password,
            db=database,
            minsize=1,
            maxsize=self.config.pool_size,
        )

    async def disconnect(self) -> None:
        """Disconnect from MySQL."""
        if self._pool:
            self._pool.close()
            await self._pool.wait_closed()
            self._pool = None

    async def execute_query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute SQL query and return results."""
        if not self._pool:
            raise ExecutionError("Not connected to database")

        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(sql, params)
                results = await cursor.fetchall()
                return [dict(row) for row in results]

    async def test_connection(self) -> bool:
        """Test database connection."""
        try:
            results = await self.execute_query("SELECT 1 as test")
            return len(results) > 0 and results[0].get("test") == 1
        except Exception:
            return False

    @property
    def dialect(self) -> str:
        """Get SQL dialect name."""
        return "mysql"


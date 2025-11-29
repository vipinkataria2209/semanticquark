"""Python SDK client for SemanticQuark."""

import httpx
from typing import Any, Dict, List, Optional


class SemanticQuarkClient:
    """Python client for SemanticQuark API."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        jwt_token: Optional[str] = None,
    ):
        """Initialize client."""
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.jwt_token = jwt_token
        self._client = httpx.AsyncClient()

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        headers = {"Content-Type": "application/json"}
        if self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"
        elif self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    async def query(
        self,
        dimensions: Optional[List[str]] = None,
        measures: Optional[List[str]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        order_by: Optional[List[Dict[str, Any]]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Execute a semantic query."""
        response = await self._client.post(
            f"{self.base_url}/api/v1/query",
            json={
                "dimensions": dimensions or [],
                "measures": measures or [],
                "filters": filters or [],
                "order_by": order_by or [],
                "limit": limit,
                "offset": offset,
            },
            headers=self._get_headers(),
        )
        response.raise_for_status()
        return response.json()

    async def get_schema(self) -> Dict[str, Any]:
        """Get schema information."""
        response = await self._client.get(
            f"{self.base_url}/api/v1/schema",
            headers=self._get_headers(),
        )
        response.raise_for_status()
        return response.json()

    async def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        response = await self._client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    async def execute_sql(self, sql: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute raw SQL query."""
        response = await self._client.post(
            f"{self.base_url}/api/v1/sql",
            json={"sql": sql, "params": params},
            headers=self._get_headers(),
        )
        response.raise_for_status()
        return response.json()

    async def get_logs(self, limit: int = 100) -> Dict[str, Any]:
        """Get query logs."""
        response = await self._client.get(
            f"{self.base_url}/api/v1/logs",
            params={"limit": limit},
            headers=self._get_headers(),
        )
        response.raise_for_status()
        return response.json()

    async def reload_schema(self) -> Dict[str, Any]:
        """Reload schema from files."""
        response = await self._client.post(
            f"{self.base_url}/api/v1/reload",
            headers=self._get_headers(),
        )
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        """Close the client."""
        await self._client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


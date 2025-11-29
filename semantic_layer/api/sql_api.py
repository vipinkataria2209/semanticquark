"""SQL API implementation."""

from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, Depends
from pydantic import BaseModel

from semantic_layer.auth.base import SecurityContext
from semantic_layer.drivers.base_driver import BaseDriver
from semantic_layer.orchestrator import QueryEngine
from semantic_layer.exceptions import ExecutionError
from semantic_layer.schema import Schema
from semantic_layer.sql import SQLBuilder
from semantic_layer.api.middleware import get_security_context


class SQLQueryRequest(BaseModel):
    """SQL query request."""
    sql: str
    params: Optional[Dict[str, Any]] = None


async def execute_sql_query(
    request: Request,
    sql_request: SQLQueryRequest,
    security_context: Optional[SecurityContext] = Depends(get_security_context),
) -> Dict[str, Any]:
    """Execute raw SQL query (with security checks)."""
    # Get connector from app state
    connector: Optional[BaseDriver] = getattr(request.app.state, "connector", None)
    if not connector:
        raise HTTPException(status_code=503, detail="Database connector not available")
    
    # Security: Only allow SELECT queries
    sql_upper = sql_request.sql.strip().upper()
    if not sql_upper.startswith("SELECT"):
        raise HTTPException(
            status_code=403,
            detail="Only SELECT queries are allowed through SQL API"
        )
    
    # Execute query
    try:
        results = await connector.execute_query(sql_request.sql, sql_request.params)
        return {
            "data": results,
            "row_count": len(results),
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"SQL execution failed: {str(e)}"
        )


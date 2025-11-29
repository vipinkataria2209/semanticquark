"""Health check utilities."""

from typing import Dict, Any
from datetime import datetime


class HealthChecker:
    """Health check utilities."""
    
    @staticmethod
    def check_health() -> Dict[str, Any]:
        """Perform health check."""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "0.1.0",
        }
    
    @staticmethod
    def check_database(driver) -> Dict[str, Any]:
        """Check database connection health."""
        try:
            # Try to execute a simple query
            import asyncio
            result = asyncio.run(driver.test_connection())
            return {
                "status": "healthy" if result else "unhealthy",
                "database": "connected" if result else "disconnected",
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "database": "error",
                "error": str(e),
            }


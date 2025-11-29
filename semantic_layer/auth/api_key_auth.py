"""API key authentication implementation."""

from typing import Dict, Optional

from semantic_layer.auth.base import BaseAuth, SecurityContext


class APIKeyAuth(BaseAuth):
    """API key authentication."""

    def __init__(self, api_keys: Optional[Dict[str, Dict[str, any]]] = None):
        """Initialize API key auth."""
        # api_keys format: {api_key: {user_id, roles, permissions, tenant_id}}
        self.api_keys = api_keys or {}

    async def authenticate(self, token: str) -> Optional[SecurityContext]:
        """Authenticate API key."""
        if token not in self.api_keys:
            return None
        
        key_info = self.api_keys[token]
        return SecurityContext(
            user_id=key_info.get("user_id"),
            roles=key_info.get("roles", []),
            permissions=key_info.get("permissions", []),
            tenant_id=key_info.get("tenant_id"),
        )

    async def authorize(
        self, context: SecurityContext, resource: str, action: str
    ) -> bool:
        """Check authorization."""
        # Check for wildcard permission
        if "*" in context.permissions:
            return True
        
        # Check for specific permission
        permission = f"{action}:{resource}"
        if permission in context.permissions:
            return True
        
        # Check role-based permissions
        if "admin" in context.roles:
            return True
        
        return False


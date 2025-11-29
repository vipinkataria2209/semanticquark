"""JWT authentication implementation."""

import os
from typing import Optional

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

from semantic_layer.auth.base import BaseAuth, SecurityContext
from semantic_layer.exceptions import ExecutionError


class JWTAuth(BaseAuth):
    """JWT authentication."""

    def __init__(self, secret: Optional[str] = None, algorithm: str = "HS256"):
        """Initialize JWT auth."""
        if not JWT_AVAILABLE:
            raise ExecutionError(
                "JWT is not available. Install with: pip install PyJWT"
            )
        self.secret = secret or os.getenv("JWT_SECRET", "secret")
        self.algorithm = algorithm

    async def authenticate(self, token: str) -> Optional[SecurityContext]:
        """Authenticate JWT token."""
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            user_id = payload.get("sub") or payload.get("user_id")
            roles = payload.get("roles", [])
            permissions = payload.get("permissions", [])
            tenant_id = payload.get("tenant_id")
            
            return SecurityContext(
                user_id=user_id,
                roles=roles,
                permissions=permissions,
                tenant_id=tenant_id,
            )
        except jwt.InvalidTokenError:
            return None

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
        
        # Check role-based permissions (simplified)
        # In production, you'd have a proper RBAC system
        if "admin" in context.roles:
            return True
        
        return False


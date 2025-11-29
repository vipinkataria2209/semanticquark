"""API middleware for authentication and security."""

from typing import Optional

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from semantic_layer.auth.base import BaseAuth, SecurityContext
from semantic_layer.config import get_settings


security = HTTPBearer(auto_error=False)


async def get_security_context(request: Request) -> Optional[SecurityContext]:
    """Extract security context from request."""
    settings = get_settings()
    
    if not settings.auth_enabled:
        return None
    
    # Get auth instance (would be initialized in app)
    auth: Optional[BaseAuth] = getattr(request.app.state, "auth", None)
    if not auth:
        return None
    
    # Try to get token from Authorization header
    authorization: Optional[HTTPAuthorizationCredentials] = await security(request)
    
    if authorization:
        token = authorization.credentials
        context = await auth.authenticate(token)
        if context:
            return context
    
    # Try API key from header
    api_key = request.headers.get("X-API-Key")
    if api_key and settings.auth_type == "api_key":
        context = await auth.authenticate(api_key)
        if context:
            return context
    
    # If auth is enabled but no valid token, raise error
    if settings.auth_enabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return None


async def check_authorization(
    request: Request, resource: str, action: str = "read"
) -> SecurityContext:
    """Check if user is authorized for resource and action."""
    context = await get_security_context(request)
    
    if not context:
        # If auth is disabled, allow access
        settings = get_settings()
        if not settings.auth_enabled:
            return SecurityContext()  # Empty context for no-auth mode
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    
    # Check authorization
    auth: Optional[BaseAuth] = getattr(request.app.state, "auth", None)
    if auth:
        authorized = await auth.authorize(context, resource, action)
        if not authorized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not authorized to {action} {resource}",
            )
    
    return context


"""Base authentication interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class SecurityContext:
    """Security context for a user."""

    def __init__(
        self,
        user_id: Optional[str] = None,
        roles: Optional[list[str]] = None,
        permissions: Optional[list[str]] = None,
        tenant_id: Optional[str] = None,
        **kwargs
    ):
        self.user_id = user_id
        self.roles = roles or []
        self.permissions = permissions or []
        self.tenant_id = tenant_id
        self.extra = kwargs

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "roles": self.roles,
            "permissions": self.permissions,
            "tenant_id": self.tenant_id,
            **self.extra,
        }


class BaseAuth(ABC):
    """Base authentication interface."""

    @abstractmethod
    async def authenticate(self, token: str) -> Optional[SecurityContext]:
        """Authenticate a token and return security context."""
        pass

    @abstractmethod
    async def authorize(
        self, context: SecurityContext, resource: str, action: str
    ) -> bool:
        """Check if user is authorized for resource and action."""
        pass


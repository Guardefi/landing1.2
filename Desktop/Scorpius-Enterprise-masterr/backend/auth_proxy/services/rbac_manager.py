"""
Role-Based Access Control Manager
Handles permissions and role mappings
"""

import asyncio
from typing import Any, Dict, List

from ..models import RoleEnum


class RBACManager:
    """RBAC permission manager"""

    # Role -> Permission mapping
    ROLE_PERMISSIONS = {
        RoleEnum.VIEWER: ["scanner:read", "reports:read"],
        RoleEnum.ANALYST: [
            "scanner:read",
            "scanner:scan",
            "reports:read",
            "reports:create",
            "wallet_guard:check",
        ],
        RoleEnum.ADMIN: [
            "scanner:*",
            "reports:*",
            "wallet_guard:*",
            "users:read",
            "settings:*",
        ],
        RoleEnum.BILLING_ADMIN: ["billing:*", "usage:read", "reports:read"],
    }

    async def get_user_permissions(self, user_id: str, org_id: str) -> List[str]:
        """Get all permissions for a user based on their roles"""
        # Mock implementation - in production this would query the database
        await asyncio.sleep(0.1)

        # For demo, return admin permissions
        return self.ROLE_PERMISSIONS[RoleEnum.ADMIN]

    async def check_permission(
        self, user_roles: List[RoleEnum], required_permission: str
    ) -> bool:
        """Check if user has required permission"""
        user_permissions = set()

        for role in user_roles:
            role_perms = self.ROLE_PERMISSIONS.get(role, [])
            user_permissions.update(role_perms)

        # Check exact match or wildcard
        if required_permission in user_permissions:
            return True

        # Check wildcard permissions
        for perm in user_permissions:
            if perm.endswith("*"):
                resource = perm.split(":")[0]
                if required_permission.startswith(f"{resource}:"):
                    return True

        return False

    async def get_org_scan_quota(self, org_id: str) -> Dict[str, Any]:
        """Get organization scan quota and usage"""
        await asyncio.sleep(0.1)
        return {
            "org_id": org_id,
            "plan": "enterprise",
            "quota": 10000,
            "used": 150,
            "remaining": 9850,
        }

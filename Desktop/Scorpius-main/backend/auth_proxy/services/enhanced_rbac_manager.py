"""
Enhanced Role-Based Access Control Manager
Provides fine-grained permissions, context-aware access control, and audit integration
"""

import json
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set

import asyncpg
from pydantic import BaseModel

from ..models import User
from .worm_audit_service import AuditEvent, WORMAuditService

logger = logging.getLogger(__name__)


class PermissionEffect(str, Enum):
    """Permission effect"""

    ALLOW = "allow"
    DENY = "deny"


class ResourceType(str, Enum):
    """Resource types in the system"""

    SCANNER = "scanner"
    REPORTS = "reports"
    WALLET_GUARD = "wallet_guard"
    USERS = "users"
    SETTINGS = "settings"
    BILLING = "billing"
    AUDIT = "audit"
    HONEYPOT = "honeypot"
    MEV_BOT = "mev_bot"
    BRIDGE = "bridge"
    MEMPOOL = "mempool"
    QUANTUM = "quantum"


class Action(str, Enum):
    """Available actions"""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    SCAN = "scan"
    EXPORT = "export"
    APPROVE = "approve"
    CONFIGURE = "configure"
    MONITOR = "monitor"


class Permission(BaseModel):
    """Fine-grained permission model"""

    id: str
    resource_type: ResourceType
    action: Action
    effect: PermissionEffect = PermissionEffect.ALLOW
    conditions: Optional[Dict[str, Any]] = None
    description: str


class Role(BaseModel):
    """Enhanced role model"""

    id: str
    name: str
    display_name: str
    description: str
    permissions: List[str]  # Permission IDs
    is_system_role: bool = False
    created_at: datetime
    updated_at: datetime


class AccessContext(BaseModel):
    """Context for access control decisions"""

    user_id: str
    org_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    time_of_day: Optional[int] = None  # Hour of day (0-23)
    resource_owner: Optional[str] = None
    resource_sensitivity: Optional[str] = None  # low, medium, high, critical
    request_metadata: Dict[str, Any] = {}


class AccessDecision(BaseModel):
    """Access control decision"""

    granted: bool
    reason: str
    applied_permissions: List[str]
    denied_permissions: List[str]
    conditions_met: Dict[str, bool]
    risk_score: int  # 0-100


class EnhancedRBACManager:
    """Enhanced RBAC manager with fine-grained permissions and audit integration"""

    def __init__(self, postgres_url: str, audit_service: WORMAuditService):
        self.postgres_url = postgres_url
        self.audit_service = audit_service
        self.pool: Optional[asyncpg.Pool] = None
        self._permission_cache: Dict[str, Permission] = {}
        self._role_cache: Dict[str, Role] = {}

        # System permissions definition
        self.system_permissions = self._define_system_permissions()
        self.system_roles = self._define_system_roles()

    def _define_system_permissions(self) -> List[Permission]:
        """Define system permissions"""
        permissions = []

        # Scanner permissions
        permissions.extend(
            [
                Permission(
                    id="scanner:read",
                    resource_type=ResourceType.SCANNER,
                    action=Action.READ,
                    description="Read scanner results and configurations",
                ),
                Permission(
                    id="scanner:scan",
                    resource_type=ResourceType.SCANNER,
                    action=Action.SCAN,
                    description="Execute security scans",
                ),
                Permission(
                    id="scanner:configure",
                    resource_type=ResourceType.SCANNER,
                    action=Action.CONFIGURE,
                    description="Configure scanner settings",
                ),
                Permission(
                    id="scanner:export",
                    resource_type=ResourceType.SCANNER,
                    action=Action.EXPORT,
                    description="Export scanner results",
                ),
            ]
        )

        # Reports permissions
        permissions.extend(
            [
                Permission(
                    id="reports:read",
                    resource_type=ResourceType.REPORTS,
                    action=Action.READ,
                    description="Read reports",
                ),
                Permission(
                    id="reports:create",
                    resource_type=ResourceType.REPORTS,
                    action=Action.CREATE,
                    description="Create new reports",
                ),
                Permission(
                    id="reports:export",
                    resource_type=ResourceType.REPORTS,
                    action=Action.EXPORT,
                    description="Export reports",
                ),
                Permission(
                    id="reports:delete",
                    resource_type=ResourceType.REPORTS,
                    action=Action.DELETE,
                    description="Delete reports",
                    conditions={"resource_owner_only": True},
                ),
            ]
        )

        # Wallet Guard permissions
        permissions.extend(
            [
                Permission(
                    id="wallet_guard:read",
                    resource_type=ResourceType.WALLET_GUARD,
                    action=Action.READ,
                    description="Read wallet guard results",
                ),
                Permission(
                    id="wallet_guard:check",
                    resource_type=ResourceType.WALLET_GUARD,
                    action=Action.EXECUTE,
                    description="Execute wallet security checks",
                ),
                Permission(
                    id="wallet_guard:configure",
                    resource_type=ResourceType.WALLET_GUARD,
                    action=Action.CONFIGURE,
                    description="Configure wallet guard settings",
                ),
            ]
        )

        # User management permissions
        permissions.extend(
            [
                Permission(
                    id="users:read",
                    resource_type=ResourceType.USERS,
                    action=Action.READ,
                    description="Read user information",
                ),
                Permission(
                    id="users:create",
                    resource_type=ResourceType.USERS,
                    action=Action.CREATE,
                    description="Create new users",
                ),
                Permission(
                    id="users:update",
                    resource_type=ResourceType.USERS,
                    action=Action.UPDATE,
                    description="Update user information",
                ),
                Permission(
                    id="users:delete",
                    resource_type=ResourceType.USERS,
                    action=Action.DELETE,
                    description="Delete users",
                ),
            ]
        )

        # Settings permissions
        permissions.extend(
            [
                Permission(
                    id="settings:read",
                    resource_type=ResourceType.SETTINGS,
                    action=Action.READ,
                    description="Read system settings",
                ),
                Permission(
                    id="settings:update",
                    resource_type=ResourceType.SETTINGS,
                    action=Action.UPDATE,
                    description="Update system settings",
                ),
            ]
        )

        # Billing permissions
        permissions.extend(
            [
                Permission(
                    id="billing:read",
                    resource_type=ResourceType.BILLING,
                    action=Action.READ,
                    description="Read billing information",
                ),
                Permission(
                    id="billing:update",
                    resource_type=ResourceType.BILLING,
                    action=Action.UPDATE,
                    description="Update billing settings",
                ),
            ]
        )

        # Audit permissions
        permissions.extend(
            [
                Permission(
                    id="audit:read",
                    resource_type=ResourceType.AUDIT,
                    action=Action.READ,
                    description="Read audit logs",
                ),
                Permission(
                    id="audit:export",
                    resource_type=ResourceType.AUDIT,
                    action=Action.EXPORT,
                    description="Export audit logs",
                ),
            ]
        )

        return permissions

    def _define_system_roles(self) -> List[Role]:
        """Define system roles"""
        now = datetime.now(timezone.utc)

        return [
            Role(
                id="viewer",
                name="viewer",
                display_name="Viewer",
                description="Read-only access to basic resources",
                permissions=["scanner:read", "reports:read", "wallet_guard:read"],
                is_system_role=True,
                created_at=now,
                updated_at=now,
            ),
            Role(
                id="analyst",
                name="analyst",
                display_name="Security Analyst",
                description="Can perform scans and create reports",
                permissions=[
                    "scanner:read",
                    "scanner:scan",
                    "scanner:export",
                    "reports:read",
                    "reports:create",
                    "reports:export",
                    "wallet_guard:read",
                    "wallet_guard:check",
                ],
                is_system_role=True,
                created_at=now,
                updated_at=now,
            ),
            Role(
                id="admin",
                name="admin",
                display_name="Administrator",
                description="Full access to all resources",
                permissions=[
                    "scanner:read",
                    "scanner:scan",
                    "scanner:configure",
                    "scanner:export",
                    "reports:read",
                    "reports:create",
                    "reports:export",
                    "reports:delete",
                    "wallet_guard:read",
                    "wallet_guard:check",
                    "wallet_guard:configure",
                    "users:read",
                    "users:create",
                    "users:update",
                    "users:delete",
                    "settings:read",
                    "settings:update",
                    "audit:read",
                    "audit:export",
                ],
                is_system_role=True,
                created_at=now,
                updated_at=now,
            ),
            Role(
                id="billing_admin",
                name="billing_admin",
                display_name="Billing Administrator",
                description="Manages billing and usage",
                permissions=["billing:read", "billing:update", "reports:read"],
                is_system_role=True,
                created_at=now,
                updated_at=now,
            ),
        ]

    async def initialize(self):
        """Initialize RBAC manager"""
        # Initialize database connection
        self.pool = await asyncpg.create_pool(
            self.postgres_url, min_size=2, max_size=10
        )

        # Create RBAC tables
        await self._create_rbac_tables()

        # Initialize system permissions and roles
        await self._initialize_system_data()

        # Load caches
        await self._load_caches()

    async def _create_rbac_tables(self):
        """Create RBAC tables"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS rbac_permissions (
                    id VARCHAR(255) PRIMARY KEY,
                    resource_type VARCHAR(100) NOT NULL,
                    action VARCHAR(100) NOT NULL,
                    effect VARCHAR(10) NOT NULL DEFAULT 'allow',
                    conditions JSONB DEFAULT '{}',
                    description TEXT NOT NULL,
                    is_system_permission BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS rbac_roles (
                    id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    display_name VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    is_system_role BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS rbac_role_permissions (
                    role_id VARCHAR(255) NOT NULL,
                    permission_id VARCHAR(255) NOT NULL,
                    PRIMARY KEY (role_id, permission_id),
                    FOREIGN KEY (role_id) REFERENCES rbac_roles(id) ON DELETE CASCADE,
                    FOREIGN KEY (permission_id) REFERENCES rbac_permissions(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS rbac_user_roles (
                    user_id VARCHAR(255) NOT NULL,
                    org_id VARCHAR(255) NOT NULL,
                    role_id VARCHAR(255) NOT NULL,
                    granted_by VARCHAR(255),
                    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    expires_at TIMESTAMPTZ,
                    PRIMARY KEY (user_id, org_id, role_id),
                    FOREIGN KEY (role_id) REFERENCES rbac_roles(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS rbac_user_permissions (
                    user_id VARCHAR(255) NOT NULL,
                    org_id VARCHAR(255) NOT NULL,
                    permission_id VARCHAR(255) NOT NULL,
                    effect VARCHAR(10) NOT NULL DEFAULT 'allow',
                    conditions JSONB DEFAULT '{}',
                    granted_by VARCHAR(255),
                    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    expires_at TIMESTAMPTZ,
                    PRIMARY KEY (user_id, org_id, permission_id),
                    FOREIGN KEY (permission_id) REFERENCES rbac_permissions(id) ON DELETE CASCADE
                );

                -- Indexes
                CREATE INDEX IF NOT EXISTS idx_rbac_user_roles_user_org
                    ON rbac_user_roles(user_id, org_id);
                CREATE INDEX IF NOT EXISTS idx_rbac_user_permissions_user_org
                    ON rbac_user_permissions(user_id, org_id);
            """
            )

    async def _initialize_system_data(self):
        """Initialize system permissions and roles"""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Insert system permissions
                for permission in self.system_permissions:
                    await conn.execute(
                        """
                        INSERT INTO rbac_permissions (
                            id, resource_type, action, effect, conditions,
                            description, is_system_permission
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                        ON CONFLICT (id) DO UPDATE SET
                            resource_type = EXCLUDED.resource_type,
                            action = EXCLUDED.action,
                            effect = EXCLUDED.effect,
                            conditions = EXCLUDED.conditions,
                            description = EXCLUDED.description,
                            updated_at = NOW()
                    """,
                        permission.id,
                        permission.resource_type.value,
                        permission.action.value,
                        permission.effect.value,
                        json.dumps(permission.conditions or {}),
                        permission.description,
                        True,
                    )

                # Insert system roles
                for role in self.system_roles:
                    await conn.execute(
                        """
                        INSERT INTO rbac_roles (
                            id, name, display_name, description, is_system_role
                        ) VALUES ($1, $2, $3, $4, $5)
                        ON CONFLICT (id) DO UPDATE SET
                            name = EXCLUDED.name,
                            display_name = EXCLUDED.display_name,
                            description = EXCLUDED.description,
                            updated_at = NOW()
                    """,
                        role.id,
                        role.name,
                        role.display_name,
                        role.description,
                        role.is_system_role,
                    )

                    # Insert role permissions
                    await conn.execute(
                        "DELETE FROM rbac_role_permissions WHERE role_id = $1", role.id
                    )
                    for permission_id in role.permissions:
                        await conn.execute(
                            """
                            INSERT INTO rbac_role_permissions (role_id, permission_id)
                            VALUES ($1, $2)
                        """,
                            role.id,
                            permission_id,
                        )

    async def _load_caches(self):
        """Load permissions and roles into cache"""
        async with self.pool.acquire() as conn:
            # Load permissions
            permission_records = await conn.fetch("SELECT * FROM rbac_permissions")
            for record in permission_records:
                permission = Permission(
                    id=record["id"],
                    resource_type=ResourceType(record["resource_type"]),
                    action=Action(record["action"]),
                    effect=PermissionEffect(record["effect"]),
                    conditions=record["conditions"],
                    description=record["description"],
                )
                self._permission_cache[permission.id] = permission

            # Load roles with permissions
            role_records = await conn.fetch(
                """
                SELECT r.*, array_agg(rp.permission_id) as permissions
                FROM rbac_roles r
                LEFT JOIN rbac_role_permissions rp ON r.id = rp.role_id
                GROUP BY r.id, r.name, r.display_name, r.description,
                         r.is_system_role, r.created_at, r.updated_at
            """
            )

            for record in role_records:
                role = Role(
                    id=record["id"],
                    name=record["name"],
                    display_name=record["display_name"],
                    description=record["description"],
                    permissions=record["permissions"] or [],
                    is_system_role=record["is_system_role"],
                    created_at=record["created_at"],
                    updated_at=record["updated_at"],
                )
                self._role_cache[role.id] = role

    async def check_permission(
        self, user: User, permission_id: str, context: AccessContext
    ) -> AccessDecision:
        """Check if user has permission with context-aware access control"""
        try:
            # Get user's effective permissions
            user_permissions = await self._get_user_effective_permissions(
                user.id, user.org_id
            )

            # Check if user has the permission
            if permission_id not in user_permissions:
                decision = AccessDecision(
                    granted=False,
                    reason=f"User does not have permission: {permission_id}",
                    applied_permissions=[],
                    denied_permissions=[permission_id],
                    conditions_met={},
                    risk_score=0,
                )
            else:
                # Check conditions
                permission = self._permission_cache.get(permission_id)
                conditions_met = (
                    await self._evaluate_conditions(permission, context)
                    if permission
                    else {}
                )

                # Calculate risk score
                risk_score = self._calculate_risk_score(context, permission)

                # Determine if access should be granted
                granted = all(
                    conditions_met.values()) if conditions_met else True

                decision = AccessDecision(
                    granted=granted,
                    reason="Access granted" if granted else "Conditions not met",
                    applied_permissions=[permission_id] if granted else [],
                    denied_permissions=[] if granted else [permission_id],
                    conditions_met=conditions_met,
                    risk_score=risk_score,
                )

            # Log access decision
            await self._log_access_decision(user, permission_id, context, decision)

            return decision

        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return AccessDecision(
                granted=False,
                reason=f"Error checking permission: {str(e)}",
                applied_permissions=[],
                denied_permissions=[permission_id],
                conditions_met={},
                risk_score=100,
            )

    async def _get_user_effective_permissions(
        self, user_id: str, org_id: str
    ) -> Set[str]:
        """Get all effective permissions for a user"""
        permissions = set()

        async with self.pool.acquire() as conn:
            # Get permissions from roles
            role_permissions = await conn.fetch(
                """
                SELECT DISTINCT rp.permission_id
                FROM rbac_user_roles ur
                JOIN rbac_role_permissions rp ON ur.role_id = rp.role_id
                WHERE ur.user_id = $1 AND ur.org_id = $2
                AND (ur.expires_at IS NULL OR ur.expires_at > NOW())
            """,
                user_id,
                org_id,
            )

            for record in role_permissions:
                permissions.add(record["permission_id"])

            # Get direct user permissions
            user_permissions = await conn.fetch(
                """
                SELECT permission_id, effect
                FROM rbac_user_permissions
                WHERE user_id = $1 AND org_id = $2
                AND (expires_at IS NULL OR expires_at > NOW())
            """,
                user_id,
                org_id,
            )

            for record in user_permissions:
                if record["effect"] == "allow":
                    permissions.add(record["permission_id"])
                else:
                    permissions.discard(record["permission_id"])

        return permissions

    async def _evaluate_conditions(
        self, permission: Optional[Permission], context: AccessContext
    ) -> Dict[str, bool]:
        """Evaluate permission conditions"""
        if not permission or not permission.conditions:
            return {}

        conditions_met = {}

        for condition_name, condition_value in permission.conditions.items():
            if condition_name == "resource_owner_only":
                conditions_met[condition_name] = (
                    context.resource_owner == context.user_id
                    if context.resource_owner
                    else True
                )
            elif condition_name == "business_hours_only":
                current_hour = context.time_of_day or datetime.now().hour
                conditions_met[condition_name] = 9 <= current_hour <= 17
            elif condition_name == "high_sensitivity_approval":
                conditions_met[condition_name] = (
                    context.resource_sensitivity != "critical"
                    if context.resource_sensitivity
                    else True
                )
            else:
                conditions_met[condition_name] = True

        return conditions_met

    def _calculate_risk_score(
        self, context: AccessContext, permission: Optional[Permission]
    ) -> int:
        """Calculate risk score for access request"""
        risk_score = 0

        # Time-based risk
        if context.time_of_day:
            if context.time_of_day < 6 or context.time_of_day > 22:
                risk_score += 20

        # Resource sensitivity risk
        if context.resource_sensitivity:
            sensitivity_scores = {
                "low": 0,
                "medium": 10,
                "high": 25,
                "critical": 50}
            risk_score += sensitivity_scores.get(
                context.resource_sensitivity, 0)

        # Permission risk
        if permission:
            if permission.action in [Action.DELETE, Action.CONFIGURE]:
                risk_score += 15
            if permission.resource_type in [
                    ResourceType.USERS, ResourceType.SETTINGS]:
                risk_score += 10

        return min(risk_score, 100)

    async def _log_access_decision(
        self,
        user: User,
        permission_id: str,
        context: AccessContext,
        decision: AccessDecision,
    ):
        """Log access control decision to audit trail"""
        audit_event = AuditEvent(
            event_id="",
            timestamp=datetime.now(timezone.utc),
            event_type="access_control",
            user_id=user.id,
            org_id=user.org_id,
            resource_type="rbac",
            resource_id=permission_id,
            action="check_permission",
            ip_address=context.ip_address,
            user_agent=context.user_agent,
            details={
                "permission_id": permission_id,
                "granted": decision.granted,
                "reason": decision.reason,
                "risk_score": decision.risk_score,
                "conditions_met": decision.conditions_met,
                "context": context.dict(),
            },
            success=decision.granted,
            risk_score=decision.risk_score,
        )

        try:
            await self.audit_service.log_audit_event(audit_event)
        except Exception as e:
            logger.error(f"Failed to log access decision: {e}")

    async def get_user_roles(self, user_id: str, org_id: str) -> List[Role]:
        """Get user's roles"""
        async with self.pool.acquire() as conn:
            records = await conn.fetch(
                """
                SELECT r.*
                FROM rbac_roles r
                JOIN rbac_user_roles ur ON r.id = ur.role_id
                WHERE ur.user_id = $1 AND ur.org_id = $2
                AND (ur.expires_at IS NULL OR ur.expires_at > NOW())
            """,
                user_id,
                org_id,
            )

            return [
                self._role_cache.get(record["id"])
                for record in records
                if record["id"] in self._role_cache
            ]

    async def assign_role(
        self,
        user_id: str,
        org_id: str,
        role_id: str,
        granted_by: str,
        expires_at: Optional[datetime] = None,
    ) -> bool:
        """Assign role to user"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO rbac_user_roles (user_id, org_id, role_id, granted_by, expires_at)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (user_id, org_id, role_id) DO UPDATE SET
                        granted_by = EXCLUDED.granted_by,
                        granted_at = NOW(),
                        expires_at = EXCLUDED.expires_at
                """,
                    user_id,
                    org_id,
                    role_id,
                    granted_by,
                    expires_at,
                )

            # Log role assignment
            audit_event = AuditEvent(
                event_id="",
                timestamp=datetime.now(
                    timezone.utc),
                event_type="role_assignment",
                user_id=granted_by,
                org_id=org_id,
                resource_type="rbac",
                resource_id=f"user:{user_id}",
                action="assign_role",
                details={
                    "target_user_id": user_id,
                    "role_id": role_id,
                    "expires_at": expires_at.isoformat() if expires_at else None,
                },
                success=True,
            )
            await self.audit_service.log_audit_event(audit_event)

            return True

        except Exception as e:
            logger.error(f"Failed to assign role: {e}")
            return False

    async def close(self):
        """Close database connections"""
        if self.pool:
            await self.pool.close()

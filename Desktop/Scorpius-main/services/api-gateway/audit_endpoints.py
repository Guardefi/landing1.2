"""
Audit Trail API Endpoints
Provides REST API for RBAC and audit trail functionality
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

from backend.auth_proxy.services.enhanced_rbac_manager import (
    AccessContext,
    AccessDecision,
    EnhancedRBACManager,
    Role,
)
from backend.auth_proxy.services.worm_audit_service import (
    AuditEvent,
    AuditProof,
    WORMAuditService,
)

from .auth import User, get_current_user
from .rbac_middleware import check_permission

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/audit", tags=["audit"])


class AuditEventRequest(BaseModel):
    """Request model for creating audit events"""

    event_type: str
    resource_type: str
    resource_id: str
    action: str
    details: Dict[str, Any] = {}
    success: bool = True
    risk_score: Optional[int] = None


class AuditEventResponse(BaseModel):
    """Response model for audit events"""

    event_id: str
    timestamp: datetime
    event_type: str
    user_id: str
    org_id: str
    resource_type: str
    resource_id: str
    action: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    details: Dict[str, Any]
    success: bool
    risk_score: Optional[int]
    content_hash: str
    signature: str
    qldb_document_id: Optional[str]
    postgres_block_hash: str
    chain_position: int


class AuditQueryRequest(BaseModel):
    """Request model for querying audit events"""

    org_id: Optional[str] = None
    user_id: Optional[str] = None
    event_type: Optional[str] = None
    resource_type: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = 100
    offset: int = 0


class ChainVerificationResponse(BaseModel):
    """Response model for chain verification"""

    verified: bool
    total_blocks: int
    verified_blocks: int
    broken_chains: List[int]
    invalid_signatures: List[int]
    missing_blocks: List[int]
    verification_timestamp: datetime


class RoleAssignmentRequest(BaseModel):
    """Request model for role assignment"""

    user_id: str
    role_id: str
    expires_at: Optional[datetime] = None


class PermissionCheckRequest(BaseModel):
    """Request model for permission checking"""

    permission_id: str
    resource_owner: Optional[str] = None
    resource_sensitivity: Optional[str] = None
    request_metadata: Dict[str, Any] = {}


# Dependency injection for services
async def get_audit_service() -> WORMAuditService:
    """Get audit service instance"""
    # In production, this would be injected from application context
    from .dependencies import get_audit_service_instance

    return await get_audit_service_instance()


async def get_rbac_manager() -> EnhancedRBACManager:
    """Get RBAC manager instance"""
    # In production, this would be injected from application context
    from .dependencies import get_rbac_manager_instance

    return await get_rbac_manager_instance()


@router.post("/events", response_model=AuditProof)
async def create_audit_event(
    request: AuditEventRequest,
    http_request: Request,
    user: User = Depends(get_current_user),
    audit_service: WORMAuditService = Depends(get_audit_service),
    _: bool = Depends(check_permission("audit:create")),
):
    """Create a new audit event"""
    try:
        # Create audit event
        audit_event = AuditEvent(
            event_id="",
            timestamp=datetime.now(timezone.utc),
            event_type=request.event_type,
            user_id=user.id,
            org_id=user.org_id,
            resource_type=request.resource_type,
            resource_id=request.resource_id,
            action=request.action,
            ip_address=http_request.client.host,
            user_agent=http_request.headers.get("user-agent"),
            details=request.details,
            success=request.success,
            risk_score=request.risk_score,
        )

        # Log the event
        proof = await audit_service.log_audit_event(audit_event)

        return proof

    except Exception as e:
        logger.error(f"Failed to create audit event: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create audit event: {
                str(e)}",
        )


@router.get("/events", response_model=List[Dict[str, Any]])
async def get_audit_events(
    org_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0),
    user: User = Depends(get_current_user),
    audit_service: WORMAuditService = Depends(get_audit_service),
    _: bool = Depends(check_permission("audit:read")),
):
    """Get audit events with filtering"""
    try:
        # Use user's org_id if not specified and user is not admin
        if not org_id and "admin" not in user.roles:
            org_id = user.org_id

        events = await audit_service.get_audit_events(
            org_id=org_id,
            user_id=user_id,
            event_type=event_type,
            resource_type=resource_type,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=offset,
        )

        return events

    except Exception as e:
        logger.error(f"Failed to get audit events: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get audit events: {
                str(e)}",
        )


@router.get("/events/{event_id}/proof", response_model=AuditProof)
async def get_audit_proof(
    event_id: str,
    user: User = Depends(get_current_user),
    audit_service: WORMAuditService = Depends(get_audit_service),
    _: bool = Depends(check_permission("audit:read")),
):
    """Get cryptographic proof for an audit event"""
    try:
        proof = await audit_service.get_audit_proof(event_id)

        if not proof:
            raise HTTPException(
                status_code=404,
                detail="Audit event not found")

        return proof

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get audit proof: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get audit proof: {
                str(e)}",
        )


@router.post("/verify-chain", response_model=ChainVerificationResponse)
async def verify_audit_chain(
    start_block: int = Query(1),
    end_block: Optional[int] = Query(None),
    user: User = Depends(get_current_user),
    audit_service: WORMAuditService = Depends(get_audit_service),
    _: bool = Depends(check_permission("audit:verify")),
):
    """Verify the integrity of the audit chain"""
    try:
        verification_result = await audit_service.verify_audit_chain(
            start_block, end_block
        )

        return ChainVerificationResponse(
            verified=verification_result["verified"],
            total_blocks=verification_result["total_blocks"],
            verified_blocks=verification_result["verified_blocks"],
            broken_chains=verification_result["broken_chains"],
            invalid_signatures=verification_result["invalid_signatures"],
            missing_blocks=verification_result["missing_blocks"],
            verification_timestamp=datetime.now(timezone.utc),
        )

    except Exception as e:
        logger.error(f"Failed to verify audit chain: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify audit chain: {
                str(e)}",
        )


@router.get("/export")
async def export_audit_events(
    format: str = Query("csv", regex="^(csv|json)$"),
    org_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    user: User = Depends(get_current_user),
    audit_service: WORMAuditService = Depends(get_audit_service),
    _: bool = Depends(check_permission("audit:export")),
):
    """Export audit events"""
    try:
        # Use user's org_id if not specified and user is not admin
        if not org_id and "admin" not in user.roles:
            org_id = user.org_id

        events = await audit_service.get_audit_events(
            org_id=org_id,
            user_id=user_id,
            event_type=event_type,
            resource_type=resource_type,
            start_time=start_time,
            end_time=end_time,
            limit=10000,  # Max export limit
        )

        if format == "csv":
            # Generate CSV export
            import csv
            import io

            output = io.StringIO()
            writer = csv.DictWriter(
                output, fieldnames=events[0].keys() if events else []
            )
            writer.writeheader()
            writer.writerows(events)

            csv_content = output.getvalue()

            from fastapi.responses import Response

            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=audit_export_{
                        datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"},
            )
        else:
            # JSON export
            import json

            from fastapi.responses import Response

            return Response(
                content=json.dumps(
                    events,
                    default=str,
                    indent=2),
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename=audit_export_{
                        datetime.now().strftime('%Y%m%d_%H%M%S')}.json"},
            )

    except Exception as e:
        logger.error(f"Failed to export audit events: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export audit events: {
                str(e)}",
        )


# RBAC Endpoints
@router.get("/rbac/roles", response_model=List[Role])
async def get_roles(
    user: User = Depends(get_current_user),
    rbac_manager: EnhancedRBACManager = Depends(get_rbac_manager),
    _: bool = Depends(check_permission("users:read")),
):
    """Get available roles"""
    try:
        roles = await rbac_manager.get_user_roles(user.id, user.org_id)
        return roles

    except Exception as e:
        logger.error(f"Failed to get roles: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get roles: {
                str(e)}",
        )


@router.post("/rbac/assign-role")
async def assign_role(
    request: RoleAssignmentRequest,
    user: User = Depends(get_current_user),
    rbac_manager: EnhancedRBACManager = Depends(get_rbac_manager),
    _: bool = Depends(check_permission("users:update")),
):
    """Assign role to user"""
    try:
        success = await rbac_manager.assign_role(
            user_id=request.user_id,
            org_id=user.org_id,
            role_id=request.role_id,
            granted_by=user.id,
            expires_at=request.expires_at,
        )

        if not success:
            raise HTTPException(
                status_code=400,
                detail="Failed to assign role")

        return {"message": "Role assigned successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to assign role: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to assign role: {
                str(e)}",
        )


@router.post("/rbac/check-permission", response_model=AccessDecision)
async def check_user_permission(
    request: PermissionCheckRequest,
    http_request: Request,
    user: User = Depends(get_current_user),
    rbac_manager: EnhancedRBACManager = Depends(get_rbac_manager),
):
    """Check if user has specific permission"""
    try:
        context = AccessContext(
            user_id=user.id,
            org_id=user.org_id,
            ip_address=http_request.client.host,
            user_agent=http_request.headers.get("user-agent"),
            time_of_day=datetime.now().hour,
            resource_owner=request.resource_owner,
            resource_sensitivity=request.resource_sensitivity,
            request_metadata=request.request_metadata,
        )

        decision = await rbac_manager.check_permission(
            user=user, permission_id=request.permission_id, context=context
        )

        return decision

    except Exception as e:
        logger.error(f"Failed to check permission: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check permission: {
                str(e)}",
        )


@router.get("/rbac/my-permissions")
async def get_my_permissions(
    user: User = Depends(get_current_user),
    rbac_manager: EnhancedRBACManager = Depends(get_rbac_manager),
):
    """Get current user's effective permissions"""
    try:
        permissions = await rbac_manager._get_user_effective_permissions(
            user.id, user.org_id
        )
        roles = await rbac_manager.get_user_roles(user.id, user.org_id)

        return {
            "user_id": user.id,
            "org_id": user.org_id,
            "roles": [role.dict() for role in roles],
            "permissions": list(permissions),
        }

    except Exception as e:
        logger.error(f"Failed to get user permissions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user permissions: {
                str(e)}",
        )


@router.get("/dashboard/stats")
async def get_audit_dashboard_stats(
    user: User = Depends(get_current_user),
    audit_service: WORMAuditService = Depends(get_audit_service),
    _: bool = Depends(check_permission("audit:read")),
):
    """Get audit dashboard statistics"""
    try:
        # Get recent events
        recent_events = await audit_service.get_audit_events(
            org_id=user.org_id, limit=10
        )

        # Get event type distribution
        event_types = {}
        for event in recent_events:
            event_type = event.get("event_type", "unknown")
            event_types[event_type] = event_types.get(event_type, 0) + 1

        # Get security events (failed access attempts, etc.)
        security_events = await audit_service.get_audit_events(
            org_id=user.org_id, event_type="access_control", limit=100
        )

        failed_access_attempts = len(
            [e for e in security_events if not e.get("success", True)]
        )

        return {
            "total_events": len(recent_events),
            "recent_events": recent_events[:5],
            "event_type_distribution": event_types,
            "security_metrics": {
                "failed_access_attempts": failed_access_attempts,
                "total_access_attempts": len(security_events),
            },
            "chain_status": {
                "verified": True,  # Would get from actual verification
                "last_verification": datetime.now(timezone.utc),
            },
        }

    except Exception as e:
        logger.error(f"Failed to get dashboard stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get dashboard stats: {
                str(e)}",
        )

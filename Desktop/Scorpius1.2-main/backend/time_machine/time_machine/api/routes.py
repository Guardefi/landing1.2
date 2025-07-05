"""
Time Machine API Routes
FastAPI routes for blockchain forensic analysis operations.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import JSONResponse, StreamingResponse

from ..core.controller import TimeMachineEngine
from ..core.models import JobStatus, ReplayJob, SessionType, VMBackend
from .schemas import (
    AnalysisRequest,
    AnalysisResult,
    BookmarkRequest,
    BranchInfo,
    DiffRequest,
    DiffResponse,
    EngineStats,
    ErrorResponse,
    ExportRequest,
    ExportResponse,
    FindingRequest,
    ForensicSessionInfo,
    ForensicSessionRequest,
    JobInfo,
    MacroInfo,
    PatchRequest,
    PatchResponse,
    ReplayRequest,
    ReplayResponse,
    SnapshotInfo,
    TimelineEventResponse,
    ValidationResult,
    WSJobStatus,
    WSMessage,
    WSTimelineEvent,
)

logger = logging.getLogger(__name__)

# Global engine instance - in production would use dependency injection
engine = TimeMachineEngine()

# Create API router
router = APIRouter()


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = []
        self.active_connections[client_id].append(websocket)

    def disconnect(self, websocket: WebSocket, client_id: str):
        if client_id in self.active_connections:
            self.active_connections[client_id].remove(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]

    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            for connection in self.active_connections[client_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Failed to send message to {client_id}: {e}")

    async def broadcast(self, message: str):
        for connections in self.active_connections.values():
            for connection in connections:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Failed to broadcast message: {e}")


manager = ConnectionManager()

# Create router
router = APIRouter(prefix="/api/v1/timeline", tags=["timeline"])


# Dependency to get engine instance
async def get_engine() -> TimeMachineEngine:
    return engine


# Main API Routes


@router.post("/replay", response_model=ReplayResponse)
async def replay_timeline(
    request: ReplayRequest,
    background_tasks: BackgroundTasks,
    engine: TimeMachineEngine = Depends(get_engine),
):
    """Start a new replay job."""
    try:
        # Create replay job
        job = ReplayJob(
            name=request.name or f"Replay-{int(time.time())}",
            description=request.description or "",
            block_number=request.block_number,
            tx_hash=request.tx_hash,
            from_block=request.from_block,
            to_block=request.to_block,
            vm_backend=request.vm_backend,
            patches=request.patches,
            metadata=request.metadata,
        )

        # Start replay in background
        background_tasks.add_task(execute_replay_job, job, engine)

        return ReplayResponse(
            job_id=job.job_id,
            branch_id="",  # Will be set when job completes
            status=job.status,
            name=job.name,
            description=job.description,
            vm_backend=job.vm_backend.value,
            created_at=job.created_at,
            metadata=job.metadata,
        )

    except Exception as e:
        logger.error(f"Replay failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def execute_replay_job(job: ReplayJob, engine: TimeMachineEngine):
    """Execute replay job in background."""
    try:
        branch = await engine.replay(job)

        # Notify WebSocket clients
        message = WSJobStatus(
            job_id=job.job_id,
            status=JobStatus.COMPLETED,
            message=f"Replay completed, branch: {branch.branch_id}",
        )
        await manager.broadcast(json.dumps(message.dict()))

    except Exception as e:
        logger.error(f"Background replay job {job.job_id} failed: {e}")

        # Notify WebSocket clients
        message = WSJobStatus(
            job_id=job.job_id, status=JobStatus.FAILED, message=str(e)
        )
        await manager.broadcast(json.dumps(message.dict()))


@router.post("/patch", response_model=PatchResponse)
async def apply_patches(
    request: PatchRequest, engine: TimeMachineEngine = Depends(get_engine)
):
    """Apply patches to a branch."""
    try:
        branch = engine.get_branch(request.branch_id)
        if not branch:
            raise HTTPException(status_code=404, detail="Branch not found")

        # Validate patches if needed
        validation_errors = []
        if request.validation_level == "strict":
            for patch_data in request.patches:
                validation = engine.patch_engine.validate_patch(patch_data)
                if not validation.valid:
                    validation_errors.extend(validation.errors)

        if validation_errors and request.validation_level == "strict":
            raise HTTPException(
                status_code=400, detail=f"Patch validation failed: {validation_errors}"
            )

        # Apply patches
        new_branch = await engine.patch(branch, request.patches)

        return PatchResponse(
            original_branch_id=request.branch_id,
            new_branch_id=new_branch.branch_id,
            patches_applied=len(request.patches),
            conflicts_detected=0,  # Would be calculated by patch engine
            conflicts_resolved=0,
            validation_errors=validation_errors,
            metadata=request.metadata,
        )

    except Exception as e:
        logger.error(f"Patch failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/diff", response_model=DiffResponse)
async def generate_diff(
    request: DiffRequest, engine: TimeMachineEngine = Depends(get_engine)
):
    """Generate diff between two branches."""
    try:
        diff = await engine.diff(request.from_branch_id, request.to_branch_id)

        # Calculate summary statistics
        summary = {
            "storage_changes": len(diff.storage_changes),
            "balance_changes": len(diff.balance_changes),
            "code_changes": len(diff.code_changes),
            "nonce_changes": len(diff.nonce_changes),
            "log_changes": len(diff.log_changes),
            "total_changes": (
                len(diff.storage_changes)
                + len(diff.balance_changes)
                + len(diff.code_changes)
                + len(diff.nonce_changes)
                + len(diff.log_changes)
            ),
        }

        return DiffResponse(
            diff_id=diff.diff_id,
            from_branch_id=request.from_branch_id,
            to_branch_id=request.to_branch_id,
            format=request.format,
            storage_changes=diff.storage_changes,
            balance_changes=diff.balance_changes,
            code_changes=diff.code_changes,
            nonce_changes=diff.nonce_changes,
            summary=summary,
            created_at=diff.created_at,
            metadata=diff.metadata,
        )

    except Exception as e:
        logger.error(f"Diff generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/branches", response_model=List[BranchInfo])
async def list_branches(
    limit: int = Query(50, description="Maximum number of branches to return"),
    offset: int = Query(0, description="Number of branches to skip"),
    engine: TimeMachineEngine = Depends(get_engine),
):
    """List all branches with pagination."""
    branches = engine.list_branches()

    # Apply pagination
    total_branches = len(branches)
    paginated_branches = branches[offset : offset + limit]

    result = []
    for branch in paginated_branches:
        result.append(
            BranchInfo(
                branch_id=branch.branch_id,
                name=branch.name,
                description=branch.description,
                parent_branch_id=branch.parent_branch_id,
                snapshot_id=branch.snapshot_id,
                block_number=branch.block_number,
                tx_index=branch.tx_index,
                patches_applied=len(branch.patches_applied),
                created_at=branch.created_at,
                tags=branch.tags,
                metadata=branch.metadata,
            )
        )

    return result


@router.get("/branches/{branch_id}", response_model=BranchInfo)
async def get_branch(branch_id: str, engine: TimeMachineEngine = Depends(get_engine)):
    """Get branch details."""
    branch = engine.get_branch(branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    return BranchInfo(
        branch_id=branch.branch_id,
        name=branch.name,
        description=branch.description,
        parent_branch_id=branch.parent_branch_id,
        snapshot_id=branch.snapshot_id,
        block_number=branch.block_number,
        tx_index=branch.tx_index,
        patches_applied=len(branch.patches_applied),
        created_at=branch.created_at,
        tags=branch.tags,
        metadata=branch.metadata,
    )


@router.get("/jobs", response_model=List[JobInfo])
async def list_jobs(
    status: Optional[str] = Query(None, description="Filter by job status"),
    engine: TimeMachineEngine = Depends(get_engine),
):
    """List all jobs."""
    jobs = engine.list_jobs()

    # Filter by status if provided
    if status:
        jobs = [job for job in jobs if job.status.value == status]

    result = []
    for job in jobs:
        result.append(
            JobInfo(
                job_id=job.job_id,
                name=job.name,
                description=job.description,
                status=job.status,
                vm_backend=job.vm_backend.value,
                block_number=job.block_number,
                tx_hash=job.tx_hash,
                from_block=job.from_block,
                to_block=job.to_block,
                created_at=job.created_at,
                started_at=job.started_at,
                completed_at=job.completed_at,
                error_message=job.error_message,
                metadata=job.metadata,
            )
        )

    return result


@router.get("/jobs/{job_id}", response_model=JobInfo)
async def get_job(job_id: str, engine: TimeMachineEngine = Depends(get_engine)):
    """Get job details."""
    job = engine.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobInfo(
        job_id=job.job_id,
        name=job.name,
        description=job.description,
        status=job.status,
        vm_backend=job.vm_backend.value,
        block_number=job.block_number,
        tx_hash=job.tx_hash,
        from_block=job.from_block,
        to_block=job.to_block,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error_message=job.error_message,
        metadata=job.metadata,
    )


# Forensic Sessions


@router.post("/forensic-sessions", response_model=ForensicSessionInfo)
async def create_forensic_session(
    request: ForensicSessionRequest, engine: TimeMachineEngine = Depends(get_engine)
):
    """Create a new forensic analysis session."""
    try:
        session = await engine.create_forensic_session(
            name=request.name,
            session_type=request.session_type,
            analyst=request.analyst or "",
            description=request.description or "",
        )

        # Add target contracts and transactions
        session.target_contracts = request.target_contracts
        session.target_transactions = request.target_transactions
        session.metadata.update(request.metadata)

        return ForensicSessionInfo(
            session_id=session.session_id,
            name=session.name,
            session_type=session.session_type,
            description=session.description,
            analyst=session.analyst,
            target_contracts=session.target_contracts,
            target_transactions=session.target_transactions,
            bookmarks_count=len(session.bookmarks),
            findings_count=len(session.findings),
            created_at=session.created_at,
            last_updated=session.last_updated,
            metadata=session.metadata,
        )

    except Exception as e:
        logger.error(f"Failed to create forensic session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forensic-sessions", response_model=List[ForensicSessionInfo])
async def list_forensic_sessions(
    session_type: Optional[SessionType] = Query(
        None, description="Filter by session type"
    ),
    analyst: Optional[str] = Query(None, description="Filter by analyst"),
    engine: TimeMachineEngine = Depends(get_engine),
):
    """List forensic analysis sessions."""
    sessions = engine.list_forensic_sessions()

    # Apply filters
    if session_type:
        sessions = [s for s in sessions if s.session_type == session_type]
    if analyst:
        sessions = [s for s in sessions if s.analyst == analyst]

    result = []
    for session in sessions:
        result.append(
            ForensicSessionInfo(
                session_id=session.session_id,
                name=session.name,
                session_type=session.session_type,
                description=session.description,
                analyst=session.analyst,
                target_contracts=session.target_contracts,
                target_transactions=session.target_transactions,
                bookmarks_count=len(session.bookmarks),
                findings_count=len(session.findings),
                created_at=session.created_at,
                last_updated=session.last_updated,
                metadata=session.metadata,
            )
        )

    return result


@router.post("/forensic-sessions/{session_id}/bookmarks")
async def add_bookmark(
    session_id: str,
    request: BookmarkRequest,
    engine: TimeMachineEngine = Depends(get_engine),
):
    """Add a bookmark to a forensic session."""
    session = engine.get_forensic_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Forensic session not found")

    session.add_bookmark(
        name=request.name,
        block_number=request.block_number,
        tx_index=request.tx_index,
        description=request.description or "",
        tags=request.tags,
    )

    return {"message": "Bookmark added successfully"}


@router.post("/forensic-sessions/{session_id}/findings")
async def add_finding(
    session_id: str,
    request: FindingRequest,
    engine: TimeMachineEngine = Depends(get_engine),
):
    """Add a finding to a forensic session."""
    session = engine.get_forensic_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Forensic session not found")

    session.add_finding(
        title=request.title,
        severity=request.severity,
        description=request.description,
        evidence=request.evidence,
        recommendations=request.recommendations,
    )

    return {"message": "Finding added successfully"}


# Analysis


@router.post("/analyze", response_model=Dict[str, AnalysisResult])
async def run_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    engine: TimeMachineEngine = Depends(get_engine),
):
    """Run analysis plugins on a branch."""
    try:
        # Run analysis in background
        background_tasks.add_task(
            execute_analysis, request.branch_id, request.session_type, engine
        )

        return {"message": "Analysis started", "branch_id": request.branch_id}

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def execute_analysis(
    branch_id: str, session_type: SessionType, engine: TimeMachineEngine
):
    """Execute analysis in background."""
    try:
        results = await engine.analyze_with_plugins(branch_id, session_type)

        # Notify WebSocket clients
        for plugin_name, result in results.items():
            message = {
                "type": "analysis_complete",
                "branch_id": branch_id,
                "plugin_name": plugin_name,
                "result": result,
            }
            await manager.broadcast(json.dumps(message))

    except Exception as e:
        logger.error(f"Background analysis failed: {e}")


# Snapshots


@router.get("/snapshots", response_model=List[SnapshotInfo])
async def list_snapshots(
    branch_id: Optional[str] = Query(None, description="Filter by branch ID"),
    engine: TimeMachineEngine = Depends(get_engine),
):
    """List available snapshots."""
    snapshots = engine.snapshot_manager.list_snapshots(branch_id)

    result = []
    for snapshot in snapshots:
        result.append(
            SnapshotInfo(
                snapshot_id=snapshot["snapshot_id"],
                branch_id=snapshot["branch_id"],
                block_number=snapshot["block_number"],
                content_hash="",  # Would need to add to snapshot manager
                created_at=datetime.fromisoformat(snapshot["created_at"]),
                size_bytes=snapshot["size_bytes"],
                incremental=snapshot["incremental"],
                parent_snapshot_id=snapshot["parent_snapshot_id"],
            )
        )

    return result


# Engine Management


@router.get("/stats", response_model=EngineStats)
async def get_engine_stats(engine: TimeMachineEngine = Depends(get_engine)):
    """Get engine statistics."""
    stats = engine.get_engine_stats()
    storage_stats = engine.snapshot_manager.get_storage_stats()

    return EngineStats(
        total_branches=int(stats["total_branches"]),
        active_jobs=int(stats["active_jobs"]),
        forensic_sessions=int(stats["forensic_sessions"]),
        registered_plugins=int(stats["registered_plugins"]),
        vm_backend=stats["vm_backend"],
        storage_stats=storage_stats,
    )


@router.get("/macros", response_model=List[MacroInfo])
async def list_macros(engine: TimeMachineEngine = Depends(get_engine)):
    """List available patch macros."""
    macros = engine.patch_engine.list_macros()

    result = []
    for macro in macros:
        result.append(
            MacroInfo(
                name=macro["name"],
                description=macro["description"],
                parameters=[],  # Would need to extract from template
                template={},
            )
        )

    return result


@router.post("/cleanup")
async def cleanup_snapshots(
    max_age_days: int = Query(30, description="Maximum age in days"),
    engine: TimeMachineEngine = Depends(get_engine),
):
    """Clean up old snapshots."""
    try:
        deleted_count = await engine.cleanup_old_snapshots(max_age_days)
        return {"message": f"Cleaned up {deleted_count} snapshots"}
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoints


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            if message.get("type") == "subscribe_timeline":
                branch_id = message.get("branch_id")
                if branch_id:
                    # Start streaming timeline events
                    asyncio.create_task(stream_timeline_events(websocket, branch_id))

            elif message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))

    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id)
        logger.info(f"WebSocket client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        manager.disconnect(websocket, client_id)


async def stream_timeline_events(websocket: WebSocket, branch_id: str):
    """Stream timeline events for a branch."""
    try:
        async for event in engine.get_timeline_events(branch_id):
            event_response = TimelineEventResponse(
                frame_id=event.frame_id,
                frame_type=event.frame_type,
                block_number=event.block_number,
                tx_index=event.tx_index,
                gas_used=event.gas_used,
                gas_limit=event.gas_limit,
                opcode=event.opcode,
                pc=event.pc,
                depth=event.depth,
                address=event.address,
                caller=event.caller,
                value=event.value,
                input_data=event.input_data,
                output_data=event.output_data,
                stack=event.stack,
                memory=event.memory,
                storage=event.storage,
                logs=event.logs,
                error=event.error,
                timestamp=event.timestamp,
                metadata=event.metadata,
            )

            ws_event = WSTimelineEvent(branch_id=branch_id, event=event_response)

            await websocket.send_text(json.dumps(ws_event.dict()))

    except Exception as e:
        logger.error(f"Timeline streaming error for branch {branch_id}: {e}")


# Health check
@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

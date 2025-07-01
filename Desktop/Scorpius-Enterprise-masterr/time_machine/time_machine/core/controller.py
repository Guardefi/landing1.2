"""
Time Machine Core Controller
Orchestrates replay jobs, branch management, and forensic sessions.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncIterator, Dict, List, Optional

from .execution_vm import BaseVMAdapter, get_vm
from .models import (
    AnalysisPlugin,
    Branch,
    Diff,
    ForensicSession,
    JobStatus,
    Patch,
    ReplayJob,
    SessionType,
    StateManipulation,
    TimelineEvent,
    VMBackend,
)
from .patch_engine import PatchEngine
from .snapshot_manager import SnapshotManager

logger = logging.getLogger(__name__)


class TimeMachineEngine:
    """
    Core orchestration engine for blockchain forensic analysis.

    Manages replay jobs, branches, forensic sessions, and coordinates
    VM adapters, snapshot management, and analysis plugins.
    """

    def __init__(
        self,
        vm_backend: VMBackend = VMBackend.ANVIL,
        snapshot_path: str = "./store/snapshots",
        max_concurrent_jobs: int = 5,
    ):
        self.vm_backend = vm_backend
        self.snapshot_manager = SnapshotManager(snapshot_path)
        self.patch_engine = PatchEngine()
        self.active_jobs: Dict[str, ReplayJob] = {}
        self.branches: Dict[str, Branch] = {}
        self.forensic_sessions: Dict[str, ForensicSession] = {}
        self.analysis_plugins: Dict[str, AnalysisPlugin] = {}
        self.semaphore = asyncio.Semaphore(max_concurrent_jobs)

    async def start(self):
        """Initialize the Time Machine engine."""
        logger.info("Starting Time Machine Engine")
        await self.snapshot_manager.initialize()

    async def stop(self):
        """Shutdown the Time Machine engine."""
        logger.info("Stopping Time Machine Engine")
        # Cancel any running jobs
        for job in self.active_jobs.values():
            if job.status == JobStatus.RUNNING:
                job.status = JobStatus.CANCELLED

    def register_plugin(self, plugin: AnalysisPlugin):
        """Register an analysis plugin."""
        self.analysis_plugins[plugin.name] = plugin
        logger.info(f"Registered analysis plugin: {plugin.name} v{plugin.version}")

    async def replay(self, job: ReplayJob) -> Branch:
        """
        Execute a replay job and return the resulting branch.

        Args:
            job: ReplayJob configuration

        Returns:
            Branch: The resulting execution branch

        Raises:
            Exception: If replay fails
        """
        async with self.semaphore:
            logger.info(f"Starting replay job {job.job_id}")
            job.status = JobStatus.RUNNING
            job.started_at = datetime.now()
            self.active_jobs[job.job_id] = job

            try:
                # Get VM adapter
                vm = get_vm(job.vm_backend)
                await vm.start()

                # Initialize VM at target block
                if job.block_number:
                    await vm.load_block(job.block_number)
                elif job.from_block:
                    await vm.load_block(job.from_block)

                # Create initial branch
                branch = Branch(
                    name=job.name or f"Replay-{job.job_id[:8]}",
                    description=job.description,
                    block_number=job.block_number or job.from_block or 0,
                    metadata={"job_id": job.job_id},
                )

                # Take initial snapshot
                snapshot_id = await self.snapshot_manager.create_snapshot(
                    branch.branch_id, branch.block_number, await vm.get_state()
                )
                branch.snapshot_id = snapshot_id

                # Execute specific transaction if provided
                if job.tx_hash:
                    await vm.execute_tx(job.tx_hash)

                # Apply any patches
                if job.patches:
                    patched_branch = await self.patch(branch, job.patches)
                    branch = patched_branch

                # Execute block range if provided
                if job.from_block and job.to_block:
                    for block_num in range(job.from_block, job.to_block + 1):
                        await vm.load_block(block_num)
                        await vm.execute_block()

                # Update job status
                job.status = JobStatus.COMPLETED
                job.completed_at = datetime.now()

                self.branches[branch.branch_id] = branch
                logger.info(f"Replay job {job.job_id} completed successfully")

                await vm.stop()
                return branch

            except Exception as e:
                job.status = JobStatus.FAILED
                job.error_message = str(e)
                job.completed_at = datetime.now()
                logger.error(f"Replay job {job.job_id} failed: {str(e)}")
                raise
            finally:
                self.active_jobs.pop(job.job_id, None)

    async def patch(self, branch: Branch, patch_ops: List[Dict[str, str]]) -> Branch:
        """
        Apply patches to a branch and create a new branch.

        Args:
            branch: Source branch to patch
            patch_ops: List of patch operations

        Returns:
            Branch: New branch with patches applied
        """
        logger.info(f"Applying {len(patch_ops)} patches to branch {branch.branch_id}")

        # Create new branch
        new_branch = Branch(
            name=f"{branch.name}-patched",
            description=f"Patched version of {branch.name}",
            parent_branch_id=branch.branch_id,
            block_number=branch.block_number,
            tx_index=branch.tx_index,
            patches_applied=patch_ops,
        )

        # Get VM adapter and restore state
        vm = get_vm(self.vm_backend)
        await vm.start()

        state = await self.snapshot_manager.restore_snapshot(branch.snapshot_id)
        await vm.load_state(state)

        # Apply patches
        for patch_op in patch_ops:
            patch = self.patch_engine.parse_patch(patch_op)
            await vm.apply_patch(patch)

        # Create new snapshot
        new_snapshot_id = await self.snapshot_manager.create_snapshot(
            new_branch.branch_id, new_branch.block_number, await vm.get_state()
        )
        new_branch.snapshot_id = new_snapshot_id

        await vm.stop()
        self.branches[new_branch.branch_id] = new_branch
        return new_branch

    async def diff(self, from_branch_id: str, to_branch_id: str) -> Diff:
        """
        Generate diff between two branches.

        Args:
            from_branch_id: Source branch ID
            to_branch_id: Target branch ID

        Returns:
            Diff: Difference between the branches
        """
        logger.info(f"Generating diff between {from_branch_id} and {to_branch_id}")

        from_branch = self.branches.get(from_branch_id)
        to_branch = self.branches.get(to_branch_id)

        if not from_branch or not to_branch:
            raise ValueError("One or both branches not found")

        from_state = await self.snapshot_manager.restore_snapshot(
            from_branch.snapshot_id
        )
        to_state = await self.snapshot_manager.restore_snapshot(to_branch.snapshot_id)

        # For now, create a basic diff structure
        # TODO: Implement proper diff engine
        diff = Diff(
            from_branch=from_branch_id,
            to_branch=to_branch_id,
            metadata={
                "from_block": from_branch.block_number,
                "to_block": to_branch.block_number,
            },
        )

        return diff

    async def get_timeline_events(self, branch_id: str) -> AsyncIterator[TimelineEvent]:
        """
        Stream timeline events for a branch.

        Args:
            branch_id: Branch ID to get events for

        Yields:
            TimelineEvent: Individual timeline events
        """
        branch = self.branches.get(branch_id)
        if not branch:
            raise ValueError(f"Branch {branch_id} not found")

        vm = get_vm(self.vm_backend)
        await vm.start()

        state = await self.snapshot_manager.restore_snapshot(branch.snapshot_id)
        await vm.load_state(state)

        try:
            async for event in vm.get_timeline_events():
                yield event
        finally:
            await vm.stop()

    async def create_forensic_session(
        self,
        name: str,
        session_type: SessionType,
        analyst: str = "",
        description: str = "",
    ) -> ForensicSession:
        """Create a new forensic analysis session."""
        session = ForensicSession(
            name=name,
            session_type=session_type,
            description=description,
            analyst=analyst,
        )
        self.forensic_sessions[session.session_id] = session
        logger.info(f"Created forensic session: {session.session_id}")
        return session

    async def analyze_with_plugins(
        self, branch_id: str, session_type: SessionType
    ) -> Dict[str, str]:
        """Run analysis plugins on a branch."""
        branch = self.branches.get(branch_id)
        if not branch:
            raise ValueError(f"Branch {branch_id} not found")

        results = {}
        events = []

        # Collect timeline events
        async for event in self.get_timeline_events(branch_id):
            events.append(event)

        # Run applicable plugins
        for plugin_name, plugin in self.analysis_plugins.items():
            if await plugin.supports_session_type(session_type):
                try:
                    result = await plugin.analyze(events, {"branch": branch})
                    results[plugin_name] = result
                    logger.info(f"Plugin {plugin_name} completed analysis")
                except Exception as e:
                    logger.error(f"Plugin {plugin_name} failed: {str(e)}")
                    results[plugin_name] = {"error": str(e)}

        return results

    def get_job(self, job_id: str) -> Optional[ReplayJob]:
        """Get job by ID."""
        return self.active_jobs.get(job_id)

    def get_branch(self, branch_id: str) -> Optional[Branch]:
        """Get branch by ID."""
        return self.branches.get(branch_id)

    def get_forensic_session(self, session_id: str) -> Optional[ForensicSession]:
        """Get forensic session by ID."""
        return self.forensic_sessions.get(session_id)

    def list_branches(self) -> List[Branch]:
        """List all branches."""
        return list(self.branches.values())

    def list_jobs(self) -> List[ReplayJob]:
        """List all jobs."""
        return list(self.active_jobs.values())

    def list_forensic_sessions(self) -> List[ForensicSession]:
        """List all forensic sessions."""
        return list(self.forensic_sessions.values())

    def list_plugins(self) -> List[str]:
        """List registered plugin names."""
        return list(self.analysis_plugins.keys())

    async def export_branch(
        self, branch_id: str, format: str = "json"
    ) -> Dict[str, str]:
        """
        Export branch data in specified format.

        Args:
            branch_id: Branch ID to export
            format: Export format (json, bundle)

        Returns:
            Dict with export metadata
        """
        branch = self.branches.get(branch_id)
        if not branch:
            raise ValueError(f"Branch {branch_id} not found")

        if format == "json":
            export_data = {
                "branch": branch.to_dict(),
                "snapshot_id": branch.snapshot_id,
                "exported_at": datetime.now().isoformat(),
            }

            return {
                "format": "json",
                "data": export_data,
                "size": len(str(export_data)),
            }

        raise ValueError(f"Unsupported export format: {format}")

    async def cleanup_old_snapshots(self, max_age_days: int = 30):
        """Clean up old snapshots to save storage space."""
        await self.snapshot_manager.cleanup_old_snapshots(max_age_days)
        logger.info(f"Cleaned up snapshots older than {max_age_days} days")

    def get_engine_stats(self) -> Dict[str, str]:
        """Get engine statistics."""
        return {
            "total_branches": len(self.branches),
            "active_jobs": len(
                [j for j in self.active_jobs.values() if j.status == JobStatus.RUNNING]
            ),
            "forensic_sessions": len(self.forensic_sessions),
            "registered_plugins": len(self.analysis_plugins),
            "vm_backend": self.vm_backend.value,
        }

"""
Advanced Snapshot Manager with Deduplication and Compression
Manages blockchain state snapshots with incremental backups and metadata.
"""

import asyncio
import gzip
import hashlib
import json
import logging
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class SnapshotManager:
    """
    Advanced snapshot manager with deduplication, compression,
    incremental snapshots, metadata tracking, and retention policies.
    """

    def __init__(self, storage_path: str = "./store/snapshots"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.metadata_path = self.storage_path / "metadata"
        self.metadata_path.mkdir(exist_ok=True)
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.compression_enabled = True
        self.deduplication_enabled = True
        self.max_cache_size = 100  # Maximum cached snapshots

    async def initialize(self):
        """Initialize the snapshot manager."""
        logger.info("Initializing Snapshot Manager")
        await self._load_metadata_cache()

    async def _load_metadata_cache(self):
        """Load snapshot metadata into cache."""
        metadata_files = list(self.metadata_path.glob("*.meta.json"))
        loaded_count = 0

        for meta_file in metadata_files:
            try:
                with open(meta_file, "r") as f:
                    metadata = json.load(f)
                    snapshot_id = metadata.get("snapshot_id")
                    if snapshot_id:
                        self.cache[snapshot_id] = metadata
                        loaded_count += 1
            except Exception as e:
                logger.warning(f"Failed to load metadata {meta_file}: {e}")

        logger.info(f"Loaded {loaded_count} snapshot metadata entries")

    def _generate_content_hash(self, state: Dict[str, Any]) -> str:
        """Generate content hash for deduplication."""
        state_json = json.dumps(state, sort_keys=True)
        return hashlib.sha256(state_json.encode()).hexdigest()

    def _generate_snapshot_id(
        self, branch_id: str, block_number: int, content_hash: str
    ) -> str:
        """Generate unique snapshot ID."""
        return f"{branch_id}_{block_number}_{content_hash[:16]}"

    async def create_snapshot(
        self,
        branch_id: str,
        block_number: int,
        state: Dict[str, Any],
        incremental: bool = False,
        parent_snapshot_id: Optional[str] = None,
    ) -> str:
        """
        Create a new snapshot with optional incremental support.

        Args:
            branch_id: Branch identifier
            block_number: Block number for the snapshot
            state: Current VM state
            incremental: Whether to create incremental snapshot
            parent_snapshot_id: Parent snapshot for incremental

        Returns:
            str: Generated snapshot ID
        """
        content_hash = self._generate_content_hash(state)
        snapshot_id = self._generate_snapshot_id(branch_id, block_number, content_hash)

        # Check for deduplication
        if self.deduplication_enabled:
            existing_snapshot = await self._find_duplicate_snapshot(content_hash)
            if existing_snapshot:
                logger.info(
                    f"Deduplicating snapshot {snapshot_id} -> {existing_snapshot}"
                )
                await self._create_snapshot_link(snapshot_id, existing_snapshot)
                return snapshot_id

        # Create snapshot directory
        snapshot_dir = self.storage_path / snapshot_id
        snapshot_dir.mkdir(exist_ok=True)

        try:
            # Create snapshot data
            snapshot_data = {
                "snapshot_id": snapshot_id,
                "branch_id": branch_id,
                "block_number": block_number,
                "content_hash": content_hash,
                "state": state,
                "created_at": datetime.now().isoformat(),
                "incremental": incremental,
                "parent_snapshot_id": parent_snapshot_id,
                "compressed": self.compression_enabled,
                "size_bytes": len(json.dumps(state)),
            }

            # Save state data
            state_file = snapshot_dir / "state.json"
            if self.compression_enabled:
                state_file = snapshot_dir / "state.json.gz"
                with gzip.open(state_file, "wt") as f:
                    json.dump(state, f, indent=2)
            else:
                with open(state_file, "w") as f:
                    json.dump(state, f, indent=2)

            # Save metadata
            metadata = {k: v for k, v in snapshot_data.items() if k != "state"}
            metadata_file = self.metadata_path / f"{snapshot_id}.meta.json"
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

            # Update cache
            self.cache[snapshot_id] = metadata
            await self._manage_cache_size()

            logger.info(
                f"Created snapshot {snapshot_id} (size: {metadata['size_bytes']} bytes)"
            )
            return snapshot_id

        except Exception as e:
            # Cleanup on failure
            if snapshot_dir.exists():
                shutil.rmtree(snapshot_dir)
            logger.error(f"Failed to create snapshot {snapshot_id}: {e}")
            raise

    async def restore_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """
        Restore a snapshot by ID.

        Args:
            snapshot_id: Snapshot ID to restore

        Returns:
            Dict[str, Any]: Restored state data
        """
        # Check if it's a link
        link_target = await self._resolve_snapshot_link(snapshot_id)
        if link_target:
            return await self.restore_snapshot(link_target)

        snapshot_dir = self.storage_path / snapshot_id
        if not snapshot_dir.exists():
            raise ValueError(f"Snapshot {snapshot_id} not found")

        try:
            # Load state data
            state_file_gz = snapshot_dir / "state.json.gz"
            state_file = snapshot_dir / "state.json"

            if state_file_gz.exists():
                with gzip.open(state_file_gz, "rt") as f:
                    state = json.load(f)
            elif state_file.exists():
                with open(state_file, "r") as f:
                    state = json.load(f)
            else:
                raise FileNotFoundError("State file not found")

            logger.info(f"Restored snapshot {snapshot_id}")
            return state

        except Exception as e:
            logger.error(f"Failed to restore snapshot {snapshot_id}: {e}")
            raise

    async def delete_snapshot(self, snapshot_id: str, cascade: bool = False) -> bool:
        """
        Delete a snapshot.

        Args:
            snapshot_id: Snapshot ID to delete
            cascade: Whether to delete dependent snapshots

        Returns:
            bool: Success status
        """
        try:
            # Check for dependencies if not cascading
            if not cascade:
                dependents = await self._find_dependent_snapshots(snapshot_id)
                if dependents:
                    raise ValueError(f"Snapshot has dependents: {dependents}")

            # Remove snapshot directory
            snapshot_dir = self.storage_path / snapshot_id
            if snapshot_dir.exists():
                shutil.rmtree(snapshot_dir)

            # Remove metadata
            metadata_file = self.metadata_path / f"{snapshot_id}.meta.json"
            if metadata_file.exists():
                os.remove(metadata_file)

            # Remove from cache
            self.cache.pop(snapshot_id, None)

            # Handle cascade deletion
            if cascade:
                dependents = await self._find_dependent_snapshots(snapshot_id)
                for dependent_id in dependents:
                    await self.delete_snapshot(dependent_id, cascade=True)

            logger.info(f"Deleted snapshot {snapshot_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete snapshot {snapshot_id}: {e}")
            return False

    def list_snapshots(self, branch_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all available snapshots.

        Args:
            branch_id: Optional branch filter

        Returns:
            List[Dict[str, Any]]: List of snapshot metadata
        """
        snapshots = []

        for snapshot_id, metadata in self.cache.items():
            if branch_id and metadata.get("branch_id") != branch_id:
                continue

            snapshots.append(
                {
                    "snapshot_id": snapshot_id,
                    "branch_id": metadata.get("branch_id"),
                    "block_number": metadata.get("block_number"),
                    "created_at": metadata.get("created_at"),
                    "size_bytes": metadata.get("size_bytes", 0),
                    "incremental": metadata.get("incremental", False),
                    "parent_snapshot_id": metadata.get("parent_snapshot_id"),
                }
            )

        # Sort by creation time
        snapshots.sort(key=lambda x: x["created_at"], reverse=True)
        return snapshots

    async def get_snapshot_info(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed snapshot information."""
        metadata = self.cache.get(snapshot_id)
        if not metadata:
            return None

        # Add file system information
        snapshot_dir = self.storage_path / snapshot_id
        if snapshot_dir.exists():
            total_size = sum(
                f.stat().st_size for f in snapshot_dir.rglob("*") if f.is_file()
            )
            metadata = metadata.copy()
            metadata["disk_size_bytes"] = total_size

        return metadata

    async def cleanup_old_snapshots(
        self, max_age_days: int = 30, keep_minimum: int = 10
    ) -> int:
        """
        Clean up old snapshots based on retention policy.

        Args:
            max_age_days: Maximum age in days
            keep_minimum: Minimum snapshots to keep

        Returns:
            int: Number of snapshots deleted
        """
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        deleted_count = 0

        # Get snapshots sorted by creation time
        snapshots = self.list_snapshots()
        old_snapshots = [
            s
            for s in snapshots
            if datetime.fromisoformat(s["created_at"]) < cutoff_date
        ]

        # Keep minimum number of snapshots
        if len(snapshots) - len(old_snapshots) < keep_minimum:
            keep_count = keep_minimum - (len(snapshots) - len(old_snapshots))
            old_snapshots = old_snapshots[keep_count:]

        # Delete old snapshots
        for snapshot in old_snapshots:
            if await self.delete_snapshot(snapshot["snapshot_id"]):
                deleted_count += 1

        logger.info(f"Cleaned up {deleted_count} old snapshots")
        return deleted_count

    async def create_incremental_snapshot(
        self,
        branch_id: str,
        block_number: int,
        current_state: Dict[str, Any],
        parent_snapshot_id: str,
    ) -> str:
        """Create incremental snapshot with delta compression."""
        parent_state = await self.restore_snapshot(parent_snapshot_id)

        # Calculate delta (simplified - would be more sophisticated in reality)
        delta = self._calculate_state_delta(parent_state, current_state)

        # Create incremental snapshot
        incremental_state = {
            "type": "incremental",
            "parent_snapshot_id": parent_snapshot_id,
            "delta": delta,
            "full_state_hash": self._generate_content_hash(current_state),
        }

        return await self.create_snapshot(
            branch_id,
            block_number,
            incremental_state,
            incremental=True,
            parent_snapshot_id=parent_snapshot_id,
        )

    def _calculate_state_delta(
        self, old_state: Dict[str, Any], new_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate delta between two states."""
        delta = {"added": {}, "modified": {}, "removed": {}}

        # This is a simplified delta calculation
        # In reality, would need sophisticated tree diff algorithms
        old_keys = set(old_state.keys())
        new_keys = set(new_state.keys())

        delta["added"] = {k: new_state[k] for k in new_keys - old_keys}
        delta["removed"] = {k: old_state[k] for k in old_keys - new_keys}

        for key in old_keys & new_keys:
            if old_state[key] != new_state[key]:
                delta["modified"][key] = new_state[key]

        return delta

    async def _find_duplicate_snapshot(self, content_hash: str) -> Optional[str]:
        """Find existing snapshot with same content hash."""
        for snapshot_id, metadata in self.cache.items():
            if metadata.get("content_hash") == content_hash:
                return snapshot_id
        return None

    async def _create_snapshot_link(self, snapshot_id: str, target_id: str):
        """Create a symbolic link between snapshots."""
        link_file = self.storage_path / f"{snapshot_id}.link"
        with open(link_file, "w") as f:
            json.dump({"target": target_id}, f)

    async def _resolve_snapshot_link(self, snapshot_id: str) -> Optional[str]:
        """Resolve snapshot link to target ID."""
        link_file = self.storage_path / f"{snapshot_id}.link"
        if link_file.exists():
            with open(link_file, "r") as f:
                link_data = json.load(f)
                return link_data.get("target")
        return None

    async def _find_dependent_snapshots(self, snapshot_id: str) -> List[str]:
        """Find snapshots that depend on this one."""
        dependents = []
        for sid, metadata in self.cache.items():
            if metadata.get("parent_snapshot_id") == snapshot_id:
                dependents.append(sid)
        return dependents

    async def _manage_cache_size(self):
        """Manage cache size by removing least recently used entries."""
        if len(self.cache) > self.max_cache_size:
            # Simple LRU eviction - would be more sophisticated in reality
            excess_count = len(self.cache) - self.max_cache_size
            sorted_items = sorted(
                self.cache.items(),
                key=lambda x: x[1].get("created_at", ""),
            )

            for i in range(excess_count):
                snapshot_id, _ = sorted_items[i]
                self.cache.pop(snapshot_id, None)

            logger.info(f"Evicted {excess_count} entries from cache")

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        total_snapshots = len(self.cache)
        total_size = 0

        # Calculate total disk usage
        for snapshot_dir in self.storage_path.iterdir():
            if snapshot_dir.is_dir():
                dir_size = sum(
                    f.stat().st_size for f in snapshot_dir.rglob("*") if f.is_file()
                )
                total_size += dir_size

        return {
            "total_snapshots": total_snapshots,
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "storage_path": str(self.storage_path),
            "compression_enabled": self.compression_enabled,
            "deduplication_enabled": self.deduplication_enabled,
        }

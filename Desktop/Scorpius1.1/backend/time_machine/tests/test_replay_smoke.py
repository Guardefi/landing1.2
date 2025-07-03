"""
Test suite for Time Machine replay functionality
Smoke tests to validate core replay operations
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

sys.path.append(str(Path(__file__).parent.parent))

from packages.core.core.controller import TimeMachineEngine
from packages.core.core.execution_vm import BaseVMAdapter
from packages.core.core.models import JobStatus, ReplayJob, VMType


class MockVMAdapter(BaseVMAdapter):
    """Mock VM adapter for testing"""

    def __init__(self, config=None):
        super().__init__(config or {})
        self.initialized = False
        self.blocks_data = []
        self.snapshots = {}

    async def initialize(self):
        self.initialized = True

    async def cleanup(self):
        self.initialized = False

    async def load_block_range(self, start_block, end_block):
        """Return mock block data"""
        blocks = []
        for i in range(start_block, end_block + 1):
            blocks.append(
                {
                    "number": hex(i),
                    "hash": f'0x{"0"*63}{i:x}',
                    "parentHash": f'0x{"0"*63}{i-1:x}' if i > 0 else "0x0",
                    "timestamp": hex(1700000000 + i * 12),  # 12 second blocks
                    "gasUsed": hex(21000 * (i % 10 + 1)),
                    "transactions": [
                        {
                            "hash": f'0x{"1"*63}{j:x}',
                            "from": f'0x{"a"*40}',
                            "to": f'0x{"b"*40}',
                            "value": hex(1000000),
                            "gas": hex(21000),
                            "gasPrice": hex(20000000000),
                        }
                        for j in range(i % 3 + 1)  # 1-3 transactions per block
                    ],
                }
            )
        return blocks

    async def load_transaction(self, tx_hash):
        return {
            "hash": tx_hash,
            "blockNumber": hex(100),
            "from": "0x" + "a" * 40,
            "to": "0x" + "b" * 40,
            "value": hex(1000000),
            "gas": hex(21000),
            "gasPrice": hex(20000000000),
        }

    async def get_state_at_block(self, block_number):
        return {
            "block_number": block_number,
            "accounts": {
                "0x"
                + "a"
                * 40: {
                    "balance": hex(1000000000),
                    "nonce": hex(block_number),
                    "code": "0x",
                    "storage": {},
                }
            },
        }

    async def apply_state_patch(self, patch_data):
        return True

    async def create_snapshot(self):
        snapshot_id = f"snapshot_{len(self.snapshots)}"
        self.snapshots[snapshot_id] = {"created_at": "now"}
        return snapshot_id

    async def restore_snapshot(self, snapshot_id):
        return snapshot_id in self.snapshots

    async def execute_transaction(self, tx_data):
        return {
            "hash": "0x" + "1" * 64,
            "receipt": {
                "status": "0x1",
                "gasUsed": hex(21000),
                "blockNumber": hex(101),
            },
        }

    async def trace_transaction(self, tx_hash):
        return {
            "type": "CALL",
            "from": "0x" + "a" * 40,
            "to": "0x" + "b" * 40,
            "value": hex(1000000),
            "gas": hex(21000),
            "gasUsed": hex(21000),
        }

    async def stream_events(self, start_block, end_block=None):
        # Mock event stream
        for i in range(start_block, (end_block or start_block + 5) + 1):
            yield {
                "event_type": "block_processed",
                "block_number": i,
                "timestamp": 1700000000 + i * 12,
            }

    async def get_gas_estimates(self, transactions):
        return [
            {"tx": tx, "gas_estimate": 21000, "gas_price": 20000000000}
            for tx in transactions
        ]


@pytest.fixture
def mock_vm_adapter():
    """Fixture providing mock VM adapter"""
    return MockVMAdapter()


@pytest.fixture
async def engine():
    """Fixture providing Time Machine engine"""
    engine = TimeMachineEngine()
    await engine.initialize()
    yield engine
    await engine.cleanup()


class TestReplaySmoke:
    """Smoke tests for replay functionality"""

    @pytest.mark.asyncio
    async def test_engine_initialization(self, engine):
        """Test engine can be initialized and cleaned up"""
        assert engine.initialized
        assert len(engine.vm_adapters) >= 0

    @pytest.mark.asyncio
    async def test_create_replay_job(self, engine, mock_vm_adapter):
        """Test creating a basic replay job"""
        # Register mock adapter
        engine.vm_adapters[VMType.ANVIL] = lambda config: mock_vm_adapter

        job = await engine.create_replay_job(
            start_block=100, end_block=105, vm_type=VMType.ANVIL, config={"test": True}
        )

        assert job.id is not None
        assert job.start_block == 100
        assert job.end_block == 105
        assert job.vm_type == VMType.ANVIL
        assert job.status == JobStatus.PENDING

    @pytest.mark.asyncio
    async def test_run_replay_job(self, engine, mock_vm_adapter):
        """Test running a replay job to completion"""
        # Register mock adapter
        engine.vm_adapters[VMType.ANVIL] = lambda config: mock_vm_adapter

        # Create job
        job = await engine.create_replay_job(
            start_block=100, end_block=102, vm_type=VMType.ANVIL
        )

        # Run job
        result = await engine.run_replay_job(job.id)

        assert result is not None
        assert result.status == JobStatus.COMPLETED
        assert len(result.snapshots) > 0

    @pytest.mark.asyncio
    async def test_create_branch(self, engine, mock_vm_adapter):
        """Test creating a branch from a snapshot"""
        # Register mock adapter and run a job to get snapshots
        engine.vm_adapters[VMType.ANVIL] = lambda config: mock_vm_adapter

        job = await engine.create_replay_job(
            start_block=100, end_block=101, vm_type=VMType.ANVIL
        )

        result = await engine.run_replay_job(job.id)
        snapshot_id = result.snapshots[0]

        # Create branch
        branch = await engine.create_branch(
            name="test-branch",
            description="Test branch for smoke test",
            base_snapshot_id=snapshot_id,
        )

        assert branch.id is not None
        assert branch.name == "test-branch"
        assert branch.base_snapshot_id == snapshot_id

    @pytest.mark.asyncio
    async def test_apply_patch(self, engine, mock_vm_adapter):
        """Test applying a state patch"""
        # Register mock adapter
        engine.vm_adapters[VMType.ANVIL] = lambda config: mock_vm_adapter

        # Create and run job
        job = await engine.create_replay_job(
            start_block=100, end_block=100, vm_type=VMType.ANVIL
        )

        result = await engine.run_replay_job(job.id)
        snapshot_id = result.snapshots[0]

        # Create patch
        patch_data = {
            "name": "test-patch",
            "description": "Test state patch",
            "operations": [
                {
                    "op_type": "set",
                    "path": "accounts.0xaaa.balance",
                    "value": "0x1000000000",
                }
            ],
        }

        patch_result = await engine.apply_patch(snapshot_id, patch_data)

        assert patch_result is not None
        assert "result_snapshot_id" in patch_result

    @pytest.mark.asyncio
    async def test_generate_diff(self, engine, mock_vm_adapter):
        """Test generating diff between snapshots"""
        # Register mock adapter
        engine.vm_adapters[VMType.ANVIL] = lambda config: mock_vm_adapter

        # Create job and get multiple snapshots
        job = await engine.create_replay_job(
            start_block=100, end_block=102, vm_type=VMType.ANVIL
        )

        result = await engine.run_replay_job(job.id)
        snapshot1 = result.snapshots[0]
        snapshot2 = result.snapshots[1]

        # Generate diff
        diff_result = await engine.generate_diff(
            left_snapshot_id=snapshot1, right_snapshot_id=snapshot2, format="json"
        )

        assert diff_result is not None
        assert "content" in diff_result
        assert "format" in diff_result

    @pytest.mark.asyncio
    async def test_list_jobs(self, engine, mock_vm_adapter):
        """Test listing replay jobs"""
        # Register mock adapter
        engine.vm_adapters[VMType.ANVIL] = lambda config: mock_vm_adapter

        # Create a few jobs
        job1 = await engine.create_replay_job(100, 105, VMType.ANVIL)
        job2 = await engine.create_replay_job(200, 205, VMType.ANVIL)

        # List jobs
        jobs = await engine.list_jobs()

        assert len(jobs) >= 2
        job_ids = [job.id for job in jobs]
        assert job1.id in job_ids
        assert job2.id in job_ids

    @pytest.mark.asyncio
    async def test_get_job_status(self, engine, mock_vm_adapter):
        """Test getting job status"""
        # Register mock adapter
        engine.vm_adapters[VMType.ANVIL] = lambda config: mock_vm_adapter

        job = await engine.create_replay_job(100, 102, VMType.ANVIL)

        # Get status before running
        status = await engine.get_job_status(job.id)
        assert status.status == JobStatus.PENDING

        # Run job
        await engine.run_replay_job(job.id)

        # Get status after running
        status = await engine.get_job_status(job.id)
        assert status.status == JobStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_cleanup_old_jobs(self, engine, mock_vm_adapter):
        """Test cleanup of old jobs"""
        # Register mock adapter
        engine.vm_adapters[VMType.ANVIL] = lambda config: mock_vm_adapter

        # Create and run a job
        job = await engine.create_replay_job(100, 101, VMType.ANVIL)
        await engine.run_replay_job(job.id)

        # Test cleanup (dry run)
        cleanup_result = await engine.cleanup_old_data(
            older_than_days=0, dry_run=True  # Clean everything
        )

        assert "jobs_to_delete" in cleanup_result
        assert "snapshots_to_delete" in cleanup_result
        assert cleanup_result["dry_run"] is True


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

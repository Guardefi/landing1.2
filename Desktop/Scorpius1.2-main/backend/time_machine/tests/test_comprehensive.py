# Time Machine Test Suite
# Comprehensive testing configuration for the blockchain forensic platform

import asyncio
import json
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from packages.core.core.controller import TimeMachineEngine
from packages.core.core.diff_engine import DiffEngine
from packages.core.core.execution_vm import BaseVMAdapter
from packages.core.core.models import *
from packages.core.core.patch_engine import PatchEngine
from packages.core.core.snapshot_manager import SnapshotManager
from packages.core.plugins.gas_analysis import GasAnalysisPlugin


class MockVMAdapter(BaseVMAdapter):
    """Enhanced mock VM adapter for comprehensive testing"""

    def __init__(self, config=None):
        super().__init__(config or {})
        self.initialized = False
        self.blocks_data = []
        self.snapshots = {}
        self.state = {}
        self.call_count = 0

    async def initialize(self):
        self.initialized = True

    async def cleanup(self):
        self.initialized = False

    async def load_block_range(self, start_block, end_block):
        """Return comprehensive mock block data"""
        self.call_count += 1
        blocks = []

        for i in range(start_block, end_block + 1):
            block = {
                "number": hex(i),
                "hash": f'0x{"0"*63}{i:x}',
                "parentHash": f'0x{"0"*63}{i-1:x}' if i > 0 else "0x0",
                "timestamp": hex(1700000000 + i * 12),
                "gasUsed": hex(21000 * (i % 10 + 1)),
                "gasLimit": hex(30000000),
                "baseFeePerGas": hex(20 * 10**9),
                "difficulty": hex(2**20),
                "stateRoot": f'0x{"a"*63}{i:x}',
                "transactionsRoot": f'0x{"b"*63}{i:x}',
                "receiptsRoot": f'0x{"c"*63}{i:x}',
                "miner": "0x" + "f" * 40,
                "extraData": "0x",
                "transactions": [],
            }

            # Add mock transactions
            for j in range(i % 3 + 1):
                tx = {
                    "hash": f'0x{"1"*63}{j:x}',
                    "blockNumber": hex(i),
                    "blockHash": block["hash"],
                    "transactionIndex": hex(j),
                    "from": f'0x{"a"*40}',
                    "to": f'0x{"b"*40}',
                    "value": hex(1000000 * (j + 1)),
                    "gas": hex(21000),
                    "gasPrice": hex(20000000000),
                    "gasUsed": hex(21000),
                    "nonce": hex(i + j),
                    "input": "0x",
                    "type": "0x2",
                    "chainId": hex(31337),
                    "v": "0x1",
                    "r": "0x" + "2" * 64,
                    "s": "0x" + "3" * 64,
                }
                block["transactions"].append(tx)

            blocks.append(block)

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
            "gasUsed": hex(21000),
            "status": "0x1",
        }

    async def get_state_at_block(self, block_number):
        return {
            "block_number": block_number,
            "state_root": f'0x{"a"*63}{block_number:x}',
            "accounts": {
                "0x"
                + "a"
                * 40: {
                    "balance": hex(1000000000 + block_number * 1000),
                    "nonce": hex(block_number),
                    "code": "0x",
                    "storage": {"0x" + "0" * 64: hex(block_number * 100)},
                },
                "0x"
                + "b"
                * 40: {
                    "balance": hex(500000000 + block_number * 500),
                    "nonce": hex(0),
                    "code": "0x6080604052",
                    "storage": {},
                },
            },
            "timestamp": 1700000000 + block_number * 12,
        }

    async def apply_state_patch(self, patch_data):
        """Apply mock state patch"""
        success = True
        for op in patch_data.get("operations", []):
            if op.get("op_type") == "set":
                # Mock successful patch application
                continue
            elif op.get("op_type") == "invalid":
                success = False
                break
        return success

    async def create_snapshot(self):
        snapshot_id = f"mock_snapshot_{len(self.snapshots)}"
        self.snapshots[snapshot_id] = {
            "created_at": "2024-01-01T00:00:00Z",
            "block_number": 100,
            "state_root": "0x" + "a" * 64,
        }
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
                "logs": [],
            },
            "block_number": 101,
        }

    async def trace_transaction(self, tx_hash):
        return {
            "type": "CALL",
            "from": "0x" + "a" * 40,
            "to": "0x" + "b" * 40,
            "value": hex(1000000),
            "gas": hex(21000),
            "gasUsed": hex(21000),
            "output": "0x",
            "calls": [],
        }

    async def stream_events(self, start_block, end_block=None):
        """Stream mock events"""
        for i in range(start_block, (end_block or start_block + 5) + 1):
            yield TimelineEvent(
                event_type=EventType.BLOCK_PROCESSED,
                description=f"Block {i} processed",
                metadata={
                    "block_number": i,
                    "tx_count": i % 3 + 1,
                    "gas_used": 21000 * (i % 10 + 1),
                    "timestamp": 1700000000 + i * 12,
                },
            )

            # Emit some transaction events
            for j in range(i % 2 + 1):
                yield TimelineEvent(
                    event_type=EventType.TRANSACTION_EXECUTED,
                    description=f"Transaction {j} in block {i}",
                    metadata={
                        "tx_hash": f'0x{"1"*63}{j:x}',
                        "block_number": i,
                        "gas_used": 21000,
                    },
                )

    async def get_gas_estimates(self, transactions):
        return [
            {
                "tx": tx,
                "gas_estimate": 21000 + len(tx.get("input", "0x")) // 2 * 16,
                "gas_price": 20000000000,
            }
            for tx in transactions
        ]


@pytest.fixture
def mock_vm_adapter():
    return MockVMAdapter()


@pytest.fixture
async def engine():
    """Fixture providing initialized Time Machine engine"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config = {
            "storage": {
                "snapshots_dir": str(Path(temp_dir) / "snapshots"),
                "bundles_dir": str(Path(temp_dir) / "bundles"),
                "compression": True,
                "deduplication": True,
            }
        }

        engine = TimeMachineEngine(config)
        await engine.initialize()

        yield engine

        await engine.cleanup()


@pytest.fixture
def sample_patch_data():
    return {
        "name": "test-patch",
        "description": "Test state patch",
        "operations": [
            {
                "op_type": "set",
                "path": "accounts.0xaaa.balance",
                "value": "0x1000000000",
                "condition": None,
            },
            {
                "op_type": "set",
                "path": "accounts.0xbbb.storage.0x0",
                "value": "0x123",
                "condition": None,
            },
        ],
    }


@pytest.fixture
def sample_diff_config():
    return {
        "format": "json",
        "include_metadata": True,
        "ignore_fields": ["timestamp"],
        "context_lines": 3,
    }


class TestTimeMachineEngine:
    """Comprehensive tests for TimeMachine engine"""

    @pytest.mark.asyncio
    async def test_engine_initialization(self, engine):
        """Test engine initialization and cleanup"""
        assert engine.initialized
        assert hasattr(engine, "vm_adapters")
        assert hasattr(engine, "snapshot_manager")
        assert hasattr(engine, "patch_engine")
        assert hasattr(engine, "diff_engine")

    @pytest.mark.asyncio
    async def test_vm_adapter_registration(self, engine, mock_vm_adapter):
        """Test VM adapter registration"""
        engine.register_vm_adapter(VMType.ANVIL, lambda config: mock_vm_adapter)
        assert VMType.ANVIL in engine.vm_adapters

        adapter = engine.vm_adapters[VMType.ANVIL]({})
        assert isinstance(adapter, MockVMAdapter)

    @pytest.mark.asyncio
    async def test_create_replay_job(self, engine, mock_vm_adapter):
        """Test replay job creation"""
        engine.register_vm_adapter(VMType.ANVIL, lambda config: mock_vm_adapter)

        job = await engine.create_replay_job(
            start_block=100, end_block=105, vm_type=VMType.ANVIL, config={"test": True}
        )

        assert job.id is not None
        assert job.start_block == 100
        assert job.end_block == 105
        assert job.vm_type == VMType.ANVIL
        assert job.status == JobStatus.PENDING
        assert job.config.get("test") is True

    @pytest.mark.asyncio
    async def test_run_replay_job_success(self, engine, mock_vm_adapter):
        """Test successful replay job execution"""
        engine.register_vm_adapter(VMType.ANVIL, lambda config: mock_vm_adapter)

        job = await engine.create_replay_job(
            start_block=100, end_block=102, vm_type=VMType.ANVIL
        )

        result = await engine.run_replay_job(job.id)

        assert result is not None
        assert result.status == JobStatus.COMPLETED
        assert len(result.snapshots) > 0
        assert mock_vm_adapter.call_count > 0

    @pytest.mark.asyncio
    async def test_run_replay_job_failure(self, engine):
        """Test replay job failure handling"""
        # Create job with unregistered VM type
        job = await engine.create_replay_job(
            start_block=100, end_block=102, vm_type=VMType.GETH  # Not registered
        )

        result = await engine.run_replay_job(job.id)

        assert result.status == JobStatus.FAILED
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_create_branch(self, engine, mock_vm_adapter):
        """Test branch creation"""
        engine.register_vm_adapter(VMType.ANVIL, lambda config: mock_vm_adapter)

        # Create job and get snapshot
        job = await engine.create_replay_job(100, 101, VMType.ANVIL)
        result = await engine.run_replay_job(job.id)
        snapshot_id = result.snapshots[0]

        # Create branch
        branch = await engine.create_branch(
            name="test-branch", description="Test branch", base_snapshot_id=snapshot_id
        )

        assert branch.id is not None
        assert branch.name == "test-branch"
        assert branch.base_snapshot_id == snapshot_id
        assert not branch.is_active  # New branches start inactive

    @pytest.mark.asyncio
    async def test_apply_patch_success(
        self, engine, mock_vm_adapter, sample_patch_data
    ):
        """Test successful patch application"""
        engine.register_vm_adapter(VMType.ANVIL, lambda config: mock_vm_adapter)

        # Create job and get snapshot
        job = await engine.create_replay_job(100, 100, VMType.ANVIL)
        result = await engine.run_replay_job(job.id)
        snapshot_id = result.snapshots[0]

        # Apply patch
        patch_result = await engine.apply_patch(snapshot_id, sample_patch_data)

        assert patch_result is not None
        assert "result_snapshot_id" in patch_result
        assert patch_result["success"] is True

    @pytest.mark.asyncio
    async def test_apply_patch_failure(self, engine, mock_vm_adapter):
        """Test patch application failure"""
        engine.register_vm_adapter(VMType.ANVIL, lambda config: mock_vm_adapter)

        # Create job and get snapshot
        job = await engine.create_replay_job(100, 100, VMType.ANVIL)
        result = await engine.run_replay_job(job.id)
        snapshot_id = result.snapshots[0]

        # Apply invalid patch
        invalid_patch = {
            "name": "invalid-patch",
            "operations": [{"op_type": "invalid", "path": "test"}],
        }

        patch_result = await engine.apply_patch(snapshot_id, invalid_patch)

        assert patch_result["success"] is False
        assert "error" in patch_result

    @pytest.mark.asyncio
    async def test_generate_diff(self, engine, mock_vm_adapter, sample_diff_config):
        """Test diff generation"""
        engine.register_vm_adapter(VMType.ANVIL, lambda config: mock_vm_adapter)

        # Create job and get multiple snapshots
        job = await engine.create_replay_job(100, 102, VMType.ANVIL)
        result = await engine.run_replay_job(job.id)

        snapshot1 = result.snapshots[0]
        snapshot2 = result.snapshots[1]

        # Generate diff
        diff_result = await engine.generate_diff(
            left_snapshot_id=snapshot1,
            right_snapshot_id=snapshot2,
            **sample_diff_config,
        )

        assert diff_result is not None
        assert "content" in diff_result
        assert "format" in diff_result
        assert diff_result["format"] == "json"

    @pytest.mark.asyncio
    async def test_list_jobs(self, engine, mock_vm_adapter):
        """Test job listing"""
        engine.register_vm_adapter(VMType.ANVIL, lambda config: mock_vm_adapter)

        # Create multiple jobs
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
        """Test job status retrieval"""
        engine.register_vm_adapter(VMType.ANVIL, lambda config: mock_vm_adapter)

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
    async def test_engine_stats(self, engine, mock_vm_adapter):
        """Test engine statistics"""
        engine.register_vm_adapter(VMType.ANVIL, lambda config: mock_vm_adapter)

        # Create and run some jobs
        job1 = await engine.create_replay_job(100, 102, VMType.ANVIL)
        job2 = await engine.create_replay_job(200, 203, VMType.ANVIL)

        await engine.run_replay_job(job1.id)
        await engine.run_replay_job(job2.id)

        # Get stats
        stats = await engine.get_engine_stats()

        assert "total_jobs" in stats
        assert "completed_jobs" in stats
        assert "total_snapshots" in stats
        assert stats["total_jobs"] >= 2
        assert stats["completed_jobs"] >= 2

    @pytest.mark.asyncio
    async def test_cleanup_old_data(self, engine, mock_vm_adapter):
        """Test data cleanup functionality"""
        engine.register_vm_adapter(VMType.ANVIL, lambda config: mock_vm_adapter)

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
        assert isinstance(cleanup_result["jobs_to_delete"], int)
        assert isinstance(cleanup_result["snapshots_to_delete"], int)


class TestSnapshotManager:
    """Test snapshot management functionality"""

    @pytest.fixture
    def snapshot_manager(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "snapshots_dir": str(Path(temp_dir) / "snapshots"),
                "compression": True,
                "deduplication": True,
            }
            yield SnapshotManager(config)

    def test_snapshot_manager_initialization(self, snapshot_manager):
        """Test snapshot manager initialization"""
        assert snapshot_manager.config["compression"] is True
        assert snapshot_manager.config["deduplication"] is True

    @pytest.mark.asyncio
    async def test_create_snapshot(self, snapshot_manager):
        """Test snapshot creation"""
        job_id = "test-job-123"
        block_number = 100
        state_data = {
            "accounts": {
                "0x"
                + "a"
                * 40: {
                    "balance": "0x1000000",
                    "nonce": "0x1",
                    "code": "0x",
                    "storage": {},
                }
            }
        }

        snapshot_id = await snapshot_manager.create_snapshot(
            job_id, block_number, state_data
        )

        assert snapshot_id is not None
        assert isinstance(snapshot_id, str)

    @pytest.mark.asyncio
    async def test_load_snapshot(self, snapshot_manager):
        """Test snapshot loading"""
        # Create a snapshot first
        job_id = "test-job-123"
        block_number = 100
        state_data = {"test": "data"}

        snapshot_id = await snapshot_manager.create_snapshot(
            job_id, block_number, state_data
        )

        # Load the snapshot
        loaded_data = await snapshot_manager.load_snapshot(snapshot_id)

        assert loaded_data is not None
        assert "test" in loaded_data
        assert loaded_data["test"] == "data"


class TestPatchEngine:
    """Test patch engine functionality"""

    @pytest.fixture
    def patch_engine(self):
        return PatchEngine()

    def test_patch_engine_initialization(self, patch_engine):
        """Test patch engine initialization"""
        assert patch_engine is not None

    @pytest.mark.asyncio
    async def test_validate_patch_success(self, patch_engine, sample_patch_data):
        """Test successful patch validation"""
        result = await patch_engine.validate_patch(sample_patch_data)

        assert result["valid"] is True
        assert "errors" not in result or len(result["errors"]) == 0

    @pytest.mark.asyncio
    async def test_validate_patch_failure(self, patch_engine):
        """Test patch validation failure"""
        invalid_patch = {
            "name": "invalid-patch",
            "operations": [{"op_type": "invalid_operation", "path": "test"}],
        }

        result = await patch_engine.validate_patch(invalid_patch)

        assert result["valid"] is False
        assert "errors" in result
        assert len(result["errors"]) > 0


class TestDiffEngine:
    """Test diff engine functionality"""

    @pytest.fixture
    def diff_engine(self):
        return DiffEngine()

    def test_diff_engine_initialization(self, diff_engine):
        """Test diff engine initialization"""
        assert diff_engine is not None

    @pytest.mark.asyncio
    async def test_generate_json_diff(self, diff_engine):
        """Test JSON diff generation"""
        left_data = {
            "accounts": {"0xaaa": {"balance": "0x1000"}, "0xbbb": {"balance": "0x2000"}}
        }

        right_data = {
            "accounts": {
                "0xaaa": {"balance": "0x1500"},  # Changed
                "0xbbb": {"balance": "0x2000"},  # Same
                "0xccc": {"balance": "0x3000"},  # Added
            }
        }

        result = await diff_engine.generate_diff(left_data, right_data, format="json")

        assert result is not None
        assert "content" in result
        assert "format" in result
        assert result["format"] == "json"

    @pytest.mark.asyncio
    async def test_generate_html_diff(self, diff_engine):
        """Test HTML diff generation"""
        left_data = {"test": "old_value"}
        right_data = {"test": "new_value"}

        result = await diff_engine.generate_diff(left_data, right_data, format="html")

        assert result is not None
        assert result["format"] == "html"
        assert "content" in result


class TestGasAnalysisPlugin:
    """Test gas analysis plugin"""

    @pytest.fixture
    def gas_plugin(self):
        return GasAnalysisPlugin()

    def test_plugin_initialization(self, gas_plugin):
        """Test plugin initialization"""
        assert gas_plugin.plugin_id == "gas_analyzer"
        assert gas_plugin.name == "Gas Analysis Plugin"
        assert gas_plugin.plugin_type == "gas"

    @pytest.mark.asyncio
    async def test_gas_analysis(self, gas_plugin, mock_vm_adapter):
        """Test gas analysis execution"""
        config = {
            "start_block": 100,
            "end_block": 105,
            "analyze_patterns": True,
            "include_optimizations": True,
        }

        result = await gas_plugin.analyze(mock_vm_adapter, config)

        assert result.plugin_id == "gas_analyzer"
        assert result.status == "completed"
        assert "metrics" in result.results
        assert "patterns" in result.results
        assert "optimizations" in result.results


class TestIntegration:
    """Integration tests for the complete system"""

    @pytest.mark.asyncio
    async def test_complete_replay_workflow(self, engine, mock_vm_adapter):
        """Test complete replay workflow"""
        engine.register_vm_adapter(VMType.ANVIL, lambda config: mock_vm_adapter)

        # 1. Create replay job
        job = await engine.create_replay_job(
            start_block=100,
            end_block=105,
            vm_type=VMType.ANVIL,
            config={"enable_tracing": True},
        )

        # 2. Run replay job
        result = await engine.run_replay_job(job.id)
        assert result.status == JobStatus.COMPLETED

        # 3. Create branch from snapshot
        snapshot_id = result.snapshots[0]
        branch = await engine.create_branch(
            name="analysis-branch",
            description="Analysis branch",
            base_snapshot_id=snapshot_id,
        )

        # 4. Apply patch
        patch_data = {
            "name": "test-patch",
            "operations": [
                {
                    "op_type": "set",
                    "path": "accounts.0xtest.balance",
                    "value": "0x1000000",
                }
            ],
        }

        patch_result = await engine.apply_patch(snapshot_id, patch_data)
        assert patch_result["success"] is True

        # 5. Generate diff
        new_snapshot_id = patch_result["result_snapshot_id"]
        diff_result = await engine.generate_diff(
            left_snapshot_id=snapshot_id,
            right_snapshot_id=new_snapshot_id,
            format="json",
        )

        assert diff_result is not None

    @pytest.mark.asyncio
    async def test_forensic_session_workflow(self, engine, mock_vm_adapter):
        """Test forensic session workflow"""
        engine.register_vm_adapter(VMType.ANVIL, lambda config: mock_vm_adapter)

        # 1. Create forensic session
        session = await engine.create_forensic_session(
            name="forensic-analysis",
            description="Comprehensive forensic analysis",
            base_block=100,
            config={"enable_detailed_tracing": True, "capture_all_state_changes": True},
        )

        assert session.id is not None
        assert session.name == "forensic-analysis"

        # 2. Apply multiple state manipulations
        manipulations = []

        for i in range(3):
            patch_data = {
                "name": f"manipulation-{i}",
                "operations": [
                    {
                        "op_type": "set",
                        "path": f"accounts.0xtest{i}.balance",
                        "value": hex(1000000 * (i + 1)),
                    }
                ],
            }

            manipulation = await engine.apply_session_manipulation(
                session.id, patch_data
            )
            manipulations.append(manipulation)

        assert len(manipulations) == 3

        # 3. Generate session report
        report = await engine.generate_session_report(session.id)

        assert report is not None
        assert "manipulations" in report
        assert len(report["manipulations"]) == 3


if __name__ == "__main__":
    # Run the test suite
    pytest.main([__file__, "-v", "--tb=short"])

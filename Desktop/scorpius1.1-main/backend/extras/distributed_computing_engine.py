"""
SCORPIUS DISTRIBUTED COMPUTING ENGINE
Advanced distributed computing system for scalable parallel processing,
distributed task execution, and high-performance blockchain operations.
"""

import asyncio
import json
import logging
import time
import hashlib
import uuid
from typing import Dict, List, Optional, Any, Callable, Union, Tuple, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal
from collections import defaultdict, deque
import multiprocessing as mp
import concurrent.futures
import pickle
import gzip
import socket
import threading
from queue import Queue, Empty
import secrets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Types of distributed tasks."""
    BLOCKCHAIN_ANALYSIS = "blockchain_analysis"
    PORTFOLIO_OPTIMIZATION = "portfolio_optimization"
    RISK_CALCULATION = "risk_calculation"
    MARKET_SIMULATION = "market_simulation"
    MACHINE_LEARNING = "machine_learning"
    DATA_PROCESSING = "data_processing"
    CRYPTOGRAPHIC = "cryptographic"
    VALIDATION = "validation"
    COMPUTATION = "computation"

class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

class TaskStatus(Enum):
    """Task execution statuses."""
    PENDING = "pending"
    QUEUED = "queued"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class NodeType(Enum):
    """Types of compute nodes."""
    COORDINATOR = "coordinator"
    WORKER = "worker"
    HYBRID = "hybrid"
    SPECIALIZED = "specialized"

class ResourceType(Enum):
    """Types of compute resources."""
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    STORAGE = "storage"
    NETWORK = "network"

@dataclass
class ComputeTask:
    """A distributed computing task."""
    id: str
    task_type: TaskType
    priority: TaskPriority
    function_name: str
    arguments: Dict[str, Any]
    requirements: Dict[ResourceType, float]
    dependencies: List[str] = field(default_factory=list)
    
    # Execution details
    status: TaskStatus = TaskStatus.PENDING
    assigned_node: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results and metadata
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    
    # Resource usage
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    
    # Security and validation
    checksum: Optional[str] = None
    signature: Optional[str] = None

@dataclass
class ComputeNode:
    """A compute node in the distributed system."""
    id: str
    node_type: NodeType
    address: str
    port: int
    
    # Capabilities
    capabilities: Set[TaskType] = field(default_factory=set)
    resources: Dict[ResourceType, float] = field(default_factory=dict)
    max_concurrent_tasks: int = 4
    
    # Status
    status: str = "active"
    last_heartbeat: datetime = field(default_factory=datetime.now)
    current_tasks: Set[str] = field(default_factory=set)
    completed_tasks: int = 0
    failed_tasks: int = 0
    
    # Performance metrics
    avg_execution_time: float = 0.0
    reliability_score: float = 1.0
    load_factor: float = 0.0

@dataclass
class ClusterStats:
    """Cluster performance statistics."""
    total_nodes: int
    active_nodes: int
    total_tasks_completed: int
    total_tasks_failed: int
    avg_task_execution_time: float
    cluster_throughput: float
    resource_utilization: Dict[ResourceType, float]
    timestamp: datetime = field(default_factory=datetime.now)

class TaskScheduler:
    """Schedules tasks across compute nodes."""
    
    def __init__(self):
        self.pending_tasks: deque = deque()
        self.running_tasks: Dict[str, ComputeTask] = {}
        self.completed_tasks: List[ComputeTask] = []
        self.failed_tasks: List[ComputeTask] = []
        
        self.scheduling_algorithms = {
            "round_robin": self._round_robin_schedule,
            "load_balanced": self._load_balanced_schedule,
            "capability_based": self._capability_based_schedule,
            "priority_based": self._priority_based_schedule
        }
        
        self.current_algorithm = "load_balanced"
        
    async def submit_task(self, task: ComputeTask) -> str:
        """Submit a task for execution."""
        # Generate checksum for task integrity
        task.checksum = self._generate_task_checksum(task)
        
        # Add to pending queue (sorted by priority)
        self.pending_tasks.append(task)
        self.pending_tasks = deque(sorted(self.pending_tasks, 
                                        key=lambda t: t.priority.value, reverse=True))
        
        task.status = TaskStatus.QUEUED
        logger.info(f"Task {task.id} submitted and queued")
        
        return task.id
        
    async def schedule_tasks(self, available_nodes: List[ComputeNode]) -> Dict[str, str]:
        """Schedule pending tasks to available nodes."""
        if not self.pending_tasks or not available_nodes:
            return {}
            
        scheduler = self.scheduling_algorithms[self.current_algorithm]
        assignments = await scheduler(list(self.pending_tasks), available_nodes)
        
        # Update task statuses
        for task_id, node_id in assignments.items():
            task = next((t for t in self.pending_tasks if t.id == task_id), None)
            if task:
                task.status = TaskStatus.ASSIGNED
                task.assigned_node = node_id
                self.running_tasks[task_id] = task
                self.pending_tasks.remove(task)
                
        return assignments
        
    async def _round_robin_schedule(self, tasks: List[ComputeTask], 
                                  nodes: List[ComputeNode]) -> Dict[str, str]:
        """Round-robin scheduling algorithm."""
        assignments = {}
        node_index = 0
        
        for task in tasks:
            if node_index >= len(nodes):
                break
                
            node = nodes[node_index]
            if self._can_assign_task(task, node):
                assignments[task.id] = node.id
                node_index = (node_index + 1) % len(nodes)
                
        return assignments
        
    async def _load_balanced_schedule(self, tasks: List[ComputeTask],
                                    nodes: List[ComputeNode]) -> Dict[str, str]:
        """Load-balanced scheduling algorithm."""
        assignments = {}
        
        # Sort nodes by current load
        sorted_nodes = sorted(nodes, key=lambda n: n.load_factor)
        
        for task in tasks:
            for node in sorted_nodes:
                if self._can_assign_task(task, node):
                    assignments[task.id] = node.id
                    # Update estimated load
                    node.load_factor += 0.1  # Temporary load increase
                    break
                    
        return assignments
        
    async def _capability_based_schedule(self, tasks: List[ComputeTask],
                                       nodes: List[ComputeNode]) -> Dict[str, str]:
        """Capability-based scheduling algorithm."""
        assignments = {}
        
        for task in tasks:
            # Find nodes with required capabilities
            capable_nodes = [n for n in nodes 
                           if task.task_type in n.capabilities and self._can_assign_task(task, n)]
            
            if capable_nodes:
                # Choose node with highest reliability
                best_node = max(capable_nodes, key=lambda n: n.reliability_score)
                assignments[task.id] = best_node.id
                
        return assignments
        
    async def _priority_based_schedule(self, tasks: List[ComputeTask],
                                     nodes: List[ComputeNode]) -> Dict[str, str]:
        """Priority-based scheduling algorithm."""
        assignments = {}
        
        # Sort tasks by priority (already done in submit_task)
        for task in tasks:
            # Find best available node
            available_nodes = [n for n in nodes if self._can_assign_task(task, n)]
            
            if available_nodes:
                if task.priority.value >= TaskPriority.HIGH.value:
                    # High priority tasks get best performing nodes
                    best_node = max(available_nodes, 
                                  key=lambda n: n.reliability_score / (n.load_factor + 0.1))
                else:
                    # Normal priority tasks use any available node
                    best_node = min(available_nodes, key=lambda n: n.load_factor)
                    
                assignments[task.id] = best_node.id
                
        return assignments
        
    def _can_assign_task(self, task: ComputeTask, node: ComputeNode) -> bool:
        """Check if a task can be assigned to a node."""
        # Check node capacity
        if len(node.current_tasks) >= node.max_concurrent_tasks:
            return False
            
        # Check capabilities
        if task.task_type not in node.capabilities:
            return False
            
        # Check resource requirements
        for resource_type, required in task.requirements.items():
            available = node.resources.get(resource_type, 0)
            if available < required:
                return False
                
        return True
        
    def _generate_task_checksum(self, task: ComputeTask) -> str:
        """Generate checksum for task integrity."""
        task_data = f"{task.function_name}:{json.dumps(task.arguments, sort_keys=True)}"
        return hashlib.sha256(task_data.encode()).hexdigest()
        
    async def mark_task_completed(self, task_id: str, result: Any, execution_time: float):
        """Mark a task as completed."""
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.execution_time = execution_time
            task.completed_at = datetime.now()
            
            self.completed_tasks.append(task)
            del self.running_tasks[task_id]
            
            logger.info(f"Task {task_id} completed in {execution_time:.2f}s")
            
    async def mark_task_failed(self, task_id: str, error: str):
        """Mark a task as failed."""
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            task.status = TaskStatus.FAILED
            task.error = error
            task.completed_at = datetime.now()
            
            # Check if task should be retried
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.RETRYING
                task.assigned_node = None
                self.pending_tasks.appendleft(task)  # High priority for retry
                logger.info(f"Task {task_id} failed, retrying ({task.retry_count}/{task.max_retries})")
            else:
                self.failed_tasks.append(task)
                logger.error(f"Task {task_id} failed permanently: {error}")
                
            del self.running_tasks[task_id]

class WorkerNode:
    """A worker node that executes distributed tasks."""
    
    def __init__(self, node_info: ComputeNode):
        self.node_info = node_info
        self.task_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=node_info.max_concurrent_tasks
        )
        self.running = False
        self.task_functions: Dict[str, Callable] = {}
        
        # Register default task functions
        self._register_default_functions()
        
    def _register_default_functions(self):
        """Register default task functions."""
        self.task_functions.update({
            "blockchain_analysis": self._blockchain_analysis_task,
            "portfolio_optimization": self._portfolio_optimization_task,
            "risk_calculation": self._risk_calculation_task,
            "market_simulation": self._market_simulation_task,
            "data_processing": self._data_processing_task,
            "cryptographic": self._cryptographic_task,
            "computation": self._computation_task
        })
        
    async def start_worker(self):
        """Start the worker node."""
        logger.info(f"Starting worker node {self.node_info.id}")
        self.running = True
        
        # Start heartbeat
        heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        await heartbeat_task
        
    async def stop_worker(self):
        """Stop the worker node."""
        logger.info(f"Stopping worker node {self.node_info.id}")
        self.running = False
        self.task_executor.shutdown(wait=True)
        
    async def execute_task(self, task: ComputeTask) -> Tuple[Any, float]:
        """Execute a task."""
        start_time = time.time()
        
        try:
            # Verify task integrity
            if not self._verify_task_integrity(task):
                raise ValueError("Task integrity check failed")
                
            # Get task function
            if task.function_name not in self.task_functions:
                raise ValueError(f"Unknown task function: {task.function_name}")
                
            function = self.task_functions[task.function_name]
            
            # Execute task in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.task_executor,
                function,
                task.arguments
            )
            
            execution_time = time.time() - start_time
            
            # Update node statistics
            self.node_info.completed_tasks += 1
            self._update_performance_metrics(execution_time)
            
            return result, execution_time
            
        except Exception as e:
            self.node_info.failed_tasks += 1
            execution_time = time.time() - start_time
            logger.error(f"Task {task.id} failed: {e}")
            raise
            
    def _verify_task_integrity(self, task: ComputeTask) -> bool:
        """Verify task integrity using checksum."""
        if not task.checksum:
            return True  # No checksum to verify
            
        task_data = f"{task.function_name}:{json.dumps(task.arguments, sort_keys=True)}"
        expected_checksum = hashlib.sha256(task_data.encode()).hexdigest()
        
        return task.checksum == expected_checksum
        
    def _update_performance_metrics(self, execution_time: float):
        """Update node performance metrics."""
        total_tasks = self.node_info.completed_tasks + self.node_info.failed_tasks
        
        if total_tasks > 0:
            # Update average execution time
            current_avg = self.node_info.avg_execution_time
            self.node_info.avg_execution_time = (
                (current_avg * (total_tasks - 1) + execution_time) / total_tasks
            )
            
            # Update reliability score
            success_rate = self.node_info.completed_tasks / total_tasks
            self.node_info.reliability_score = success_rate
            
    async def _heartbeat_loop(self):
        """Send periodic heartbeats."""
        while self.running:
            self.node_info.last_heartbeat = datetime.now()
            self.node_info.load_factor = len(self.node_info.current_tasks) / self.node_info.max_concurrent_tasks
            
            # Send heartbeat to coordinator (simulated)
            logger.debug(f"Node {self.node_info.id} heartbeat - Load: {self.node_info.load_factor:.2f}")
            
            await asyncio.sleep(30)  # Heartbeat every 30 seconds
            
    # Task function implementations
    def _blockchain_analysis_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Blockchain analysis task."""
        block_range = args.get("block_range", [1, 100])
        analysis_type = args.get("analysis_type", "transaction_volume")
        
        # Simulate blockchain analysis
        time.sleep(2)  # Simulate computation time
        
        return {
            "analysis_type": analysis_type,
            "block_range": block_range,
            "total_transactions": hash(str(block_range)) % 10000,
            "total_volume": hash(str(block_range)) % 1000000,
            "unique_addresses": hash(str(block_range)) % 5000,
            "gas_used": hash(str(block_range)) % 500000
        }
        
    def _portfolio_optimization_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Portfolio optimization task."""
        assets = args.get("assets", [])
        risk_tolerance = args.get("risk_tolerance", 0.5)
        
        # Simulate portfolio optimization
        time.sleep(3)  # Simulate computation time
        
        # Generate optimized weights
        weights = {}
        total_weight = 0
        for asset in assets:
            weight = (hash(asset) % 100) / 100.0
            weights[asset] = weight
            total_weight += weight
            
        # Normalize weights
        if total_weight > 0:
            weights = {asset: weight / total_weight for asset, weight in weights.items()}
            
        return {
            "optimized_weights": weights,
            "expected_return": 0.12 + (risk_tolerance * 0.08),
            "expected_volatility": 0.15 + (risk_tolerance * 0.10),
            "sharpe_ratio": 1.2 - (risk_tolerance * 0.5)
        }
        
    def _risk_calculation_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Risk calculation task."""
        portfolio = args.get("portfolio", {})
        confidence_level = args.get("confidence_level", 0.95)
        
        # Simulate risk calculations
        time.sleep(1)  # Simulate computation time
        
        total_value = sum(portfolio.values()) if portfolio else 100000
        
        return {
            "var_95": total_value * 0.05,  # 5% VaR
            "cvar_95": total_value * 0.08,  # 8% CVaR
            "max_drawdown": 0.15,
            "beta": 1.2,
            "correlation_matrix": {asset: hash(asset) % 100 / 100 for asset in portfolio.keys()}
        }
        
    def _market_simulation_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Market simulation task."""
        simulation_days = args.get("days", 30)
        scenarios = args.get("scenarios", 1000)
        
        # Simulate market simulation
        time.sleep(5)  # Simulate computation time
        
        # Generate simulation results
        results = []
        for i in range(min(scenarios, 100)):  # Limit for demo
            result = {
                "scenario": i,
                "final_portfolio_value": 100000 + (hash(str(i)) % 50000 - 25000),
                "max_drawdown": (hash(str(i)) % 30) / 100,
                "total_return": (hash(str(i)) % 60 - 30) / 100
            }
            results.append(result)
            
        return {
            "simulation_results": results,
            "summary": {
                "mean_return": 0.08,
                "std_return": 0.15,
                "probability_of_loss": 0.25,
                "expected_shortfall": -0.12
            }
        }
        
    def _data_processing_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Data processing task."""
        data_size = args.get("data_size", 1000)
        operation = args.get("operation", "aggregate")
        
        # Simulate data processing
        time.sleep(data_size / 1000)  # Scale with data size
        
        return {
            "operation": operation,
            "records_processed": data_size,
            "processing_time": data_size / 1000,
            "output_size": data_size // 2,
            "compression_ratio": 0.6
        }
        
    def _cryptographic_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Cryptographic task."""
        operation = args.get("operation", "hash")
        data = args.get("data", "sample_data")
        
        # Simulate cryptographic operations
        time.sleep(1)
        
        if operation == "hash":
            result = hashlib.sha256(str(data).encode()).hexdigest()
        elif operation == "sign":
            result = f"signature_{hashlib.sha256(str(data).encode()).hexdigest()[:16]}"
        else:
            result = f"crypto_result_{hash(str(data))}"
            
        return {
            "operation": operation,
            "input_data": str(data)[:100],  # Truncate for display
            "result": result,
            "algorithm": "SHA256"
        }
        
    def _computation_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """General computation task."""
        iterations = args.get("iterations", 1000000)
        computation_type = args.get("type", "fibonacci")
        
        # Simulate computation
        start_time = time.time()
        
        if computation_type == "fibonacci":
            result = self._fibonacci(min(iterations, 50))  # Limit for performance
        elif computation_type == "prime":
            result = self._count_primes(min(iterations, 100000))
        else:
            result = sum(i * i for i in range(min(iterations, 10000)))
            
        computation_time = time.time() - start_time
        
        return {
            "computation_type": computation_type,
            "iterations": iterations,
            "result": result,
            "computation_time": computation_time
        }
        
    def _fibonacci(self, n: int) -> int:
        """Calculate Fibonacci number."""
        if n <= 1:
            return n
        return self._fibonacci(n - 1) + self._fibonacci(n - 2)
        
    def _count_primes(self, limit: int) -> int:
        """Count prime numbers up to limit."""
        if limit < 2:
            return 0
            
        is_prime = [True] * (limit + 1)
        is_prime[0] = is_prime[1] = False
        
        for i in range(2, int(limit**0.5) + 1):
            if is_prime[i]:
                for j in range(i*i, limit + 1, i):
                    is_prime[j] = False
                    
        return sum(is_prime)

class DistributedComputingEngine:
    """Main distributed computing engine coordinator."""
    
    def __init__(self):
        self.nodes: Dict[str, ComputeNode] = {}
        self.worker_instances: Dict[str, WorkerNode] = {}
        self.task_scheduler = TaskScheduler()
        
        self.running = False
        self.cluster_stats = ClusterStats(
            total_nodes=0,
            active_nodes=0,
            total_tasks_completed=0,
            total_tasks_failed=0,
            avg_task_execution_time=0.0,
            cluster_throughput=0.0,
            resource_utilization={}
        )
        
    async def start_engine(self):
        """Start the distributed computing engine."""
        logger.info("Starting Distributed Computing Engine...")
        self.running = True
        
        # Start coordinator tasks
        coordinator_task = asyncio.create_task(self._coordinator_loop())
        monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        await asyncio.gather(coordinator_task, monitoring_task)
        
    async def stop_engine(self):
        """Stop the distributed computing engine."""
        logger.info("Stopping Distributed Computing Engine...")
        self.running = False
        
        # Stop all worker nodes
        for worker in self.worker_instances.values():
            await worker.stop_worker()
            
    async def add_node(self, node: ComputeNode) -> bool:
        """Add a compute node to the cluster."""
        try:
            self.nodes[node.id] = node
            
            # Create worker instance for worker/hybrid nodes
            if node.node_type in [NodeType.WORKER, NodeType.HYBRID]:
                worker = WorkerNode(node)
                self.worker_instances[node.id] = worker
                
                # Start worker
                asyncio.create_task(worker.start_worker())
                
            self.cluster_stats.total_nodes += 1
            if node.status == "active":
                self.cluster_stats.active_nodes += 1
                
            logger.info(f"Node {node.id} added to cluster")
            return True
            
        except Exception as e:
            logger.error(f"Error adding node {node.id}: {e}")
            return False
            
    async def remove_node(self, node_id: str) -> bool:
        """Remove a compute node from the cluster."""
        try:
            if node_id in self.nodes:
                # Stop worker if exists
                if node_id in self.worker_instances:
                    await self.worker_instances[node_id].stop_worker()
                    del self.worker_instances[node_id]
                    
                # Reassign tasks from this node
                await self._reassign_node_tasks(node_id)
                
                del self.nodes[node_id]
                self.cluster_stats.total_nodes -= 1
                
                logger.info(f"Node {node_id} removed from cluster")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error removing node {node_id}: {e}")
            return False
            
    async def submit_task(self, task_type: TaskType, function_name: str, 
                         arguments: Dict[str, Any], priority: TaskPriority = TaskPriority.NORMAL,
                         requirements: Optional[Dict[ResourceType, float]] = None) -> str:
        """Submit a task for distributed execution."""
        task = ComputeTask(
            id=f"task_{uuid.uuid4().hex[:8]}",
            task_type=task_type,
            priority=priority,
            function_name=function_name,
            arguments=arguments,
            requirements=requirements or {ResourceType.CPU: 1.0, ResourceType.MEMORY: 512.0}
        )
        
        return await self.task_scheduler.submit_task(task)
        
    async def get_task_result(self, task_id: str) -> Optional[ComputeTask]:
        """Get the result of a completed task."""
        # Check running tasks
        if task_id in self.task_scheduler.running_tasks:
            return self.task_scheduler.running_tasks[task_id]
            
        # Check completed tasks
        for task in self.task_scheduler.completed_tasks:
            if task.id == task_id:
                return task
                
        # Check failed tasks
        for task in self.task_scheduler.failed_tasks:
            if task.id == task_id:
                return task
                
        return None
        
    async def _coordinator_loop(self):
        """Main coordinator loop for task scheduling."""
        while self.running:
            try:
                # Get available nodes
                available_nodes = [
                    node for node in self.nodes.values()
                    if node.status == "active" and len(node.current_tasks) < node.max_concurrent_tasks
                ]
                
                if available_nodes and self.task_scheduler.pending_tasks:
                    # Schedule tasks
                    assignments = await self.task_scheduler.schedule_tasks(available_nodes)
                    
                    # Execute assigned tasks
                    for task_id, node_id in assignments.items():
                        asyncio.create_task(self._execute_task_on_node(task_id, node_id))
                        
                await asyncio.sleep(5)  # Schedule every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in coordinator loop: {e}")
                await asyncio.sleep(10)
                
    async def _execute_task_on_node(self, task_id: str, node_id: str):
        """Execute a task on a specific node."""
        try:
            task = self.task_scheduler.running_tasks.get(task_id)
            node = self.nodes.get(node_id)
            worker = self.worker_instances.get(node_id)
            
            if not all([task, node, worker]):
                logger.error(f"Missing components for task {task_id} on node {node_id}")
                return
                
            # Update task and node status
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            node.current_tasks.add(task_id)
            
            # Execute task
            result, execution_time = await worker.execute_task(task)
            
            # Mark task as completed
            await self.task_scheduler.mark_task_completed(task_id, result, execution_time)
            
            # Update cluster stats
            self.cluster_stats.total_tasks_completed += 1
            self._update_cluster_stats(execution_time)
            
        except Exception as e:
            # Mark task as failed
            await self.task_scheduler.mark_task_failed(task_id, str(e))
            self.cluster_stats.total_tasks_failed += 1
            
        finally:
            # Clean up node state
            if node_id in self.nodes:
                self.nodes[node_id].current_tasks.discard(task_id)
                
    async def _monitoring_loop(self):
        """Monitor cluster health and performance."""
        while self.running:
            try:
                # Update node statuses
                current_time = datetime.now()
                
                for node in self.nodes.values():
                    # Check if node is responsive (heartbeat within last 2 minutes)
                    if current_time - node.last_heartbeat > timedelta(minutes=2):
                        if node.status == "active":
                            node.status = "unresponsive"
                            self.cluster_stats.active_nodes -= 1
                            logger.warning(f"Node {node.id} marked as unresponsive")
                    else:
                        if node.status == "unresponsive":
                            node.status = "active"
                            self.cluster_stats.active_nodes += 1
                            logger.info(f"Node {node.id} back online")
                            
                # Update cluster statistics
                await self._calculate_cluster_stats()
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(120)
                
    async def _calculate_cluster_stats(self):
        """Calculate cluster performance statistics."""
        # Calculate average execution time
        completed_tasks = self.task_scheduler.completed_tasks
        if completed_tasks:
            total_time = sum(task.execution_time or 0 for task in completed_tasks)
            self.cluster_stats.avg_task_execution_time = total_time / len(completed_tasks)
            
        # Calculate throughput (tasks per minute)
        recent_tasks = [
            task for task in completed_tasks
            if task.completed_at and 
            datetime.now() - task.completed_at < timedelta(minutes=10)
        ]
        
        self.cluster_stats.cluster_throughput = len(recent_tasks) / 10.0  # per minute
        
        # Calculate resource utilization
        if self.nodes:
            total_resources = defaultdict(float)
            used_resources = defaultdict(float)
            
            for node in self.nodes.values():
                if node.status == "active":
                    for resource_type, capacity in node.resources.items():
                        total_resources[resource_type] += capacity
                        used_resources[resource_type] += capacity * node.load_factor
                        
            self.cluster_stats.resource_utilization = {
                resource_type: used_resources[resource_type] / total_resources[resource_type]
                if total_resources[resource_type] > 0 else 0.0
                for resource_type in total_resources.keys()
            }
            
    def _update_cluster_stats(self, execution_time: float):
        """Update cluster statistics with new task completion."""
        # Update rolling average execution time
        current_avg = self.cluster_stats.avg_task_execution_time
        total_completed = self.cluster_stats.total_tasks_completed
        
        if total_completed > 0:
            self.cluster_stats.avg_task_execution_time = (
                (current_avg * (total_completed - 1) + execution_time) / total_completed
            )
            
    async def _reassign_node_tasks(self, node_id: str):
        """Reassign tasks from a failed node."""
        # Find tasks assigned to this node
        tasks_to_reassign = [
            task for task in self.task_scheduler.running_tasks.values()
            if task.assigned_node == node_id
        ]
        
        # Move tasks back to pending queue
        for task in tasks_to_reassign:
            task.status = TaskStatus.PENDING
            task.assigned_node = None
            task.retry_count += 1
            
            if task.retry_count <= task.max_retries:
                self.task_scheduler.pending_tasks.appendleft(task)
                del self.task_scheduler.running_tasks[task.id]
                logger.info(f"Task {task.id} reassigned due to node {node_id} failure")
            else:
                await self.task_scheduler.mark_task_failed(task.id, f"Node {node_id} failed")
                
    async def get_cluster_status(self) -> Dict[str, Any]:
        """Get current cluster status."""
        return {
            "cluster_stats": asdict(self.cluster_stats),
            "nodes": {
                node_id: {
                    "status": node.status,
                    "load_factor": node.load_factor,
                    "current_tasks": len(node.current_tasks),
                    "completed_tasks": node.completed_tasks,
                    "failed_tasks": node.failed_tasks,
                    "reliability_score": node.reliability_score
                }
                for node_id, node in self.nodes.items()
            },
            "task_queue": {
                "pending": len(self.task_scheduler.pending_tasks),
                "running": len(self.task_scheduler.running_tasks),
                "completed": len(self.task_scheduler.completed_tasks),
                "failed": len(self.task_scheduler.failed_tasks)
            },
            "timestamp": datetime.now().isoformat()
        }

# Global computing engine instance
_computing_engine_instance: Optional[DistributedComputingEngine] = None

async def initialize_computing_engine() -> DistributedComputingEngine:
    """Initialize the distributed computing engine."""
    global _computing_engine_instance
    
    if _computing_engine_instance is None:
        _computing_engine_instance = DistributedComputingEngine()
        
        # Add default nodes
        await _add_default_nodes(_computing_engine_instance)
        
        logger.info("Distributed Computing Engine initialized successfully")
        
    return _computing_engine_instance

async def _add_default_nodes(engine: DistributedComputingEngine):
    """Add default compute nodes."""
    # Add coordinator node
    coordinator = ComputeNode(
        id="coordinator_1",
        node_type=NodeType.COORDINATOR,
        address="localhost",
        port=8080,
        capabilities=set(TaskType),
        resources={
            ResourceType.CPU: 8.0,
            ResourceType.MEMORY: 16384.0,
            ResourceType.STORAGE: 1000.0
        },
        max_concurrent_tasks=8
    )
    await engine.add_node(coordinator)
    
    # Add worker nodes
    for i in range(2, 5):  # 3 worker nodes
        worker = ComputeNode(
            id=f"worker_{i}",
            node_type=NodeType.WORKER,
            address="localhost",
            port=8080 + i,
            capabilities={
                TaskType.BLOCKCHAIN_ANALYSIS,
                TaskType.PORTFOLIO_OPTIMIZATION,
                TaskType.RISK_CALCULATION,
                TaskType.DATA_PROCESSING,
                TaskType.COMPUTATION
            },
            resources={
                ResourceType.CPU: 4.0,
                ResourceType.MEMORY: 8192.0,
                ResourceType.STORAGE: 500.0
            },
            max_concurrent_tasks=4
        )
        await engine.add_node(worker)

def get_computing_engine_instance() -> Optional[DistributedComputingEngine]:
    """Get the current computing engine instance."""
    return _computing_engine_instance

async def start_computing_engine():
    """Start the distributed computing engine."""
    engine = await initialize_computing_engine()
    await engine.start_engine()

async def stop_computing_engine():
    """Stop the distributed computing engine."""
    global _computing_engine_instance
    if _computing_engine_instance:
        await _computing_engine_instance.stop_engine()
        _computing_engine_instance = None

if __name__ == "__main__":
    # Example usage
    async def main():
        engine = await initialize_computing_engine()
        
        # Submit sample tasks
        task_id_1 = await engine.submit_task(
            TaskType.BLOCKCHAIN_ANALYSIS,
            "blockchain_analysis",
            {"block_range": [1000, 2000], "analysis_type": "gas_usage"},
            TaskPriority.HIGH
        )
        
        task_id_2 = await engine.submit_task(
            TaskType.PORTFOLIO_OPTIMIZATION,
            "portfolio_optimization",
            {"assets": ["BTC", "ETH", "ADA"], "risk_tolerance": 0.6},
            TaskPriority.NORMAL
        )
        
        print(f"Submitted tasks: {task_id_1}, {task_id_2}")
        
        # Start the engine
        await engine.start_engine()

    asyncio.run(main())

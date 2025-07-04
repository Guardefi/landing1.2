"""
SCORPIUS ADVANCED MONITORING DASHBOARD
Enterprise-grade real-time monitoring, observability, and alerting system.
Provides comprehensive insights into system health, performance, and security.
"""

import asyncio
import json
import logging
import time
import psutil
import aiohttp
import websockets
from typing import Dict, List, Optional, Any, Callable, Union, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import statistics
from collections import defaultdict, deque
import numpy as np
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of monitoring metrics."""
    COUNTER = "counter"
    GAUGE = "gauge" 
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"
    PERCENTAGE = "percentage"

class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class DashboardComponent(Enum):
    """Dashboard component types."""
    METRICS_OVERVIEW = "metrics_overview"
    SYSTEM_HEALTH = "system_health"
    SECURITY_STATUS = "security_status"
    PERFORMANCE_CHARTS = "performance_charts"
    ALERT_MANAGEMENT = "alert_management"
    REAL_TIME_LOGS = "real_time_logs"
    NETWORK_TOPOLOGY = "network_topology"
    BLOCKCHAIN_MONITORING = "blockchain_monitoring"

@dataclass
class Metric:
    """A monitoring metric."""
    name: str
    value: Union[float, int]
    metric_type: MetricType
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    unit: Optional[str] = None
    description: Optional[str] = None

@dataclass
class Alert:
    """A monitoring alert."""
    id: str
    title: str
    description: str
    severity: AlertSeverity
    timestamp: datetime
    source: str
    tags: Set[str] = field(default_factory=set)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SystemResource:
    """System resource information."""
    cpu_percent: float
    memory_percent: float
    disk_usage: Dict[str, float]
    network_io: Dict[str, int]
    process_count: int
    uptime: float
    load_average: List[float]
    timestamp: datetime

class MetricsCollector:
    """Collects and manages system metrics."""
    
    def __init__(self):
        self.metrics: Dict[str, List[Metric]] = defaultdict(list)
        self.max_metrics_per_type = 1000
        self.registry = CollectorRegistry()
        self.counters: Dict[str, Counter] = {}
        self.gauges: Dict[str, Gauge] = {}
        self.histograms: Dict[str, Histogram] = {}
        
    def add_metric(self, metric: Metric):
        """Add a new metric."""
        metric_list = self.metrics[metric.name]
        metric_list.append(metric)
        
        # Keep only recent metrics
        if len(metric_list) > self.max_metrics_per_type:
            metric_list.pop(0)
            
        # Update Prometheus metrics
        self._update_prometheus_metric(metric)
        
    def _update_prometheus_metric(self, metric: Metric):
        """Update Prometheus metric."""
        labels = list(metric.labels.keys())
        label_values = list(metric.labels.values())
        
        if metric.metric_type == MetricType.COUNTER:
            if metric.name not in self.counters:
                self.counters[metric.name] = Counter(
                    metric.name, metric.description or metric.name, 
                    labels, registry=self.registry
                )
            self.counters[metric.name].labels(*label_values).inc(metric.value)
            
        elif metric.metric_type == MetricType.GAUGE:
            if metric.name not in self.gauges:
                self.gauges[metric.name] = Gauge(
                    metric.name, metric.description or metric.name,
                    labels, registry=self.registry
                )
            self.gauges[metric.name].labels(*label_values).set(metric.value)
            
        elif metric.metric_type == MetricType.HISTOGRAM:
            if metric.name not in self.histograms:
                self.histograms[metric.name] = Histogram(
                    metric.name, metric.description or metric.name,
                    labels, registry=self.registry
                )
            self.histograms[metric.name].labels(*label_values).observe(metric.value)
    
    def get_metrics(self, name: str, limit: int = 100) -> List[Metric]:
        """Get metrics by name."""
        return self.metrics[name][-limit:]
    
    def get_prometheus_metrics(self) -> str:
        """Get Prometheus formatted metrics."""
        return generate_latest(self.registry).decode('utf-8')

class AlertManager:
    """Manages alerts and notifications."""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules: List[Callable] = []
        self.notification_channels: List[Callable] = []
        
    def add_alert_rule(self, rule: Callable):
        """Add an alert rule."""
        self.alert_rules.append(rule)
        
    def add_notification_channel(self, channel: Callable):
        """Add a notification channel."""
        self.notification_channels.append(channel)
        
    async def create_alert(self, alert: Alert):
        """Create a new alert."""
        self.alerts[alert.id] = alert
        
        # Send notifications
        for channel in self.notification_channels:
            try:
                await channel(alert)
            except Exception as e:
                logger.error(f"Failed to send alert notification: {e}")
                
    async def resolve_alert(self, alert_id: str):
        """Resolve an alert."""
        if alert_id in self.alerts:
            self.alerts[alert_id].resolved = True
            self.alerts[alert_id].resolved_at = datetime.now()
            
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        return [alert for alert in self.alerts.values() if not alert.resolved]
    
    async def evaluate_rules(self, metrics: Dict[str, List[Metric]]):
        """Evaluate alert rules against current metrics."""
        for rule in self.alert_rules:
            try:
                alerts = await rule(metrics)
                if alerts:
                    for alert in alerts:
                        await self.create_alert(alert)
            except Exception as e:
                logger.error(f"Error evaluating alert rule: {e}")

class SystemMonitor:
    """Monitors system resources and health."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.running = False
        
    async def start_monitoring(self):
        """Start system monitoring."""
        self.running = True
        while self.running:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(10)  # Collect every 10 seconds
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                await asyncio.sleep(30)
                
    def stop_monitoring(self):
        """Stop system monitoring."""
        self.running = False
        
    async def _collect_system_metrics(self):
        """Collect system resource metrics."""
        timestamp = datetime.now()
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        self.metrics_collector.add_metric(Metric(
            name="system_cpu_percent",
            value=cpu_percent,
            metric_type=MetricType.GAUGE,
            timestamp=timestamp,
            unit="percent",
            description="CPU usage percentage"
        ))
        
        # Memory metrics
        memory = psutil.virtual_memory()
        self.metrics_collector.add_metric(Metric(
            name="system_memory_percent",
            value=memory.percent,
            metric_type=MetricType.GAUGE,
            timestamp=timestamp,
            unit="percent",
            description="Memory usage percentage"
        ))
        
        self.metrics_collector.add_metric(Metric(
            name="system_memory_available",
            value=memory.available,
            metric_type=MetricType.GAUGE,
            timestamp=timestamp,
            unit="bytes",
            description="Available memory in bytes"
        ))
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        self.metrics_collector.add_metric(Metric(
            name="system_disk_percent",
            value=disk.percent,
            metric_type=MetricType.GAUGE,
            timestamp=timestamp,
            unit="percent",
            description="Disk usage percentage"
        ))
        
        # Network metrics
        network = psutil.net_io_counters()
        self.metrics_collector.add_metric(Metric(
            name="system_network_bytes_sent",
            value=network.bytes_sent,
            metric_type=MetricType.COUNTER,
            timestamp=timestamp,
            unit="bytes",
            description="Network bytes sent"
        ))
        
        self.metrics_collector.add_metric(Metric(
            name="system_network_bytes_recv",
            value=network.bytes_recv,
            metric_type=MetricType.COUNTER,
            timestamp=timestamp,
            unit="bytes",
            description="Network bytes received"
        ))

class AdvancedMonitoringDashboard:
    """Main advanced monitoring dashboard system."""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.system_monitor = SystemMonitor(self.metrics_collector)
        self.websocket_clients: Set[websockets.WebSocketServerProtocol] = set()
        self.dashboard_data: Dict[str, Any] = {}
        self.running = False
        
        # Setup default alert rules
        self._setup_default_alert_rules()
        
    def _setup_default_alert_rules(self):
        """Setup default alert rules."""
        
        async def high_cpu_rule(metrics: Dict[str, List[Metric]]) -> List[Alert]:
            """Alert for high CPU usage."""
            alerts = []
            cpu_metrics = metrics.get("system_cpu_percent", [])
            if cpu_metrics and cpu_metrics[-1].value > 90:
                alerts.append(Alert(
                    id=f"high_cpu_{int(time.time())}",
                    title="High CPU Usage",
                    description=f"CPU usage is {cpu_metrics[-1].value:.1f}%",
                    severity=AlertSeverity.WARNING,
                    timestamp=datetime.now(),
                    source="system_monitor",
                    tags={"cpu", "performance"}
                ))
            return alerts
            
        async def high_memory_rule(metrics: Dict[str, List[Metric]]) -> List[Alert]:
            """Alert for high memory usage."""
            alerts = []
            memory_metrics = metrics.get("system_memory_percent", [])
            if memory_metrics and memory_metrics[-1].value > 85:
                alerts.append(Alert(
                    id=f"high_memory_{int(time.time())}",
                    title="High Memory Usage",
                    description=f"Memory usage is {memory_metrics[-1].value:.1f}%",
                    severity=AlertSeverity.WARNING,
                    timestamp=datetime.now(),
                    source="system_monitor",
                    tags={"memory", "performance"}
                ))
            return alerts
            
        self.alert_manager.add_alert_rule(high_cpu_rule)
        self.alert_manager.add_alert_rule(high_memory_rule)
        
    async def start(self):
        """Start the monitoring dashboard."""
        logger.info("Starting Advanced Monitoring Dashboard...")
        self.running = True
        
        # Start system monitoring
        monitor_task = asyncio.create_task(self.system_monitor.start_monitoring())
        
        # Start dashboard update loop
        dashboard_task = asyncio.create_task(self._dashboard_update_loop())
        
        # Start alert evaluation loop
        alert_task = asyncio.create_task(self._alert_evaluation_loop())
        
        await asyncio.gather(monitor_task, dashboard_task, alert_task)
        
    async def stop(self):
        """Stop the monitoring dashboard."""
        logger.info("Stopping Advanced Monitoring Dashboard...")
        self.running = False
        self.system_monitor.stop_monitoring()
        
    async def _dashboard_update_loop(self):
        """Update dashboard data continuously."""
        while self.running:
            try:
                await self._update_dashboard_data()
                await self._broadcast_dashboard_data()
                await asyncio.sleep(5)  # Update every 5 seconds
            except Exception as e:
                logger.error(f"Error updating dashboard: {e}")
                await asyncio.sleep(10)
                
    async def _alert_evaluation_loop(self):
        """Evaluate alerts continuously."""
        while self.running:
            try:
                await self.alert_manager.evaluate_rules(self.metrics_collector.metrics)
                await asyncio.sleep(30)  # Evaluate every 30 seconds
            except Exception as e:
                logger.error(f"Error evaluating alerts: {e}")
                await asyncio.sleep(60)
                
    async def _update_dashboard_data(self):
        """Update dashboard data."""
        current_time = datetime.now()
        
        # Get recent metrics
        recent_metrics = {}
        for metric_name, metric_list in self.metrics_collector.metrics.items():
            if metric_list:
                recent_metrics[metric_name] = metric_list[-10:]  # Last 10 values
                
        # Get active alerts
        active_alerts = self.alert_manager.get_active_alerts()
        
        # Calculate system health score
        health_score = await self._calculate_health_score()
        
        self.dashboard_data = {
            "timestamp": current_time.isoformat(),
            "metrics": {
                name: [asdict(m) for m in metrics] 
                for name, metrics in recent_metrics.items()
            },
            "alerts": [asdict(alert) for alert in active_alerts],
            "health_score": health_score,
            "system_status": self._get_system_status(),
            "performance_summary": self._get_performance_summary(recent_metrics)
        }
        
    async def _calculate_health_score(self) -> float:
        """Calculate overall system health score (0-100)."""
        score = 100.0
        
        # Check CPU usage
        cpu_metrics = self.metrics_collector.get_metrics("system_cpu_percent", 5)
        if cpu_metrics:
            avg_cpu = sum(m.value for m in cpu_metrics) / len(cpu_metrics)
            if avg_cpu > 80:
                score -= 20
            elif avg_cpu > 60:
                score -= 10
                
        # Check memory usage
        memory_metrics = self.metrics_collector.get_metrics("system_memory_percent", 5)
        if memory_metrics:
            avg_memory = sum(m.value for m in memory_metrics) / len(memory_metrics)
            if avg_memory > 85:
                score -= 25
            elif avg_memory > 70:
                score -= 15
                
        # Check active alerts
        active_alerts = self.alert_manager.get_active_alerts()
        critical_alerts = [a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]
        warning_alerts = [a for a in active_alerts if a.severity == AlertSeverity.WARNING]
        
        score -= len(critical_alerts) * 15
        score -= len(warning_alerts) * 5
        
        return max(0.0, score)
        
    def _get_system_status(self) -> str:
        """Get overall system status."""
        health_score = self.dashboard_data.get("health_score", 0)
        
        if health_score >= 90:
            return "excellent"
        elif health_score >= 80:
            return "good"
        elif health_score >= 70:
            return "warning"
        elif health_score >= 50:
            return "degraded"
        else:
            return "critical"
            
    def _get_performance_summary(self, metrics: Dict[str, List[Metric]]) -> Dict[str, Any]:
        """Get performance summary."""
        summary = {}
        
        # CPU summary
        cpu_metrics = metrics.get("system_cpu_percent", [])
        if cpu_metrics:
            cpu_values = [m.value for m in cpu_metrics]
            summary["cpu"] = {
                "current": cpu_values[-1] if cpu_values else 0,
                "average": statistics.mean(cpu_values),
                "max": max(cpu_values),
                "trend": "increasing" if len(cpu_values) > 1 and cpu_values[-1] > cpu_values[0] else "stable"
            }
            
        # Memory summary
        memory_metrics = metrics.get("system_memory_percent", [])
        if memory_metrics:
            memory_values = [m.value for m in memory_metrics]
            summary["memory"] = {
                "current": memory_values[-1] if memory_values else 0,
                "average": statistics.mean(memory_values),
                "max": max(memory_values),
                "trend": "increasing" if len(memory_values) > 1 and memory_values[-1] > memory_values[0] else "stable"
            }
            
        return summary
        
    async def _broadcast_dashboard_data(self):
        """Broadcast dashboard data to connected WebSocket clients."""
        if self.websocket_clients and self.dashboard_data:
            message = json.dumps(self.dashboard_data)
            disconnected_clients = set()
            
            for client in self.websocket_clients:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected_clients.add(client)
                except Exception as e:
                    logger.error(f"Error sending data to WebSocket client: {e}")
                    disconnected_clients.add(client)
                    
            # Remove disconnected clients
            self.websocket_clients -= disconnected_clients
            
    async def add_websocket_client(self, websocket: websockets.WebSocketServerProtocol):
        """Add a WebSocket client for real-time updates."""
        self.websocket_clients.add(websocket)
        
        # Send current dashboard data immediately
        if self.dashboard_data:
            await websocket.send(json.dumps(self.dashboard_data))
            
    def remove_websocket_client(self, websocket: websockets.WebSocketServerProtocol):
        """Remove a WebSocket client."""
        self.websocket_clients.discard(websocket)
        
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data."""
        return self.dashboard_data
        
    async def get_metrics_export(self, format_type: str = "prometheus") -> str:
        """Export metrics in specified format."""
        if format_type == "prometheus":
            return self.metrics_collector.get_prometheus_metrics()
        elif format_type == "json":
            return json.dumps({
                name: [asdict(m) for m in metrics]
                for name, metrics in self.metrics_collector.metrics.items()
            })
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
            
    async def create_custom_alert(self, alert_data: Dict[str, Any]) -> str:
        """Create a custom alert."""
        alert = Alert(
            id=alert_data.get("id", f"custom_{int(time.time())}"),
            title=alert_data["title"],
            description=alert_data["description"],
            severity=AlertSeverity(alert_data.get("severity", "info")),
            timestamp=datetime.now(),
            source=alert_data.get("source", "custom"),
            tags=set(alert_data.get("tags", [])),
            metadata=alert_data.get("metadata", {})
        )
        
        await self.alert_manager.create_alert(alert)
        return alert.id
        
    async def add_custom_metric(self, metric_data: Dict[str, Any]):
        """Add a custom metric."""
        metric = Metric(
            name=metric_data["name"],
            value=metric_data["value"],
            metric_type=MetricType(metric_data.get("type", "gauge")),
            timestamp=datetime.now(),
            labels=metric_data.get("labels", {}),
            unit=metric_data.get("unit"),
            description=metric_data.get("description")
        )
        
        self.metrics_collector.add_metric(metric)

# Global dashboard instance
_dashboard_instance: Optional[AdvancedMonitoringDashboard] = None

async def initialize_monitoring_dashboard() -> AdvancedMonitoringDashboard:
    """Initialize the advanced monitoring dashboard."""
    global _dashboard_instance
    
    if _dashboard_instance is None:
        _dashboard_instance = AdvancedMonitoringDashboard()
        logger.info("Advanced Monitoring Dashboard initialized successfully")
        
    return _dashboard_instance

def get_dashboard_instance() -> Optional[AdvancedMonitoringDashboard]:
    """Get the current dashboard instance."""
    return _dashboard_instance

async def start_monitoring_dashboard():
    """Start the monitoring dashboard."""
    dashboard = await initialize_monitoring_dashboard()
    await dashboard.start()

async def stop_monitoring_dashboard():
    """Stop the monitoring dashboard."""
    global _dashboard_instance
    if _dashboard_instance:
        await _dashboard_instance.stop()
        _dashboard_instance = None

if __name__ == "__main__":
    # Example usage
    async def main():
        dashboard = await initialize_monitoring_dashboard()
        
        # Start monitoring
        await dashboard.start()

    asyncio.run(main())

#!/usr/bin/env python3
"""
Scorpius Enterprise Platform - Cost Optimization Engine
Provides automated cost analysis, optimization recommendations, and budget management.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

import aiohttp
# import asyncpg  # Commented out for now - will be added when asyncpg is available

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OptimizationType(Enum):
    CPU_DOWNSIZE = "cpu_downsize"
    MEMORY_DOWNSIZE = "memory_downsize"
    INSTANCE_DOWNSIZE = "instance_downsize"
    SPOT_INSTANCE = "spot_instance"
    STORAGE_OPTIMIZE = "storage_optimize"
    IDLE_REMOVAL = "idle_removal"
    SCHEDULE_OPTIMIZE = "schedule_optimize"

@dataclass
class CostMetric:
    """Cost metric data structure"""
    namespace: str
    pod: str
    resource_type: str
    current_cost: float
    projected_cost: float
    efficiency: float
    timestamp: datetime

@dataclass
class OptimizationRecommendation:
    """Cost optimization recommendation"""
    resource_id: str
    resource_type: str
    optimization_type: OptimizationType
    current_cost: float
    projected_savings: float
    implementation_difficulty: str  # low, medium, high
    risk_level: str  # low, medium, high
    description: str
    implementation_steps: List[str]
    estimated_implementation_time: str

@dataclass
class BudgetAlert:
    """Budget alert configuration"""
    budget_name: str
    current_spend: float
    budget_limit: float
    threshold_percentage: float
    period: str  # daily, weekly, monthly
    alert_level: str  # info, warning, critical

class CostOptimizationEngine:
    """Main cost optimization engine"""
    
    def __init__(self):
        self.prometheus_url = os.getenv("PROMETHEUS_URL", "http://prometheus-server.monitoring.svc.cluster.local:80")
        self.opencost_url = os.getenv("OPENCOST_URL", "http://opencost.opencost.svc.cluster.local:9003")
        self.database_url = os.getenv("DATABASE_URL", "postgresql://scorpius:password@postgres:5432/scorpius")
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
        
        # Optimization thresholds
        self.cpu_efficiency_threshold = 0.7
        self.memory_efficiency_threshold = 0.8
        self.idle_threshold_hours = 24
        self.cost_anomaly_threshold = 1.2
        
        # Budget configurations
        self.daily_budget = float(os.getenv("DAILY_BUDGET", "1500"))
        self.monthly_budget = float(os.getenv("MONTHLY_BUDGET", "45000"))
        
    async def initialize(self):
        """Initialize the cost optimization engine"""
        logger.info("Initializing Cost Optimization Engine")
        
        # Initialize database connection (placeholder for now)
        # self.db_pool = await asyncpg.create_pool(self.database_url)
        
        # Create tables if they don't exist
        # await self._create_tables()
        
        logger.info("Cost Optimization Engine initialized successfully")
    
    async def _create_tables(self):
        """Create necessary database tables"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS cost_metrics (
                    id SERIAL PRIMARY KEY,
                    namespace VARCHAR(255) NOT NULL,
                    pod VARCHAR(255) NOT NULL,
                    resource_type VARCHAR(100) NOT NULL,
                    current_cost DECIMAL(10,2) NOT NULL,
                    projected_cost DECIMAL(10,2) NOT NULL,
                    efficiency DECIMAL(5,4) NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                
                CREATE TABLE IF NOT EXISTS optimization_recommendations (
                    id SERIAL PRIMARY KEY,
                    resource_id VARCHAR(255) NOT NULL,
                    resource_type VARCHAR(100) NOT NULL,
                    optimization_type VARCHAR(100) NOT NULL,
                    current_cost DECIMAL(10,2) NOT NULL,
                    projected_savings DECIMAL(10,2) NOT NULL,
                    implementation_difficulty VARCHAR(50) NOT NULL,
                    risk_level VARCHAR(50) NOT NULL,
                    description TEXT NOT NULL,
                    implementation_steps JSONB NOT NULL,
                    estimated_implementation_time VARCHAR(100) NOT NULL,
                    status VARCHAR(50) DEFAULT 'pending',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                
                CREATE TABLE IF NOT EXISTS budget_alerts (
                    id SERIAL PRIMARY KEY,
                    budget_name VARCHAR(255) NOT NULL,
                    current_spend DECIMAL(10,2) NOT NULL,
                    budget_limit DECIMAL(10,2) NOT NULL,
                    threshold_percentage DECIMAL(5,2) NOT NULL,
                    period VARCHAR(50) NOT NULL,
                    alert_level VARCHAR(50) NOT NULL,
                    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                
                CREATE INDEX IF NOT EXISTS idx_cost_metrics_timestamp ON cost_metrics(timestamp);
                CREATE INDEX IF NOT EXISTS idx_optimization_recommendations_status ON optimization_recommendations(status);
                CREATE INDEX IF NOT EXISTS idx_budget_alerts_sent_at ON budget_alerts(sent_at);
            """)
    
    async def collect_metrics(self) -> List[CostMetric]:
        """Collect cost metrics from Prometheus and OpenCost"""
        logger.info("Collecting cost metrics")
        
        metrics = []
        
        try:
            # Query Prometheus for resource utilization
            async with aiohttp.ClientSession() as session:
                # CPU utilization by pod
                cpu_query = 'avg by (namespace, pod) (rate(container_cpu_usage_seconds_total[5m]))'
                cpu_metrics = await self._query_prometheus(session, cpu_query)
                
                # Memory utilization by pod
                memory_query = 'avg by (namespace, pod) (container_memory_working_set_bytes)'
                memory_metrics = await self._query_prometheus(session, memory_query)
                
                # Cost data from OpenCost
                cost_data = await self._query_opencost(session)
                
                # Combine metrics
                metrics = await self._combine_metrics(cpu_metrics, memory_metrics, cost_data)
                
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            
        return metrics
    
    async def _query_prometheus(self, session: aiohttp.ClientSession, query: str) -> Dict:
        """Query Prometheus API"""
        url = f"{self.prometheus_url}/api/v1/query"
        params = {"query": query}
        
        async with session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                logger.error(f"Prometheus query failed: {response.status}")
                return {}
    
    async def _query_opencost(self, session: aiohttp.ClientSession) -> Dict:
        """Query OpenCost API for cost data"""
        url = f"{self.opencost_url}/model/allocation"
        params = {
            "window": "1d",
            "aggregate": "namespace,pod",
            "accumulate": "false"
        }
        
        async with session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                logger.error(f"OpenCost query failed: {response.status}")
                return {}
    
    async def _combine_metrics(self, cpu_data: Dict, memory_data: Dict, cost_data: Dict) -> List[CostMetric]:
        """Combine CPU, memory, and cost data into unified metrics"""
        metrics = []
        
        # Process cost data and combine with utilization
        if 'data' in cost_data:
            for allocation in cost_data['data']:
                namespace = allocation.get('namespace', 'unknown')
                pod = allocation.get('pod', 'unknown')
                
                # Calculate efficiency scores
                cpu_efficiency = self._calculate_cpu_efficiency(cpu_data, namespace, pod)
                memory_efficiency = self._calculate_memory_efficiency(memory_data, namespace, pod)
                
                # Overall efficiency (weighted average)
                overall_efficiency = (cpu_efficiency * 0.6) + (memory_efficiency * 0.4)
                
                # Current and projected costs
                current_cost = allocation.get('totalCost', 0)
                projected_cost = current_cost * overall_efficiency
                
                metric = CostMetric(
                    namespace=namespace,
                    pod=pod,
                    resource_type='compute',
                    current_cost=current_cost,
                    projected_cost=projected_cost,
                    efficiency=overall_efficiency,
                    timestamp=datetime.utcnow()
                )
                
                metrics.append(metric)
        
        return metrics
    
    def _calculate_cpu_efficiency(self, cpu_data: Dict, namespace: str, pod: str) -> float:
        """Calculate CPU efficiency for a specific pod"""
        if 'data' not in cpu_data or 'result' not in cpu_data['data']:
            return 0.7  # Default efficiency
        
        for result in cpu_data['data']['result']:
            metric = result.get('metric', {})
            if metric.get('namespace') == namespace and metric.get('pod') == pod:
                # Calculate efficiency based on usage vs allocation
                usage = float(result['value'][1])
                # Assuming 1 CPU core allocated (would need allocation data)
                allocated = 1.0
                return min(usage / allocated, 1.0) if allocated > 0 else 0.0
        
        return 0.7  # Default efficiency
    
    def _calculate_memory_efficiency(self, memory_data: Dict, namespace: str, pod: str) -> float:
        """Calculate memory efficiency for a specific pod"""
        if 'data' not in memory_data or 'result' not in memory_data['data']:
            return 0.8  # Default efficiency
        
        for result in memory_data['data']['result']:
            metric = result.get('metric', {})
            if metric.get('namespace') == namespace and metric.get('pod') == pod:
                # Calculate efficiency based on usage vs allocation
                usage = float(result['value'][1])
                # Assuming 2GB allocated (would need allocation data)
                allocated = 2 * 1024 * 1024 * 1024
                return min(usage / allocated, 1.0) if allocated > 0 else 0.0
        
        return 0.8  # Default efficiency
    
    async def analyze_costs(self, metrics: List[CostMetric]) -> List[OptimizationRecommendation]:
        """Analyze costs and generate optimization recommendations"""
        logger.info("Analyzing costs for optimization opportunities")
        
        recommendations = []
        
        for metric in metrics:
            # CPU optimization recommendations
            if metric.efficiency < self.cpu_efficiency_threshold:
                cpu_recommendation = await self._generate_cpu_recommendation(metric)
                if cpu_recommendation:
                    recommendations.append(cpu_recommendation)
            
            # Memory optimization recommendations
            if metric.efficiency < self.memory_efficiency_threshold:
                memory_recommendation = await self._generate_memory_recommendation(metric)
                if memory_recommendation:
                    recommendations.append(memory_recommendation)
            
            # Idle resource detection
            if metric.efficiency < 0.1:
                idle_recommendation = await self._generate_idle_recommendation(metric)
                if idle_recommendation:
                    recommendations.append(idle_recommendation)
        
        # Store recommendations in database
        await self._store_recommendations(recommendations)
        
        return recommendations
    
    async def _generate_cpu_recommendation(self, metric: CostMetric) -> Optional[OptimizationRecommendation]:
        """Generate CPU optimization recommendation"""
        if metric.efficiency >= self.cpu_efficiency_threshold:
            return None
        
        # Calculate potential savings
        optimal_cpu = metric.efficiency * 1.2  # 20% buffer
        projected_savings = metric.current_cost * (1 - optimal_cpu)
        
        return OptimizationRecommendation(
            resource_id=f"{metric.namespace}/{metric.pod}",
            resource_type="cpu",
            optimization_type=OptimizationType.CPU_DOWNSIZE,
            current_cost=metric.current_cost,
            projected_savings=projected_savings,
            implementation_difficulty="medium",
            risk_level="low",
            description=f"CPU over-provisioned. Current efficiency: {metric.efficiency:.2%}. Recommended: Reduce CPU allocation by {(1-optimal_cpu)*100:.1f}%",
            implementation_steps=[
                "1. Update deployment CPU requests/limits",
                "2. Monitor performance for 24-48 hours",
                "3. Adjust if needed based on performance metrics"
            ],
            estimated_implementation_time="30 minutes"
        )
    
    async def _generate_memory_recommendation(self, metric: CostMetric) -> Optional[OptimizationRecommendation]:
        """Generate memory optimization recommendation"""
        if metric.efficiency >= self.memory_efficiency_threshold:
            return None
        
        # Calculate potential savings
        optimal_memory = metric.efficiency * 1.15  # 15% buffer
        projected_savings = metric.current_cost * (1 - optimal_memory)
        
        return OptimizationRecommendation(
            resource_id=f"{metric.namespace}/{metric.pod}",
            resource_type="memory",
            optimization_type=OptimizationType.MEMORY_DOWNSIZE,
            current_cost=metric.current_cost,
            projected_savings=projected_savings,
            implementation_difficulty="medium",
            risk_level="medium",
            description=f"Memory over-provisioned. Current efficiency: {metric.efficiency:.2%}. Recommended: Reduce memory allocation by {(1-optimal_memory)*100:.1f}%",
            implementation_steps=[
                "1. Analyze memory usage patterns over 7 days",
                "2. Update deployment memory requests/limits",
                "3. Monitor for OOMKilled events",
                "4. Adjust if memory pressure detected"
            ],
            estimated_implementation_time="45 minutes"
        )
    
    async def _generate_idle_recommendation(self, metric: CostMetric) -> Optional[OptimizationRecommendation]:
        """Generate idle resource recommendation"""
        return OptimizationRecommendation(
            resource_id=f"{metric.namespace}/{metric.pod}",
            resource_type="compute",
            optimization_type=OptimizationType.IDLE_REMOVAL,
            current_cost=metric.current_cost,
            projected_savings=metric.current_cost * 0.95,  # 95% savings
            implementation_difficulty="low",
            risk_level="low",
            description=f"Idle resource detected. Efficiency: {metric.efficiency:.2%}. Consider scaling down or removing.",
            implementation_steps=[
                "1. Verify resource is truly idle",
                "2. Check for scheduled jobs or batch processes",
                "3. Scale down to zero replicas or delete",
                "4. Monitor for any impact"
            ],
            estimated_implementation_time="15 minutes"
        )
    
    async def _store_recommendations(self, recommendations: List[OptimizationRecommendation]):
        """Store optimization recommendations in database"""
        if not recommendations:
            return
        
        async with self.db_pool.acquire() as conn:
            for rec in recommendations:
                await conn.execute("""
                    INSERT INTO optimization_recommendations 
                    (resource_id, resource_type, optimization_type, current_cost, 
                     projected_savings, implementation_difficulty, risk_level, 
                     description, implementation_steps, estimated_implementation_time)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    ON CONFLICT (resource_id, optimization_type) 
                    DO UPDATE SET
                        current_cost = EXCLUDED.current_cost,
                        projected_savings = EXCLUDED.projected_savings,
                        description = EXCLUDED.description,
                        updated_at = NOW()
                """, 
                rec.resource_id, rec.resource_type, rec.optimization_type.value,
                rec.current_cost, rec.projected_savings, rec.implementation_difficulty,
                rec.risk_level, rec.description, json.dumps(rec.implementation_steps),
                rec.estimated_implementation_time)
    
    async def check_budgets(self) -> List[BudgetAlert]:
        """Check budget limits and generate alerts"""
        logger.info("Checking budget limits")
        
        alerts = []
        
        # Get current spend
        current_daily_spend = await self._get_current_spend('daily')
        current_monthly_spend = await self._get_current_spend('monthly')
        
        # Check daily budget
        daily_usage_pct = (current_daily_spend / self.daily_budget) * 100
        if daily_usage_pct > 80:
            alert_level = "critical" if daily_usage_pct > 100 else "warning"
            alerts.append(BudgetAlert(
                budget_name="Daily Budget",
                current_spend=current_daily_spend,
                budget_limit=self.daily_budget,
                threshold_percentage=daily_usage_pct,
                period="daily",
                alert_level=alert_level
            ))
        
        # Check monthly budget
        monthly_usage_pct = (current_monthly_spend / self.monthly_budget) * 100
        if monthly_usage_pct > 70:
            alert_level = "critical" if monthly_usage_pct > 90 else "warning"
            alerts.append(BudgetAlert(
                budget_name="Monthly Budget",
                current_spend=current_monthly_spend,
                budget_limit=self.monthly_budget,
                threshold_percentage=monthly_usage_pct,
                period="monthly",
                alert_level=alert_level
            ))
        
        # Store alerts
        await self._store_budget_alerts(alerts)
        
        return alerts
    
    async def _get_current_spend(self, period: str) -> float:
        """Get current spending for specified period"""
        async with aiohttp.ClientSession() as session:
            if period == 'daily':
                url = f"{self.opencost_url}/model/allocation?window=1d&aggregate=cluster"
            elif period == 'monthly':
                url = f"{self.opencost_url}/model/allocation?window=30d&aggregate=cluster"
            else:
                return 0.0
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'data' in data and data['data']:
                        return sum(allocation.get('totalCost', 0) for allocation in data['data'])
        
        return 0.0
    
    async def _store_budget_alerts(self, alerts: List[BudgetAlert]):
        """Store budget alerts in database"""
        if not alerts:
            return
        
        async with self.db_pool.acquire() as conn:
            for alert in alerts:
                await conn.execute("""
                    INSERT INTO budget_alerts 
                    (budget_name, current_spend, budget_limit, threshold_percentage, period, alert_level)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, 
                alert.budget_name, alert.current_spend, alert.budget_limit,
                alert.threshold_percentage, alert.period, alert.alert_level)
    
    async def send_notifications(self, recommendations: List[OptimizationRecommendation], 
                               budget_alerts: List[BudgetAlert]):
        """Send notifications via Slack"""
        if not self.slack_webhook:
            logger.warning("Slack webhook not configured, skipping notifications")
            return
        
        # Prepare notification message
        message = self._prepare_notification_message(recommendations, budget_alerts)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.slack_webhook, json={"text": message}) as response:
                    if response.status == 200:
                        logger.info("Notification sent successfully")
                    else:
                        logger.error(f"Failed to send notification: {response.status}")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
    
    def _prepare_notification_message(self, recommendations: List[OptimizationRecommendation], 
                                    budget_alerts: List[BudgetAlert]) -> str:
        """Prepare notification message"""
        message_parts = ["📊 *Scorpius Cost Optimization Report*\n"]
        
        # Budget alerts
        if budget_alerts:
            message_parts.append("🚨 *Budget Alerts:*")
            for alert in budget_alerts:
                icon = "🔴" if alert.alert_level == "critical" else "🟡"
                message_parts.append(
                    f"{icon} {alert.budget_name}: ${alert.current_spend:.2f} / ${alert.budget_limit:.2f} "
                    f"({alert.threshold_percentage:.1f}%)"
                )
            message_parts.append("")
        
        # Top recommendations
        if recommendations:
            total_savings = sum(rec.projected_savings for rec in recommendations)
            message_parts.append(f"💰 *Optimization Opportunities: ${total_savings:.2f}/month potential savings*")
            
            # Top 5 recommendations by savings
            top_recommendations = sorted(recommendations, key=lambda x: x.projected_savings, reverse=True)[:5]
            for i, rec in enumerate(top_recommendations, 1):
                message_parts.append(
                    f"{i}. {rec.resource_id}: ${rec.projected_savings:.2f}/month savings "
                    f"({rec.optimization_type.value})"
                )
        
        return "\n".join(message_parts)
    
    async def generate_report(self) -> Dict:
        """Generate comprehensive cost optimization report"""
        logger.info("Generating cost optimization report")
        
        # Collect metrics
        metrics = await self.collect_metrics()
        
        # Analyze costs
        recommendations = await self.analyze_costs(metrics)
        
        # Check budgets
        budget_alerts = await self.check_budgets()
        
        # Send notifications
        await self.send_notifications(recommendations, budget_alerts)
        
        # Generate report
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_metrics": len(metrics),
                "total_recommendations": len(recommendations),
                "total_potential_savings": sum(rec.projected_savings for rec in recommendations),
                "budget_alerts": len(budget_alerts)
            },
            "metrics": [asdict(metric) for metric in metrics],
            "recommendations": [asdict(rec) for rec in recommendations],
            "budget_alerts": [asdict(alert) for alert in budget_alerts]
        }
        
        return report
    
    async def close(self):
        """Close database connections"""
        if hasattr(self, 'db_pool'):
            await self.db_pool.close()

async def main():
    """Main execution function"""
    engine = CostOptimizationEngine()
    
    try:
        await engine.initialize()
        report = await engine.generate_report()
        
        # Output report
        print(f"Cost Optimization Report Generated: {datetime.utcnow()}")
        print(f"Total Recommendations: {report['summary']['total_recommendations']}")
        print(f"Potential Monthly Savings: ${report['summary']['total_potential_savings']:.2f}")
        print(f"Budget Alerts: {report['summary']['budget_alerts']}")
        
        # Save report to file
        with open(f"/tmp/cost-optimization-report-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json", 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Cost optimization failed: {e}")
        raise
    finally:
        await engine.close()

if __name__ == "__main__":
    asyncio.run(main())

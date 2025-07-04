"""
SCORPIUS ENTERPRISE ANALYTICS PLATFORM
Advanced data analytics, reporting, and business intelligence system
for comprehensive blockchain and trading insights.
"""

import asyncio
import json
import logging
import time
import math
import statistics
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal, getcontext
from collections import defaultdict, deque
import hashlib
import pickle
import gzip
import csv
import io

# Configure decimal precision
getcontext().prec = 28

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsType(Enum):
    """Types of analytics."""
    TRADING_PERFORMANCE = "trading_performance"
    RISK_METRICS = "risk_metrics"
    PORTFOLIO_ANALYSIS = "portfolio_analysis"
    MARKET_TRENDS = "market_trends"
    SECURITY_ANALYTICS = "security_analytics"
    OPERATIONAL_METRICS = "operational_metrics"
    USER_BEHAVIOR = "user_behavior"
    PROFITABILITY = "profitability"
    COMPLIANCE = "compliance"

class TimeFrame(Enum):
    """Time frames for analytics."""
    MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    HOUR = "1h"
    FOUR_HOURS = "4h"
    DAY = "1d"
    WEEK = "1w"
    MONTH = "1M"
    QUARTER = "3M"
    YEAR = "1Y"

class MetricAggregation(Enum):
    """Metric aggregation methods."""
    SUM = "sum"
    AVERAGE = "average"
    MEDIAN = "median"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    PERCENTILE = "percentile"
    STANDARD_DEVIATION = "std_dev"
    VARIANCE = "variance"

class ReportFormat(Enum):
    """Report output formats."""
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"
    EXCEL = "excel"
    HTML = "html"

@dataclass
class DataPoint:
    """A single data point for analytics."""
    timestamp: datetime
    metric_name: str
    value: Union[float, int, str, bool]
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalyticsQuery:
    """Query for analytics data."""
    metric_names: List[str]
    start_time: datetime
    end_time: datetime
    time_frame: TimeFrame
    aggregation: MetricAggregation
    filters: Dict[str, Any] = field(default_factory=dict)
    group_by: List[str] = field(default_factory=list)
    limit: Optional[int] = None

@dataclass
class AnalyticsResult:
    """Result of an analytics query."""
    query: AnalyticsQuery
    data: List[Dict[str, Any]]
    summary: Dict[str, Any]
    execution_time: float
    total_records: int
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class Report:
    """Analytics report."""
    id: str
    title: str
    description: str
    analytics_type: AnalyticsType
    data: AnalyticsResult
    insights: List[str]
    recommendations: List[str]
    charts: List[Dict[str, Any]]
    created_at: datetime
    format_type: ReportFormat = ReportFormat.JSON

class DataStorage:
    """Handles data storage and retrieval for analytics."""
    
    def __init__(self, max_data_points: int = 1000000):
        self.data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_data_points))
        self.indices: Dict[str, Dict[str, List[int]]] = defaultdict(lambda: defaultdict(list))
        self.compressed_data: Dict[str, bytes] = {}
        
    async def store_data_point(self, data_point: DataPoint):
        """Store a data point."""
        metric_key = data_point.metric_name
        
        # Add to main storage
        self.data[metric_key].append(data_point)
        
        # Update indices for fast querying
        point_index = len(self.data[metric_key]) - 1
        
        # Time-based index
        time_key = data_point.timestamp.strftime("%Y-%m-%d-%H")
        self.indices[metric_key][f"time_{time_key}"].append(point_index)
        
        # Tag-based indices
        for tag_key, tag_value in data_point.tags.items():
            self.indices[metric_key][f"tag_{tag_key}_{tag_value}"].append(point_index)
            
    async def query_data(self, query: AnalyticsQuery) -> List[DataPoint]:
        """Query data points based on criteria."""
        start_time = time.time()
        results = []
        
        for metric_name in query.metric_names:
            if metric_name not in self.data:
                continue
                
            # Get all data points for this metric
            metric_data = list(self.data[metric_name])
            
            # Filter by time range
            filtered_data = [
                dp for dp in metric_data
                if query.start_time <= dp.timestamp <= query.end_time
            ]
            
            # Apply additional filters
            for filter_key, filter_value in query.filters.items():
                filtered_data = [
                    dp for dp in filtered_data
                    if dp.tags.get(filter_key) == filter_value
                ]
                
            results.extend(filtered_data)
            
        # Apply limit
        if query.limit:
            results = results[:query.limit]
            
        logger.info(f"Query executed in {time.time() - start_time:.3f}s, returned {len(results)} points")
        return results
        
    async def aggregate_data(self, data_points: List[DataPoint], 
                           aggregation: MetricAggregation) -> Union[float, int]:
        """Aggregate data points."""
        if not data_points:
            return 0
            
        values = [dp.value for dp in data_points if isinstance(dp.value, (int, float))]
        
        if not values:
            return 0
            
        if aggregation == MetricAggregation.SUM:
            return sum(values)
        elif aggregation == MetricAggregation.AVERAGE:
            return statistics.mean(values)
        elif aggregation == MetricAggregation.MEDIAN:
            return statistics.median(values)
        elif aggregation == MetricAggregation.MIN:
            return min(values)
        elif aggregation == MetricAggregation.MAX:
            return max(values)
        elif aggregation == MetricAggregation.COUNT:
            return len(values)
        elif aggregation == MetricAggregation.STANDARD_DEVIATION:
            return statistics.stdev(values) if len(values) > 1 else 0
        elif aggregation == MetricAggregation.VARIANCE:
            return statistics.variance(values) if len(values) > 1 else 0
        else:
            return statistics.mean(values)
            
    async def compress_old_data(self, cutoff_date: datetime):
        """Compress old data to save memory."""
        for metric_name, data_deque in self.data.items():
            old_data = []
            new_data = deque()
            
            for dp in data_deque:
                if dp.timestamp < cutoff_date:
                    old_data.append(dp)
                else:
                    new_data.append(dp)
                    
            if old_data:
                # Compress old data
                compressed = gzip.compress(pickle.dumps(old_data))
                self.compressed_data[f"{metric_name}_{cutoff_date.isoformat()}"] = compressed
                
                # Update main storage
                self.data[metric_name] = new_data
                
        logger.info(f"Compressed data older than {cutoff_date}")

class TradingAnalytics:
    """Trading-specific analytics calculations."""
    
    @staticmethod
    async def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio."""
        if len(returns) < 2:
            return 0.0
            
        mean_return = statistics.mean(returns)
        std_return = statistics.stdev(returns)
        
        if std_return == 0:
            return 0.0
            
        return (mean_return - risk_free_rate) / std_return
        
    @staticmethod
    async def calculate_max_drawdown(equity_curve: List[float]) -> float:
        """Calculate maximum drawdown."""
        if not equity_curve:
            return 0.0
            
        peak = equity_curve[0]
        max_dd = 0.0
        
        for value in equity_curve:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_dd = max(max_dd, drawdown)
            
        return max_dd
        
    @staticmethod
    async def calculate_win_rate(trades: List[Dict[str, Any]]) -> float:
        """Calculate win rate from trades."""
        if not trades:
            return 0.0
            
        profitable_trades = sum(1 for trade in trades if trade.get("profit", 0) > 0)
        return profitable_trades / len(trades)
        
    @staticmethod
    async def calculate_profit_factor(trades: List[Dict[str, Any]]) -> float:
        """Calculate profit factor."""
        gross_profit = sum(trade.get("profit", 0) for trade in trades if trade.get("profit", 0) > 0)
        gross_loss = abs(sum(trade.get("profit", 0) for trade in trades if trade.get("profit", 0) < 0))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
            
        return gross_profit / gross_loss
        
    @staticmethod
    async def calculate_calmar_ratio(annual_return: float, max_drawdown: float) -> float:
        """Calculate Calmar ratio."""
        if max_drawdown == 0:
            return float('inf') if annual_return > 0 else 0.0
            
        return annual_return / max_drawdown

class RiskAnalytics:
    """Risk management analytics."""
    
    @staticmethod
    async def calculate_var(returns: List[float], confidence_level: float = 0.95) -> float:
        """Calculate Value at Risk (VaR)."""
        if not returns:
            return 0.0
            
        sorted_returns = sorted(returns)
        index = int((1 - confidence_level) * len(sorted_returns))
        return abs(sorted_returns[index]) if index < len(sorted_returns) else 0.0
        
    @staticmethod
    async def calculate_cvar(returns: List[float], confidence_level: float = 0.95) -> float:
        """Calculate Conditional Value at Risk (CVaR)."""
        if not returns:
            return 0.0
            
        var = await RiskAnalytics.calculate_var(returns, confidence_level)
        tail_losses = [abs(r) for r in returns if abs(r) >= var]
        
        return statistics.mean(tail_losses) if tail_losses else 0.0
        
    @staticmethod
    async def calculate_beta(asset_returns: List[float], market_returns: List[float]) -> float:
        """Calculate beta coefficient."""
        if len(asset_returns) != len(market_returns) or len(asset_returns) < 2:
            return 1.0
            
        # Calculate covariance and variance
        mean_asset = statistics.mean(asset_returns)
        mean_market = statistics.mean(market_returns)
        
        covariance = sum((a - mean_asset) * (m - mean_market) 
                        for a, m in zip(asset_returns, market_returns)) / (len(asset_returns) - 1)
        
        market_variance = statistics.variance(market_returns)
        
        if market_variance == 0:
            return 1.0
            
        return covariance / market_variance

class MarketAnalytics:
    """Market trend and behavior analytics."""
    
    @staticmethod
    async def detect_trend(prices: List[float], window: int = 20) -> str:
        """Detect market trend using moving averages."""
        if len(prices) < window:
            return "insufficient_data"
            
        recent_avg = statistics.mean(prices[-window:])
        older_avg = statistics.mean(prices[-2*window:-window]) if len(prices) >= 2*window else recent_avg
        
        if recent_avg > older_avg * 1.02:
            return "uptrend"
        elif recent_avg < older_avg * 0.98:
            return "downtrend"
        else:
            return "sideways"
            
    @staticmethod
    async def calculate_volatility(prices: List[float], window: int = 20) -> float:
        """Calculate price volatility."""
        if len(prices) < 2:
            return 0.0
            
        returns = [(prices[i] / prices[i-1] - 1) for i in range(1, len(prices))]
        recent_returns = returns[-window:] if len(returns) >= window else returns
        
        return statistics.stdev(recent_returns) if len(recent_returns) > 1 else 0.0
        
    @staticmethod
    async def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index."""
        if len(prices) < period + 1:
            return 50.0  # Neutral RSI
            
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
                
        if len(gains) < period:
            return 50.0
            
        avg_gain = statistics.mean(gains[-period:])
        avg_loss = statistics.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi

class ReportGenerator:
    """Generates various types of analytics reports."""
    
    def __init__(self, data_storage: DataStorage):
        self.data_storage = data_storage
        
    async def generate_trading_performance_report(self, start_date: datetime, 
                                                 end_date: datetime) -> Report:
        """Generate trading performance report."""
        # Query trading data
        query = AnalyticsQuery(
            metric_names=["trade_profit", "trade_volume", "trade_count"],
            start_time=start_date,
            end_time=end_date,
            time_frame=TimeFrame.DAY,
            aggregation=MetricAggregation.SUM
        )
        
        data_points = await self.data_storage.query_data(query)
        
        # Calculate performance metrics
        trades = [{"profit": dp.value} for dp in data_points if dp.metric_name == "trade_profit"]
        
        total_profit = sum(t["profit"] for t in trades)
        win_rate = await TradingAnalytics.calculate_win_rate(trades)
        profit_factor = await TradingAnalytics.calculate_profit_factor(trades)
        
        # Generate insights
        insights = []
        recommendations = []
        
        if win_rate > 0.6:
            insights.append(f"High win rate of {win_rate:.1%} indicates good strategy performance")
        elif win_rate < 0.4:
            insights.append(f"Low win rate of {win_rate:.1%} suggests strategy needs improvement")
            recommendations.append("Review and optimize trading strategies")
            
        if profit_factor > 1.5:
            insights.append(f"Strong profit factor of {profit_factor:.2f}")
        elif profit_factor < 1.0:
            insights.append(f"Negative profit factor of {profit_factor:.2f}")
            recommendations.append("Focus on risk management and loss reduction")
            
        # Create charts data
        charts = [
            {
                "type": "line",
                "title": "Cumulative P&L",
                "data": [{"x": dp.timestamp.isoformat(), "y": dp.value} 
                        for dp in data_points if dp.metric_name == "trade_profit"]
            },
            {
                "type": "bar",
                "title": "Daily Trade Volume",
                "data": [{"x": dp.timestamp.isoformat(), "y": dp.value}
                        for dp in data_points if dp.metric_name == "trade_volume"]
            }
        ]
        
        result = AnalyticsResult(
            query=query,
            data=[asdict(dp) for dp in data_points],
            summary={
                "total_profit": total_profit,
                "win_rate": win_rate,
                "profit_factor": profit_factor,
                "total_trades": len(trades)
            },
            execution_time=0.1,
            total_records=len(data_points)
        )
        
        return Report(
            id=f"trading_performance_{int(time.time())}",
            title="Trading Performance Report",
            description=f"Trading performance analysis from {start_date.date()} to {end_date.date()}",
            analytics_type=AnalyticsType.TRADING_PERFORMANCE,
            data=result,
            insights=insights,
            recommendations=recommendations,
            charts=charts,
            created_at=datetime.now()
        )
        
    async def generate_risk_assessment_report(self, start_date: datetime,
                                            end_date: datetime) -> Report:
        """Generate risk assessment report."""
        # Query risk-related data
        query = AnalyticsQuery(
            metric_names=["portfolio_value", "drawdown", "volatility"],
            start_time=start_date,
            end_time=end_date,
            time_frame=TimeFrame.DAY,
            aggregation=MetricAggregation.AVERAGE
        )
        
        data_points = await self.data_storage.query_data(query)
        
        # Calculate risk metrics
        portfolio_values = [dp.value for dp in data_points if dp.metric_name == "portfolio_value"]
        returns = [(portfolio_values[i] / portfolio_values[i-1] - 1) 
                  for i in range(1, len(portfolio_values))] if len(portfolio_values) > 1 else []
        
        max_drawdown = await TradingAnalytics.calculate_max_drawdown(portfolio_values)
        var_95 = await RiskAnalytics.calculate_var(returns, 0.95)
        cvar_95 = await RiskAnalytics.calculate_cvar(returns, 0.95)
        
        # Generate insights
        insights = []
        recommendations = []
        
        if max_drawdown > 0.2:
            insights.append(f"High maximum drawdown of {max_drawdown:.1%}")
            recommendations.append("Implement stricter position sizing and stop-loss rules")
        elif max_drawdown < 0.05:
            insights.append(f"Low maximum drawdown of {max_drawdown:.1%} indicates conservative approach")
            
        if var_95 > 0.05:
            insights.append(f"High 95% VaR of {var_95:.1%}")
            recommendations.append("Consider reducing position sizes or diversifying portfolio")
            
        charts = [
            {
                "type": "line",
                "title": "Portfolio Value Over Time",
                "data": [{"x": dp.timestamp.isoformat(), "y": dp.value}
                        for dp in data_points if dp.metric_name == "portfolio_value"]
            },
            {
                "type": "histogram",
                "title": "Return Distribution",
                "data": [{"value": r} for r in returns]
            }
        ]
        
        result = AnalyticsResult(
            query=query,
            data=[asdict(dp) for dp in data_points],
            summary={
                "max_drawdown": max_drawdown,
                "var_95": var_95,
                "cvar_95": cvar_95,
                "avg_volatility": statistics.mean([dp.value for dp in data_points 
                                                 if dp.metric_name == "volatility"]) if data_points else 0
            },
            execution_time=0.15,
            total_records=len(data_points)
        )
        
        return Report(
            id=f"risk_assessment_{int(time.time())}",
            title="Risk Assessment Report",
            description=f"Risk analysis from {start_date.date()} to {end_date.date()}",
            analytics_type=AnalyticsType.RISK_METRICS,
            data=result,
            insights=insights,
            recommendations=recommendations,
            charts=charts,
            created_at=datetime.now()
        )
        
    async def export_report(self, report: Report, format_type: ReportFormat) -> str:
        """Export report in specified format."""
        if format_type == ReportFormat.JSON:
            return json.dumps(asdict(report), default=str, indent=2)
            
        elif format_type == ReportFormat.CSV:
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(["Timestamp", "Metric", "Value", "Tags"])
            
            # Write data
            for data_point in report.data.data:
                writer.writerow([
                    data_point.get("timestamp", ""),
                    data_point.get("metric_name", ""),
                    data_point.get("value", ""),
                    json.dumps(data_point.get("tags", {}))
                ])
                
            return output.getvalue()
            
        elif format_type == ReportFormat.HTML:
            html_content = f"""
            <html>
            <head><title>{report.title}</title></head>
            <body>
                <h1>{report.title}</h1>
                <p>{report.description}</p>
                <h2>Summary</h2>
                <ul>
                    {"".join(f"<li>{k}: {v}</li>" for k, v in report.data.summary.items())}
                </ul>
                <h2>Insights</h2>
                <ul>
                    {"".join(f"<li>{insight}</li>" for insight in report.insights)}
                </ul>
                <h2>Recommendations</h2>
                <ul>
                    {"".join(f"<li>{rec}</li>" for rec in report.recommendations)}
                </ul>
            </body>
            </html>
            """
            return html_content
            
        else:
            return json.dumps(asdict(report), default=str, indent=2)

class AnalyticsDashboard:
    """Real-time analytics dashboard."""
    
    def __init__(self):
        self.widgets: Dict[str, Dict[str, Any]] = {}
        self.subscribers: List[Callable] = []
        
    async def add_widget(self, widget_id: str, widget_config: Dict[str, Any]):
        """Add a dashboard widget."""
        self.widgets[widget_id] = widget_config
        
    async def update_widget(self, widget_id: str, data: Dict[str, Any]):
        """Update widget data."""
        if widget_id in self.widgets:
            self.widgets[widget_id]["data"] = data
            self.widgets[widget_id]["last_updated"] = datetime.now().isoformat()
            
            # Notify subscribers
            for subscriber in self.subscribers:
                try:
                    await subscriber(widget_id, data)
                except Exception as e:
                    logger.error(f"Error notifying dashboard subscriber: {e}")
                    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data."""
        return {
            "widgets": self.widgets,
            "timestamp": datetime.now().isoformat()
        }

class EnterpriseAnalyticsPlatform:
    """Main enterprise analytics platform."""
    
    def __init__(self):
        self.data_storage = DataStorage()
        self.report_generator = ReportGenerator(self.data_storage)
        self.dashboard = AnalyticsDashboard()
        
        self.running = False
        self.data_collectors: List[Callable] = []
        
        # Initialize dashboard widgets
        self._initialize_dashboard()
        
    def _initialize_dashboard(self):
        """Initialize default dashboard widgets."""
        asyncio.create_task(self.dashboard.add_widget("trading_summary", {
            "type": "summary_card",
            "title": "Trading Summary",
            "metrics": ["total_profit", "win_rate", "total_trades"],
            "refresh_interval": 60
        }))
        
        asyncio.create_task(self.dashboard.add_widget("portfolio_chart", {
            "type": "line_chart",
            "title": "Portfolio Value",
            "metric": "portfolio_value",
            "timeframe": "24h",
            "refresh_interval": 300
        }))
        
        asyncio.create_task(self.dashboard.add_widget("risk_metrics", {
            "type": "gauge",
            "title": "Risk Metrics",
            "metrics": ["max_drawdown", "var_95"],
            "refresh_interval": 3600
        }))
        
    async def start_analytics_platform(self):
        """Start the analytics platform."""
        logger.info("Starting Enterprise Analytics Platform...")
        self.running = True
        
        # Start data collection
        collection_task = asyncio.create_task(self._data_collection_loop())
        
        # Start dashboard updates
        dashboard_task = asyncio.create_task(self._dashboard_update_loop())
        
        # Start data compression
        compression_task = asyncio.create_task(self._data_compression_loop())
        
        await asyncio.gather(collection_task, dashboard_task, compression_task)
        
    async def stop_analytics_platform(self):
        """Stop the analytics platform."""
        logger.info("Stopping Enterprise Analytics Platform...")
        self.running = False
        
    async def _data_collection_loop(self):
        """Collect data from various sources."""
        while self.running:
            try:
                # Generate sample data points
                await self._generate_sample_data()
                
                # Run custom data collectors
                for collector in self.data_collectors:
                    try:
                        data_points = await collector()
                        for dp in data_points:
                            await self.data_storage.store_data_point(dp)
                    except Exception as e:
                        logger.error(f"Error in data collector: {e}")
                        
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"Error in data collection loop: {e}")
                await asyncio.sleep(120)
                
    async def _generate_sample_data(self):
        """Generate sample data for demonstration."""
        current_time = datetime.now()
        
        # Sample trading data
        sample_data_points = [
            DataPoint(
                timestamp=current_time,
                metric_name="trade_profit",
                value=hash(str(current_time)) % 1000 - 500,  # Random profit/loss
                tags={"strategy": "arbitrage", "pair": "ETH/USDC"}
            ),
            DataPoint(
                timestamp=current_time,
                metric_name="portfolio_value",
                value=100000 + (hash(str(current_time)) % 10000),  # Random portfolio value
                tags={"currency": "USD"}
            ),
            DataPoint(
                timestamp=current_time,
                metric_name="trade_volume",
                value=hash(str(current_time)) % 50000 + 10000,  # Random volume
                tags={"exchange": "uniswap"}
            )
        ]
        
        for dp in sample_data_points:
            await self.data_storage.store_data_point(dp)
            
    async def _dashboard_update_loop(self):
        """Update dashboard widgets."""
        while self.running:
            try:
                # Update trading summary
                current_time = datetime.now()
                start_time = current_time - timedelta(days=1)
                
                profit_data = await self.data_storage.query_data(AnalyticsQuery(
                    metric_names=["trade_profit"],
                    start_time=start_time,
                    end_time=current_time,
                    time_frame=TimeFrame.HOUR,
                    aggregation=MetricAggregation.SUM
                ))
                
                total_profit = await self.data_storage.aggregate_data(
                    profit_data, MetricAggregation.SUM
                )
                
                await self.dashboard.update_widget("trading_summary", {
                    "total_profit": total_profit,
                    "win_rate": 0.65,  # Placeholder
                    "total_trades": len(profit_data)
                })
                
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                logger.error(f"Error updating dashboard: {e}")
                await asyncio.sleep(600)
                
    async def _data_compression_loop(self):
        """Compress old data periodically."""
        while self.running:
            try:
                # Compress data older than 30 days
                cutoff_date = datetime.now() - timedelta(days=30)
                await self.data_storage.compress_old_data(cutoff_date)
                
                await asyncio.sleep(86400)  # Run daily
                
            except Exception as e:
                logger.error(f"Error in data compression: {e}")
                await asyncio.sleep(3600)
                
    async def add_data_collector(self, collector: Callable):
        """Add a custom data collector."""
        self.data_collectors.append(collector)
        
    async def generate_report(self, analytics_type: AnalyticsType, 
                            start_date: datetime, end_date: datetime) -> Report:
        """Generate an analytics report."""
        if analytics_type == AnalyticsType.TRADING_PERFORMANCE:
            return await self.report_generator.generate_trading_performance_report(
                start_date, end_date
            )
        elif analytics_type == AnalyticsType.RISK_METRICS:
            return await self.report_generator.generate_risk_assessment_report(
                start_date, end_date
            )
        else:
            raise ValueError(f"Unsupported analytics type: {analytics_type}")
            
    async def export_report(self, report: Report, format_type: ReportFormat) -> str:
        """Export a report."""
        return await self.report_generator.export_report(report, format_type)
        
    async def query_analytics(self, query: AnalyticsQuery) -> AnalyticsResult:
        """Execute an analytics query."""
        start_time = time.time()
        
        data_points = await self.data_storage.query_data(query)
        aggregated_value = await self.data_storage.aggregate_data(data_points, query.aggregation)
        
        execution_time = time.time() - start_time
        
        return AnalyticsResult(
            query=query,
            data=[asdict(dp) for dp in data_points],
            summary={"aggregated_value": aggregated_value},
            execution_time=execution_time,
            total_records=len(data_points)
        )
        
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data."""
        return await self.dashboard.get_dashboard_data()

# Global analytics platform instance
_analytics_platform_instance: Optional[EnterpriseAnalyticsPlatform] = None

async def initialize_analytics_platform() -> EnterpriseAnalyticsPlatform:
    """Initialize the enterprise analytics platform."""
    global _analytics_platform_instance
    
    if _analytics_platform_instance is None:
        _analytics_platform_instance = EnterpriseAnalyticsPlatform()
        logger.info("Enterprise Analytics Platform initialized successfully")
        
    return _analytics_platform_instance

def get_analytics_platform_instance() -> Optional[EnterpriseAnalyticsPlatform]:
    """Get the current analytics platform instance."""
    return _analytics_platform_instance

async def start_analytics_platform():
    """Start the analytics platform."""
    platform = await initialize_analytics_platform()
    await platform.start_analytics_platform()

async def stop_analytics_platform():
    """Stop the analytics platform."""
    global _analytics_platform_instance
    if _analytics_platform_instance:
        await _analytics_platform_instance.stop_analytics_platform()
        _analytics_platform_instance = None

if __name__ == "__main__":
    # Example usage
    async def main():
        platform = await initialize_analytics_platform()
        
        # Generate a trading performance report
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        report = await platform.generate_report(
            AnalyticsType.TRADING_PERFORMANCE,
            start_date,
            end_date
        )
        
        print(f"Generated report: {report.title}")
        print(f"Insights: {report.insights}")
        
        # Start the platform
        await platform.start_analytics_platform()

    asyncio.run(main())

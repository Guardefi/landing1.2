"""
SCORPIUS AI-POWERED TRADING ENGINE
Advanced intelligent trading system with MEV protection, arbitrage detection,
and AI-driven decision making for maximum profit and security.
"""

import asyncio
import json
import logging
import time
import math
from typing import Dict, List, Optional, Any, Callable, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import statistics
from collections import defaultdict, deque
import concurrent.futures
from decimal import Decimal, getcontext

# Configure decimal precision for financial calculations
getcontext().prec = 28

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingStrategy(Enum):
    """Available trading strategies."""
    ARBITRAGE = "arbitrage"
    MEV_PROTECTION = "mev_protection"
    LIQUIDITY_PROVISION = "liquidity_provision"
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    GRID_TRADING = "grid_trading"
    AI_PREDICTION = "ai_prediction"
    FLASH_LOAN = "flash_loan"

class OrderType(Enum):
    """Order types."""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    FLASH_LOAN = "flash_loan"
    MEV_PROTECTED = "mev_protected"

class TradingPair(Enum):
    """Common trading pairs."""
    ETH_USDC = "ETH/USDC"
    BTC_ETH = "BTC/ETH"
    USDC_USDT = "USDC/USDT"
    ETH_DAI = "ETH/DAI"
    WBTC_ETH = "WBTC/ETH"

class ExchangeType(Enum):
    """Supported exchange types."""
    UNISWAP_V3 = "uniswap_v3"
    SUSHISWAP = "sushiswap"
    CURVE = "curve"
    BALANCER = "balancer"
    PANCAKESWAP = "pancakeswap"
    ONE_INCH = "1inch"

class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"

@dataclass
class MarketData:
    """Market data for a trading pair."""
    pair: str
    price: Decimal
    volume_24h: Decimal
    bid: Decimal
    ask: Decimal
    spread: Decimal
    timestamp: datetime
    exchange: str
    liquidity: Decimal = Decimal('0')
    volatility: Decimal = Decimal('0')

@dataclass
class TradingOpportunity:
    """A detected trading opportunity."""
    id: str
    strategy: TradingStrategy
    pair: str
    expected_profit: Decimal
    profit_percentage: Decimal
    confidence: float
    risk_level: float
    execution_time: timedelta
    exchanges: List[str]
    requirements: Dict[str, Any]
    timestamp: datetime
    expires_at: datetime

@dataclass
class TradeOrder:
    """A trading order."""
    id: str
    pair: str
    order_type: OrderType
    side: str  # 'buy' or 'sell'
    amount: Decimal
    price: Decimal
    timestamp: datetime
    status: str = "pending"
    filled_amount: Decimal = Decimal('0')
    fees: Decimal = Decimal('0')
    exchange: Optional[str] = None
    strategy: Optional[TradingStrategy] = None

@dataclass
class Portfolio:
    """Trading portfolio state."""
    balances: Dict[str, Decimal] = field(default_factory=dict)
    total_value_usd: Decimal = Decimal('0')
    profit_loss_24h: Decimal = Decimal('0')
    profit_loss_percentage: Decimal = Decimal('0')
    active_positions: List[Dict[str, Any]] = field(default_factory=list)
    trade_count_24h: int = 0
    last_updated: datetime = field(default_factory=datetime.now)

class MarketDataProvider:
    """Provides real-time market data from multiple sources."""
    
    def __init__(self):
        self.data_cache: Dict[str, MarketData] = {}
        self.price_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.subscribers: List[Callable] = []
        
    async def start_data_feed(self):
        """Start real-time data feed."""
        while True:
            try:
                await self._fetch_market_data()
                await asyncio.sleep(1)  # Update every second
            except Exception as e:
                logger.error(f"Error fetching market data: {e}")
                await asyncio.sleep(5)
                
    async def _fetch_market_data(self):
        """Fetch market data from exchanges."""
        # Simulate fetching real market data
        pairs = ["ETH/USDC", "BTC/ETH", "USDC/USDT", "ETH/DAI"]
        
        for pair in pairs:
            # Simulate price movement
            current_price = self.data_cache.get(pair, MarketData(
                pair=pair, price=Decimal('2000'), volume_24h=Decimal('1000000'),
                bid=Decimal('1999'), ask=Decimal('2001'), spread=Decimal('2'),
                timestamp=datetime.now(), exchange="uniswap_v3"
            )).price
            
            # Add some randomness
            price_change = Decimal(str((hash(pair + str(time.time())) % 1000 - 500) / 10000))
            new_price = current_price * (Decimal('1') + price_change)
            
            market_data = MarketData(
                pair=pair,
                price=new_price,
                volume_24h=Decimal('1000000') + Decimal(str(hash(pair) % 500000)),
                bid=new_price * Decimal('0.999'),
                ask=new_price * Decimal('1.001'),
                spread=new_price * Decimal('0.002'),
                timestamp=datetime.now(),
                exchange="uniswap_v3",
                liquidity=Decimal('5000000'),
                volatility=Decimal('0.05')
            )
            
            self.data_cache[pair] = market_data
            self.price_history[pair].append((datetime.now(), new_price))
            
            # Notify subscribers
            for subscriber in self.subscribers:
                try:
                    await subscriber(market_data)
                except Exception as e:
                    logger.error(f"Error notifying subscriber: {e}")
    
    def subscribe(self, callback: Callable):
        """Subscribe to market data updates."""
        self.subscribers.append(callback)
        
    def get_market_data(self, pair: str) -> Optional[MarketData]:
        """Get current market data for a pair."""
        return self.data_cache.get(pair)
        
    def get_price_history(self, pair: str, periods: int = 100) -> List[Tuple[datetime, Decimal]]:
        """Get price history for a pair."""
        history = list(self.price_history[pair])
        return history[-periods:] if history else []

class ArbitrageDetector:
    """Detects arbitrage opportunities across exchanges."""
    
    def __init__(self, market_data_provider: MarketDataProvider):
        self.market_data_provider = market_data_provider
        self.min_profit_threshold = Decimal('0.005')  # 0.5% minimum profit
        
    async def scan_for_arbitrage(self) -> List[TradingOpportunity]:
        """Scan for arbitrage opportunities."""
        opportunities = []
        
        # Get market data from multiple exchanges (simulated)
        exchanges = ["uniswap_v3", "sushiswap", "curve"]
        pairs = ["ETH/USDC", "BTC/ETH", "USDC/USDT"]
        
        for pair in pairs:
            exchange_prices = {}
            
            # Simulate getting prices from different exchanges
            base_price = self.market_data_provider.get_market_data(pair)
            if not base_price:
                continue
                
            for exchange in exchanges:
                # Simulate price differences between exchanges
                price_variance = Decimal(str((hash(exchange + pair) % 200 - 100) / 10000))
                exchange_prices[exchange] = base_price.price * (Decimal('1') + price_variance)
                
            # Find arbitrage opportunities
            prices = list(exchange_prices.values())
            min_price = min(prices)
            max_price = max(prices)
            
            profit_percentage = (max_price - min_price) / min_price
            
            if profit_percentage > self.min_profit_threshold:
                buy_exchange = [ex for ex, price in exchange_prices.items() if price == min_price][0]
                sell_exchange = [ex for ex, price in exchange_prices.items() if price == max_price][0]
                
                opportunity = TradingOpportunity(
                    id=f"arb_{pair.replace('/', '_')}_{int(time.time())}",
                    strategy=TradingStrategy.ARBITRAGE,
                    pair=pair,
                    expected_profit=Decimal('10000') * profit_percentage,  # Assuming $10k trade
                    profit_percentage=profit_percentage,
                    confidence=0.9,
                    risk_level=0.2,
                    execution_time=timedelta(seconds=15),
                    exchanges=[buy_exchange, sell_exchange],
                    requirements={
                        "buy_exchange": buy_exchange,
                        "sell_exchange": sell_exchange,
                        "buy_price": min_price,
                        "sell_price": max_price,
                        "min_amount": Decimal('1000')
                    },
                    timestamp=datetime.now(),
                    expires_at=datetime.now() + timedelta(minutes=2)
                )
                opportunities.append(opportunity)
                
        return opportunities

class MEVProtectionEngine:
    """Protects trades from MEV attacks."""
    
    def __init__(self):
        self.protected_mempool = []
        self.flashbots_relay_enabled = True
        self.private_mempool_enabled = True
        
    async def protect_trade(self, order: TradeOrder) -> TradeOrder:
        """Apply MEV protection to a trade."""
        # Add MEV protection measures
        order.order_type = OrderType.MEV_PROTECTED
        
        # Simulate adding to private mempool
        if self.private_mempool_enabled:
            order.requirements = order.requirements or {}
            order.requirements["private_mempool"] = True
            order.requirements["protection_level"] = "high"
            
        # Add timing randomization
        order.requirements = order.requirements or {}
        order.requirements["execution_delay"] = hash(order.id) % 5 + 1  # 1-5 second delay
        
        logger.info(f"Applied MEV protection to order {order.id}")
        return order
        
    async def detect_mev_attack(self, order: TradeOrder) -> bool:
        """Detect potential MEV attacks."""
        # Simulate MEV detection logic
        suspicious_patterns = [
            "sandwich_attack",
            "front_running",
            "back_running"
        ]
        
        # Check for suspicious activity (simplified)
        order_hash = hash(f"{order.pair}{order.amount}{order.price}")
        if order_hash % 100 < 5:  # 5% chance of detecting MEV
            logger.warning(f"Potential MEV attack detected for order {order.id}")
            return True
            
        return False

class AITradingModel:
    """AI model for trading predictions and decisions."""
    
    def __init__(self):
        self.model_accuracy = 0.75
        self.prediction_cache = {}
        
    async def predict_price_movement(self, pair: str, timeframe: timedelta) -> Dict[str, Any]:
        """Predict price movement for a trading pair."""
        # Simulate AI prediction
        prediction_id = f"{pair}_{timeframe.total_seconds()}"
        
        if prediction_id in self.prediction_cache:
            return self.prediction_cache[prediction_id]
            
        # Generate prediction (simplified)
        confidence = 0.6 + (hash(prediction_id) % 40) / 100  # 0.6-1.0
        direction = "up" if hash(prediction_id) % 2 == 0 else "down"
        magnitude = (hash(prediction_id) % 20 + 5) / 1000  # 0.5%-2.5% movement
        
        prediction = {
            "direction": direction,
            "magnitude": magnitude,
            "confidence": confidence,
            "timeframe": timeframe.total_seconds(),
            "timestamp": datetime.now(),
            "model_version": "v2.1.0"
        }
        
        self.prediction_cache[prediction_id] = prediction
        return prediction
        
    async def evaluate_opportunity(self, opportunity: TradingOpportunity) -> float:
        """Evaluate a trading opportunity using AI."""
        # Get price prediction
        prediction = await self.predict_price_movement(
            opportunity.pair, 
            opportunity.execution_time
        )
        
        # Calculate AI score
        base_score = opportunity.confidence
        
        # Adjust based on prediction
        if opportunity.strategy == TradingStrategy.ARBITRAGE:
            # Arbitrage is less dependent on price prediction
            ai_score = base_score * 0.9 + prediction["confidence"] * 0.1
        else:
            # Other strategies more dependent on prediction
            direction_match = (
                (opportunity.expected_profit > 0 and prediction["direction"] == "up") or
                (opportunity.expected_profit < 0 and prediction["direction"] == "down")
            )
            direction_bonus = 0.2 if direction_match else -0.1
            ai_score = base_score * 0.7 + prediction["confidence"] * 0.3 + direction_bonus
            
        return max(0.0, min(1.0, ai_score))

class RiskManager:
    """Manages trading risks and position sizing."""
    
    def __init__(self):
        self.max_position_size = Decimal('0.1')  # 10% of portfolio per trade
        self.max_daily_loss = Decimal('0.05')  # 5% max daily loss
        self.max_drawdown = Decimal('0.15')  # 15% max drawdown
        self.daily_pnl = Decimal('0')
        
    async def check_risk_limits(self, order: TradeOrder, portfolio: Portfolio) -> bool:
        """Check if order violates risk limits."""
        # Position size check
        order_value = order.amount * order.price
        portfolio_value = portfolio.total_value_usd
        
        if portfolio_value > 0:
            position_percentage = order_value / portfolio_value
            if position_percentage > self.max_position_size:
                logger.warning(f"Order {order.id} exceeds max position size")
                return False
                
        # Daily loss check
        if portfolio.profit_loss_24h < -abs(self.max_daily_loss * portfolio_value):
            logger.warning("Daily loss limit exceeded")
            return False
            
        return True
        
    async def calculate_position_size(self, opportunity: TradingOpportunity, 
                                    portfolio: Portfolio, 
                                    ai_score: float) -> Decimal:
        """Calculate optimal position size."""
        if portfolio.total_value_usd == 0:
            return Decimal('1000')  # Default size
            
        # Base position size
        base_size = portfolio.total_value_usd * self.max_position_size
        
        # Adjust based on confidence and AI score
        confidence_multiplier = Decimal(str(opportunity.confidence * ai_score))
        risk_multiplier = Decimal(str(1 - opportunity.risk_level))
        
        position_size = base_size * confidence_multiplier * risk_multiplier
        
        # Ensure minimum trade size
        min_size = Decimal('100')
        return max(min_size, position_size)

class OrderExecutor:
    """Executes trading orders across exchanges."""
    
    def __init__(self, mev_protection: MEVProtectionEngine):
        self.mev_protection = mev_protection
        self.active_orders: Dict[str, TradeOrder] = {}
        self.execution_history: List[TradeOrder] = []
        
    async def execute_order(self, order: TradeOrder) -> bool:
        """Execute a trading order."""
        try:
            # Apply MEV protection
            if order.order_type != OrderType.MEV_PROTECTED:
                order = await self.mev_protection.protect_trade(order)
                
            # Check for MEV attacks
            if await self.mev_protection.detect_mev_attack(order):
                logger.warning(f"MEV attack detected, cancelling order {order.id}")
                return False
                
            # Simulate order execution
            self.active_orders[order.id] = order
            
            # Simulate execution delay
            execution_delay = order.requirements.get("execution_delay", 1)
            await asyncio.sleep(execution_delay)
            
            # Mark as filled (simplified)
            order.status = "filled"
            order.filled_amount = order.amount
            order.fees = order.amount * order.price * Decimal('0.003')  # 0.3% fee
            
            self.execution_history.append(order)
            del self.active_orders[order.id]
            
            logger.info(f"Order {order.id} executed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error executing order {order.id}: {e}")
            order.status = "failed"
            return False

class AITradingEngine:
    """Main AI-powered trading engine."""
    
    def __init__(self):
        self.market_data_provider = MarketDataProvider()
        self.arbitrage_detector = ArbitrageDetector(self.market_data_provider)
        self.mev_protection = MEVProtectionEngine()
        self.ai_model = AITradingModel()
        self.risk_manager = RiskManager()
        self.order_executor = OrderExecutor(self.mev_protection)
        
        self.portfolio = Portfolio()
        self.active_strategies: Set[TradingStrategy] = {
            TradingStrategy.ARBITRAGE,
            TradingStrategy.MEV_PROTECTION,
            TradingStrategy.AI_PREDICTION
        }
        
        self.running = False
        self.performance_metrics = {
            "total_trades": 0,
            "profitable_trades": 0,
            "total_profit": Decimal('0'),
            "max_drawdown": Decimal('0'),
            "sharpe_ratio": 0.0,
            "win_rate": 0.0
        }
        
    async def start_trading(self):
        """Start the AI trading engine."""
        logger.info("Starting AI Trading Engine...")
        self.running = True
        
        # Start market data feed
        data_feed_task = asyncio.create_task(self.market_data_provider.start_data_feed())
        
        # Start trading loop
        trading_task = asyncio.create_task(self._trading_loop())
        
        # Start portfolio monitoring
        portfolio_task = asyncio.create_task(self._portfolio_monitoring_loop())
        
        await asyncio.gather(data_feed_task, trading_task, portfolio_task)
        
    async def stop_trading(self):
        """Stop the trading engine."""
        logger.info("Stopping AI Trading Engine...")
        self.running = False
        
    async def _trading_loop(self):
        """Main trading loop."""
        while self.running:
            try:
                # Scan for opportunities
                opportunities = await self._scan_opportunities()
                
                # Evaluate and execute opportunities
                for opportunity in opportunities:
                    if await self._should_trade(opportunity):
                        await self._execute_opportunity(opportunity)
                        
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                await asyncio.sleep(30)
                
    async def _scan_opportunities(self) -> List[TradingOpportunity]:
        """Scan for trading opportunities."""
        opportunities = []
        
        # Arbitrage opportunities
        if TradingStrategy.ARBITRAGE in self.active_strategies:
            arb_opportunities = await self.arbitrage_detector.scan_for_arbitrage()
            opportunities.extend(arb_opportunities)
            
        # AI prediction opportunities
        if TradingStrategy.AI_PREDICTION in self.active_strategies:
            ai_opportunities = await self._scan_ai_opportunities()
            opportunities.extend(ai_opportunities)
            
        return opportunities
        
    async def _scan_ai_opportunities(self) -> List[TradingOpportunity]:
        """Scan for AI-based opportunities."""
        opportunities = []
        pairs = ["ETH/USDC", "BTC/ETH"]
        
        for pair in pairs:
            prediction = await self.ai_model.predict_price_movement(
                pair, timedelta(minutes=15)
            )
            
            if prediction["confidence"] > 0.8:  # High confidence prediction
                market_data = self.market_data_provider.get_market_data(pair)
                if not market_data:
                    continue
                    
                expected_profit = Decimal(str(prediction["magnitude"])) * Decimal('10000')
                
                opportunity = TradingOpportunity(
                    id=f"ai_{pair.replace('/', '_')}_{int(time.time())}",
                    strategy=TradingStrategy.AI_PREDICTION,
                    pair=pair,
                    expected_profit=expected_profit,
                    profit_percentage=Decimal(str(prediction["magnitude"])),
                    confidence=prediction["confidence"],
                    risk_level=0.4,
                    execution_time=timedelta(minutes=1),
                    exchanges=["uniswap_v3"],
                    requirements={
                        "prediction": prediction,
                        "entry_price": market_data.price
                    },
                    timestamp=datetime.now(),
                    expires_at=datetime.now() + timedelta(minutes=10)
                )
                opportunities.append(opportunity)
                
        return opportunities
        
    async def _should_trade(self, opportunity: TradingOpportunity) -> bool:
        """Determine if we should trade an opportunity."""
        # Get AI evaluation
        ai_score = await self.ai_model.evaluate_opportunity(opportunity)
        
        # Check if AI score is sufficient
        if ai_score < 0.7:
            return False
            
        # Check risk limits
        test_order = TradeOrder(
            id=f"test_{opportunity.id}",
            pair=opportunity.pair,
            order_type=OrderType.MARKET,
            side="buy",
            amount=Decimal('1000'),
            price=Decimal('1'),
            timestamp=datetime.now()
        )
        
        if not await self.risk_manager.check_risk_limits(test_order, self.portfolio):
            return False
            
        return True
        
    async def _execute_opportunity(self, opportunity: TradingOpportunity):
        """Execute a trading opportunity."""
        try:
            # Calculate position size
            ai_score = await self.ai_model.evaluate_opportunity(opportunity)
            position_size = await self.risk_manager.calculate_position_size(
                opportunity, self.portfolio, ai_score
            )
            
            # Create orders based on strategy
            if opportunity.strategy == TradingStrategy.ARBITRAGE:
                await self._execute_arbitrage(opportunity, position_size)
            elif opportunity.strategy == TradingStrategy.AI_PREDICTION:
                await self._execute_ai_trade(opportunity, position_size)
                
        except Exception as e:
            logger.error(f"Error executing opportunity {opportunity.id}: {e}")
            
    async def _execute_arbitrage(self, opportunity: TradingOpportunity, position_size: Decimal):
        """Execute arbitrage opportunity."""
        buy_exchange = opportunity.requirements["buy_exchange"]
        sell_exchange = opportunity.requirements["sell_exchange"]
        buy_price = opportunity.requirements["buy_price"]
        sell_price = opportunity.requirements["sell_price"]
        
        amount = position_size / buy_price
        
        # Create buy order
        buy_order = TradeOrder(
            id=f"buy_{opportunity.id}",
            pair=opportunity.pair,
            order_type=OrderType.MARKET,
            side="buy",
            amount=amount,
            price=buy_price,
            timestamp=datetime.now(),
            exchange=buy_exchange,
            strategy=opportunity.strategy
        )
        
        # Create sell order
        sell_order = TradeOrder(
            id=f"sell_{opportunity.id}",
            pair=opportunity.pair,
            order_type=OrderType.MARKET,
            side="sell",
            amount=amount,
            price=sell_price,
            timestamp=datetime.now(),
            exchange=sell_exchange,
            strategy=opportunity.strategy
        )
        
        # Execute orders simultaneously
        buy_success = await self.order_executor.execute_order(buy_order)
        sell_success = await self.order_executor.execute_order(sell_order)
        
        if buy_success and sell_success:
            profit = (sell_price - buy_price) * amount
            logger.info(f"Arbitrage executed successfully. Profit: {profit}")
            self._update_performance_metrics(profit, True)
        else:
            logger.warning(f"Arbitrage execution failed for {opportunity.id}")
            self._update_performance_metrics(Decimal('0'), False)
            
    async def _execute_ai_trade(self, opportunity: TradingOpportunity, position_size: Decimal):
        """Execute AI-predicted trade."""
        prediction = opportunity.requirements["prediction"]
        entry_price = opportunity.requirements["entry_price"]
        
        side = "buy" if prediction["direction"] == "up" else "sell"
        amount = position_size / entry_price
        
        order = TradeOrder(
            id=f"ai_{opportunity.id}",
            pair=opportunity.pair,
            order_type=OrderType.MEV_PROTECTED,
            side=side,
            amount=amount,
            price=entry_price,
            timestamp=datetime.now(),
            exchange="uniswap_v3",
            strategy=opportunity.strategy
        )
        
        success = await self.order_executor.execute_order(order)
        
        if success:
            logger.info(f"AI trade executed: {side} {amount} {opportunity.pair}")
        else:
            logger.warning(f"AI trade execution failed for {opportunity.id}")
            
    def _update_performance_metrics(self, profit: Decimal, profitable: bool):
        """Update trading performance metrics."""
        self.performance_metrics["total_trades"] += 1
        
        if profitable:
            self.performance_metrics["profitable_trades"] += 1
            
        self.performance_metrics["total_profit"] += profit
        self.performance_metrics["win_rate"] = (
            self.performance_metrics["profitable_trades"] / 
            self.performance_metrics["total_trades"]
        )
        
    async def _portfolio_monitoring_loop(self):
        """Monitor portfolio performance."""
        while self.running:
            try:
                await self._update_portfolio()
                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                logger.error(f"Error updating portfolio: {e}")
                await asyncio.sleep(120)
                
    async def _update_portfolio(self):
        """Update portfolio state."""
        # Simulate portfolio updates
        self.portfolio.last_updated = datetime.now()
        
        # Update balances based on executed trades
        total_value = Decimal('100000')  # Starting value
        for trade in self.order_executor.execution_history:
            if trade.status == "filled":
                if trade.side == "buy":
                    total_value -= trade.filled_amount * trade.price + trade.fees
                else:
                    total_value += trade.filled_amount * trade.price - trade.fees
                    
        self.portfolio.total_value_usd = total_value
        self.portfolio.profit_loss_24h = self.performance_metrics["total_profit"]
        
        if total_value > 0:
            self.portfolio.profit_loss_percentage = (
                self.performance_metrics["total_profit"] / total_value
            )
            
    async def get_performance_report(self) -> Dict[str, Any]:
        """Get detailed performance report."""
        return {
            "portfolio": {
                "total_value_usd": float(self.portfolio.total_value_usd),
                "profit_loss_24h": float(self.portfolio.profit_loss_24h),
                "profit_loss_percentage": float(self.portfolio.profit_loss_percentage)
            },
            "performance_metrics": {
                k: float(v) if isinstance(v, Decimal) else v
                for k, v in self.performance_metrics.items()
            },
            "active_orders": len(self.order_executor.active_orders),
            "completed_trades": len(self.order_executor.execution_history),
            "active_strategies": [s.value for s in self.active_strategies],
            "timestamp": datetime.now().isoformat()
        }

# Global trading engine instance
_trading_engine_instance: Optional[AITradingEngine] = None

async def initialize_trading_engine() -> AITradingEngine:
    """Initialize the AI trading engine."""
    global _trading_engine_instance
    
    if _trading_engine_instance is None:
        _trading_engine_instance = AITradingEngine()
        logger.info("AI Trading Engine initialized successfully")
        
    return _trading_engine_instance

def get_trading_engine_instance() -> Optional[AITradingEngine]:
    """Get the current trading engine instance."""
    return _trading_engine_instance

async def start_ai_trading():
    """Start the AI trading engine."""
    engine = await initialize_trading_engine()
    await engine.start_trading()

async def stop_ai_trading():
    """Stop the AI trading engine."""
    global _trading_engine_instance
    if _trading_engine_instance:
        await _trading_engine_instance.stop_trading()
        _trading_engine_instance = None

if __name__ == "__main__":
    # Example usage
    async def main():
        engine = await initialize_trading_engine()
        
        # Start trading
        await engine.start_trading()

    asyncio.run(main())

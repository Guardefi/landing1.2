import { httpClient } from './httpClient';

// Type definitions that match the backend
export interface TradingStrategy {
  id: string;
  name: string;
  status: 'active' | 'paused' | 'stopped';
  strategy_type: string;
  pnl: number;
  winRate: number;
  trades: number;
  allocation: number;
  confidence: number;
  risk_level: number;
}

export interface TradingOpportunity {
  id: string;
  strategy: string;
  pair: string;
  expected_profit: number;
  profit_percentage: number;
  confidence: number;
  risk_level: number;
  execution_time: number; // in seconds
  exchanges: string[];
  requirements: Record<string, any>;
  timestamp: string;
  expires_at: string;
}

export interface MarketData {
  pair: string;
  price: number;
  volume_24h: number;
  bid: number;
  ask: number;
  spread: number;
  timestamp: string;
  exchange: string;
  liquidity: number;
  volatility: number;
}

export interface Portfolio {
  balances: Record<string, number>;
  total_value_usd: number;
  profit_loss_24h: number;
  profit_loss_percentage: number;
  active_positions: any[];
  trade_count_24h: number;
  last_updated: string;
}

export interface PerformanceReport {
  portfolio: {
    total_value_usd: number;
    profit_loss_24h: number;
    profit_loss_percentage: number;
  };
  performance_metrics: {
    total_trades: number;
    profitable_trades: number;
    total_profit: number;
    max_drawdown: number;
    sharpe_ratio: number;
    win_rate: number;
  };
  active_orders: number;
  completed_trades: number;
  active_strategies: string[];
  timestamp: string;
}

export interface TradeOrder {
  id: string;
  pair: string;
  order_type: string;
  side: string;
  amount: number;
  price: number;
  timestamp: string;
  status: string;
  filled_amount: number;
  fees: number;
  exchange?: string;
  strategy?: string;
}

export interface AIPrediction {
  direction: 'up' | 'down';
  magnitude: number;
  confidence: number;
  timeframe: number;
  timestamp: string;
  model_version: string;
}

class AITradingApiService {
  private baseUrl = '/api/ai-trading';

  // Engine Control
  async startTradingEngine(): Promise<{ success: boolean; message: string }> {
    try {
      const response = await httpClient.post(`${this.baseUrl}/start`);
      return response.data;
    } catch (error) {
      console.error('Error starting trading engine:', error);
      throw error;
    }
  }

  async stopTradingEngine(): Promise<{ success: boolean; message: string }> {
    try {
      const response = await httpClient.post(`${this.baseUrl}/stop`);
      return response.data;
    } catch (error) {
      console.error('Error stopping trading engine:', error);
      throw error;
    }
  }

  async getEngineStatus(): Promise<{ running: boolean; uptime: number }> {
    try {
      const response = await httpClient.get(`${this.baseUrl}/status`);
      return response.data;
    } catch (error) {
      console.error('Error getting engine status:', error);
      throw error;
    }
  }

  // Performance and Portfolio
  async getPerformanceReport(): Promise<PerformanceReport> {
    try {
      const response = await httpClient.get(`${this.baseUrl}/performance`);
      return response.data;
    } catch (error) {
      console.error('Error fetching performance report:', error);
      throw error;
    }
  }

  async getPortfolio(): Promise<Portfolio> {
    try {
      const response = await httpClient.get(`${this.baseUrl}/portfolio`);
      return response.data;
    } catch (error) {
      console.error('Error fetching portfolio:', error);
      throw error;
    }
  }

  // Trading Opportunities
  async getTradingOpportunities(): Promise<TradingOpportunity[]> {
    try {
      const response = await httpClient.get(`${this.baseUrl}/opportunities`);
      return response.data;
    } catch (error) {
      console.error('Error fetching trading opportunities:', error);
      throw error;
    }
  }

  async getArbitrageOpportunities(): Promise<TradingOpportunity[]> {
    try {
      const response = await httpClient.get(`${this.baseUrl}/opportunities/arbitrage`);
      return response.data;
    } catch (error) {
      console.error('Error fetching arbitrage opportunities:', error);
      throw error;
    }
  }

  // Market Data
  async getMarketData(pair?: string): Promise<MarketData[]> {
    try {
      const url = pair
        ? `${this.baseUrl}/market-data/${pair}`
        : `${this.baseUrl}/market-data`;
      const response = await httpClient.get(url);
      return response.data;
    } catch (error) {
      console.error('Error fetching market data:', error);
      throw error;
    }
  }

  async getPriceHistory(
    pair: string,
    periods: number = 100,
  ): Promise<Array<{ timestamp: string; price: number }>> {
    try {
      const response = await httpClient.get(
        `${this.baseUrl}/market-data/${pair}/history`,
        {
          params: { periods },
        },
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching price history:', error);
      throw error;
    }
  }

  // AI Predictions
  async getAIPrediction(pair: string, timeframe: number): Promise<AIPrediction> {
    try {
      const response = await httpClient.post(`${this.baseUrl}/ai/predict`, {
        pair,
        timeframe,
      });
      return response.data;
    } catch (error) {
      console.error('Error getting AI prediction:', error);
      throw error;
    }
  }

  // Strategy Management
  async getActiveStrategies(): Promise<string[]> {
    try {
      const response = await httpClient.get(`${this.baseUrl}/strategies/active`);
      return response.data;
    } catch (error) {
      console.error('Error fetching active strategies:', error);
      throw error;
    }
  }

  async updateStrategyStatus(
    strategy: string,
    enabled: boolean,
  ): Promise<{ success: boolean }> {
    try {
      const response = await httpClient.put(`${this.baseUrl}/strategies/${strategy}`, {
        enabled,
      });
      return response.data;
    } catch (error) {
      console.error('Error updating strategy status:', error);
      throw error;
    }
  }

  // Orders and Trades
  async getActiveOrders(): Promise<TradeOrder[]> {
    try {
      const response = await httpClient.get(`${this.baseUrl}/orders/active`);
      return response.data;
    } catch (error) {
      console.error('Error fetching active orders:', error);
      throw error;
    }
  }

  async getTradeHistory(limit: number = 50): Promise<TradeOrder[]> {
    try {
      const response = await httpClient.get(`${this.baseUrl}/orders/history`, {
        params: { limit },
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching trade history:', error);
      throw error;
    }
  }

  async cancelOrder(orderId: string): Promise<{ success: boolean }> {
    try {
      const response = await httpClient.delete(`${this.baseUrl}/orders/${orderId}`);
      return response.data;
    } catch (error) {
      console.error('Error cancelling order:', error);
      throw error;
    }
  }

  // Risk Management
  async getRiskParameters(): Promise<{
    max_position_size: number;
    max_daily_loss: number;
    max_drawdown: number;
  }> {
    try {
      const response = await httpClient.get(`${this.baseUrl}/risk/parameters`);
      return response.data;
    } catch (error) {
      console.error('Error fetching risk parameters:', error);
      throw error;
    }
  }

  async updateRiskParameters(params: {
    max_position_size?: number;
    max_daily_loss?: number;
    max_drawdown?: number;
  }): Promise<{ success: boolean }> {
    try {
      const response = await httpClient.put(`${this.baseUrl}/risk/parameters`, params);
      return response.data;
    } catch (error) {
      console.error('Error updating risk parameters:', error);
      throw error;
    }
  }

  // Real-time Data Subscription
  async subscribeToUpdates(callback: (data: any) => void): Promise<() => void> {
    // This would typically use WebSocket or Server-Sent Events
    // For now, we'll implement polling
    const interval = setInterval(async () => {
      try {
        const [performance, opportunities, portfolio] = await Promise.all([
          this.getPerformanceReport(),
          this.getTradingOpportunities(),
          this.getPortfolio(),
        ]);

        callback({
          type: 'update',
          data: {
            performance,
            opportunities,
            portfolio,
            timestamp: new Date().toISOString(),
          },
        });
      } catch (error) {
        console.error('Error in real-time update:', error);
      }
    }, 5000); // Poll every 5 seconds

    // Return unsubscribe function
    return () => clearInterval(interval);
  }

  // Utility Methods
  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(amount);
  }

  formatPercentage(value: number): string {
    return `${(value * 100).toFixed(2)}%`;
  }

  getStrategyDisplayName(strategy: string): string {
    const strategyNames: Record<string, string> = {
      arbitrage: 'Cross-DEX Arbitrage',
      mev_protection: 'MEV Protection',
      liquidity_provision: 'Liquidity Provision',
      momentum: 'Momentum Trading',
      mean_reversion: 'Mean Reversion',
      grid_trading: 'Grid Trading',
      ai_prediction: 'AI Prediction',
      flash_loan: 'Flash Loan Arbitrage',
    };
    return strategyNames[strategy] || strategy;
  }

  getRiskColor(riskLevel: number): string {
    if (riskLevel >= 0.7) return 'text-red-500';
    if (riskLevel >= 0.4) return 'text-yellow-500';
    return 'text-green-500';
  }

  getStatusColor(status: string): string {
    switch (status) {
      case 'active':
        return 'bg-green-500';
      case 'paused':
        return 'bg-yellow-500';
      case 'stopped':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  }
}

export const aiTradingApi = new AITradingApiService();

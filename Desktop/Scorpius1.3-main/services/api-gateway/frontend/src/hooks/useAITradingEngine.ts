import { useState, useEffect, useCallback, useRef } from 'react';
import {
  aiTradingApi,
  PerformanceReport,
  TradingOpportunity,
  Portfolio,
  TradeOrder,
  MarketData,
} from '../services/aiTradingApi';

interface AITradingEngineState {
  // Engine status
  isRunning: boolean;
  uptime: number;

  // Performance data
  performance: PerformanceReport | null;
  portfolio: Portfolio | null;

  // Trading data
  opportunities: TradingOpportunity[];
  activeOrders: TradeOrder[];
  tradeHistory: TradeOrder[];
  marketData: MarketData[];

  // Strategy data
  activeStrategies: string[];

  // Loading states
  loading: {
    engine: boolean;
    performance: boolean;
    opportunities: boolean;
    orders: boolean;
    marketData: boolean;
  };

  // Error states
  errors: {
    engine: string | null;
    performance: string | null;
    opportunities: string | null;
    orders: string | null;
    marketData: string | null;
  };

  // Last update timestamp
  lastUpdated: string | null;
}

const initialState: AITradingEngineState = {
  isRunning: false,
  uptime: 0,
  performance: null,
  portfolio: null,
  opportunities: [],
  activeOrders: [],
  tradeHistory: [],
  marketData: [],
  activeStrategies: [],
  loading: {
    engine: false,
    performance: false,
    opportunities: false,
    orders: false,
    marketData: false,
  },
  errors: {
    engine: null,
    performance: null,
    opportunities: null,
    orders: null,
    marketData: null,
  },
  lastUpdated: null,
};

export function useAITradingEngine() {
  const [state, setState] = useState<AITradingEngineState>(initialState);
  const unsubscribeRef = useRef<(() => void) | null>(null);

  // Helper function to update loading state
  const setLoading = useCallback(
    (key: keyof AITradingEngineState['loading'], value: boolean) => {
      setState(prev => ({
        ...prev,
        loading: { ...prev.loading, [key]: value },
      }));
    },
    [],
  );

  // Helper function to update error state
  const setError = useCallback(
    (key: keyof AITradingEngineState['errors'], value: string | null) => {
      setState(prev => ({
        ...prev,
        errors: { ...prev.errors, [key]: value },
      }));
    },
    [],
  );

  // Engine control functions
  const startEngine = useCallback(async () => {
    try {
      setLoading('engine', true);
      setError('engine', null);

      const result = await aiTradingApi.startTradingEngine();
      if (result.success) {
        setState(prev => ({ ...prev, isRunning: true }));
      }
      return result;
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to start engine';
      setError('engine', errorMessage);
      throw error;
    } finally {
      setLoading('engine', false);
    }
  }, [setLoading, setError]);

  const stopEngine = useCallback(async () => {
    try {
      setLoading('engine', true);
      setError('engine', null);

      const result = await aiTradingApi.stopTradingEngine();
      if (result.success) {
        setState(prev => ({ ...prev, isRunning: false }));
      }
      return result;
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to stop engine';
      setError('engine', errorMessage);
      throw error;
    } finally {
      setLoading('engine', false);
    }
  }, [setLoading, setError]);

  // Data fetching functions
  const fetchPerformance = useCallback(async () => {
    try {
      setLoading('performance', true);
      setError('performance', null);

      const performance = await aiTradingApi.getPerformanceReport();
      const portfolio = await aiTradingApi.getPortfolio();

      setState(prev => ({
        ...prev,
        performance,
        portfolio,
        lastUpdated: new Date().toISOString(),
      }));
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to fetch performance data';
      setError('performance', errorMessage);
      console.error('Error fetching performance:', error);
    } finally {
      setLoading('performance', false);
    }
  }, [setLoading, setError]);

  const fetchOpportunities = useCallback(async () => {
    try {
      setLoading('opportunities', true);
      setError('opportunities', null);

      const opportunities = await aiTradingApi.getTradingOpportunities();

      setState(prev => ({
        ...prev,
        opportunities,
        lastUpdated: new Date().toISOString(),
      }));
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to fetch opportunities';
      setError('opportunities', errorMessage);
      console.error('Error fetching opportunities:', error);
    } finally {
      setLoading('opportunities', false);
    }
  }, [setLoading, setError]);

  const fetchOrders = useCallback(async () => {
    try {
      setLoading('orders', true);
      setError('orders', null);

      const [activeOrders, tradeHistory] = await Promise.all([
        aiTradingApi.getActiveOrders(),
        aiTradingApi.getTradeHistory(50),
      ]);

      setState(prev => ({
        ...prev,
        activeOrders,
        tradeHistory,
        lastUpdated: new Date().toISOString(),
      }));
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to fetch orders';
      setError('orders', errorMessage);
      console.error('Error fetching orders:', error);
    } finally {
      setLoading('orders', false);
    }
  }, [setLoading, setError]);

  const fetchMarketData = useCallback(async () => {
    try {
      setLoading('marketData', true);
      setError('marketData', null);

      const marketData = await aiTradingApi.getMarketData();

      setState(prev => ({
        ...prev,
        marketData,
        lastUpdated: new Date().toISOString(),
      }));
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to fetch market data';
      setError('marketData', errorMessage);
      console.error('Error fetching market data:', error);
    } finally {
      setLoading('marketData', false);
    }
  }, [setLoading, setError]);

  const fetchEngineStatus = useCallback(async () => {
    try {
      const status = await aiTradingApi.getEngineStatus();
      const strategies = await aiTradingApi.getActiveStrategies();

      setState(prev => ({
        ...prev,
        isRunning: status.running,
        uptime: status.uptime,
        activeStrategies: strategies,
        lastUpdated: new Date().toISOString(),
      }));
    } catch (error) {
      console.error('Error fetching engine status:', error);
    }
  }, []);

  // Strategy management
  const toggleStrategy = useCallback(
    async (strategy: string, enabled: boolean) => {
      try {
        await aiTradingApi.updateStrategyStatus(strategy, enabled);
        await fetchEngineStatus(); // Refresh strategies
      } catch (error) {
        console.error('Error toggling strategy:', error);
        throw error;
      }
    },
    [fetchEngineStatus],
  );

  // Order management
  const cancelOrder = useCallback(
    async (orderId: string) => {
      try {
        await aiTradingApi.cancelOrder(orderId);
        await fetchOrders(); // Refresh orders
      } catch (error) {
        console.error('Error cancelling order:', error);
        throw error;
      }
    },
    [fetchOrders],
  );

  // Initialize data and real-time updates
  const initialize = useCallback(async () => {
    await Promise.all([
      fetchEngineStatus(),
      fetchPerformance(),
      fetchOpportunities(),
      fetchOrders(),
      fetchMarketData(),
    ]);
  }, [
    fetchEngineStatus,
    fetchPerformance,
    fetchOpportunities,
    fetchOrders,
    fetchMarketData,
  ]);

  const startRealTimeUpdates = useCallback(async () => {
    if (unsubscribeRef.current) {
      unsubscribeRef.current();
    }

    try {
      const unsubscribe = await aiTradingApi.subscribeToUpdates(data => {
        if (data.type === 'update') {
          setState(prev => ({
            ...prev,
            performance: data.data.performance,
            opportunities: data.data.opportunities,
            portfolio: data.data.portfolio,
            lastUpdated: data.data.timestamp,
          }));
        }
      });

      unsubscribeRef.current = unsubscribe;
    } catch (error) {
      console.error('Error starting real-time updates:', error);
    }
  }, []);

  const stopRealTimeUpdates = useCallback(() => {
    if (unsubscribeRef.current) {
      unsubscribeRef.current();
      unsubscribeRef.current = null;
    }
  }, []);

  // Initialize on mount
  useEffect(() => {
    initialize();
    startRealTimeUpdates();

    return () => {
      stopRealTimeUpdates();
    };
  }, [initialize, startRealTimeUpdates, stopRealTimeUpdates]);

  // Computed values
  const totalPnL = state.performance?.portfolio.profit_loss_24h || 0;
  const totalValue = state.performance?.portfolio.total_value_usd || 0;
  const winRate = state.performance?.performance_metrics.win_rate || 0;
  const totalTrades = state.performance?.performance_metrics.total_trades || 0;

  // Format helpers
  const formatCurrency = aiTradingApi.formatCurrency;
  const formatPercentage = aiTradingApi.formatPercentage;

  return {
    // State
    ...state,

    // Computed values
    totalPnL,
    totalValue,
    winRate,
    totalTrades,

    // Actions
    startEngine,
    stopEngine,
    toggleStrategy,
    cancelOrder,

    // Data refresh
    refresh: {
      performance: fetchPerformance,
      opportunities: fetchOpportunities,
      orders: fetchOrders,
      marketData: fetchMarketData,
      status: fetchEngineStatus,
      all: initialize,
    },

    // Real-time controls
    startRealTimeUpdates,
    stopRealTimeUpdates,

    // Utilities
    formatCurrency,
    formatPercentage,
  };
}

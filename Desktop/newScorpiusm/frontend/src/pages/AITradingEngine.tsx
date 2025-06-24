import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Switch } from '@/components/ui/switch';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Target,
  Zap,
  BarChart3,
  Play,
  Pause,
  Settings,
  AlertTriangle,
  RefreshCw,
  Clock,
} from 'lucide-react';
import { useAITradingEngine } from '@/hooks/useAITradingEngine';
import { aiTradingApi } from '@/services/aiTradingApi';

interface TradingStrategy {
  id: string;
  name: string;
  status: 'active' | 'paused' | 'stopped';
  pnl: number;
  winRate: number;
  trades: number;
  allocation: number;
}

interface ArbitrageOpportunity {
  id: string;
  tokenPair: string;
  exchange1: string;
  exchange2: string;
  profitMargin: number;
  volume: number;
  timeLeft: number;
}

export default function AITradingEngine() {
  const {
    isRunning,
    uptime,
    performance,
    portfolio,
    opportunities,
    activeOrders,
    tradeHistory,
    activeStrategies,
    loading,
    errors,
    lastUpdated,
    totalPnL,
    totalValue,
    winRate,
    totalTrades,
    startEngine,
    stopEngine,
    toggleStrategy,
    refresh,
    formatCurrency,
    formatPercentage,
  } = useAITradingEngine();

  // Engine control handlers
  const handleEngineToggle = async () => {
    try {
      if (isRunning) {
        await stopEngine();
      } else {
        await startEngine();
      }
    } catch (error) {
      console.error('Error toggling engine:', error);
    }
  };

  const handleStrategyToggle = async (strategy: string) => {
    try {
      const isActive = activeStrategies.includes(strategy);
      await toggleStrategy(strategy, !isActive);
    } catch (error) {
      console.error('Error toggling strategy:', error);
    }
  };

  const getStatusColor = (status: string) => {
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
  };

  // Convert backend opportunities to frontend format
  const formattedOpportunities: ArbitrageOpportunity[] = opportunities.map(opp => ({
    id: opp.id,
    tokenPair: opp.pair,
    exchange1: opp.exchanges[0] || 'N/A',
    exchange2: opp.exchanges[1] || 'N/A',
    profitMargin: opp.profit_percentage * 100,
    volume: opp.expected_profit,
    timeLeft: Math.max(0, new Date(opp.expires_at).getTime() - Date.now()) / 1000,
  }));

  // Convert backend strategies to frontend format
  const formattedStrategies: TradingStrategy[] = activeStrategies.map(
    (strategy, index) => ({
      id: strategy,
      name: aiTradingApi.getStrategyDisplayName(strategy),
      status: 'active' as const,
      pnl: performance?.performance_metrics.total_profit || 0,
      winRate: (performance?.performance_metrics.win_rate || 0) * 100,
      trades: Math.floor(
        (performance?.performance_metrics.total_trades || 0) / activeStrategies.length,
      ),
      allocation: Math.floor(100 / activeStrategies.length),
    }),
  );

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #181a1b 0%, #004242 50%, #181a1b 100%)',
        padding: '24px',
        fontFamily: 'ui-monospace, SFMono-Regular, monospace',
      }}
    >
      <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
        {/* Header */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '32px',
          }}
        >
          <div>
            <h1
              style={{
                fontSize: '32px',
                fontWeight: '700',
                color: '#00ff88',
                letterSpacing: '2px',
                textShadow: '0 0 20px rgba(0, 255, 136, 0.6)',
                marginBottom: '8px',
              }}
            >
              AI TRADING ENGINE
            </h1>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <p style={{ color: '#a8a095', letterSpacing: '1px' }}>
                Intelligent MEV protection and arbitrage opportunities
              </p>
              {lastUpdated && (
                <span style={{ color: '#666', fontSize: '12px' }}>
                  <Clock className="inline h-3 w-3 mr-1" />
                  Last updated: {new Date(lastUpdated).toLocaleTimeString()}
                </span>
              )}
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '14px', color: '#cccccc' }}>Engine Status:</span>
              <Badge variant={isRunning ? 'default' : 'secondary'}>
                {isRunning ? 'RUNNING' : 'STOPPED'}
              </Badge>
            </div>
            <Button
              onClick={handleEngineToggle}
              disabled={loading.engine}
              style={{
                background: isRunning
                  ? 'linear-gradient(135deg, #ff4444, #ff6666)'
                  : 'linear-gradient(135deg, #00ff88, #00ffff)',
                border: 'none',
                color: isRunning ? '#fff' : '#000',
              }}
            >
              {loading.engine ? (
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              ) : isRunning ? (
                <Pause className="h-4 w-4 mr-2" />
              ) : (
                <Play className="h-4 w-4 mr-2" />
              )}
              {isRunning ? 'Stop Engine' : 'Start Engine'}
            </Button>
            <Button
              variant="outline"
              onClick={() => refresh.all()}
              disabled={Object.values(loading).some(Boolean)}
            >
              <RefreshCw
                className={`h-4 w-4 mr-2 ${
                  Object.values(loading).some(Boolean) ? 'animate-spin' : ''
                }`}
              />
              Refresh
            </Button>
          </div>
        </div>

        {/* Error Alerts */}
        {Object.values(errors).some(error => error) && (
          <div style={{ marginBottom: '24px' }}>
            {Object.entries(errors).map(
              ([key, error]) =>
                error && (
                  <Alert
                    key={key}
                    style={{
                      marginBottom: '8px',
                      backgroundColor: 'rgba(239, 68, 68, 0.1)',
                      border: '1px solid rgba(239, 68, 68, 0.3)',
                    }}
                  >
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription style={{ color: '#ef4444' }}>
                      {key}: {error}
                    </AlertDescription>
                  </Alert>
                ),
            )}
          </div>
        )}

        {/* Performance Overview */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '24px',
            marginBottom: '32px',
          }}
        >
          <Card
            style={{
              background:
                'linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 0, 0, 0.2))',
              border: '1px solid rgba(0, 255, 136, 0.3)',
            }}
          >
            <CardHeader
              style={{
                display: 'flex',
                flexDirection: 'row',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingBottom: '8px',
              }}
            >
              <CardTitle
                style={{
                  fontSize: '14px',
                  fontWeight: '500',
                  color: '#cccccc',
                }}
              >
                Total P&L (24h)
              </CardTitle>
              {totalPnL >= 0 ? (
                <TrendingUp className="h-4 w-4" style={{ color: '#00ff88' }} />
              ) : (
                <TrendingDown className="h-4 w-4" style={{ color: '#ef4444' }} />
              )}
            </CardHeader>
            <CardContent>
              <div
                style={{
                  fontSize: '24px',
                  fontWeight: '700',
                  color: totalPnL >= 0 ? '#00ff88' : '#ef4444',
                }}
              >
                {formatCurrency(totalPnL)}
              </div>
              <p style={{ fontSize: '12px', color: '#888', marginTop: '4px' }}>
                {portfolio ? formatPercentage(portfolio.profit_loss_percentage) : 'N/A'}{' '}
                from total portfolio
              </p>
            </CardContent>
          </Card>

          <Card
            style={{
              background:
                'linear-gradient(135deg, rgba(0, 255, 255, 0.1), rgba(0, 0, 0, 0.2))',
              border: '1px solid rgba(0, 255, 255, 0.3)',
            }}
          >
            <CardHeader
              style={{
                display: 'flex',
                flexDirection: 'row',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingBottom: '8px',
              }}
            >
              <CardTitle
                style={{
                  fontSize: '14px',
                  fontWeight: '500',
                  color: '#cccccc',
                }}
              >
                Win Rate
              </CardTitle>
              <Target className="h-4 w-4" style={{ color: '#00ffff' }} />
            </CardHeader>
            <CardContent>
              <div
                style={{
                  fontSize: '24px',
                  fontWeight: '700',
                  color: '#00ffff',
                }}
              >
                {formatPercentage(winRate)}
              </div>
              <p style={{ fontSize: '12px', color: '#888', marginTop: '4px' }}>
                Across all strategies
              </p>
            </CardContent>
          </Card>

          <Card
            style={{
              background:
                'linear-gradient(135deg, rgba(147, 51, 234, 0.1), rgba(0, 0, 0, 0.2))',
              border: '1px solid rgba(147, 51, 234, 0.3)',
            }}
          >
            <CardHeader
              style={{
                display: 'flex',
                flexDirection: 'row',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingBottom: '8px',
              }}
            >
              <CardTitle
                style={{
                  fontSize: '14px',
                  fontWeight: '500',
                  color: '#cccccc',
                }}
              >
                Total Trades
              </CardTitle>
              <BarChart3 className="h-4 w-4" style={{ color: '#9333ea' }} />
            </CardHeader>
            <CardContent>
              <div
                style={{
                  fontSize: '24px',
                  fontWeight: '700',
                  color: '#9333ea',
                }}
              >
                {totalTrades}
              </div>
              <p style={{ fontSize: '12px', color: '#888', marginTop: '4px' }}>
                Total executed
              </p>
            </CardContent>
          </Card>

          <Card
            style={{
              background:
                'linear-gradient(135deg, rgba(255, 165, 0, 0.1), rgba(0, 0, 0, 0.2))',
              border: '1px solid rgba(255, 165, 0, 0.3)',
            }}
          >
            <CardHeader
              style={{
                display: 'flex',
                flexDirection: 'row',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingBottom: '8px',
              }}
            >
              <CardTitle
                style={{
                  fontSize: '14px',
                  fontWeight: '500',
                  color: '#cccccc',
                }}
              >
                Portfolio Value
              </CardTitle>
              <DollarSign className="h-4 w-4" style={{ color: '#ffa500' }} />
            </CardHeader>
            <CardContent>
              <div
                style={{
                  fontSize: '24px',
                  fontWeight: '700',
                  color: '#ffa500',
                }}
              >
                {formatCurrency(totalValue)}
              </div>
              <p style={{ fontSize: '12px', color: '#888', marginTop: '4px' }}>
                Current total value
              </p>
            </CardContent>
          </Card>
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '24px',
            marginBottom: '32px',
          }}
        >
          {/* Active Strategies */}
          <Card
            style={{
              background: 'rgba(0, 0, 0, 0.6)',
              border: '1px solid rgba(0, 255, 136, 0.3)',
            }}
          >
            <CardHeader>
              <CardTitle
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  color: '#00ff88',
                }}
              >
                <Target className="h-5 w-5" />
                <span>Active Trading Strategies</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading.performance ? (
                <div
                  style={{
                    color: '#888',
                    textAlign: 'center',
                    padding: '20px',
                  }}
                >
                  <RefreshCw className="h-6 w-6 animate-spin mx-auto mb-2" />
                  Loading strategies...
                </div>
              ) : formattedStrategies.length > 0 ? (
                <div
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '16px',
                  }}
                >
                  {formattedStrategies.map(strategy => (
                    <div
                      key={strategy.id}
                      style={{
                        padding: '16px',
                        borderRadius: '8px',
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                        background: 'rgba(0, 0, 0, 0.3)',
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          marginBottom: '12px',
                        }}
                      >
                        <div
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px',
                          }}
                        >
                          <div
                            style={{
                              width: '12px',
                              height: '12px',
                              borderRadius: '50%',
                            }}
                            className={getStatusColor(strategy.status)}
                          />
                          <h3 style={{ fontWeight: '500', color: '#ffffff' }}>
                            {strategy.name}
                          </h3>
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => toggleStrategy(strategy.id)}
                          style={{ padding: '4px 8px' }}
                        >
                          {strategy.status === 'active' ? (
                            <Pause className="h-4 w-4" />
                          ) : (
                            <Play className="h-4 w-4" />
                          )}
                        </Button>
                      </div>

                      <div
                        style={{
                          display: 'grid',
                          gridTemplateColumns: '1fr 1fr',
                          gap: '16px',
                          fontSize: '14px',
                        }}
                      >
                        <div>
                          <p style={{ color: '#888' }}>P&L</p>
                          <p
                            style={{
                              fontWeight: '700',
                              color: strategy.pnl >= 0 ? '#00ff88' : '#ff4444',
                            }}
                          >
                            {formatCurrency(strategy.pnl)}
                          </p>
                        </div>
                        <div>
                          <p style={{ color: '#888' }}>Win Rate</p>
                          <p style={{ fontWeight: '700', color: '#ffffff' }}>
                            {strategy.winRate}%
                          </p>
                        </div>
                        <div>
                          <p style={{ color: '#888' }}>Trades</p>
                          <p style={{ fontWeight: '700', color: '#ffffff' }}>
                            {strategy.trades}
                          </p>
                        </div>
                        <div>
                          <p style={{ color: '#888' }}>Allocation</p>
                          <p style={{ fontWeight: '700', color: '#ffffff' }}>
                            {strategy.allocation}%
                          </p>
                        </div>
                      </div>

                      <div style={{ marginTop: '12px' }}>
                        <div
                          style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            fontSize: '12px',
                            marginBottom: '4px',
                          }}
                        >
                          <span style={{ color: '#888' }}>Capital Allocation</span>
                          <span style={{ color: '#888' }}>{strategy.allocation}%</span>
                        </div>
                        <Progress
                          value={strategy.allocation}
                          style={{ height: '8px' }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div
                  style={{
                    color: '#888',
                    textAlign: 'center',
                    padding: '20px',
                  }}
                >
                  No active strategies found
                </div>
              )}
            </CardContent>
          </Card>

          {/* Arbitrage Opportunities */}
          <Card
            style={{
              background: 'rgba(0, 0, 0, 0.6)',
              border: '1px solid rgba(0, 255, 255, 0.3)',
            }}
          >
            <CardHeader>
              <CardTitle
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  color: '#00ffff',
                }}
              >
                <TrendingUp className="h-5 w-5" />
                <span>Live Arbitrage Opportunities</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading.opportunities ? (
                <div
                  style={{
                    color: '#888',
                    textAlign: 'center',
                    padding: '20px',
                  }}
                >
                  <RefreshCw className="h-6 w-6 animate-spin mx-auto mb-2" />
                  Loading opportunities...
                </div>
              ) : formattedOpportunities.length > 0 ? (
                <div
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '16px',
                  }}
                >
                  {formattedOpportunities.map(opportunity => (
                    <div
                      key={opportunity.id}
                      style={{
                        padding: '16px',
                        borderRadius: '8px',
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                        background: 'rgba(0, 0, 0, 0.3)',
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          marginBottom: '12px',
                        }}
                      >
                        <div>
                          <h3 style={{ fontWeight: '500', color: '#ffffff' }}>
                            {opportunity.tokenPair}
                          </h3>
                          <p style={{ fontSize: '14px', color: '#888' }}>
                            {opportunity.exchange1} → {opportunity.exchange2}
                          </p>
                        </div>
                        <Badge
                          style={{
                            color: '#00ff88',
                            borderColor: '#00ff88',
                            background: 'rgba(0, 255, 136, 0.1)',
                          }}
                        >
                          +{opportunity.profitMargin}%
                        </Badge>
                      </div>

                      <div
                        style={{
                          display: 'grid',
                          gridTemplateColumns: '1fr 1fr',
                          gap: '16px',
                          fontSize: '14px',
                          marginBottom: '12px',
                        }}
                      >
                        <div>
                          <p style={{ color: '#888' }}>Volume</p>
                          <p style={{ fontWeight: '700', color: '#ffffff' }}>
                            {formatCurrency(opportunity.volume)}
                          </p>
                        </div>
                        <div>
                          <p style={{ color: '#888' }}>Time Left</p>
                          <p style={{ fontWeight: '700', color: '#ffffff' }}>
                            {opportunity.timeLeft}s
                          </p>
                        </div>
                      </div>

                      <div
                        style={{
                          display: 'flex',
                          gap: '8px',
                          marginBottom: '8px',
                        }}
                      >
                        <Button
                          size="sm"
                          style={{
                            flex: 1,
                            background: 'linear-gradient(135deg, #00ff88, #00ffff)',
                            border: 'none',
                            color: '#000',
                          }}
                        >
                          Execute Trade
                        </Button>
                        <Button variant="outline" size="sm">
                          Details
                        </Button>
                      </div>

                      <Progress
                        value={((60 - opportunity.timeLeft) / 60) * 100}
                        style={{ height: '4px' }}
                      />
                    </div>
                  ))}
                </div>
              ) : (
                <div
                  style={{
                    color: '#888',
                    textAlign: 'center',
                    padding: '20px',
                  }}
                >
                  No arbitrage opportunities found
                </div>
              )}

              <div
                style={{
                  marginTop: '16px',
                  padding: '12px',
                  background: 'rgba(255, 170, 0, 0.1)',
                  border: '1px solid rgba(255, 170, 0, 0.3)',
                  borderRadius: '8px',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    fontSize: '14px',
                  }}
                >
                  <Zap className="h-4 w-4" style={{ color: '#ffaa00' }} />
                  <span style={{ fontWeight: '500', color: '#ffaa00' }}>
                    MEV Protection Active
                  </span>
                </div>
                <p style={{ fontSize: '12px', color: '#888', marginTop: '4px' }}>
                  Real-time monitoring for sandwich attacks and front-running
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Portfolio Analytics */}
        <Card
          style={{
            background: 'rgba(0, 0, 0, 0.6)',
            border: '1px solid rgba(0, 255, 136, 0.3)',
          }}
        >
          <CardHeader>
            <CardTitle style={{ color: '#00ff88' }}>Portfolio Risk Metrics</CardTitle>
          </CardHeader>
          <CardContent>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '24px',
              }}
            >
              <div style={{ textAlign: 'center' }}>
                <p
                  style={{
                    fontSize: '14px',
                    fontWeight: '500',
                    color: '#cccccc',
                    marginBottom: '8px',
                  }}
                >
                  Value at Risk (VaR)
                </p>
                <p
                  style={{
                    fontSize: '24px',
                    fontWeight: '700',
                    color: '#ffffff',
                  }}
                >
                  2.3%
                </p>
                <p style={{ fontSize: '12px', color: '#888' }}>95% confidence, 1-day</p>
              </div>
              <div style={{ textAlign: 'center' }}>
                <p
                  style={{
                    fontSize: '14px',
                    fontWeight: '500',
                    color: '#cccccc',
                    marginBottom: '8px',
                  }}
                >
                  Maximum Drawdown
                </p>
                <p
                  style={{
                    fontSize: '24px',
                    fontWeight: '700',
                    color: '#ff4444',
                  }}
                >
                  -5.7%
                </p>
                <p style={{ fontSize: '12px', color: '#888' }}>Peak to trough</p>
              </div>
              <div style={{ textAlign: 'center' }}>
                <p
                  style={{
                    fontSize: '14px',
                    fontWeight: '500',
                    color: '#cccccc',
                    marginBottom: '8px',
                  }}
                >
                  Beta
                </p>
                <p
                  style={{
                    fontSize: '24px',
                    fontWeight: '700',
                    color: '#ffffff',
                  }}
                >
                  0.82
                </p>
                <p style={{ fontSize: '12px', color: '#888' }}>vs market</p>
              </div>
              <div style={{ textAlign: 'center' }}>
                <p
                  style={{
                    fontSize: '14px',
                    fontWeight: '500',
                    color: '#cccccc',
                    marginBottom: '8px',
                  }}
                >
                  Alpha
                </p>
                <p
                  style={{
                    fontSize: '24px',
                    fontWeight: '700',
                    color: '#00ff88',
                  }}
                >
                  +4.2%
                </p>
                <p style={{ fontSize: '12px', color: '#888' }}>Annualized</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

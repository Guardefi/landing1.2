import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Activity,
  Radio,
  Zap,
  TrendingUp,
  Shield,
  AlertTriangle,
  Database,
  Network,
  Eye,
  Clock,
  BarChart3,
  TrendingDown,
  CheckCircle,
  XCircle,
  RefreshCw,
  Wifi,
  WifiOff,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { LiveCounter } from '@/components/ui/live-counter';
import { ScrollReveal, StaggeredReveal } from '@/components/ui/scroll-reveal';
import { Badge } from '@/components/ui/badge';
import { useRealtimeConnection } from '@/hooks/useRealtimeConnection';

const RealTime = () => {
  const { socket, connected, data } = useRealtimeConnection();
  const [activeTab, setActiveTab] = useState<
    'overview' | 'threats' | 'trading' | 'bridge' | 'analytics'
  >('overview');

  // Mock data for when real backend data isn't available
  const mockData = {
    systemStatus: {
      cpu_usage: Math.floor(Math.random() * 40) + 30,
      memory_usage: Math.floor(Math.random() * 50) + 40,
      network_latency: Math.floor(Math.random() * 10) + 5,
      active_connections: Math.floor(Math.random() * 100) + 50,
      uptime: '72h 15m',
      status: connected ? 'online' : 'connecting',
    },
    threats: [
      {
        id: 'THR-001',
        type: 'Flash Loan Attack',
        severity: 'critical',
        target: '0x1234...abcd',
        timestamp: new Date().toISOString(),
        status: 'active',
      },
      {
        id: 'THR-002',
        type: 'MEV Sandwich',
        severity: 'warning',
        target: 'USDT/WETH Pool',
        timestamp: new Date(Date.now() - 300000).toISOString(),
        status: 'investigating',
      },
    ],
    tradingMetrics: {
      total_volume: 15420000,
      mev_extracted: 847000,
      sandwich_attacks: 23,
      arbitrage_opportunities: 156,
      profit_24h: 12300,
      gas_saved: 2.4,
    },
    bridgeStats: {
      total_bridges: 12,
      active_routes: 8,
      volume_24h: 45200000,
      avg_time: 4.2,
      success_rate: 98.7,
      failed_txs: 3,
    },
  };

  // Use real data if available, otherwise use mock data
  const currentData = {
    systemStatus: data.systemStatus || mockData.systemStatus,
    threats: data.threats || mockData.threats,
    tradingMetrics: data.tradingMetrics || mockData.tradingMetrics,
    bridgeStats: data.bridgeStats || mockData.bridgeStats,
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #181a1b 0%, #004242 50%, #181a1b 100%)',
        padding: '20px',
        position: 'relative',
      }}
    >
      {/* Background Effects */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background:
            'radial-gradient(circle at 50% 50%, rgba(0, 255, 136, 0.1) 0%, transparent 50%)',
          pointerEvents: 'none',
        }}
      />

      {/* Header */}
      <ScrollReveal>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '32px',
            padding: '24px',
            background: 'rgba(0, 0, 0, 0.6)',
            border: '1px solid rgba(0, 255, 136, 0.3)',
            borderRadius: '16px',
            backdropFilter: 'blur(10px)',
            boxShadow: '0 0 30px rgba(0, 255, 136, 0.2)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <motion.div
              animate={{ rotate: connected ? 360 : 0 }}
              transition={{
                duration: 2,
                repeat: connected ? Infinity : 0,
                ease: 'linear',
              }}
              style={{
                padding: '12px',
                borderRadius: '16px',
                boxShadow: connected ? '0 0 30px rgba(0, 255, 136, 0.5)' : 'none',
              }}
            >
              <Radio size={24} style={{ color: connected ? '#00ff88' : '#666' }} />
            </motion.div>
            <div>
              <h1
                style={{
                  fontSize: '32px',
                  fontWeight: '700',
                  color: '#1aff94',
                  letterSpacing: '2px',
                  textShadow: '0 0 20px rgba(0, 255, 136, 0.6)',
                }}
              >
                REAL-TIME FEED
              </h1>
              <p style={{ color: '#a8a095', letterSpacing: '1px' }}>
                Live Backend Data Monitoring & Analytics
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <motion.div
              animate={{ scale: connected ? [1, 1.1, 1] : 1 }}
              transition={{ duration: 2, repeat: connected ? Infinity : 0 }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 16px',
                background: connected
                  ? 'rgba(0, 255, 136, 0.1)'
                  : 'rgba(255, 68, 68, 0.1)',
                border: `1px solid ${
                  connected ? 'rgba(0, 255, 136, 0.3)' : 'rgba(255, 68, 68, 0.3)'
                }`,
                borderRadius: '8px',
              }}
            >
              {connected ? (
                <Wifi size={16} style={{ color: '#00ff88' }} />
              ) : (
                <WifiOff size={16} style={{ color: '#ff4444' }} />
              )}
              <span
                style={{
                  color: connected ? '#00ff88' : '#ff4444',
                  fontSize: '14px',
                  fontWeight: '500',
                }}
              >
                {connected ? 'CONNECTED' : 'DISCONNECTED'}
              </span>
            </motion.div>
          </div>
        </div>
      </ScrollReveal>

      {/* Connection Stats */}
      <ScrollReveal delay={0.1}>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '20px',
            marginBottom: '32px',
          }}
        >
          {[
            {
              label: 'CPU Usage',
              value: currentData.systemStatus.cpu_usage,
              suffix: '%',
              color: '#00ff88',
              icon: Activity,
            },
            {
              label: 'Memory',
              value: currentData.systemStatus.memory_usage,
              suffix: '%',
              color: '#00ffff',
              icon: Database,
            },
            {
              label: 'Network Latency',
              value: currentData.systemStatus.network_latency,
              suffix: 'ms',
              color: '#ff6b35',
              icon: Network,
            },
            {
              label: 'Active Connections',
              value: currentData.systemStatus.active_connections,
              color: '#9333ea',
              icon: Eye,
            },
          ].map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + index * 0.1 }}
              style={{
                padding: '20px',
                background: `linear-gradient(135deg, ${stat.color}15, rgba(0, 0, 0, 0.2))`,
                border: `1px solid ${stat.color}30`,
                borderRadius: '12px',
                textAlign: 'center',
              }}
            >
              <stat.icon size={24} style={{ color: stat.color, marginBottom: '8px' }} />
              <div
                style={{
                  fontSize: '24px',
                  fontWeight: '700',
                  color: stat.color,
                  marginBottom: '4px',
                }}
              >
                <LiveCounter
                  value={stat.value}
                  suffix={stat.suffix || ''}
                  duration={1500}
                />
              </div>
              <div
                style={{
                  fontSize: '12px',
                  color: '#cccccc',
                  textTransform: 'uppercase',
                }}
              >
                {stat.label}
              </div>
            </motion.div>
          ))}
        </div>
      </ScrollReveal>

      {/* Tab Navigation */}
      <ScrollReveal delay={0.2}>
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            marginBottom: '32px',
          }}
        >
          <div
            style={{
              display: 'flex',
              background: 'rgba(0, 0, 0, 0.8)',
              border: '1px solid rgba(0, 255, 136, 0.3)',
              borderRadius: '16px',
              padding: '6px',
              backdropFilter: 'blur(20px)',
              boxShadow: '0 0 30px rgba(0, 255, 136, 0.2)',
            }}
          >
            {[
              {
                id: 'overview',
                label: 'Overview',
                icon: BarChart3,
                color: '#00ff88',
              },
              {
                id: 'threats',
                label: 'Threats',
                icon: Shield,
                color: '#ff4444',
              },
              {
                id: 'trading',
                label: 'Trading',
                icon: TrendingUp,
                color: '#00ffff',
              },
              {
                id: 'bridge',
                label: 'Bridge',
                icon: Network,
                color: '#9333ea',
              },
              {
                id: 'analytics',
                label: 'Analytics',
                icon: Activity,
                color: '#ff6b35',
              },
            ].map(tab => (
              <motion.button
                key={tab.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setActiveTab(tab.id as any)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '12px 20px',
                  background:
                    activeTab === tab.id
                      ? `linear-gradient(135deg, ${tab.color}20, ${tab.color}10)`
                      : 'transparent',
                  border: 'none',
                  borderRadius: '12px',
                  color: activeTab === tab.id ? tab.color : '#cccccc',
                  fontSize: '14px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  position: 'relative',
                  transition: 'all 0.3s ease',
                }}
              >
                {activeTab === tab.id && (
                  <motion.div
                    layoutId="activeRealtimeTab"
                    style={{
                      position: 'absolute',
                      inset: 0,
                      background: `linear-gradient(135deg, ${tab.color}15, ${tab.color}05)`,
                      borderRadius: '12px',
                    }}
                  />
                )}
                <tab.icon size={16} />
                <span style={{ position: 'relative', zIndex: 1 }}>{tab.label}</span>
              </motion.button>
            ))}
          </div>
        </div>
      </ScrollReveal>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        {activeTab === 'overview' && (
          <motion.div
            key="overview"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <ScrollReveal delay={0.3}>
              <div
                style={{
                  padding: '24px',
                  background:
                    'linear-gradient(135deg, rgba(0, 255, 136, 0.05), rgba(0, 0, 0, 0.2))',
                  border: '1px solid rgba(0, 255, 136, 0.2)',
                  borderRadius: '12px',
                }}
              >
                <h3
                  style={{
                    color: '#00ff88',
                    marginBottom: '20px',
                    fontSize: '18px',
                    fontWeight: '600',
                  }}
                >
                  System Overview
                </h3>
                <div
                  style={{
                    fontSize: '14px',
                    color: '#cccccc',
                    textAlign: 'center',
                    padding: '40px',
                  }}
                >
                  {connected
                    ? 'Live system data streaming...'
                    : 'Connecting to backend real-time feed...'}
                </div>
              </div>
            </ScrollReveal>
          </motion.div>
        )}

        {activeTab === 'threats' && (
          <motion.div
            key="threats"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <ScrollReveal delay={0.3}>
              <div
                style={{
                  padding: '24px',
                  background:
                    'linear-gradient(135deg, rgba(255, 68, 68, 0.05), rgba(0, 0, 0, 0.2))',
                  border: '1px solid rgba(255, 68, 68, 0.2)',
                  borderRadius: '12px',
                }}
              >
                <h3
                  style={{
                    color: '#ff4444',
                    marginBottom: '20px',
                    fontSize: '18px',
                    fontWeight: '600',
                  }}
                >
                  Live Threat Detection
                </h3>
                <div
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '12px',
                  }}
                >
                  {currentData.threats.map((threat, index) => (
                    <motion.div
                      key={threat.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      style={{
                        padding: '16px',
                        background: 'rgba(255, 68, 68, 0.1)',
                        border: '1px solid rgba(255, 68, 68, 0.3)',
                        borderRadius: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '12px',
                        }}
                      >
                        <AlertTriangle size={20} style={{ color: '#ff4444' }} />
                        <div>
                          <div style={{ color: '#ffffff', fontWeight: '500' }}>
                            {threat.type}
                          </div>
                          <div style={{ color: '#cccccc', fontSize: '12px' }}>
                            {threat.target}
                          </div>
                        </div>
                      </div>
                      <Badge
                        variant={
                          threat.severity === 'critical' ? 'destructive' : 'secondary'
                        }
                      >
                        {threat.severity}
                      </Badge>
                    </motion.div>
                  ))}
                </div>
              </div>
            </ScrollReveal>
          </motion.div>
        )}

        {activeTab === 'trading' && (
          <motion.div
            key="trading"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <ScrollReveal delay={0.3}>
              <div
                style={{
                  padding: '24px',
                  background:
                    'linear-gradient(135deg, rgba(0, 255, 255, 0.05), rgba(0, 0, 0, 0.2))',
                  border: '1px solid rgba(0, 255, 255, 0.2)',
                  borderRadius: '12px',
                }}
              >
                <h3
                  style={{
                    color: '#00ffff',
                    marginBottom: '20px',
                    fontSize: '18px',
                    fontWeight: '600',
                  }}
                >
                  Trading Metrics
                </h3>
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                    gap: '16px',
                  }}
                >
                  {[
                    {
                      label: 'Total Volume',
                      value: currentData.tradingMetrics.total_volume,
                      prefix: '$',
                      color: '#00ffff',
                    },
                    {
                      label: 'MEV Extracted',
                      value: currentData.tradingMetrics.mev_extracted,
                      prefix: '$',
                      color: '#00ff88',
                    },
                    {
                      label: 'Sandwich Attacks',
                      value: currentData.tradingMetrics.sandwich_attacks,
                      color: '#ff4444',
                    },
                    {
                      label: 'Arbitrage Ops',
                      value: currentData.tradingMetrics.arbitrage_opportunities,
                      color: '#9333ea',
                    },
                  ].map((metric, index) => (
                    <div key={index} style={{ textAlign: 'center' }}>
                      <div
                        style={{
                          fontSize: '20px',
                          fontWeight: '700',
                          color: metric.color,
                          marginBottom: '4px',
                        }}
                      >
                        <LiveCounter
                          value={metric.value}
                          prefix={metric.prefix || ''}
                          duration={2000}
                        />
                      </div>
                      <div style={{ fontSize: '12px', color: '#cccccc' }}>
                        {metric.label}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </ScrollReveal>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default RealTime;

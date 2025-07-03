# React Dashboard Integration Examples

This document provides complete examples for integrating the Scorpius Bridge WebSocket API with a Vite + React dashboard.

## Installation

```bash
npm install @tanstack/react-query react-hot-toast
```

## Custom Hooks

### useWebSocket Hook

```typescript
// hooks/useWebSocket.ts
import { useEffect, useState, useRef, useCallback } from 'react';

export interface WebSocketMessage {
  type: string;
  data?: any;
  event_type?: string;
  timestamp?: string;
  transaction_id?: string;
  user_id?: string;
}

export interface UseWebSocketOptions {
  url: string;
  token?: string;
  clientId?: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export function useWebSocket(options: UseWebSocketOptions) {
  const {
    url,
    token,
    clientId,
    reconnectInterval = 5000,
    maxReconnectAttempts = 10
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const messageQueue = useRef<string[]>([]);

  const buildUrl = useCallback(() => {
    const params = new URLSearchParams();
    if (token) params.append('token', token);
    if (clientId) params.append('client_id', clientId);
    
    return params.toString() ? `${url}?${params.toString()}` : url;
  }, [url, token, clientId]);

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) return;

    try {
      setConnectionStatus('connecting');
      ws.current = new WebSocket(buildUrl());

      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setConnectionStatus('connected');
        setReconnectAttempts(0);

        // Send queued messages
        while (messageQueue.current.length > 0) {
          const message = messageQueue.current.shift();
          if (message && ws.current?.readyState === WebSocket.OPEN) {
            ws.current.send(message);
          }
        }
      };

      ws.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          setLastMessage(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.current.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setIsConnected(false);
        setConnectionStatus('disconnected');

        // Attempt to reconnect if not manually closed
        if (event.code !== 1000 && reconnectAttempts < maxReconnectAttempts) {
          setReconnectAttempts(prev => prev + 1);
          reconnectTimeoutRef.current = setTimeout(connect, reconnectInterval);
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('error');
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setConnectionStatus('error');
    }
  }, [buildUrl, reconnectAttempts, maxReconnectAttempts, reconnectInterval]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (ws.current) {
      ws.current.close(1000, 'Manual disconnect');
      ws.current = null;
    }
    
    setIsConnected(false);
    setConnectionStatus('disconnected');
    setReconnectAttempts(0);
  }, []);

  const sendMessage = useCallback((message: object) => {
    const messageStr = JSON.stringify(message);
    
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(messageStr);
    } else {
      // Queue message for when connection is restored
      messageQueue.current.push(messageStr);
    }
  }, []);

  const subscribe = useCallback((topic: string, filters?: object) => {
    sendMessage({
      type: 'subscribe',
      data: { topic, filters }
    });
  }, [sendMessage]);

  const unsubscribe = useCallback((topic: string) => {
    sendMessage({
      type: 'unsubscribe',
      data: { topic }
    });
  }, [sendMessage]);

  useEffect(() => {
    connect();
    
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    connectionStatus,
    lastMessage,
    reconnectAttempts,
    sendMessage,
    subscribe,
    unsubscribe,
    connect,
    disconnect
  };
}
```

### useBridgeEvents Hook

```typescript
// hooks/useBridgeEvents.ts
import { useEffect, useState } from 'react';
import { useWebSocket } from './useWebSocket';

export interface BridgeEvent {
  event_type: string;
  timestamp: string;
  data: any;
  source_chain?: string;
  target_chain?: string;
  transaction_id?: string;
  user_id?: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
}

export function useBridgeEvents(wsUrl: string, token?: string) {
  const [events, setEvents] = useState<BridgeEvent[]>([]);
  const [transactions, setTransactions] = useState<Map<string, BridgeEvent[]>>(new Map());

  const { lastMessage, subscribe, unsubscribe, isConnected } = useWebSocket({
    url: wsUrl,
    token,
    clientId: 'dashboard-events'
  });

  useEffect(() => {
    if (isConnected) {
      subscribe('events');
    }
    
    return () => {
      if (isConnected) {
        unsubscribe('events');
      }
    };
  }, [isConnected, subscribe, unsubscribe]);

  useEffect(() => {
    if (lastMessage?.type === 'event') {
      const event = lastMessage as BridgeEvent;
      
      setEvents(prev => [event, ...prev].slice(0, 100)); // Keep last 100 events
      
      // Group by transaction ID
      if (event.transaction_id) {
        setTransactions(prev => {
          const newMap = new Map(prev);
          const txEvents = newMap.get(event.transaction_id!) || [];
          newMap.set(event.transaction_id!, [...txEvents, event]);
          return newMap;
        });
      }
    }
  }, [lastMessage]);

  return {
    events,
    transactions,
    isConnected
  };
}
```

### useBridgeStats Hook

```typescript
// hooks/useBridgeStats.ts
import { useEffect, useState } from 'react';
import { useWebSocket } from './useWebSocket';

export interface BridgeStats {
  total_transactions: number;
  active_validators: number;
  total_liquidity: string;
  network_health: 'healthy' | 'degraded' | 'down';
  timestamp: string;
}

export function useBridgeStats(wsUrl: string, token?: string, refreshInterval = 30000) {
  const [stats, setStats] = useState<BridgeStats | null>(null);
  const [loading, setLoading] = useState(true);

  const { lastMessage, subscribe, unsubscribe, sendMessage, isConnected } = useWebSocket({
    url: wsUrl,
    token,
    clientId: 'dashboard-stats'
  });

  useEffect(() => {
    if (isConnected) {
      subscribe('stats');
      sendMessage({ type: 'get_stats' }); // Get initial stats
    }
    
    return () => {
      if (isConnected) {
        unsubscribe('stats');
      }
    };
  }, [isConnected, subscribe, unsubscribe, sendMessage]);

  useEffect(() => {
    if (lastMessage?.type === 'stats') {
      setStats(lastMessage.data);
      setLoading(false);
    }
  }, [lastMessage]);

  // Periodic stats refresh
  useEffect(() => {
    if (!isConnected) return;

    const interval = setInterval(() => {
      sendMessage({ type: 'get_stats' });
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [isConnected, sendMessage, refreshInterval]);

  return {
    stats,
    loading,
    isConnected
  };
}
```

## React Components

### WebSocket Status Component

```tsx
// components/WebSocketStatus.tsx
import React from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

interface WebSocketStatusProps {
  wsUrl: string;
  token?: string;
}

export function WebSocketStatus({ wsUrl, token }: WebSocketStatusProps) {
  const { isConnected, connectionStatus, reconnectAttempts } = useWebSocket({
    url: wsUrl,
    token
  });

  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'text-green-500';
      case 'connecting': return 'text-yellow-500';
      case 'error': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  const getStatusText = () => {
    switch (connectionStatus) {
      case 'connected': return 'Connected';
      case 'connecting': return 'Connecting...';
      case 'error': return 'Connection Error';
      case 'disconnected': return 'Disconnected';
      default: return 'Unknown';
    }
  };

  return (
    <div className="flex items-center space-x-2">
      <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
      <span className={getStatusColor()}>
        {getStatusText()}
      </span>
      {reconnectAttempts > 0 && (
        <span className="text-xs text-gray-500">
          (Attempt {reconnectAttempts})
        </span>
      )}
    </div>
  );
}
```

### Real-time Stats Dashboard

```tsx
// components/StatsDashboard.tsx
import React from 'react';
import { useBridgeStats } from '../hooks/useBridgeStats';

interface StatsDashboardProps {
  wsUrl: string;
  token?: string;
}

export function StatsDashboard({ wsUrl, token }: StatsDashboardProps) {
  const { stats, loading, isConnected } = useBridgeStats(wsUrl, token);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white p-6 rounded-lg shadow animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-6 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">No statistics available</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500">Total Transactions</h3>
        <p className="text-2xl font-bold text-gray-900">
          {stats.total_transactions.toLocaleString()}
        </p>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500">Active Validators</h3>
        <p className="text-2xl font-bold text-gray-900">
          {stats.active_validators}
        </p>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500">Total Liquidity</h3>
        <p className="text-2xl font-bold text-gray-900">
          ${parseFloat(stats.total_liquidity).toLocaleString()}
        </p>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500">Network Health</h3>
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${
            stats.network_health === 'healthy' ? 'bg-green-500' :
            stats.network_health === 'degraded' ? 'bg-yellow-500' : 'bg-red-500'
          }`} />
          <p className="text-2xl font-bold text-gray-900 capitalize">
            {stats.network_health}
          </p>
        </div>
      </div>
    </div>
  );
}
```

### Live Events Feed

```tsx
// components/EventsFeed.tsx
import React from 'react';
import { useBridgeEvents } from '../hooks/useBridgeEvents';
import { format } from 'date-fns';

interface EventsFeedProps {
  wsUrl: string;
  token?: string;
  maxEvents?: number;
}

export function EventsFeed({ wsUrl, token, maxEvents = 20 }: EventsFeedProps) {
  const { events, isConnected } = useBridgeEvents(wsUrl, token);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-50';
      case 'error': return 'text-red-600 bg-red-50';
      case 'warning': return 'text-yellow-600 bg-yellow-50';
      default: return 'text-blue-600 bg-blue-50';
    }
  };

  const getEventIcon = (eventType: string) => {
    if (eventType.includes('bridge_transaction')) return '🌉';
    if (eventType.includes('validator')) return '✅';
    if (eventType.includes('liquidity')) return '💧';
    if (eventType.includes('system')) return '⚙️';
    return '📝';
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">Live Events</h3>
        <div className="flex items-center space-x-2 mt-1">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm text-gray-500">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>
      
      <div className="max-h-96 overflow-y-auto">
        {events.length === 0 ? (
          <div className="px-6 py-8 text-center text-gray-500">
            No events yet
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {events.slice(0, maxEvents).map((event, index) => (
              <div key={`${event.timestamp}-${index}`} className="px-6 py-4">
                <div className="flex items-start space-x-3">
                  <span className="text-lg">{getEventIcon(event.event_type)}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getSeverityColor(event.severity)}`}>
                        {event.event_type.replace(/_/g, ' ')}
                      </span>
                      <span className="text-xs text-gray-500">
                        {format(new Date(event.timestamp), 'HH:mm:ss')}
                      </span>
                    </div>
                    
                    <div className="mt-1 text-sm text-gray-900">
                      {event.source_chain && event.target_chain && (
                        <span className="font-medium">
                          {event.source_chain} → {event.target_chain}
                        </span>
                      )}
                      {event.data && Object.keys(event.data).length > 0 && (
                        <div className="mt-1 text-xs text-gray-600">
                          {Object.entries(event.data).map(([key, value]) => (
                            <span key={key} className="mr-3">
                              <span className="font-medium">{key}:</span> {String(value)}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
```

### Transaction Tracker

```tsx
// components/TransactionTracker.tsx
import React, { useState } from 'react';
import { useBridgeEvents } from '../hooks/useBridgeEvents';

interface TransactionTrackerProps {
  wsUrl: string;
  token?: string;
}

export function TransactionTracker({ wsUrl, token }: TransactionTrackerProps) {
  const [trackingId, setTrackingId] = useState('');
  const { transactions, subscribe, unsubscribe, isConnected } = useBridgeEvents(wsUrl, token);

  const trackTransaction = () => {
    if (trackingId && isConnected) {
      subscribe(`transaction:${trackingId}`);
    }
  };

  const stopTracking = () => {
    if (trackingId && isConnected) {
      unsubscribe(`transaction:${trackingId}`);
    }
  };

  const trackedEvents = trackingId ? transactions.get(trackingId) || [] : [];

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">Transaction Tracker</h3>
        
        <div className="mt-4 flex space-x-3">
          <input
            type="text"
            value={trackingId}
            onChange={(e) => setTrackingId(e.target.value)}
            placeholder="Enter transaction ID"
            className="flex-1 border border-gray-300 rounded-md px-3 py-2 text-sm"
          />
          <button
            onClick={trackTransaction}
            disabled={!trackingId || !isConnected}
            className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700 disabled:opacity-50"
          >
            Track
          </button>
          <button
            onClick={stopTracking}
            disabled={!trackingId || !isConnected}
            className="px-4 py-2 bg-gray-600 text-white rounded-md text-sm hover:bg-gray-700 disabled:opacity-50"
          >
            Stop
          </button>
        </div>
      </div>
      
      <div className="max-h-64 overflow-y-auto">
        {trackedEvents.length === 0 ? (
          <div className="px-6 py-8 text-center text-gray-500">
            {trackingId ? 'No events for this transaction' : 'Enter a transaction ID to track'}
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {trackedEvents.map((event, index) => (
              <div key={index} className="px-6 py-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-900">
                    {event.event_type.replace(/_/g, ' ')}
                  </span>
                  <span className="text-xs text-gray-500">
                    {format(new Date(event.timestamp), 'MMM dd, HH:mm:ss')}
                  </span>
                </div>
                {event.data && (
                  <div className="mt-1 text-xs text-gray-600">
                    {JSON.stringify(event.data, null, 2)}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
```

## Main Dashboard Component

```tsx
// components/Dashboard.tsx
import React from 'react';
import { WebSocketStatus } from './WebSocketStatus';
import { StatsDashboard } from './StatsDashboard';
import { EventsFeed } from './EventsFeed';
import { TransactionTracker } from './TransactionTracker';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/ws';
const AUTH_TOKEN = localStorage.getItem('auth_token');

export function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <h1 className="text-3xl font-bold text-gray-900">
              Scorpius Bridge Dashboard
            </h1>
            <WebSocketStatus wsUrl={WS_URL} token={AUTH_TOKEN} />
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Stats Dashboard */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Real-time Statistics
            </h2>
            <StatsDashboard wsUrl={WS_URL} token={AUTH_TOKEN} />
          </section>

          {/* Events and Tracking */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Live Events
              </h2>
              <EventsFeed wsUrl={WS_URL} token={AUTH_TOKEN} />
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Transaction Tracking
              </h2>
              <TransactionTracker wsUrl={WS_URL} token={AUTH_TOKEN} />
            </section>
          </div>
        </div>
      </main>
    </div>
  );
}
```

## Environment Configuration

```typescript
// .env.local
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/api/ws

# Production
# VITE_API_URL=https://api.scorpius-bridge.com/api
# VITE_WS_URL=wss://api.scorpius-bridge.com/api/ws
```

## Package.json Scripts

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@tanstack/react-query": "^4.0.0",
    "react-hot-toast": "^2.4.0",
    "date-fns": "^2.30.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.0.0",
    "typescript": "^5.0.0",
    "vite": "^4.4.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

This integration provides a complete, production-ready solution for connecting your Vite + React dashboard to the Scorpius Bridge WebSocket API with proper error handling, reconnection logic, and real-time updates.

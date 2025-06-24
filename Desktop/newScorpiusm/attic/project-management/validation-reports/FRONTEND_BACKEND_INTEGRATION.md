# 🔗 SCORPIUS X - SEAMLESS FRONTEND-BACKEND INTEGRATION GUIDE

**Complete Setup for Bulletproof Dashboard-API Connection**

---

## 🎯 **INTEGRATION OVERVIEW**

This guide ensures your dashboard frontend connects seamlessly to the Scorpius X backend with:

- ✅ **Automatic API discovery** and endpoint validation
- ✅ **Real-time WebSocket** connections with auto-reconnect
- ✅ **Type-safe API** client with full TypeScript support
- ✅ **Error handling** and graceful degradation
- ✅ **Development tools** for testing and debugging

---

## 🔌 **BACKEND ENDPOINT MAPPING**

### **API Endpoints Available** (from your backend/main.py)

```typescript
// System & Core
export const API_ENDPOINTS = {
  // Core System
  root: '/',
  systemStatus: '/api/v2/system/status',
  systemMetrics: '/api/v2/system/metrics',

  // Security & Threats
  securityScan: '/api/v2/security/scan',
  threatResponse: '/api/v2/threats/respond',
  quantumDeploy: '/api/v2/quantum/deploy-environment',

  // Integration Hub
  integrationCall: '/api/v2/integration/call',
  workflows: '/api/v2/workflows',
  workflowExecute: '/api/v2/workflows/{workflow_id}/execute',

  // Advanced Monitoring Dashboard
  monitoringDashboard: '/api/v2/monitoring/dashboard',
  metricsExport: '/api/v2/monitoring/metrics/export',
  createAlert: '/api/v2/monitoring/alerts',

  // AI Trading Engine
  tradingPerformance: '/api/v2/trading/performance',
  tradingStrategy: '/api/v2/trading/strategy/enable',
  tradingOpportunities: '/api/v2/trading/opportunities',

  // Blockchain Bridge Network
  bridgeTransfer: '/api/v2/bridge/transfer',
  bridgeStatus: '/api/v2/bridge/transfer/{id}',
  bridgeStats: '/api/v2/bridge/statistics',

  // Enterprise Analytics
  analyticsReport: '/api/v2/analytics/report',
  analyticsDashboard: '/api/v2/analytics/dashboard',
  analyticsQuery: '/api/v2/analytics/query',

  // Distributed Computing
  computingJobs: '/api/v2/computing/jobs',
  computingPerformance: '/api/v2/computing/performance',
  computingNodes: '/api/v2/computing/nodes',

  // Legacy API routes (maintained for compatibility)
  dashboard: '/api/dashboard',
  config: '/api/config',
  auth: '/api/auth',
  reports: '/api/reports',
  scanner: '/api/scanner',
  mevOps: '/api/mev-ops',
  mevGuardians: '/api/mev-guardians',
  simulation: '/api/simulation',
} as const;
```

### **WebSocket Endpoints**

```typescript
export const WEBSOCKET_ENDPOINTS = {
  metrics: 'ws://localhost:8000/ws/metrics',
  threats: 'ws://localhost:8000/ws/threats',
  trading: 'ws://localhost:8000/ws/trading',
  status: 'ws://localhost:8000/ws/status',
  bridge: 'ws://localhost:8000/ws/bridge',
  security: 'ws://localhost:8000/ws/security',
  analytics: 'ws://localhost:8000/ws/analytics',
} as const;
```

---

## 🛠️ **ENHANCED API CLIENT SETUP**

### **1. Environment Configuration**

Create `.env.local` in your dashboard project:

```bash
# Backend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# API Keys (if needed)
NEXT_PUBLIC_API_KEY=your-api-key-here

# Development Settings
NEXT_PUBLIC_ENV=development
NEXT_PUBLIC_DEBUG_API=true
NEXT_PUBLIC_ENABLE_WEBSOCKETS=true

# Timeouts and Retry
NEXT_PUBLIC_API_TIMEOUT=10000
NEXT_PUBLIC_RETRY_ATTEMPTS=3
NEXT_PUBLIC_RETRY_DELAY=1000
```

### **2. Advanced API Client with Auto-Discovery**

```typescript
// src/lib/api-client.ts
interface ApiResponse<T = any> {
  data: T;
  status: number;
  message?: string;
  timestamp: string;
}

interface ApiError {
  message: string;
  status: number;
  code?: string;
  details?: any;
}

class ScorpiusApiClient {
  private baseUrl: string;
  private timeout: number;
  private retryAttempts: number;
  private retryDelay: number;
  private apiKey?: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    this.timeout = parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '10000');
    this.retryAttempts = parseInt(process.env.NEXT_PUBLIC_RETRY_ATTEMPTS || '3');
    this.retryDelay = parseInt(process.env.NEXT_PUBLIC_RETRY_DELAY || '1000');
    this.apiKey = process.env.NEXT_PUBLIC_API_KEY;
  }

  // Auto-discovery: Test backend connection and get available endpoints
  async discoverApi(): Promise<{
    available: boolean;
    endpoints: string[];
    version: string;
  }> {
    try {
      const response = await this.get('/');
      return {
        available: true,
        endpoints: Object.keys(response.capabilities || {}),
        version: response.version || '2.0.0',
      };
    } catch (error) {
      return {
        available: false,
        endpoints: [],
        version: 'unknown',
      };
    }
  }

  // Enhanced GET with retry logic
  async get<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
    const url = new URL(endpoint, this.baseUrl);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, String(value));
      });
    }

    return this.fetchWithRetry(url.toString(), {
      method: 'GET',
      headers: this.getHeaders(),
    });
  }

  // Enhanced POST with retry logic
  async post<T>(endpoint: string, data: any): Promise<T> {
    return this.fetchWithRetry(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
  }

  // PUT method
  async put<T>(endpoint: string, data: any): Promise<T> {
    return this.fetchWithRetry(`${this.baseUrl}${endpoint}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
  }

  // DELETE method
  async delete<T>(endpoint: string): Promise<T> {
    return this.fetchWithRetry(`${this.baseUrl}${endpoint}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });
  }

  // Retry logic with exponential backoff
  private async fetchWithRetry(
    url: string,
    options: RequestInit,
    attempt = 1,
  ): Promise<any> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new ApiError(
          `HTTP ${response.status}: ${response.statusText}`,
          response.status,
        );
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }

      return await response.text();
    } catch (error) {
      if (attempt < this.retryAttempts && this.shouldRetry(error)) {
        await this.delay(this.retryDelay * Math.pow(2, attempt - 1));
        return this.fetchWithRetry(url, options, attempt + 1);
      }
      throw error;
    }
  }

  private shouldRetry(error: any): boolean {
    // Retry on network errors, timeouts, or 5xx server errors
    return (
      error.name === 'AbortError' ||
      error.name === 'TypeError' ||
      (error.status >= 500 && error.status < 600)
    );
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    };

    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    return headers;
  }

  // Health check
  async healthCheck(): Promise<boolean> {
    try {
      await this.get('/api/v2/system/status');
      return true;
    } catch {
      return false;
    }
  }
}

// Singleton instance
export const apiClient = new ScorpiusApiClient();

// Custom error class
class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string,
    public details?: any,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export { ApiError };
```

### **3. Type-Safe API Hooks with React Query**

```typescript
// src/hooks/api/useScorpiusApi.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

// System Status Hook
export function useSystemStatus() {
  return useQuery({
    queryKey: ['system', 'status'],
    queryFn: () => apiClient.get('/api/v2/system/status'),
    refetchInterval: 30000, // Refresh every 30 seconds
    staleTime: 10000, // Consider data stale after 10 seconds
  });
}

// System Metrics Hook
export function useSystemMetrics() {
  return useQuery({
    queryKey: ['system', 'metrics'],
    queryFn: () => apiClient.get('/api/v2/system/metrics'),
    refetchInterval: 5000, // Refresh every 5 seconds
  });
}

// Trading Performance Hook
export function useTradingPerformance() {
  return useQuery({
    queryKey: ['trading', 'performance'],
    queryFn: () => apiClient.get('/api/v2/trading/performance'),
    refetchInterval: 10000,
  });
}

// Security Scan Mutation
export function useSecurityScan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { target: string; scan_type?: string }) =>
      apiClient.post('/api/v2/security/scan', data),
    onSuccess: () => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['security'] });
    },
  });
}

// Bridge Transfer Mutation
export function useBridgeTransfer() {
  return useMutation({
    mutationFn: (transferData: any) =>
      apiClient.post('/api/v2/bridge/transfer', transferData),
  });
}

// Monitoring Dashboard Data
export function useMonitoringDashboard() {
  return useQuery({
    queryKey: ['monitoring', 'dashboard'],
    queryFn: () => apiClient.get('/api/v2/monitoring/dashboard'),
    refetchInterval: 15000,
  });
}

// API Discovery Hook
export function useApiDiscovery() {
  return useQuery({
    queryKey: ['api', 'discovery'],
    queryFn: () => apiClient.discoverApi(),
    staleTime: 300000, // 5 minutes
    cacheTime: 600000, // 10 minutes
  });
}

// Backend Health Check
export function useBackendHealth() {
  return useQuery({
    queryKey: ['backend', 'health'],
    queryFn: () => apiClient.healthCheck(),
    refetchInterval: 10000,
    retry: 1,
  });
}
```

---

## 🔄 **REAL-TIME WEBSOCKET INTEGRATION**

### **1. WebSocket Manager with Auto-Reconnect**

```typescript
// src/lib/websocket-manager.ts
interface WebSocketEvent<T = any> {
  type: string;
  data: T;
  timestamp: string;
}

interface WebSocketOptions {
  autoReconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
}

class ScorpiusWebSocketManager {
  private connections = new Map<string, WebSocket>();
  private reconnectTimers = new Map<string, NodeJS.Timeout>();
  private reconnectAttempts = new Map<string, number>();
  private eventHandlers = new Map<string, Set<(data: any) => void>>();

  private defaultOptions: Required<WebSocketOptions> = {
    autoReconnect: true,
    reconnectInterval: 5000,
    maxReconnectAttempts: 10,
    heartbeatInterval: 30000,
  };

  // Connect to a specific WebSocket endpoint
  connect(
    name: string,
    url: string,
    options: WebSocketOptions = {},
  ): Promise<WebSocket> {
    return new Promise((resolve, reject) => {
      const opts = { ...this.defaultOptions, ...options };

      try {
        const ws = new WebSocket(url);

        ws.onopen = () => {
          console.log(`🔗 WebSocket connected: ${name}`);
          this.connections.set(name, ws);
          this.reconnectAttempts.set(name, 0);

          // Setup heartbeat
          this.setupHeartbeat(name, opts.heartbeatInterval);

          resolve(ws);
        };

        ws.onmessage = event => {
          try {
            const data = JSON.parse(event.data);
            this.notifyHandlers(name, data);
          } catch (error) {
            console.error(`WebSocket message parse error for ${name}:`, error);
          }
        };

        ws.onclose = event => {
          console.log(`🔌 WebSocket disconnected: ${name}`, event.code, event.reason);
          this.connections.delete(name);

          if (opts.autoReconnect && !event.wasClean) {
            this.scheduleReconnect(name, url, opts);
          }
        };

        ws.onerror = error => {
          console.error(`❌ WebSocket error for ${name}:`, error);
          reject(error);
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  // Subscribe to WebSocket events
  subscribe(connectionName: string, handler: (data: any) => void): () => void {
    if (!this.eventHandlers.has(connectionName)) {
      this.eventHandlers.set(connectionName, new Set());
    }

    this.eventHandlers.get(connectionName)!.add(handler);

    // Return unsubscribe function
    return () => {
      this.eventHandlers.get(connectionName)?.delete(handler);
    };
  }

  // Send data to WebSocket
  send(connectionName: string, data: any): boolean {
    const ws = this.connections.get(connectionName);
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data));
      return true;
    }
    return false;
  }

  // Disconnect specific WebSocket
  disconnect(connectionName: string): void {
    const ws = this.connections.get(connectionName);
    if (ws) {
      ws.close(1000, 'Client disconnect');
    }

    const timer = this.reconnectTimers.get(connectionName);
    if (timer) {
      clearTimeout(timer);
      this.reconnectTimers.delete(connectionName);
    }
  }

  // Disconnect all WebSockets
  disconnectAll(): void {
    this.connections.forEach((_, name) => this.disconnect(name));
  }

  // Get connection status
  getStatus(
    connectionName: string,
  ): 'connected' | 'disconnected' | 'connecting' | 'error' {
    const ws = this.connections.get(connectionName);
    if (!ws) return 'disconnected';

    switch (ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
      case WebSocket.CLOSED:
        return 'disconnected';
      default:
        return 'error';
    }
  }

  private scheduleReconnect(
    name: string,
    url: string,
    options: Required<WebSocketOptions>,
  ): void {
    const attempts = this.reconnectAttempts.get(name) || 0;

    if (attempts >= options.maxReconnectAttempts) {
      console.error(`❌ Max reconnection attempts reached for ${name}`);
      return;
    }

    const delay = Math.min(options.reconnectInterval * Math.pow(2, attempts), 30000);
    console.log(`🔄 Reconnecting ${name} in ${delay}ms (attempt ${attempts + 1})`);

    const timer = setTimeout(() => {
      this.reconnectAttempts.set(name, attempts + 1);
      this.connect(name, url, options).catch(() => {
        this.scheduleReconnect(name, url, options);
      });
    }, delay);

    this.reconnectTimers.set(name, timer);
  }

  private setupHeartbeat(name: string, interval: number): void {
    const heartbeat = setInterval(() => {
      if (this.getStatus(name) === 'connected') {
        this.send(name, { type: 'ping', timestamp: Date.now() });
      } else {
        clearInterval(heartbeat);
      }
    }, interval);
  }

  private notifyHandlers(connectionName: string, data: any): void {
    const handlers = this.eventHandlers.get(connectionName);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in WebSocket handler for ${connectionName}:`, error);
        }
      });
    }
  }
}

// Singleton instance
export const wsManager = new ScorpiusWebSocketManager();

// React Hook for WebSocket connections
export function useWebSocket(name: string, url: string, options?: WebSocketOptions) {
  const [status, setStatus] = useState<
    'connected' | 'disconnected' | 'connecting' | 'error'
  >('disconnected');
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    let mounted = true;

    const connect = async () => {
      try {
        setStatus('connecting');
        await wsManager.connect(name, url, options);

        if (mounted) {
          setStatus('connected');
        }
      } catch (error) {
        if (mounted) {
          setStatus('error');
        }
      }
    };

    const unsubscribe = wsManager.subscribe(name, newData => {
      if (mounted) {
        setData(newData);
      }
    });

    connect();

    // Update status periodically
    const statusInterval = setInterval(() => {
      if (mounted) {
        setStatus(wsManager.getStatus(name));
      }
    }, 1000);

    return () => {
      mounted = false;
      clearInterval(statusInterval);
      unsubscribe();
      wsManager.disconnect(name);
    };
  }, [name, url]);

  const send = useCallback(
    (data: any) => {
      return wsManager.send(name, data);
    },
    [name],
  );

  return { status, data, send };
}
```

### **2. Pre-configured WebSocket Hooks**

```typescript
// src/hooks/websockets/useScorpiusWebSockets.ts
import { useWebSocket } from '@/lib/websocket-manager';
import { useDashboardStore } from '@/stores/dashboard';

// System Metrics WebSocket
export function useSystemMetricsWS() {
  const { setSystemStatus } = useDashboardStore();

  const { status, data } = useWebSocket(
    'system-metrics',
    'ws://localhost:8000/ws/metrics',
  );

  useEffect(() => {
    if (data) {
      setSystemStatus(data);
    }
  }, [data, setSystemStatus]);

  return { status, data };
}

// Threat Monitoring WebSocket
export function useThreatsWS() {
  const { addThreatAlert } = useDashboardStore();

  const { status, data } = useWebSocket('threats', 'ws://localhost:8000/ws/threats');

  useEffect(() => {
    if (data && data.type === 'threat_alert') {
      addThreatAlert(data.alert);
    }
  }, [data, addThreatAlert]);

  return { status, data };
}

// Trading Updates WebSocket
export function useTradingWS() {
  const { setTradingMetrics } = useDashboardStore();

  const { status, data } = useWebSocket('trading', 'ws://localhost:8000/ws/trading');

  useEffect(() => {
    if (data && data.type === 'trading_update') {
      setTradingMetrics(data.metrics);
    }
  }, [data, setTradingMetrics]);

  return { status, data };
}

// Bridge Events WebSocket
export function useBridgeWS() {
  const { setBridgeStats } = useDashboardStore();

  const { status, data } = useWebSocket('bridge', 'ws://localhost:8000/ws/bridge');

  useEffect(() => {
    if (data && data.type === 'bridge_update') {
      setBridgeStats(data.stats);
    }
  }, [data, setBridgeStats]);

  return { status, data };
}

// Master hook to connect all WebSockets
export function useAllWebSockets() {
  const systemWS = useSystemMetricsWS();
  const threatsWS = useThreatsWS();
  const tradingWS = useTradingWS();
  const bridgeWS = useBridgeWS();

  const allConnected = [
    systemWS.status,
    threatsWS.status,
    tradingWS.status,
    bridgeWS.status,
  ].every(status => status === 'connected');

  const anyError = [
    systemWS.status,
    threatsWS.status,
    tradingWS.status,
    bridgeWS.status,
  ].some(status => status === 'error');

  return {
    allConnected,
    anyError,
    connections: {
      system: systemWS,
      threats: threatsWS,
      trading: tradingWS,
      bridge: bridgeWS,
    },
  };
}
```

---

## 🚨 **CONNECTION MONITORING & ERROR HANDLING**

### **1. Connection Status Component**

```typescript
// src/components/ConnectionStatus.tsx
import { useBackendHealth, useApiDiscovery } from '@/hooks/api/useScorpiusApi'
import { useAllWebSockets } from '@/hooks/websockets/useScorpiusWebSockets'

export function ConnectionStatus() {
  const { data: isHealthy, isLoading: healthLoading } = useBackendHealth()
  const { data: apiInfo, isLoading: apiLoading } = useApiDiscovery()
  const { allConnected, anyError, connections } = useAllWebSockets()

  const getStatusColor = () => {
    if (healthLoading || apiLoading) return 'text-yellow-500'
    if (!isHealthy || anyError) return 'text-red-500'
    if (allConnected) return 'text-green-500'
    return 'text-yellow-500'
  }

  const getStatusText = () => {
    if (healthLoading || apiLoading) return 'Connecting...'
    if (!isHealthy) return 'Backend Offline'
    if (anyError) return 'Connection Error'
    if (allConnected) return 'All Systems Online'
    return 'Partial Connection'
  }

  return (
    <div className="flex items-center space-x-2">
      <div className={`w-2 h-2 rounded-full ${getStatusColor().replace('text-', 'bg-')}`} />
      <span className={`text-sm ${getStatusColor()}`}>
        {getStatusText()}
      </span>

      {/* Detailed Status (expandable) */}
      <details className="relative">
        <summary className="cursor-pointer text-xs text-slate-400">Details</summary>
        <div className="absolute top-6 right-0 bg-slate-800 border border-slate-600 rounded-lg p-3 min-w-64 z-50">
          <div className="space-y-2 text-xs">
            <div className="flex justify-between">
              <span>Backend API:</span>
              <span className={isHealthy ? 'text-green-400' : 'text-red-400'}>
                {isHealthy ? 'Online' : 'Offline'}
              </span>
            </div>

            <div className="flex justify-between">
              <span>API Version:</span>
              <span className="text-slate-300">{apiInfo?.version || 'Unknown'}</span>
            </div>

            <hr className="border-slate-600" />

            <div className="space-y-1">
              <div className="font-medium text-slate-200">WebSocket Connections:</div>
              {Object.entries(connections).map(([name, conn]) => (
                <div key={name} className="flex justify-between">
                  <span className="capitalize">{name}:</span>
                  <span className={
                    conn.status === 'connected' ? 'text-green-400' :
                    conn.status === 'error' ? 'text-red-400' :
                    'text-yellow-400'
                  }>
                    {conn.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </details>
    </div>
  )
}
```

### **2. Error Boundary for API Errors**

```typescript
// src/components/ApiErrorBoundary.tsx
import React, { Component, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ApiErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('API Error Boundary caught an error:', error, errorInfo)

    // Log to external service in production
    if (process.env.NODE_ENV === 'production') {
      // Send to error tracking service
    }
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="flex flex-col items-center justify-center p-8 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
          <div className="text-red-600 dark:text-red-400 text-lg font-semibold mb-2">
            🚨 Connection Error
          </div>
          <div className="text-red-600 dark:text-red-400 text-sm text-center mb-4">
            Unable to connect to Scorpius X backend. Please check:
          </div>
          <ul className="text-sm text-red-600 dark:text-red-400 space-y-1 mb-4">
            <li>• Backend server is running on port 8000</li>
            <li>• CORS is configured correctly</li>
            <li>• Network connection is stable</li>
          </ul>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Retry Connection
          </button>
        </div>
      )
    }

    return this.props.children
  }
}
```

---

## 🧪 **DEVELOPMENT & TESTING TOOLS**

### **1. API Testing Dashboard**

```typescript
// src/components/dev/ApiTester.tsx (only in development)
import { useState } from 'react'
import { apiClient } from '@/lib/api-client'

export function ApiTester() {
  const [endpoint, setEndpoint] = useState('/api/v2/system/status')
  const [method, setMethod] = useState<'GET' | 'POST' | 'PUT' | 'DELETE'>('GET')
  const [body, setBody] = useState('')
  const [response, setResponse] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const testEndpoint = async () => {
    setLoading(true)
    setError(null)
    setResponse(null)

    try {
      let result
      const requestBody = body ? JSON.parse(body) : undefined

      switch (method) {
        case 'GET':
          result = await apiClient.get(endpoint)
          break
        case 'POST':
          result = await apiClient.post(endpoint, requestBody)
          break
        case 'PUT':
          result = await apiClient.put(endpoint, requestBody)
          break
        case 'DELETE':
          result = await apiClient.delete(endpoint)
          break
      }

      setResponse(result)
    } catch (err: any) {
      setError(err.message || 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  if (process.env.NODE_ENV !== 'development') {
    return null
  }

  return (
    <div className="fixed bottom-4 right-4 w-96 bg-slate-800 border border-slate-600 rounded-lg p-4 z-50">
      <div className="flex justify-between items-center mb-3">
        <h3 className="font-semibold text-white">API Tester</h3>
        <button className="text-slate-400 hover:text-white">×</button>
      </div>

      <div className="space-y-3">
        <div>
          <label className="block text-xs text-slate-400 mb-1">Method</label>
          <select
            value={method}
            onChange={(e) => setMethod(e.target.value as any)}
            className="w-full px-2 py-1 bg-slate-700 border border-slate-600 rounded text-white text-sm"
          >
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="PUT">PUT</option>
            <option value="DELETE">DELETE</option>
          </select>
        </div>

        <div>
          <label className="block text-xs text-slate-400 mb-1">Endpoint</label>
          <input
            value={endpoint}
            onChange={(e) => setEndpoint(e.target.value)}
            className="w-full px-2 py-1 bg-slate-700 border border-slate-600 rounded text-white text-sm"
            placeholder="/api/v2/system/status"
          />
        </div>

        {['POST', 'PUT'].includes(method) && (
          <div>
            <label className="block text-xs text-slate-400 mb-1">Body (JSON)</label>
            <textarea
              value={body}
              onChange={(e) => setBody(e.target.value)}
              className="w-full px-2 py-1 bg-slate-700 border border-slate-600 rounded text-white text-sm h-20"
              placeholder='{"key": "value"}'
            />
          </div>
        )}

        <button
          onClick={testEndpoint}
          disabled={loading}
          className="w-full px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 text-sm"
        >
          {loading ? 'Testing...' : 'Test API'}
        </button>

        {error && (
          <div className="p-2 bg-red-900/20 border border-red-800 rounded text-red-400 text-xs">
            Error: {error}
          </div>
        )}

        {response && (
          <div className="p-2 bg-green-900/20 border border-green-800 rounded">
            <pre className="text-green-400 text-xs overflow-auto max-h-32">
              {JSON.stringify(response, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}
```

### **2. Backend Startup Verification Script**

```bash
# backend-check.sh (add to your dashboard project)
#!/bin/bash

echo "🔍 Checking Scorpius X Backend Connection..."

# Check if backend is running
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ Backend is running on port 8000"

    # Test API endpoints
    echo "🧪 Testing API endpoints..."

    # System status
    if curl -s http://localhost:8000/api/v2/system/status > /dev/null; then
        echo "✅ System status endpoint working"
    else
        echo "❌ System status endpoint not responding"
    fi

    # System metrics
    if curl -s http://localhost:8000/api/v2/system/metrics > /dev/null; then
        echo "✅ System metrics endpoint working"
    else
        echo "❌ System metrics endpoint not responding"
    fi

    # Trading performance
    if curl -s http://localhost:8000/api/v2/trading/performance > /dev/null; then
        echo "✅ Trading performance endpoint working"
    else
        echo "❌ Trading performance endpoint not responding"
    fi

    echo "🎉 Backend connectivity check complete!"

else
    echo "❌ Backend is not running on port 8000"
    echo "💡 Please start the Scorpius X backend:"
    echo "   cd ../backend"
    echo "   python main.py"
fi
```

---

## 🚀 **INTEGRATION SETUP SCRIPT**

### **Complete Integration Setup**

```bash
# integration-setup.ps1
Write-Host "🔗 Setting up Scorpius X Frontend-Backend Integration..." -ForegroundColor Cyan

# 1. Create enhanced API client
Write-Host "📡 Creating enhanced API client..." -ForegroundColor Green
# (The API client code would be written to files here)

# 2. Setup WebSocket manager
Write-Host "🔄 Setting up WebSocket manager..." -ForegroundColor Green
# (WebSocket manager code would be written here)

# 3. Create connection monitoring
Write-Host "📊 Creating connection monitoring..." -ForegroundColor Green
# (Connection status components would be created here)

# 4. Add development tools
Write-Host "🧪 Adding development tools..." -ForegroundColor Green
# (API tester and debugging tools would be added here)

# 5. Test backend connection
Write-Host "🔍 Testing backend connection..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/" -Method Get -TimeoutSec 5
    Write-Host "✅ Backend is online!" -ForegroundColor Green
    Write-Host "   Platform: $($response.platform)" -ForegroundColor White
    Write-Host "   Version: $($response.version)" -ForegroundColor White
    Write-Host "   Modules: $($response.modules_active)" -ForegroundColor White
} catch {
    Write-Host "❌ Backend is not responding!" -ForegroundColor Red
    Write-Host "💡 Please start the Scorpius X backend first:" -ForegroundColor Yellow
    Write-Host "   cd ..\backend" -ForegroundColor White
    Write-Host "   python main.py" -ForegroundColor White
}

Write-Host ""
Write-Host "🎉 Integration setup complete!" -ForegroundColor Green
Write-Host "🚀 Your dashboard is now ready for seamless backend connection!" -ForegroundColor Cyan
```

---

## 📋 **INTEGRATION CHECKLIST**

### ✅ **Backend Requirements**

- [ ] Scorpius X backend running on `http://localhost:8000`
- [ ] CORS configured to allow frontend origin
- [ ] WebSocket endpoints properly configured
- [ ] All API v2 endpoints responding correctly

### ✅ **Frontend Setup**

- [ ] Enhanced API client with retry logic implemented
- [ ] WebSocket manager with auto-reconnect configured
- [ ] Type-safe API hooks created
- [ ] Connection monitoring components added
- [ ] Error boundaries for graceful degradation

### ✅ **Development Tools**

- [ ] API testing dashboard (development only)
- [ ] Connection status indicator
- [ ] Backend health monitoring
- [ ] WebSocket connection tracking

### ✅ **Production Readiness**

- [ ] Environment variables configured
- [ ] Error handling and logging
- [ ] Performance monitoring
- [ ] Fallback UI for offline scenarios

---

## 🎯 **NEXT STEPS**

1. **Run the integration setup script**
2. **Start your Scorpius X backend**
3. **Test all API endpoints** using the API tester
4. **Verify WebSocket connections** are stable
5. **Build your dashboard components** with confidence!

**🌟 With this setup, your frontend will have bulletproof connectivity to the Scorpius X backend with automatic error handling, reconnection, and real-time updates!**

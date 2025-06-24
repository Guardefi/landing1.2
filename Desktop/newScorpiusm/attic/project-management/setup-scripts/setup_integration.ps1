# 🔗 Scorpius X - Complete Frontend-Backend Integration Setup
# This script sets up bulletproof connectivity between your dashboard and backend

Write-Host "🌟 Scorpius X - Frontend-Backend Integration Setup" -ForegroundColor Cyan
Write-Host "🎯 Creating seamless dashboard-API connection..." -ForegroundColor Yellow
Write-Host ""

# Check if we're in the dashboard directory
if (-not (Test-Path "package.json")) {
    Write-Host "❌ Please run this script from your dashboard project directory" -ForegroundColor Red
    Write-Host "💡 Expected structure: scorpius-dashboard/package.json" -ForegroundColor Yellow
    exit 1
}

# 1. Install additional dependencies for enhanced integration
Write-Host "📦 Installing enhanced integration dependencies..." -ForegroundColor Green
npm install react-error-boundary @types/ws uuid
npm install -D @types/uuid

# 2. Create enhanced API client
Write-Host "📡 Creating enhanced API client..." -ForegroundColor Green
New-Item -ItemType Directory -Force -Path "src\lib" | Out-Null

@'
// Enhanced API Client with auto-discovery and retry logic
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface ApiResponse<T = any> {
  data: T
  status: number
  message?: string
  timestamp: string
}

interface ApiError {
  message: string
  status: number
  code?: string
  details?: any
}

// API Endpoints from Scorpius X backend
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

  // Advanced Monitoring
  monitoringDashboard: '/api/v2/monitoring/dashboard',
  metricsExport: '/api/v2/monitoring/metrics/export',
  createAlert: '/api/v2/monitoring/alerts',

  // AI Trading Engine
  tradingPerformance: '/api/v2/trading/performance',
  tradingStrategy: '/api/v2/trading/strategy/enable',
  tradingOpportunities: '/api/v2/trading/opportunities',

  // Blockchain Bridge
  bridgeTransfer: '/api/v2/bridge/transfer',
  bridgeStats: '/api/v2/bridge/statistics',

  // Enterprise Analytics
  analyticsReport: '/api/v2/analytics/report',
  analyticsDashboard: '/api/v2/analytics/dashboard',
  analyticsQuery: '/api/v2/analytics/query',

  // Legacy endpoints
  dashboard: '/api/dashboard',
  config: '/api/config',
  auth: '/api/auth',
  reports: '/api/reports',
  scanner: '/api/scanner'
} as const

export const WEBSOCKET_ENDPOINTS = {
  metrics: 'ws://localhost:8000/ws/metrics',
  threats: 'ws://localhost:8000/ws/threats',
  trading: 'ws://localhost:8000/ws/trading',
  status: 'ws://localhost:8000/ws/status',
  bridge: 'ws://localhost:8000/ws/bridge',
  security: 'ws://localhost:8000/ws/security'
} as const

class ScorpiusApiClient {
  private baseUrl: string
  private timeout: number
  private retryAttempts: number
  private retryDelay: number

  constructor() {
    this.baseUrl = API_BASE_URL
    this.timeout = parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '10000')
    this.retryAttempts = parseInt(process.env.NEXT_PUBLIC_RETRY_ATTEMPTS || '3')
    this.retryDelay = parseInt(process.env.NEXT_PUBLIC_RETRY_DELAY || '1000')
  }

  // Auto-discovery: Test backend connection
  async discoverApi(): Promise<{ available: boolean; endpoints: string[]; version: string }> {
    try {
      const response = await this.get('/')
      return {
        available: true,
        endpoints: response.capabilities || [],
        version: response.version || '2.0.0'
      }
    } catch (error) {
      return { available: false, endpoints: [], version: 'unknown' }
    }
  }

  // Enhanced GET with retry logic
  async get<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
    const url = new URL(endpoint, this.baseUrl)
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, String(value))
      })
    }
    return this.fetchWithRetry(url.toString(), { method: 'GET', headers: this.getHeaders() })
  }

  // Enhanced POST with retry logic
  async post<T>(endpoint: string, data: any): Promise<T> {
    return this.fetchWithRetry(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    })
  }

  async put<T>(endpoint: string, data: any): Promise<T> {
    return this.fetchWithRetry(`${this.baseUrl}${endpoint}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    })
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.fetchWithRetry(`${this.baseUrl}${endpoint}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    })
  }

  // Retry logic with exponential backoff
  private async fetchWithRetry(url: string, options: RequestInit, attempt = 1): Promise<any> {
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), this.timeout)

      const response = await fetch(url, { ...options, signal: controller.signal })
      clearTimeout(timeoutId)

      if (!response.ok) {
        throw new ApiError(`HTTP ${response.status}: ${response.statusText}`, response.status)
      }

      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        return await response.json()
      }
      return await response.text()
    } catch (error) {
      if (attempt < this.retryAttempts && this.shouldRetry(error)) {
        await this.delay(this.retryDelay * Math.pow(2, attempt - 1))
        return this.fetchWithRetry(url, options, attempt + 1)
      }
      throw error
    }
  }

  private shouldRetry(error: any): boolean {
    return (
      error.name === 'AbortError' ||
      error.name === 'TypeError' ||
      (error.status >= 500 && error.status < 600)
    )
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  private getHeaders(): Record<string, string> {
    return {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    }
  }

  async healthCheck(): Promise<boolean> {
    try {
      await this.get('/api/v2/system/status')
      return true
    } catch {
      return false
    }
  }
}

class ApiError extends Error {
  constructor(message: string, public status: number, public code?: string, public details?: any) {
    super(message)
    this.name = 'ApiError'
  }
}

export const apiClient = new ScorpiusApiClient()
export { ApiError }
'@ | Out-File -FilePath "src\lib\api-client.ts" -Encoding UTF8

# 3. Create WebSocket manager
Write-Host "🔄 Setting up WebSocket manager..." -ForegroundColor Green

@'
// WebSocket Manager with auto-reconnect
import { useState, useEffect, useCallback } from 'react'

interface WebSocketOptions {
  autoReconnect?: boolean
  reconnectInterval?: number
  maxReconnectAttempts?: number
  heartbeatInterval?: number
}

class ScorpiusWebSocketManager {
  private connections = new Map<string, WebSocket>()
  private reconnectTimers = new Map<string, NodeJS.Timeout>()
  private reconnectAttempts = new Map<string, number>()
  private eventHandlers = new Map<string, Set<(data: any) => void>>()

  private defaultOptions: Required<WebSocketOptions> = {
    autoReconnect: true,
    reconnectInterval: 5000,
    maxReconnectAttempts: 10,
    heartbeatInterval: 30000,
  }

  connect(name: string, url: string, options: WebSocketOptions = {}): Promise<WebSocket> {
    return new Promise((resolve, reject) => {
      const opts = { ...this.defaultOptions, ...options }

      try {
        const ws = new WebSocket(url)

        ws.onopen = () => {
          console.log(`🔗 WebSocket connected: ${name}`)
          this.connections.set(name, ws)
          this.reconnectAttempts.set(name, 0)
          this.setupHeartbeat(name, opts.heartbeatInterval)
          resolve(ws)
        }

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            this.notifyHandlers(name, data)
          } catch (error) {
            console.error(`WebSocket message parse error for ${name}:`, error)
          }
        }

        ws.onclose = (event) => {
          console.log(`🔌 WebSocket disconnected: ${name}`)
          this.connections.delete(name)

          if (opts.autoReconnect && !event.wasClean) {
            this.scheduleReconnect(name, url, opts)
          }
        }

        ws.onerror = (error) => {
          console.error(`❌ WebSocket error for ${name}:`, error)
          reject(error)
        }

      } catch (error) {
        reject(error)
      }
    })
  }

  subscribe(connectionName: string, handler: (data: any) => void): () => void {
    if (!this.eventHandlers.has(connectionName)) {
      this.eventHandlers.set(connectionName, new Set())
    }

    this.eventHandlers.get(connectionName)!.add(handler)

    return () => {
      this.eventHandlers.get(connectionName)?.delete(handler)
    }
  }

  send(connectionName: string, data: any): boolean {
    const ws = this.connections.get(connectionName)
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data))
      return true
    }
    return false
  }

  disconnect(connectionName: string): void {
    const ws = this.connections.get(connectionName)
    if (ws) {
      ws.close(1000, 'Client disconnect')
    }

    const timer = this.reconnectTimers.get(connectionName)
    if (timer) {
      clearTimeout(timer)
      this.reconnectTimers.delete(connectionName)
    }
  }

  getStatus(connectionName: string): 'connected' | 'disconnected' | 'connecting' | 'error' {
    const ws = this.connections.get(connectionName)
    if (!ws) return 'disconnected'

    switch (ws.readyState) {
      case WebSocket.CONNECTING: return 'connecting'
      case WebSocket.OPEN: return 'connected'
      case WebSocket.CLOSING:
      case WebSocket.CLOSED: return 'disconnected'
      default: return 'error'
    }
  }

  private scheduleReconnect(name: string, url: string, options: Required<WebSocketOptions>): void {
    const attempts = this.reconnectAttempts.get(name) || 0

    if (attempts >= options.maxReconnectAttempts) {
      console.error(`❌ Max reconnection attempts reached for ${name}`)
      return
    }

    const delay = Math.min(options.reconnectInterval * Math.pow(2, attempts), 30000)
    console.log(`🔄 Reconnecting ${name} in ${delay}ms (attempt ${attempts + 1})`)

    const timer = setTimeout(() => {
      this.reconnectAttempts.set(name, attempts + 1)
      this.connect(name, url, options).catch(() => {
        this.scheduleReconnect(name, url, options)
      })
    }, delay)

    this.reconnectTimers.set(name, timer)
  }

  private setupHeartbeat(name: string, interval: number): void {
    const heartbeat = setInterval(() => {
      if (this.getStatus(name) === 'connected') {
        this.send(name, { type: 'ping', timestamp: Date.now() })
      } else {
        clearInterval(heartbeat)
      }
    }, interval)
  }

  private notifyHandlers(connectionName: string, data: any): void {
    const handlers = this.eventHandlers.get(connectionName)
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data)
        } catch (error) {
          console.error(`Error in WebSocket handler for ${connectionName}:`, error)
        }
      })
    }
  }
}

export const wsManager = new ScorpiusWebSocketManager()

// React Hook for WebSocket connections
export function useWebSocket(name: string, url: string, options?: WebSocketOptions) {
  const [status, setStatus] = useState<'connected' | 'disconnected' | 'connecting' | 'error'>('disconnected')
  const [data, setData] = useState<any>(null)

  useEffect(() => {
    let mounted = true

    const connect = async () => {
      try {
        setStatus('connecting')
        await wsManager.connect(name, url, options)
        if (mounted) setStatus('connected')
      } catch (error) {
        if (mounted) setStatus('error')
      }
    }

    const unsubscribe = wsManager.subscribe(name, (newData) => {
      if (mounted) setData(newData)
    })

    connect()

    const statusInterval = setInterval(() => {
      if (mounted) {
        setStatus(wsManager.getStatus(name))
      }
    }, 1000)

    return () => {
      mounted = false
      clearInterval(statusInterval)
      unsubscribe()
      wsManager.disconnect(name)
    }
  }, [name, url])

  const send = useCallback((data: any) => {
    return wsManager.send(name, data)
  }, [name])

  return { status, data, send }
}
'@ | Out-File -FilePath "src\lib\websocket-manager.ts" -Encoding UTF8

# 4. Create API hooks
Write-Host "🪝 Creating API hooks..." -ForegroundColor Green
New-Item -ItemType Directory -Force -Path "src\hooks\api" | Out-Null

@'
// Type-safe API hooks with React Query
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// System Status Hook
export function useSystemStatus() {
  return useQuery({
    queryKey: ['system', 'status'],
    queryFn: () => apiClient.get('/api/v2/system/status'),
    refetchInterval: 30000,
    staleTime: 10000,
  })
}

// System Metrics Hook
export function useSystemMetrics() {
  return useQuery({
    queryKey: ['system', 'metrics'],
    queryFn: () => apiClient.get('/api/v2/system/metrics'),
    refetchInterval: 5000,
  })
}

// Trading Performance Hook
export function useTradingPerformance() {
  return useQuery({
    queryKey: ['trading', 'performance'],
    queryFn: () => apiClient.get('/api/v2/trading/performance'),
    refetchInterval: 10000,
  })
}

// Security Scan Mutation
export function useSecurityScan() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: { target: string; scan_type?: string }) =>
      apiClient.post('/api/v2/security/scan', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['security'] })
    },
  })
}

// Monitoring Dashboard Data
export function useMonitoringDashboard() {
  return useQuery({
    queryKey: ['monitoring', 'dashboard'],
    queryFn: () => apiClient.get('/api/v2/monitoring/dashboard'),
    refetchInterval: 15000,
  })
}

// API Discovery Hook
export function useApiDiscovery() {
  return useQuery({
    queryKey: ['api', 'discovery'],
    queryFn: () => apiClient.discoverApi(),
    staleTime: 300000,
    cacheTime: 600000,
  })
}

// Backend Health Check
export function useBackendHealth() {
  return useQuery({
    queryKey: ['backend', 'health'],
    queryFn: () => apiClient.healthCheck(),
    refetchInterval: 10000,
    retry: 1,
  })
}
'@ | Out-File -FilePath "src\hooks\api\useScorpiusApi.ts" -Encoding UTF8

# 5. Create WebSocket hooks
Write-Host "📡 Creating WebSocket hooks..." -ForegroundColor Green
New-Item -ItemType Directory -Force -Path "src\hooks\websockets" | Out-Null

@'
// Pre-configured WebSocket hooks
import { useEffect } from 'react'
import { useWebSocket } from '@/lib/websocket-manager'
import { useDashboardStore } from '@/stores/dashboard'

// System Metrics WebSocket
export function useSystemMetricsWS() {
  const { setSystemStatus } = useDashboardStore()

  const { status, data } = useWebSocket(
    'system-metrics',
    'ws://localhost:8000/ws/metrics'
  )

  useEffect(() => {
    if (data) {
      setSystemStatus(data)
    }
  }, [data, setSystemStatus])

  return { status, data }
}

// Threat Monitoring WebSocket
export function useThreatsWS() {
  const { addThreatAlert } = useDashboardStore()

  const { status, data } = useWebSocket(
    'threats',
    'ws://localhost:8000/ws/threats'
  )

  useEffect(() => {
    if (data && data.type === 'threat_alert') {
      addThreatAlert(data.alert)
    }
  }, [data, addThreatAlert])

  return { status, data }
}

// Trading Updates WebSocket
export function useTradingWS() {
  const { setTradingMetrics } = useDashboardStore()

  const { status, data } = useWebSocket(
    'trading',
    'ws://localhost:8000/ws/trading'
  )

  useEffect(() => {
    if (data && data.type === 'trading_update') {
      setTradingMetrics(data.metrics)
    }
  }, [data, setTradingMetrics])

  return { status, data }
}

// Master hook to connect all WebSockets
export function useAllWebSockets() {
  const systemWS = useSystemMetricsWS()
  const threatsWS = useThreatsWS()
  const tradingWS = useTradingWS()

  const allConnected = [
    systemWS.status,
    threatsWS.status,
    tradingWS.status
  ].every(status => status === 'connected')

  const anyError = [
    systemWS.status,
    threatsWS.status,
    tradingWS.status
  ].some(status => status === 'error')

  return {
    allConnected,
    anyError,
    connections: {
      system: systemWS,
      threats: threatsWS,
      trading: tradingWS
    }
  }
}
'@ | Out-File -FilePath "src\hooks\websockets\useScorpiusWebSockets.ts" -Encoding UTF8

# 6. Create connection status component
Write-Host "📊 Creating connection monitoring..." -ForegroundColor Green
New-Item -ItemType Directory -Force -Path "src\components\connection" | Out-Null

@'
// Connection Status Component
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
'@ | Out-File -FilePath "src\components\connection\ConnectionStatus.tsx" -Encoding UTF8

# 7. Create environment template
Write-Host "⚙️ Creating environment configuration..." -ForegroundColor Green

@'
# Scorpius X Backend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Development Settings
NEXT_PUBLIC_ENV=development
NEXT_PUBLIC_DEBUG_API=true
NEXT_PUBLIC_ENABLE_WEBSOCKETS=true

# Timeouts and Retry
NEXT_PUBLIC_API_TIMEOUT=10000
NEXT_PUBLIC_RETRY_ATTEMPTS=3
NEXT_PUBLIC_RETRY_DELAY=1000

# Optional: API Keys (if your backend requires them)
# NEXT_PUBLIC_API_KEY=your-api-key-here
'@ | Out-File -FilePath ".env.local" -Encoding UTF8

# 8. Update main layout to include connection monitoring
Write-Host "🔗 Integrating connection monitoring..." -ForegroundColor Green

@'
'use client'

import { ConnectionStatus } from '@/components/connection/ConnectionStatus'
import { useAllWebSockets } from '@/hooks/websockets/useScorpiusWebSockets'
import { useEffect } from 'react'

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  // Initialize all WebSocket connections
  useAllWebSockets()

  return (
    <div className="min-h-screen bg-background">
      {/* Header with connection status */}
      <header className="bg-card border-b border-border px-6 py-4">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Scorpius X</h1>
            <p className="text-sm text-muted-foreground">Blockchain Security Platform</p>
          </div>

          <ConnectionStatus />
        </div>
      </header>

      {/* Main content */}
      <main className="p-6">
        {children}
      </main>
    </div>
  )
}
'@ | Out-File -FilePath "src\components\layout\DashboardLayout.tsx" -Encoding UTF8

# 9. Test backend connection
Write-Host "🔍 Testing backend connection..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/" -Method Get -TimeoutSec 5
    Write-Host "✅ Backend is online!" -ForegroundColor Green
    Write-Host "   Platform: $($response.platform)" -ForegroundColor White
    Write-Host "   Version: $($response.version)" -ForegroundColor White

    # Test specific endpoints
    Write-Host "🧪 Testing API endpoints..." -ForegroundColor Cyan

    try {
        $statusResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v2/system/status" -Method Get -TimeoutSec 3
        Write-Host "   ✅ System Status: Working" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ System Status: Failed" -ForegroundColor Red
    }

    try {
        $metricsResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v2/system/metrics" -Method Get -TimeoutSec 3
        Write-Host "   ✅ System Metrics: Working" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ System Metrics: Failed" -ForegroundColor Red
    }

} catch {
    Write-Host "❌ Backend is not responding on http://localhost:8000" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 To start the Scorpius X backend:" -ForegroundColor Yellow
    Write-Host "   1. cd ..\backend" -ForegroundColor White
    Write-Host "   2. python main.py" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Make sure your backend is running before using the dashboard!" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Frontend-Backend Integration Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "✅ What's been configured:" -ForegroundColor Cyan
Write-Host "   • Enhanced API client with retry logic" -ForegroundColor White
Write-Host "   • WebSocket manager with auto-reconnect" -ForegroundColor White
Write-Host "   • Type-safe API hooks with React Query" -ForegroundColor White
Write-Host "   • Real-time connection monitoring" -ForegroundColor White
Write-Host "   • Error handling and graceful degradation" -ForegroundColor White
Write-Host "   • Environment configuration" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Your dashboard now has bulletproof backend connectivity!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Start your Scorpius X backend: cd ..\backend && python main.py" -ForegroundColor White
Write-Host "   2. Start your dashboard: npm run dev" -ForegroundColor White
Write-Host "   3. Open http://localhost:3000" -ForegroundColor White
Write-Host "   4. Check the connection status in the top-right corner" -ForegroundColor White
Write-Host ""
Write-Host "🌟 Ready to build an amazing dashboard! 🎨" -ForegroundColor Cyan

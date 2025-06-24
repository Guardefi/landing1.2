# 🚀 Scorpius X Dashboard - Quick Setup Script (PowerShell)
# Automatically sets up the complete dashboard project structure

Write-Host "🌟 Setting up Scorpius X Dashboard..." -ForegroundColor Cyan
Write-Host "🎯 World-Class Blockchain Security Platform UI" -ForegroundColor Yellow
Write-Host ""

# Create Next.js project
Write-Host "📦 Creating Next.js project..." -ForegroundColor Green
npx create-next-app@latest scorpius-dashboard --typescript --tailwind --eslint --app --use-npm

Set-Location scorpius-dashboard

# Install all required dependencies
Write-Host "📚 Installing dependencies..." -ForegroundColor Green
npm install @headlessui/react framer-motion zustand @tanstack/react-query
npm install recharts lucide-react socket.io-client @radix-ui/react-dialog
npm install @radix-ui/react-dropdown-menu react-hook-form class-variance-authority
npm install @radix-ui/react-select @radix-ui/react-tabs @radix-ui/react-tooltip
npm install react-flow-renderer d3 chart.js react-chartjs-2
npm install date-fns clsx tailwind-merge

# Install dev dependencies
npm install -D @types/d3 @types/node

# Create essential directory structure
Write-Host "📁 Creating project structure..." -ForegroundColor Green
New-Item -ItemType Directory -Force -Path "src\components\ui"
New-Item -ItemType Directory -Force -Path "src\components\charts"
New-Item -ItemType Directory -Force -Path "src\components\modules"
New-Item -ItemType Directory -Force -Path "src\components\layout"
New-Item -ItemType Directory -Force -Path "src\components\modules\security"
New-Item -ItemType Directory -Force -Path "src\components\modules\trading"
New-Item -ItemType Directory -Force -Path "src\components\modules\bridge"
New-Item -ItemType Directory -Force -Path "src\components\modules\analytics"
New-Item -ItemType Directory -Force -Path "src\components\modules\computing"
New-Item -ItemType Directory -Force -Path "src\components\modules\monitoring"
New-Item -ItemType Directory -Force -Path "src\components\modules\forensics"
New-Item -ItemType Directory -Force -Path "src\hooks"
New-Item -ItemType Directory -Force -Path "src\lib"
New-Item -ItemType Directory -Force -Path "src\stores"
New-Item -ItemType Directory -Force -Path "src\types"
New-Item -ItemType Directory -Force -Path "src\api"

# Create utility files
Write-Host "🛠️ Setting up utilities..." -ForegroundColor Green

# Create lib/utils.ts
@'
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const formatNumber = (num: number, decimals = 2) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(num)
}

export const formatCurrency = (amount: number, currency = 'USD') => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
  }).format(amount)
}

export const formatPercentage = (value: number, decimals = 2) => {
  return `${(value * 100).toFixed(decimals)}%`
}
'@ | Out-File -FilePath "src\lib\utils.ts" -Encoding UTF8

# Create API client
@'
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`)
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`)
    }
    return response.json()
  }

  async post<T>(endpoint: string, data: any): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`)
    }
    return response.json()
  }
}

export const apiClient = new ApiClient(API_BASE_URL)

// API endpoints
export const endpoints = {
  system: {
    status: '/api/v2/system/status',
    metrics: '/api/v2/system/metrics',
  },
  security: {
    scan: '/api/v2/security/scan',
  },
  trading: {
    performance: '/api/v2/trading/performance',
    opportunities: '/api/v2/trading/opportunities',
  },
  monitoring: {
    dashboard: '/api/v2/monitoring/dashboard',
    metrics: '/api/v2/monitoring/metrics/export',
  },
  analytics: {
    dashboard: '/api/v2/analytics/dashboard',
    report: '/api/v2/analytics/report',
  },
  bridge: {
    statistics: '/api/v2/bridge/statistics',
    transfer: '/api/v2/bridge/transfer',
  },
}
'@ | Out-File -FilePath "src\api\client.ts" -Encoding UTF8

# Create types
@'
export interface SystemStatus {
  status: string
  platform: string
  version: string
  modules_active: string
  uptime: string
  capabilities: string[]
}

export interface ThreatAlert {
  id: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  type: string
  description: string
  timestamp: string
  status: 'active' | 'resolved' | 'investigating'
}

export interface TradingMetrics {
  pnl: number
  winRate: number
  sharpeRatio: number
  totalTrades: number
  activeStrategies: number
}

export interface BridgeStats {
  totalTransfers: number
  totalVolume: number
  successRate: number
  activeLiquidity: number
  supportedChains: string[]
}

export interface AnalyticsData {
  totalUsers: number
  totalTransactions: number
  totalVolume: number
  riskScore: number
  performanceScore: number
}
'@ | Out-File -FilePath "src\types\index.ts" -Encoding UTF8

Write-Host ""
Write-Host "🎉 Scorpius X Dashboard setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Project created in: .\scorpius-dashboard" -ForegroundColor Cyan
Write-Host "🚀 Next steps:" -ForegroundColor Yellow
Write-Host "   1. cd scorpius-dashboard" -ForegroundColor White
Write-Host "   2. npm run dev" -ForegroundColor White
Write-Host "   3. Open http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Make sure Scorpius X backend is running on http://localhost:8000" -ForegroundColor Magenta
Write-Host ""
Write-Host "📚 Full build guide: ..\project-management\COMPREHENSIVE_DASHBOARD_PROMPT.md" -ForegroundColor Blue
Write-Host ""
Write-Host "🌟 Ready to build the future of blockchain security interfaces!" -ForegroundColor Green

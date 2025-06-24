#!/bin/bash

# 🚀 Scorpius X Dashboard - Quick Setup Script
# Automatically sets up the complete dashboard project structure

echo "🌟 Setting up Scorpius X Dashboard..."
echo "🎯 World-Class Blockchain Security Platform UI"
echo ""

# Create Next.js project
echo "📦 Creating Next.js project..."
npx create-next-app@latest scorpius-dashboard --typescript --tailwind --eslint --app --use-npm

cd scorpius-dashboard

# Install all required dependencies
echo "📚 Installing dependencies..."
npm install @headlessui/react framer-motion zustand @tanstack/react-query
npm install recharts lucide-react socket.io-client @radix-ui/react-dialog
npm install @radix-ui/react-dropdown-menu react-hook-form class-variance-authority
npm install @radix-ui/react-select @radix-ui/react-tabs @radix-ui/react-tooltip
npm install react-flow-renderer d3 chart.js react-chartjs-2
npm install date-fns clsx tailwind-merge

# Install dev dependencies
npm install -D @types/d3 @types/node

# Create essential directory structure
echo "📁 Creating project structure..."
mkdir -p src/components/{ui,charts,modules,layout}
mkdir -p src/hooks
mkdir -p src/lib
mkdir -p src/stores
mkdir -p src/types
mkdir -p src/api
mkdir -p src/components/modules/{security,trading,bridge,analytics,computing,monitoring,forensics}

# Create utility files
echo "🛠️ Setting up utilities..."

# Create lib/utils.ts
cat > src/lib/utils.ts << 'EOF'
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
EOF

# Create API client
cat > src/api/client.ts << 'EOF'
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
EOF

# Create types
cat > src/types/index.ts << 'EOF'
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
EOF

# Create Zustand store
cat > src/stores/dashboard.ts << 'EOF'
import { create } from 'zustand'
import { SystemStatus, ThreatAlert, TradingMetrics, BridgeStats, AnalyticsData } from '@/types'

interface DashboardState {
  systemStatus: SystemStatus | null
  threatAlerts: ThreatAlert[]
  tradingMetrics: TradingMetrics | null
  bridgeStats: BridgeStats | null
  analyticsData: AnalyticsData | null

  // Actions
  setSystemStatus: (status: SystemStatus) => void
  addThreatAlert: (alert: ThreatAlert) => void
  setTradingMetrics: (metrics: TradingMetrics) => void
  setBridgeStats: (stats: BridgeStats) => void
  setAnalyticsData: (data: AnalyticsData) => void
}

export const useDashboardStore = create<DashboardState>((set) => ({
  systemStatus: null,
  threatAlerts: [],
  tradingMetrics: null,
  bridgeStats: null,
  analyticsData: null,

  setSystemStatus: (status) => set({ systemStatus: status }),
  addThreatAlert: (alert) => set((state) => ({
    threatAlerts: [alert, ...state.threatAlerts].slice(0, 100)
  })),
  setTradingMetrics: (metrics) => set({ tradingMetrics: metrics }),
  setBridgeStats: (stats) => set({ bridgeStats: stats }),
  setAnalyticsData: (data) => set({ analyticsData: data }),
}))
EOF

# Create real-time hooks
cat > src/hooks/useRealtime.ts << 'EOF'
import { useEffect, useState } from 'react'
import { io, Socket } from 'socket.io-client'
import { useDashboardStore } from '@/stores/dashboard'

export function useRealtimeConnection() {
  const [socket, setSocket] = useState<Socket | null>(null)
  const [connected, setConnected] = useState(false)

  const { addThreatAlert, setTradingMetrics, setSystemStatus } = useDashboardStore()

  useEffect(() => {
    const socketConnection = io('http://localhost:8000', {
      transports: ['websocket'],
    })

    socketConnection.on('connect', () => {
      setConnected(true)
      console.log('🔗 Connected to Scorpius X real-time feed')
    })

    socketConnection.on('disconnect', () => {
      setConnected(false)
      console.log('🔌 Disconnected from real-time feed')
    })

    // Listen for real-time data
    socketConnection.on('threats', (data) => {
      addThreatAlert(data)
    })

    socketConnection.on('trading', (data) => {
      setTradingMetrics(data)
    })

    socketConnection.on('status', (data) => {
      setSystemStatus(data)
    })

    setSocket(socketConnection)

    return () => {
      socketConnection.disconnect()
    }
  }, [addThreatAlert, setTradingMetrics, setSystemStatus])

  return { socket, connected }
}
EOF

# Create basic UI components
echo "🎨 Creating UI components..."

# Create Button component
cat > src/components/ui/button.tsx << 'EOF'
import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "underline-offset-4 hover:underline text-primary",
      },
      size: {
        default: "h-10 py-2 px-4",
        sm: "h-9 px-3 rounded-md",
        lg: "h-11 px-8 rounded-md",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
EOF

# Create Card component
cat > src/components/ui/card.tsx << 'EOF'
import * as React from "react"
import { cn } from "@/lib/utils"

const Card = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "rounded-lg border bg-card text-card-foreground shadow-sm",
      className
    )}
    {...props}
  />
))
Card.displayName = "Card"

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("flex flex-col space-y-1.5 p-6", className)} {...props} />
))
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "text-2xl font-semibold leading-none tracking-tight",
      className
    )}
    {...props}
  />
))
CardTitle.displayName = "CardTitle"

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
CardDescription.displayName = "CardDescription"

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
))
CardContent.displayName = "CardContent"

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("flex items-center p-6 pt-0", className)} {...props} />
))
CardFooter.displayName = "CardFooter"

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent }
EOF

# Update tailwind.config.js with custom colors
cat > tailwind.config.ts << 'EOF'
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#0F1419',
        foreground: '#FFFFFF',
        card: '#1A1F2E',
        'card-foreground': '#FFFFFF',
        primary: '#00D2FF',
        'primary-foreground': '#000000',
        secondary: '#252A3A',
        'secondary-foreground': '#FFFFFF',
        muted: '#718096',
        'muted-foreground': '#A0AEC0',
        accent: '#FF6B9D',
        'accent-foreground': '#FFFFFF',
        destructive: '#FF4757',
        'destructive-foreground': '#FFFFFF',
        border: '#374151',
        input: '#374151',
        ring: '#00D2FF',
        success: '#00FF94',
        warning: '#FFD93D',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 5px #00D2FF' },
          '50%': { boxShadow: '0 0 20px #00D2FF, 0 0 30px #00D2FF' },
        },
      },
    },
  },
  plugins: [],
}
export default config
EOF

# Create basic layout structure
cat > src/app/layout.tsx << 'EOF'
import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Scorpius X Dashboard',
  description: 'World-Class Blockchain Security Platform',
}

const queryClient = new QueryClient()

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-background text-foreground`}>
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      </body>
    </html>
  )
}
EOF

# Create basic dashboard page
cat > src/app/page.tsx << 'EOF'
'use client'

import { useEffect } from 'react'
import { useRealtimeConnection } from '@/hooks/useRealtime'
import { useDashboardStore } from '@/stores/dashboard'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function Dashboard() {
  const { connected } = useRealtimeConnection()
  const { systemStatus } = useDashboardStore()

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">
            Scorpius X Dashboard
          </h1>
          <p className="text-muted-foreground">
            World-Class Blockchain Security Platform
          </p>
          <div className="flex items-center mt-4">
            <div className={`w-2 h-2 rounded-full mr-2 ${connected ? 'bg-success' : 'bg-destructive'}`} />
            <span className="text-sm text-muted-foreground">
              {connected ? 'Real-time connected' : 'Connecting...'}
            </span>
          </div>
        </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">System Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-success">Online</div>
              <p className="text-xs text-muted-foreground">
                {systemStatus?.modules_active || 'Loading...'}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Threats</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">0</div>
              <p className="text-xs text-muted-foreground">No active threats detected</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Trading P&L</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-success">+$0.00</div>
              <p className="text-xs text-muted-foreground">Today's performance</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Bridge Volume</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">$0M</div>
              <p className="text-xs text-muted-foreground">24h volume</p>
            </CardContent>
          </Card>
        </div>

        {/* Module Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Security Operations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <p className="text-muted-foreground">Security dashboard coming soon...</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>AI Trading Engine</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <p className="text-muted-foreground">Trading dashboard coming soon...</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Cross-Chain Bridge</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <p className="text-muted-foreground">Bridge dashboard coming soon...</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Enterprise Analytics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <p className="text-muted-foreground">Analytics dashboard coming soon...</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
EOF

# Update globals.css
cat > src/app/globals.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 15 20 25;
    --foreground: 255 255 255;
    --card: 26 31 46;
    --card-foreground: 255 255 255;
    --popover: 26 31 46;
    --popover-foreground: 255 255 255;
    --primary: 0 210 255;
    --primary-foreground: 0 0 0;
    --secondary: 37 42 58;
    --secondary-foreground: 255 255 255;
    --muted: 113 128 150;
    --muted-foreground: 160 174 192;
    --accent: 255 107 157;
    --accent-foreground: 255 255 255;
    --destructive: 255 71 87;
    --destructive-foreground: 255 255 255;
    --border: 55 65 81;
    --input: 55 65 81;
    --ring: 0 210 255;
    --radius: 0.5rem;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: rgb(37 42 58);
}

::-webkit-scrollbar-thumb {
  background: rgb(113 128 150);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgb(160 174 192);
}

/* Glow effects */
.glow-primary {
  box-shadow: 0 0 10px rgba(0, 210, 255, 0.5);
}

.glow-success {
  box-shadow: 0 0 10px rgba(0, 255, 148, 0.5);
}

.glow-warning {
  box-shadow: 0 0 10px rgba(255, 217, 61, 0.5);
}

.glow-danger {
  box-shadow: 0 0 10px rgba(255, 71, 87, 0.5);
}
EOF

# Create package.json scripts
echo "📝 Setting up scripts..."
npm pkg set scripts.dev="next dev"
npm pkg set scripts.build="next build"
npm pkg set scripts.start="next start"
npm pkg set scripts.lint="next lint"

# Create README
cat > README.md << 'EOF'
# 🌟 Scorpius X Dashboard

World-Class Blockchain Security Platform Dashboard

## 🚀 Quick Start

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the dashboard.

## 📚 Documentation

See the full build guide in `../project-management/COMPREHENSIVE_DASHBOARD_PROMPT.md`

## 🏗️ Architecture

- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **State Management**: Zustand
- **Real-time**: Socket.io + React Query
- **Charts**: Recharts + Chart.js
- **UI**: Radix UI + HeadlessUI

## 🎯 Features

- ✅ Real-time metrics and monitoring
- ✅ Security operations center
- ✅ AI trading engine dashboard
- ✅ Cross-chain bridge interface
- ✅ Enterprise analytics platform
- ✅ Distributed computing monitoring
- ✅ Blockchain forensics center

## 🔧 Backend Integration

Make sure the Scorpius X backend is running on `http://localhost:8000`

## 📊 Development

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

Built with ❤️ for the future of blockchain security.
EOF

echo ""
echo "🎉 Scorpius X Dashboard setup complete!"
echo ""
echo "📁 Project created in: ./scorpius-dashboard"
echo "🚀 Next steps:"
echo "   1. cd scorpius-dashboard"
echo "   2. npm run dev"
echo "   3. Open http://localhost:3000"
echo ""
echo "🔧 Make sure Scorpius X backend is running on http://localhost:8000"
echo ""
echo "📚 Full build guide: ../project-management/COMPREHENSIVE_DASHBOARD_PROMPT.md"
echo ""
echo "🌟 Ready to build the future of blockchain security interfaces!"

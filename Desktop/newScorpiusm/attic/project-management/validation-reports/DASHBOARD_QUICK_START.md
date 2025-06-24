# 🚀 SCORPIUS X DASHBOARD - QUICK START TEMPLATE

_Get Started Building Immediately_

## ⚡ **INSTANT SETUP** (5 Minutes)

### **1. Initialize Project**

```bash
# Create Next.js project
npx create-next-app@latest scorpius-dashboard --typescript --tailwind --eslint --app

cd scorpius-dashboard

# Install required dependencies
npm install @headlessui/react framer-motion zustand @tanstack/react-query react-hook-form recharts lucide-react socket.io-client @radix-ui/react-dialog @radix-ui/react-dropdown-menu
```

### **2. Project Structure Setup**

```bash
# Create essential directories
mkdir -p src/components/{ui,charts,modules,layout}
mkdir -p src/hooks
mkdir -p src/lib
mkdir -p src/stores
mkdir -p src/types
mkdir -p src/api
```

---

## 📁 **STARTER FILE TEMPLATES**

### **Layout Component** (`src/components/layout/DashboardLayout.tsx`)

```tsx
'use client';

import React, { useState } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { cn } from '@/lib/utils';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen bg-slate-900">
      {/* Sidebar */}
      <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} />

      {/* Main Content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header onMenuClick={() => setSidebarOpen(true)} />

        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  );
}
```

### **Navigation Structure** (`src/components/layout/Sidebar.tsx`)

```tsx
'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  Home,
  Shield,
  TrendingUp,
  Bridge,
  BarChart3,
  Zap,
  Activity,
  Settings,
  X,
} from 'lucide-react';

const navigation = [
  { name: 'Overview', href: '/dashboard', icon: Home },
  {
    name: 'Security',
    icon: Shield,
    children: [
      { name: 'Elite Security', href: '/security/elite' },
      { name: 'Threat Monitor', href: '/security/threats' },
      { name: 'Quantum Crypto', href: '/security/quantum' },
    ],
  },
  {
    name: 'Trading',
    icon: TrendingUp,
    children: [
      { name: 'AI Trading', href: '/trading/ai' },
      { name: 'MEV Protection', href: '/trading/mev' },
      { name: 'Portfolio', href: '/trading/portfolio' },
    ],
  },
  {
    name: 'Cross-Chain',
    icon: Bridge,
    children: [
      { name: 'Bridge Network', href: '/bridge/network' },
      { name: 'Transfers', href: '/bridge/transfers' },
      { name: 'Validators', href: '/bridge/validators' },
    ],
  },
  {
    name: 'Analytics',
    icon: BarChart3,
    children: [
      { name: 'Enterprise', href: '/analytics/enterprise' },
      { name: 'Performance', href: '/analytics/performance' },
      { name: 'Reports', href: '/analytics/reports' },
    ],
  },
  {
    name: 'Computing',
    icon: Zap,
    children: [
      { name: 'Cluster', href: '/computing/cluster' },
      { name: 'Tasks', href: '/computing/tasks' },
      { name: 'Resources', href: '/computing/resources' },
    ],
  },
  {
    name: 'Monitoring',
    icon: Activity,
    children: [
      { name: 'Health', href: '/monitoring/health' },
      { name: 'Metrics', href: '/monitoring/metrics' },
      { name: 'Alerts', href: '/monitoring/alerts' },
    ],
  },
  { name: 'Settings', href: '/settings', icon: Settings },
];

interface SidebarProps {
  open: boolean;
  setOpen: (open: boolean) => void;
}

export function Sidebar({ open, setOpen }: SidebarProps) {
  const pathname = usePathname();

  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div
            className="fixed inset-0 bg-black bg-opacity-50"
            onClick={() => setOpen(false)}
          />
        </div>
      )}

      {/* Sidebar */}
      <div
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-64 bg-slate-800 border-r border-slate-700 transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:z-auto',
          open ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-16 items-center justify-between px-4">
            <div className="flex items-center space-x-2">
              <div className="h-8 w-8 rounded bg-gradient-to-br from-indigo-500 to-purple-600" />
              <span className="text-xl font-bold text-white">Scorpius X</span>
            </div>
            <button
              onClick={() => setOpen(false)}
              className="lg:hidden text-slate-400 hover:text-white"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 px-2 py-4">
            {navigation.map(item => (
              <div key={item.name}>
                {item.children ? (
                  <div>
                    <div className="flex items-center px-2 py-2 text-sm font-medium text-slate-300">
                      <item.icon className="mr-3 h-5 w-5" />
                      {item.name}
                    </div>
                    <div className="ml-8 space-y-1">
                      {item.children.map(child => (
                        <Link
                          key={child.name}
                          href={child.href}
                          className={cn(
                            'block px-2 py-2 text-sm rounded-md transition-colors',
                            pathname === child.href
                              ? 'bg-indigo-600 text-white'
                              : 'text-slate-300 hover:bg-slate-700 hover:text-white',
                          )}
                        >
                          {child.name}
                        </Link>
                      ))}
                    </div>
                  </div>
                ) : (
                  <Link
                    href={item.href}
                    className={cn(
                      'flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors',
                      pathname === item.href
                        ? 'bg-indigo-600 text-white'
                        : 'text-slate-300 hover:bg-slate-700 hover:text-white',
                    )}
                  >
                    <item.icon className="mr-3 h-5 w-5" />
                    {item.name}
                  </Link>
                )}
              </div>
            ))}
          </nav>
        </div>
      </div>
    </>
  );
}
```

### **Header Component** (`src/components/layout/Header.tsx`)

```tsx
'use client';

import React from 'react';
import { Search, Bell, Menu, Activity } from 'lucide-react';
import { SystemStatus } from '@/components/ui/SystemStatus';
import { UserMenu } from '@/components/ui/UserMenu';

interface HeaderProps {
  onMenuClick: () => void;
}

export function Header({ onMenuClick }: HeaderProps) {
  return (
    <header className="flex h-16 items-center justify-between border-b border-slate-700 bg-slate-800 px-6">
      {/* Left: Menu + Breadcrumb */}
      <div className="flex items-center space-x-4">
        <button
          onClick={onMenuClick}
          className="lg:hidden text-slate-400 hover:text-white"
        >
          <Menu className="h-6 w-6" />
        </button>

        <nav className="flex" aria-label="Breadcrumb">
          <ol className="flex items-center space-x-2">
            <li className="text-slate-400">Dashboard</li>
            <li className="text-slate-600">/</li>
            <li className="text-white font-medium">Overview</li>
          </ol>
        </nav>
      </div>

      {/* Center: Search */}
      <div className="flex-1 max-w-md mx-8">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search across all modules..."
            className="w-full rounded-lg bg-slate-700 border border-slate-600 py-2 pl-10 pr-4 text-white placeholder-slate-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* Right: Status + Notifications + User */}
      <div className="flex items-center space-x-4">
        <SystemStatus />

        <button className="relative rounded-lg p-2 text-slate-400 hover:bg-slate-700 hover:text-white">
          <Bell className="h-5 w-5" />
          <span className="absolute -top-1 -right-1 h-3 w-3 rounded-full bg-red-500 text-[10px] font-bold text-white flex items-center justify-center">
            3
          </span>
        </button>

        <button className="rounded-lg p-2 text-slate-400 hover:bg-slate-700 hover:text-white">
          <Activity className="h-5 w-5" />
        </button>

        <UserMenu />
      </div>
    </header>
  );
}
```

### **Metric Card Component** (`src/components/ui/MetricCard.tsx`)

```tsx
'use client';

import React from 'react';
import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: string;
  trend?: 'up' | 'down' | 'neutral';
  icon: LucideIcon;
  className?: string;
}

export function MetricCard({
  title,
  value,
  change,
  trend = 'neutral',
  icon: Icon,
  className,
}: MetricCardProps) {
  return (
    <div
      className={cn(
        'bg-slate-800 border border-slate-700 rounded-xl p-6 hover:border-indigo-500/50 transition-colors',
        className,
      )}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="rounded-lg bg-indigo-500/10 p-2">
            <Icon className="h-6 w-6 text-indigo-400" />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-400">{title}</p>
            <p className="text-2xl font-bold text-white">{value}</p>
          </div>
        </div>

        {change && (
          <div
            className={cn(
              'text-sm font-medium',
              trend === 'up' && 'text-emerald-400',
              trend === 'down' && 'text-red-400',
              trend === 'neutral' && 'text-slate-400',
            )}
          >
            {change}
          </div>
        )}
      </div>
    </div>
  );
}
```

### **Overview Dashboard Page** (`src/app/dashboard/page.tsx`)

```tsx
'use client';

import React from 'react';
import { MetricCard } from '@/components/ui/MetricCard';
import { ThreatMap } from '@/components/modules/security/ThreatMap';
import { TradingChart } from '@/components/modules/trading/TradingChart';
import { SystemHealth } from '@/components/modules/monitoring/SystemHealth';
import { ActivityFeed } from '@/components/ui/ActivityFeed';
import { Shield, TrendingUp, Bridge, Zap } from 'lucide-react';

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Dashboard Overview</h1>
        <p className="text-slate-400">
          Real-time insights across all Scorpius X modules
        </p>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Security Score"
          value="98.7%"
          change="+2.3%"
          trend="up"
          icon={Shield}
        />
        <MetricCard
          title="Trading P&L"
          value="$47,832"
          change="+12.4%"
          trend="up"
          icon={TrendingUp}
        />
        <MetricCard
          title="Cross-Chain Volume"
          value="$2.3M"
          change="+8.9%"
          trend="up"
          icon={Bridge}
        />
        <MetricCard
          title="System Load"
          value="67%"
          change="-5%"
          trend="down"
          icon={Zap}
        />
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Main Content */}
        <div className="lg:col-span-2 space-y-6">
          <ThreatMap />
          <TradingChart />
        </div>

        {/* Right Column - Sidebar */}
        <div className="space-y-6">
          <SystemHealth />
          <ActivityFeed />
        </div>
      </div>
    </div>
  );
}
```

### **API Client Setup** (`src/lib/api.ts`)

```typescript
import { QueryClient } from '@tanstack/react-query';

// Create query client
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 3,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// API base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// API client class
class ScorpiusAPI {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  // Security Module
  async getSecurityStatus() {
    return this.request('/api/v2/security/status');
  }

  async getThreats() {
    return this.request('/api/v2/security/threats');
  }

  // Trading Module
  async getTradingStatus() {
    return this.request('/api/v2/trading/status');
  }

  async getPortfolio() {
    return this.request('/api/v2/trading/portfolio');
  }

  // Bridge Module
  async getBridgeStatus() {
    return this.request('/api/v2/bridge/status');
  }

  async getNetworks() {
    return this.request('/api/v2/bridge/networks');
  }

  // Analytics Module
  async getAnalytics() {
    return this.request('/api/v2/analytics/dashboard');
  }

  // Computing Module
  async getClusterStatus() {
    return this.request('/api/v2/computing/cluster');
  }

  // Monitoring Module
  async getSystemHealth() {
    return this.request('/api/v2/monitoring/health');
  }
}

export const api = new ScorpiusAPI(API_BASE_URL);
```

### **WebSocket Hook** (`src/hooks/useWebSocket.ts`)

```typescript
import { useEffect, useRef, useState } from 'react';

interface UseWebSocketOptions {
  onMessage?: (data: any) => void;
  onError?: (error: Event) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  reconnectInterval?: number;
}

export function useWebSocket(url: string, options: UseWebSocketOptions = {}) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  const {
    onMessage,
    onError,
    onConnect,
    onDisconnect,
    reconnectInterval = 5000,
  } = options;

  const connect = () => {
    try {
      wsRef.current = new WebSocket(url);

      wsRef.current.onopen = () => {
        setIsConnected(true);
        onConnect?.();
        console.log(`WebSocket connected to ${url}`);
      };

      wsRef.current.onmessage = event => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
          onMessage?.(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      wsRef.current.onclose = () => {
        setIsConnected(false);
        onDisconnect?.();
        console.log(`WebSocket disconnected from ${url}`);

        // Attempt to reconnect
        reconnectTimeoutRef.current = setTimeout(connect, reconnectInterval);
      };

      wsRef.current.onerror = error => {
        console.error('WebSocket error:', error);
        onError?.(error);
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }
  };

  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    wsRef.current?.close();
  };

  const sendMessage = (message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  };

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [url]);

  return {
    isConnected,
    lastMessage,
    sendMessage,
    disconnect,
  };
}
```

---

## 🎨 **STYLING SETUP**

### **Tailwind Configuration** (`tailwind.config.js`)

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        slate: {
          750: '#293548',
        },
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
};
```

### **Global Styles** (`src/app/globals.css`)

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  * {
    border-color: theme('colors.slate.700');
  }

  body {
    background-color: theme('colors.slate.900');
    color: theme('colors.slate.50');
  }
}

@layer components {
  .gradient-bg {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  }

  .card {
    @apply bg-slate-800 border border-slate-700 rounded-xl p-6;
  }

  .btn-primary {
    @apply bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-lg transition-colors;
  }

  .btn-secondary {
    @apply bg-slate-700 hover:bg-slate-600 text-white font-medium py-2 px-4 rounded-lg transition-colors;
  }
}
```

---

## 🔧 **UTILITY FUNCTIONS** (`src/lib/utils.ts`)

```typescript
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
}

export function formatPercentage(value: number): string {
  return `${value >= 0 ? '+' : ''}${value.toFixed(1)}%`;
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US').format(value);
}

export function getStatusColor(status: string): string {
  switch (status.toLowerCase()) {
    case 'healthy':
    case 'active':
    case 'online':
      return 'text-emerald-400';
    case 'warning':
    case 'degraded':
      return 'text-yellow-400';
    case 'critical':
    case 'error':
    case 'offline':
      return 'text-red-400';
    default:
      return 'text-slate-400';
  }
}
```

---

## 🚀 **GETTING STARTED CHECKLIST**

### ✅ **Phase 1: Basic Setup** (30 minutes)

- [ ] Initialize Next.js project with TypeScript
- [ ] Install all required dependencies
- [ ] Create project directory structure
- [ ] Setup Tailwind CSS configuration
- [ ] Add global styles

### ✅ **Phase 2: Core Layout** (1 hour)

- [ ] Implement DashboardLayout component
- [ ] Create Sidebar with navigation
- [ ] Build Header with search and status
- [ ] Add responsive design breakpoints
- [ ] Test navigation flow

### ✅ **Phase 3: UI Components** (2 hours)

- [ ] Create MetricCard component
- [ ] Build SystemStatus indicator
- [ ] Implement ActivityFeed
- [ ] Add UserMenu component
- [ ] Test component library

### ✅ **Phase 4: API Integration** (1 hour)

- [ ] Setup API client with proper typing
- [ ] Configure React Query
- [ ] Add WebSocket hook
- [ ] Test API connections
- [ ] Handle error states

### ✅ **Phase 5: Module Pages** (4 hours)

- [ ] Create Overview dashboard
- [ ] Build Security module pages
- [ ] Implement Trading interface
- [ ] Add Bridge network page
- [ ] Create Analytics dashboard

---

## 🎯 **IMMEDIATE NEXT STEPS**

1. **Run the setup commands** above to get your project started
2. **Copy the starter templates** into your project structure
3. **Customize the styling** to match your brand preferences
4. **Connect to your backend API** endpoints
5. **Start with the Overview page** and expand module by module

---

**🚀 You now have everything you need to build a world-class Scorpius X dashboard! Start coding and watch your blockchain security platform come to life!**

_Need help? Reference the detailed build guide for advanced features and patterns._

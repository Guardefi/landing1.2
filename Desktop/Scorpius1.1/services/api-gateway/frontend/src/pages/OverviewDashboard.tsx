import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import {
  Shield,
  TrendingUp,
  AlertTriangle,
  Activity,
  DollarSign,
  Users,
  Zap,
  Eye,
} from 'lucide-react';

// Mock data - replace with real API calls to your backend
const useSystemMetrics = () => {
  const [metrics, setMetrics] = useState({
    systemHealth: 98,
    activeThreats: 0,
    tradingPnL: 0,
    bridgeVolume: 0,
    totalUsers: 1247,
    transactionsToday: 8429,
    activeScanners: 12,
    quantumDeployments: 3,
  });

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        tradingPnL: prev.tradingPnL + (Math.random() - 0.5) * 100,
        transactionsToday: prev.transactionsToday + Math.floor(Math.random() * 5),
        systemHealth: Math.max(
          95,
          Math.min(100, prev.systemHealth + (Math.random() - 0.5) * 2),
        ),
      }));
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  return metrics;
};

export function OverviewDashboard() {
  const metrics = useSystemMetrics();

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard Overview</h1>
          <p className="text-muted-foreground">
            Real-time monitoring of all Scorpius X security operations
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-muted-foreground">Live</span>
          </div>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-gradient-to-r from-blue-500/10 to-cyan-500/10 border-blue-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Health</CardTitle>
            <Activity className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-500">
              {metrics.systemHealth.toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">All modules operational</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-red-500/10 to-orange-500/10 border-red-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Threats</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-500">
              {metrics.activeThreats}
            </div>
            <p className="text-xs text-muted-foreground">No threats detected</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border-green-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Trading P&L</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">
              {formatCurrency(metrics.tradingPnL)}
            </div>
            <p className="text-xs text-muted-foreground">Today's performance</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-purple-500/10 to-pink-500/10 border-purple-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Bridge Volume</CardTitle>
            <DollarSign className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-500">
              {formatCurrency(metrics.bridgeVolume)}M
            </div>
            <p className="text-xs text-muted-foreground">24h volume</p>
          </CardContent>
        </Card>
      </div>

      {/* Module Status Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Shield className="h-5 w-5 text-blue-500" />
              <span>Security Operations</span>
              <Badge variant="outline" className="ml-auto">
                Active
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Active Scanners</span>
              <span className="font-mono">{metrics.activeScanners}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Threats Blocked</span>
              <span className="font-mono">1,247</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Vulnerability Scans</span>
              <span className="font-mono">24/7</span>
            </div>
            <Button variant="outline" size="sm" className="w-full">
              View Security Center
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-green-500" />
              <span>AI Trading Engine</span>
              <Badge variant="outline" className="ml-auto">
                Profitable
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Win Rate</span>
              <span className="font-mono">73.2%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Sharpe Ratio</span>
              <span className="font-mono">2.8</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Total Trades</span>
              <span className="font-mono">847</span>
            </div>
            <Button variant="outline" size="sm" className="w-full">
              View Trading Dashboard
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Eye className="h-5 w-5 text-purple-500" />
              <span>Blockchain Forensics</span>
              <Badge variant="outline" className="ml-auto">
                Analyzing
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">
                Transactions Analyzed
              </span>
              <span className="font-mono">
                {formatNumber(metrics.transactionsToday)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Risk Score</span>
              <span className="font-mono">Low</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Compliance</span>
              <span className="font-mono">100%</span>
            </div>
            <Button variant="outline" size="sm" className="w-full">
              View Forensics Center
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="h-5 w-5 text-orange-500" />
              <span>Network Monitoring</span>
              <Badge variant="outline" className="ml-auto">
                Healthy
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Network Uptime</span>
              <span className="font-mono">99.98%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Response Time</span>
              <span className="font-mono">12ms</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Active Nodes</span>
              <span className="font-mono">247</span>
            </div>
            <Button variant="outline" size="sm" className="w-full">
              View Network Status
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Zap className="h-5 w-5 text-yellow-500" />
              <span>Quantum Security</span>
              <Badge variant="outline" className="ml-auto">
                Deployed
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Quantum Deployments</span>
              <span className="font-mono">{metrics.quantumDeployments}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Encryption Level</span>
              <span className="font-mono">Post-Quantum</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Security Rating</span>
              <span className="font-mono">AAA+</span>
            </div>
            <Button variant="outline" size="sm" className="w-full">
              View Quantum Console
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Users className="h-5 w-5 text-blue-500" />
              <span>User Analytics</span>
              <Badge variant="outline" className="ml-auto">
                Growing
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Total Users</span>
              <span className="font-mono">{formatNumber(metrics.totalUsers)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Active Sessions</span>
              <span className="font-mono">89</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Growth Rate</span>
              <span className="font-mono">+12.3%</span>
            </div>
            <Button variant="outline" size="sm" className="w-full">
              View Analytics
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

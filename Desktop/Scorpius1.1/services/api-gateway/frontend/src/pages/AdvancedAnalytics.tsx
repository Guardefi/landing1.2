'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
  ScatterChart,
  Scatter,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar as RechartsRadar,
} from 'recharts';
import {
  BarChart3,
  LineChart as LineChartIcon,
  PieChart as PieChartIcon,
  TrendingUp,
  TrendingDown,
  Activity,
  Target,
  Zap,
  Shield,
  AlertTriangle,
  Download,
  Filter,
  Calendar,
  Users,
  DollarSign,
} from 'lucide-react';

// Mock data for different analytics views
const tradingPerformanceData = [
  { date: '2024-01', profit: 4000, volume: 24000, trades: 150 },
  { date: '2024-02', profit: 3000, volume: 13980, trades: 120 },
  { date: '2024-03', profit: 2000, volume: 9800, trades: 180 },
  { date: '2024-04', profit: 2780, volume: 39080, trades: 200 },
  { date: '2024-05', profit: 1890, volume: 48000, trades: 165 },
  { date: '2024-06', profit: 2390, volume: 38000, trades: 190 },
];

const securityMetricsData = [
  { name: 'High Risk', value: 12, color: '#ef4444' },
  { name: 'Medium Risk', value: 35, color: '#f97316' },
  { name: 'Low Risk', value: 180, color: '#eab308' },
  { name: 'Secure', value: 423, color: '#22c55e' },
];

const networkAnalysisData = [
  { chain: 'Ethereum', transactions: 8420, volume: 12500000, fees: 45000 },
  { chain: 'BSC', transactions: 5240, volume: 8200000, fees: 12000 },
  { chain: 'Polygon', transactions: 12580, volume: 3400000, fees: 8000 },
  { chain: 'Arbitrum', transactions: 3420, volume: 6700000, fees: 15000 },
  { chain: 'Optimism', transactions: 2840, volume: 4200000, fees: 11000 },
];

const riskProfileData = [
  { subject: 'Liquidity', A: 80, B: 110, fullMark: 150 },
  { subject: 'Volatility', A: 70, B: 130, fullMark: 150 },
  { subject: 'Slippage', A: 86, B: 130, fullMark: 150 },
  { subject: 'Smart Contract', A: 99, B: 100, fullMark: 150 },
  { subject: 'Market Cap', A: 85, B: 90, fullMark: 150 },
  { subject: 'Trading Volume', A: 65, B: 85, fullMark: 150 },
];

const timeSeriesData = Array.from({ length: 30 }, (_, i) => ({
  time: `${i + 1}h`,
  price: 2000 + Math.sin(i * 0.3) * 200 + Math.random() * 100,
  volume: 1000 + Math.random() * 500,
  arbitrage: Math.random() * 10,
}));

export function AdvancedAnalytics() {
  const [activeTab, setActiveTab] = useState('trading');
  const [timeRange, setTimeRange] = useState('24h');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Advanced Analytics</h1>
          <p className="text-muted-foreground">
            Deep insights into trading performance, security metrics, and market
            analysis
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm">
            <Filter className="h-4 w-4 mr-2" />
            Filter
          </Button>
          <Button variant="outline" size="sm">
            <Calendar className="h-4 w-4 mr-2" />
            {timeRange}
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Key Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total P&L</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">+$45,231.89</div>
            <p className="text-xs text-muted-foreground">
              <TrendingUp className="inline h-3 w-3 mr-1" />
              +20.1% from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Volume</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">$2.4M</div>
            <p className="text-xs text-muted-foreground">
              <TrendingUp className="inline h-3 w-3 mr-1" />
              +15.3% from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Strategies</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12</div>
            <p className="text-xs text-muted-foreground">3 high performance</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Security Score</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">98.5%</div>
            <p className="text-xs text-muted-foreground">Excellent security posture</p>
          </CardContent>
        </Card>
      </div>

      {/* Analytics Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="trading">Trading</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="network">Network</TabsTrigger>
          <TabsTrigger value="risk">Risk Analysis</TabsTrigger>
          <TabsTrigger value="realtime">Real-time</TabsTrigger>
        </TabsList>

        <TabsContent value="trading" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Trading Performance</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={tradingPerformanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="profit"
                      stackId="1"
                      stroke="#8884d8"
                      fill="#8884d8"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Volume vs Trades</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <ScatterChart data={tradingPerformanceData}>
                    <CartesianGrid />
                    <XAxis dataKey="volume" name="Volume" />
                    <YAxis dataKey="trades" name="Trades" />
                    <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                    <Scatter name="Performance" dataKey="profit" fill="#8884d8" />
                  </ScatterChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="security" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Security Risk Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={securityMetricsData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) =>
                        `${name} ${(percent * 100).toFixed(0)}%`
                      }
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {securityMetricsData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Threat Detection Timeline</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={timeSeriesData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="arbitrage"
                      stroke="#ff7300"
                      name="Threat Level"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="network" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Cross-Chain Network Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={networkAnalysisData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="chain" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="transactions" fill="#8884d8" name="Transactions" />
                  <Bar dataKey="volume" fill="#82ca9d" name="Volume ($)" />
                  <Bar dataKey="fees" fill="#ffc658" name="Fees ($)" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="risk" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Risk Profile Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <RadarChart data={riskProfileData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="subject" />
                    <PolarRadiusAxis />
                    <RechartsRadar
                      name="Current"
                      dataKey="A"
                      stroke="#8884d8"
                      fill="#8884d8"
                      fillOpacity={0.6}
                    />
                    <RechartsRadar
                      name="Benchmark"
                      dataKey="B"
                      stroke="#82ca9d"
                      fill="#82ca9d"
                      fillOpacity={0.6}
                    />
                    <Legend />
                  </RadarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Risk Metrics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Value at Risk (VaR)</span>
                  <Badge variant="destructive">-$12,430</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Sharpe Ratio</span>
                  <Badge variant="secondary">1.85</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Maximum Drawdown</span>
                  <Badge variant="destructive">-8.5%</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Beta</span>
                  <Badge variant="secondary">0.92</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Volatility</span>
                  <Badge variant="outline">15.2%</Badge>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="realtime" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Real-time Market Data</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={timeSeriesData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Legend />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="price"
                    stroke="#8884d8"
                    name="Price"
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="volume"
                    stroke="#82ca9d"
                    name="Volume"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

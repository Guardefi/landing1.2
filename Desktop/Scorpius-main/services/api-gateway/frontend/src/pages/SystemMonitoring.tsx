'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import {
  Server,
  Cpu,
  HardDrive,
  Wifi,
  Battery,
  Activity,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Zap,
  Database,
  Network,
  HardDrive as Memory,
  Gauge,
  TrendingUp,
  TrendingDown,
  RefreshCw,
  Settings,
  Terminal,
  Cloud,
  Shield,
} from 'lucide-react';

// Mock system metrics data
const systemMetrics = {
  cpu: {
    usage: 78,
    cores: 16,
    frequency: 3.4,
    temperature: 65,
  },
  memory: {
    used: 24.5,
    total: 32,
    usage: 76.5,
  },
  storage: {
    used: 450,
    total: 1000,
    usage: 45,
  },
  network: {
    inbound: 125.6,
    outbound: 87.3,
    latency: 12,
  },
};

const performanceData = Array.from({ length: 24 }, (_, i) => ({
  time: `${i}:00`,
  cpu: 30 + Math.sin(i * 0.5) * 20 + Math.random() * 10,
  memory: 40 + Math.sin(i * 0.3) * 15 + Math.random() * 8,
  network: 50 + Math.sin(i * 0.4) * 25 + Math.random() * 12,
  disk: 20 + Math.sin(i * 0.2) * 10 + Math.random() * 5,
}));

const serviceStatus = [
  { name: 'API Server', status: 'running', uptime: '99.9%', cpu: 45, memory: 2.1 },
  {
    name: 'WebSocket Server',
    status: 'running',
    uptime: '99.8%',
    cpu: 32,
    memory: 1.8,
  },
  { name: 'Database', status: 'running', uptime: '99.9%', cpu: 15, memory: 4.2 },
  { name: 'Redis Cache', status: 'running', uptime: '99.7%', cpu: 8, memory: 0.5 },
  { name: 'Scanner Engine', status: 'running', uptime: '98.9%', cpu: 78, memory: 3.2 },
  { name: 'MEV Bot', status: 'warning', uptime: '97.2%', cpu: 65, memory: 2.8 },
  { name: 'Bridge Service', status: 'running', uptime: '99.5%', cpu: 23, memory: 1.1 },
  { name: 'Analytics Engine', status: 'stopped', uptime: '0%', cpu: 0, memory: 0 },
];

const networkTopology = [
  { name: 'Load Balancer', connections: 256, latency: 5 },
  { name: 'API Gateway', connections: 124, latency: 8 },
  { name: 'Main Server', connections: 89, latency: 12 },
  { name: 'Database Cluster', connections: 45, latency: 3 },
  { name: 'Cache Layer', connections: 78, latency: 2 },
];

const alertsData = [
  {
    id: 1,
    type: 'warning',
    title: 'High CPU Usage',
    description: 'Scanner engine using 85% CPU',
    time: '2 min ago',
  },
  {
    id: 2,
    type: 'error',
    title: 'Service Down',
    description: 'Analytics engine stopped responding',
    time: '5 min ago',
  },
  {
    id: 3,
    type: 'info',
    title: 'Backup Complete',
    description: 'Daily database backup completed successfully',
    time: '1 hour ago',
  },
  {
    id: 4,
    type: 'warning',
    title: 'Memory Usage',
    description: 'Memory usage above 80% threshold',
    time: '2 hours ago',
  },
];

export function SystemMonitoring() {
  const [activeTab, setActiveTab] = useState('overview');
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    // Simulate refresh delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    setRefreshing(false);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'stopped':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'running':
        return (
          <Badge variant="secondary" className="bg-green-100 text-green-800">
            Running
          </Badge>
        );
      case 'warning':
        return (
          <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
            Warning
          </Badge>
        );
      case 'stopped':
        return <Badge variant="destructive">Stopped</Badge>;
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">System Monitoring</h1>
          <p className="text-muted-foreground">
            Real-time system performance, service health, and infrastructure monitoring
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button variant="outline" size="sm">
            <Settings className="h-4 w-4 mr-2" />
            Configure
          </Button>
        </div>
      </div>

      {/* System Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">CPU Usage</CardTitle>
            <Cpu className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemMetrics.cpu.usage}%</div>
            <Progress value={systemMetrics.cpu.usage} className="mt-2" />
            <p className="text-xs text-muted-foreground mt-1">
              {systemMetrics.cpu.cores} cores @ {systemMetrics.cpu.frequency}GHz
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Memory</CardTitle>
            <Memory className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemMetrics.memory.usage}%</div>
            <Progress value={systemMetrics.memory.usage} className="mt-2" />
            <p className="text-xs text-muted-foreground mt-1">
              {systemMetrics.memory.used}GB / {systemMetrics.memory.total}GB
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Storage</CardTitle>
            <HardDrive className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemMetrics.storage.usage}%</div>
            <Progress value={systemMetrics.storage.usage} className="mt-2" />
            <p className="text-xs text-muted-foreground mt-1">
              {systemMetrics.storage.used}GB / {systemMetrics.storage.total}GB
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Network</CardTitle>
            <Wifi className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemMetrics.network.latency}ms</div>
            <p className="text-xs text-muted-foreground">
              ↓ {systemMetrics.network.inbound}MB/s ↑ {systemMetrics.network.outbound}
              MB/s
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Monitoring Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="services">Services</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="network">Network</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>System Performance (24h)</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="cpu"
                      stackId="1"
                      stroke="#8884d8"
                      fill="#8884d8"
                      name="CPU %"
                    />
                    <Area
                      type="monotone"
                      dataKey="memory"
                      stackId="1"
                      stroke="#82ca9d"
                      fill="#82ca9d"
                      name="Memory %"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Resource Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={[
                        {
                          name: 'CPU',
                          value: systemMetrics.cpu.usage,
                          color: '#8884d8',
                        },
                        {
                          name: 'Memory',
                          value: systemMetrics.memory.usage,
                          color: '#82ca9d',
                        },
                        {
                          name: 'Storage',
                          value: systemMetrics.storage.usage,
                          color: '#ffc658',
                        },
                        {
                          name: 'Available',
                          value:
                            100 -
                            (systemMetrics.cpu.usage +
                              systemMetrics.memory.usage +
                              systemMetrics.storage.usage) /
                              3,
                          color: '#e0e0e0',
                        },
                      ]}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      dataKey="value"
                      label={({ name, percent }) =>
                        `${name} ${(percent * 100).toFixed(0)}%`
                      }
                    >
                      {[
                        { color: '#8884d8' },
                        { color: '#82ca9d' },
                        { color: '#ffc658' },
                        { color: '#e0e0e0' },
                      ].map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="services" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Service Health Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {serviceStatus.map((service, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(service.status)}
                      <div>
                        <div className="font-medium">{service.name}</div>
                        <div className="text-sm text-muted-foreground">
                          Uptime: {service.uptime}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <div className="text-sm">CPU: {service.cpu}%</div>
                        <div className="text-sm text-muted-foreground">
                          Memory: {service.memory}GB
                        </div>
                      </div>
                      {getStatusBadge(service.status)}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Performance Metrics</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="cpu" stroke="#8884d8" name="CPU %" />
                  <Line
                    type="monotone"
                    dataKey="memory"
                    stroke="#82ca9d"
                    name="Memory %"
                  />
                  <Line
                    type="monotone"
                    dataKey="network"
                    stroke="#ffc658"
                    name="Network %"
                  />
                  <Line
                    type="monotone"
                    dataKey="disk"
                    stroke="#ff7300"
                    name="Disk I/O %"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="network" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Network Topology Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={networkTopology}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Legend />
                  <Bar
                    yAxisId="left"
                    dataKey="connections"
                    fill="#8884d8"
                    name="Active Connections"
                  />
                  <Bar
                    yAxisId="right"
                    dataKey="latency"
                    fill="#82ca9d"
                    name="Latency (ms)"
                  />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="alerts" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>System Alerts</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {alertsData.map(alert => (
                  <div
                    key={alert.id}
                    className="flex items-start space-x-3 p-4 border rounded-lg"
                  >
                    <div className="mt-1">
                      {alert.type === 'error' && (
                        <XCircle className="h-5 w-5 text-red-500" />
                      )}
                      {alert.type === 'warning' && (
                        <AlertTriangle className="h-5 w-5 text-yellow-500" />
                      )}
                      {alert.type === 'info' && (
                        <CheckCircle className="h-5 w-5 text-blue-500" />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="font-medium">{alert.title}</div>
                      <div className="text-sm text-muted-foreground">
                        {alert.description}
                      </div>
                      <div className="text-xs text-muted-foreground mt-1">
                        {alert.time}
                      </div>
                    </div>
                    <Button variant="outline" size="sm">
                      Resolve
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

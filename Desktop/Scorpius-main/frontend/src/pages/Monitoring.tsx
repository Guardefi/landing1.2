import { useState, useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Server,
  Eye,
  RefreshCw,
  Bell,
  Settings,
  Network,
  Database,
  Zap,
  Clock,
} from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { PageLayout } from "@/components/PageLayout";
import { NetworkTopology3D } from "@/components/ui/enhanced-3d";
import { NetworkLines, ParticleField } from "@/components/ui/particle-effects";
import {
  EnhancedAreaChart,
  RealTimeChart,
} from "@/components/ui/enhanced-charts";

const Monitoring = () => {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const systemServices = [
    {
      name: "API Gateway",
      status: "healthy",
      dependencies: ["Auth Service", "Database"],
      metrics: { cpu: 45, memory: 60, latency: 120 },
      uptime: "99.9%",
    },
    {
      name: "Trading Engine",
      status: "warning",
      dependencies: ["Market Data", "Risk Engine"],
      metrics: { cpu: 85, memory: 70, latency: 250 },
      uptime: "99.7%",
    },
    {
      name: "Security Scanner",
      status: "healthy",
      dependencies: ["Threat DB", "AI Engine"],
      metrics: { cpu: 60, memory: 55, latency: 100 },
      uptime: "100%",
    },
    {
      name: "Bridge Network",
      status: "healthy",
      dependencies: ["Validator Network", "Chain RPC"],
      metrics: { cpu: 35, memory: 45, latency: 180 },
      uptime: "99.8%",
    },
  ];

  const activeAlerts = [
    {
      id: "ALT-001",
      severity: "critical",
      title: "High CPU usage on trading nodes",
      description: "CPU utilization > 90% for 5 minutes",
      timestamp: "2 minutes ago",
      acknowledged: false,
      assignee: null,
      service: "Trading Engine",
    },
    {
      id: "ALT-002",
      severity: "warning",
      title: "Slow database queries detected",
      description: "Query response time > 2s",
      timestamp: "5 minutes ago",
      acknowledged: true,
      assignee: "admin@scorpius.com",
      service: "Database",
    },
    {
      id: "ALT-003",
      severity: "info",
      title: "Scheduled maintenance starting",
      description: "Bridge network maintenance window",
      timestamp: "10 minutes ago",
      acknowledged: true,
      assignee: "ops@scorpius.com",
      service: "Bridge Network",
    },
  ];

  const performanceMetrics = [
    {
      category: "Response Times",
      metrics: [
        { name: "API Latency", value: 120, unit: "ms", target: 200 },
        { name: "Database Queries", value: 45, unit: "ms", target: 100 },
        { name: "WebSocket Latency", value: 25, unit: "ms", target: 50 },
      ],
    },
    {
      category: "Throughput",
      metrics: [
        { name: "Requests/sec", value: 0, unit: "req/s", target: 2000 },
        { name: "Transactions/sec", value: 89, unit: "tx/s", target: 150 },
        { name: "Data Transfer", value: 234, unit: "MB/s", target: 500 },
      ],
    },
  ];

  const getServiceStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "text-emerald-600 bg-emerald-50 dark:bg-emerald-900/20";
      case "warning":
        return "text-amber-600 bg-amber-50 dark:bg-amber-900/20";
      case "error":
        return "text-red-600 bg-red-50 dark:bg-red-900/20";
      default:
        return "text-gray-600 bg-gray-50 dark:bg-gray-900/20";
    }
  };

  const getAlertSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "destructive";
      case "warning":
        return "default";
      case "info":
        return "secondary";
      default:
        return "outline";
    }
  };

  return (
    <PageLayout variant="monitoring">
      <PageHeader
        title="Advanced Monitoring Dashboard"
        description="Real-time system performance and health monitoring"
        icon={Activity}
        iconGradient="from-amber-500 to-orange-600"
        borderColor="border-amber-400/30"
      />
      {/* System Health Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* System Health Map */}
        <Card className="lg:col-span-2 relative overflow-hidden">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Network className="h-5 w-5" />
              <span>Service Dependency Graph</span>
            </CardTitle>
            <CardDescription>
              Interactive 3D network diagram of service dependencies
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <div className="relative h-64">
              <ParticleField
                particleCount={35}
                colors={["#f59e0b", "#ea580c", "#dc2626"]}
                className="opacity-40"
              />
              <NetworkTopology3D
                nodes={[
                  {
                    id: "gateway",
                    name: "API Gateway",
                    status: "healthy",
                    position: [0, 0, 0],
                  },
                  {
                    id: "trading",
                    name: "Trading",
                    status: "warning",
                    position: [-2, 2, 1],
                  },
                  {
                    id: "security",
                    name: "Security",
                    status: "healthy",
                    position: [2, 2, -1],
                  },
                  {
                    id: "bridge",
                    name: "Bridge",
                    status: "healthy",
                    position: [-2, -2, 1],
                  },
                  {
                    id: "database",
                    name: "Database",
                    status: "healthy",
                    position: [2, -2, -1],
                  },
                ]}
                connections={[
                  { from: "gateway", to: "trading", active: true },
                  { from: "gateway", to: "security", active: true },
                  { from: "gateway", to: "bridge", active: false },
                  { from: "gateway", to: "database", active: true },
                  { from: "trading", to: "database", active: true },
                  { from: "security", to: "database", active: false },
                ]}
              />

              {/* System Status */}
              <div className="absolute bottom-4 left-4 bg-black/60 backdrop-blur rounded-lg p-3 text-xs text-white">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
                    <span>
                      Healthy:{" "}
                      {
                        systemServices.filter((s) => s.status === "healthy")
                          .length
                      }
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-amber-500"></div>
                    <span>
                      Warning:{" "}
                      {
                        systemServices.filter((s) => s.status === "warning")
                          .length
                      }
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Alert Center */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5" />
              <span>Active Alerts</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {activeAlerts.slice(0, 3).map((alert) => (
              <div key={alert.id} className="p-3 border rounded-lg space-y-2">
                <div className="flex items-center justify-between">
                  <Badge variant={getAlertSeverityColor(alert.severity) as any}>
                    {alert.severity}
                  </Badge>
                  <span className="text-xs text-muted-foreground">
                    {alert.timestamp}
                  </span>
                </div>
                <div>
                  <div className="font-medium text-sm">{alert.title}</div>
                  <div className="text-xs text-muted-foreground">
                    {alert.description}
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">
                    {alert.service}
                  </span>
                  {!alert.acknowledged && (
                    <Button variant="outline" size="sm">
                      Acknowledge
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* System Services Health */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Server className="h-5 w-5" />
            <span>System Services Health</span>
          </CardTitle>
          <CardDescription>
            Health status and metrics for all core services
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {systemServices.map((service) => (
              <div
                key={service.name}
                className="p-4 border rounded-lg space-y-3"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">{service.name}</div>
                    <div className="text-sm text-muted-foreground">
                      Uptime: {service.uptime}
                    </div>
                  </div>
                  <Badge className={getServiceStatusColor(service.status)}>
                    {service.status}
                  </Badge>
                </div>

                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <div className="text-muted-foreground">CPU</div>
                    <div className="font-medium">{service.metrics.cpu}%</div>
                  </div>
                  <div>
                    <div className="text-muted-foreground">Memory</div>
                    <div className="font-medium">{service.metrics.memory}%</div>
                  </div>
                  <div>
                    <div className="text-muted-foreground">Latency</div>
                    <div className="font-medium">
                      {service.metrics.latency}ms
                    </div>
                  </div>
                </div>

                <div>
                  <div className="text-sm font-medium mb-1">Dependencies</div>
                  <div className="flex flex-wrap gap-1">
                    {service.dependencies.map((dep) => (
                      <Badge key={dep} variant="outline" className="text-xs">
                        {dep}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Metrics Dashboard */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Activity className="h-5 w-5" />
            <span>System Metrics</span>
          </CardTitle>
          <CardDescription>
            Real-time performance metrics across all modules
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="performance" className="space-y-4">
            <TabsList>
              <TabsTrigger value="performance">Performance</TabsTrigger>
              <TabsTrigger value="resources">Resources</TabsTrigger>
              <TabsTrigger value="errors">Errors</TabsTrigger>
            </TabsList>

            <TabsContent value="performance" className="space-y-6">
              {performanceMetrics.map((category) => (
                <div key={category.category}>
                  <h4 className="font-medium mb-4">{category.category}</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {category.metrics.map((metric) => (
                      <Card key={metric.name}>
                        <CardContent className="p-4">
                          <div className="space-y-2">
                            <div className="flex justify-between items-center">
                              <span className="text-sm font-medium">
                                {metric.name}
                              </span>
                              <span className="text-xs text-muted-foreground">
                                Target: {metric.target}
                                {metric.unit}
                              </span>
                            </div>
                            <div className="text-2xl font-bold">
                              {metric.value}
                              <span className="text-sm text-muted-foreground ml-1">
                                {metric.unit}
                              </span>
                            </div>
                            <Progress
                              value={(metric.value / metric.target) * 100}
                              className="h-2"
                            />
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              ))}
            </TabsContent>

            <TabsContent value="resources">
              <div className="h-64">
                <EnhancedAreaChart
                  data={[
                    { name: "00:00", cpu: 45, memory: 52, storage: 34 },
                    { name: "04:00", cpu: 52, memory: 58, storage: 36 },
                    { name: "08:00", cpu: 73, memory: 68, storage: 42 },
                    { name: "12:00", cpu: 68, memory: 65, storage: 45 },
                    { name: "16:00", cpu: 78, memory: 71, storage: 48 },
                    { name: "20:00", cpu: 65, memory: 62, storage: 44 },
                    { name: "24:00", cpu: 73, memory: 68, storage: 46 },
                  ]}
                  dataKey="cpu"
                  color="#f59e0b"
                />
              </div>
            </TabsContent>

            <TabsContent value="errors">
              <div className="h-64 bg-gradient-to-br from-red-100 to-pink-100 dark:from-red-900/20 dark:to-pink-900/20 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <AlertTriangle className="h-12 w-12 mx-auto text-red-600 mb-4" />
                  <p className="text-sm text-muted-foreground mb-4">
                    Error Rate Monitoring
                  </p>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="font-bold text-red-600">0.8%</div>
                      <div className="text-muted-foreground">Error Rate</div>
                    </div>
                    <div>
                      <div className="font-bold text-orange-600">23</div>
                      <div className="text-muted-foreground">Errors (24h)</div>
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </PageLayout>
  );
};

export default Monitoring;

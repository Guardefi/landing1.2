import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { PageLayout } from "@/components/PageLayout";
import { PageHeader } from "@/components/PageHeader";
import { GrafanaDashboard } from "@/components/GrafanaDashboard";
import {
  GrafanaPanel,
  CPUUsagePanel,
  MemoryUsagePanel,
  NetworkTrafficPanel,
  RequestRatePanel,
  ErrorRatePanel,
  ResponseTimePanel,
} from "@/components/GrafanaPanel";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Separator } from "@/components/ui/separator";
import {
  Activity,
  Server,
  Database,
  Network,
  Cpu,
  MemoryStick,
  HardDrive,
  Gauge,
  BarChart3,
  LineChart,
  PieChart,
  TrendingUp,
  TrendingDown,
  Zap,
  Shield,
  Globe,
  Users,
  DollarSign,
  Clock,
  ExternalLink,
  RefreshCw,
  Settings,
  AlertTriangle,
  CheckCircle,
  Maximize2,
  Minimize2,
  Monitor,
  Target,
  Eye,
  CloudSnow,
  Thermometer,
  Wifi,
  Container,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  change?: number;
  changeLabel?: string;
  status?: "healthy" | "warning" | "critical";
  icon: React.ElementType;
  trend?: number[];
  className?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  unit,
  change,
  changeLabel,
  status = "healthy",
  icon: Icon,
  trend = [],
  className,
}) => {
  const getStatusColor = () => {
    switch (status) {
      case "critical":
        return "border-red-500 bg-red-50 dark:bg-red-950/20";
      case "warning":
        return "border-yellow-500 bg-yellow-50 dark:bg-yellow-950/20";
      default:
        return "border-green-500 bg-green-50 dark:bg-green-950/20";
    }
  };

  const getValueColor = () => {
    switch (status) {
      case "critical":
        return "text-red-600 dark:text-red-400";
      case "warning":
        return "text-yellow-600 dark:text-yellow-400";
      default:
        return "text-green-600 dark:text-green-400";
    }
  };

  return (
    <Card
      className={cn(
        "relative overflow-hidden border-l-4",
        getStatusColor(),
        className,
      )}
    >
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <Icon className={cn("h-4 w-4", getValueColor())} />
            <span className="text-sm font-medium text-muted-foreground">
              {title}
            </span>
          </div>
          {status !== "healthy" && (
            <AlertTriangle className={cn("h-4 w-4", getValueColor())} />
          )}
        </div>

        <div className="flex items-baseline space-x-2 mb-2">
          <span className={cn("text-2xl font-bold", getValueColor())}>
            {typeof value === "number" ? value.toLocaleString() : value}
          </span>
          {unit && (
            <span className="text-sm text-muted-foreground">{unit}</span>
          )}
        </div>

        {change !== undefined && (
          <div className="flex items-center space-x-1 mb-2">
            {change > 0 ? (
              <TrendingUp className="h-3 w-3 text-green-500" />
            ) : (
              <TrendingDown className="h-3 w-3 text-red-500" />
            )}
            <span className="text-xs text-muted-foreground">
              {Math.abs(change)}% {changeLabel || "vs last hour"}
            </span>
          </div>
        )}

        {trend.length > 0 && (
          <div className="mt-2">
            <div className="flex items-center space-x-1 h-8">
              {trend.map((point, index) => (
                <div
                  key={index}
                  className={cn(
                    "w-1 bg-current opacity-60 rounded-full",
                    getValueColor(),
                  )}
                  style={{ height: `${(point / 100) * 100}%` }}
                />
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

interface GrafanaWidgetProps {
  title: string;
  dashboardId: string;
  panelId?: number;
  height?: number;
  timeRange?: string;
  refresh?: string;
  type?: "graph" | "singlestat" | "table" | "heatmap";
  className?: string;
}

const GrafanaWidget: React.FC<GrafanaWidgetProps> = ({
  title,
  dashboardId,
  panelId,
  height = 300,
  timeRange = "1h",
  refresh = "30s",
  type = "graph",
  className,
}) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const grafanaUrl = process.env.VITE_GRAFANA_URL || "http://localhost:3001";

  const buildWidgetUrl = () => {
    let url = `${grafanaUrl}/d-solo/${dashboardId}`;
    if (panelId) {
      url += `?panelId=${panelId}`;
    }
    const params = new URLSearchParams({
      orgId: "1",
      theme: "dark",
      from: `now-${timeRange}`,
      to: "now",
      refresh: refresh,
    });
    return url + (panelId ? "&" : "?") + params.toString();
  };

  const openFullscreen = () => {
    const fullUrl = `${grafanaUrl}/d/${dashboardId}`;
    window.open(fullUrl, "_blank");
  };

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <div className="flex space-x-1">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="h-7 w-7 p-0"
          >
            {isFullscreen ? (
              <Minimize2 className="h-3 w-3" />
            ) : (
              <Maximize2 className="h-3 w-3" />
            )}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={openFullscreen}
            className="h-7 w-7 p-0"
          >
            <ExternalLink className="h-3 w-3" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-2">
        <iframe
          src={buildWidgetUrl()}
          width="100%"
          height={isFullscreen ? 600 : height}
          frameBorder="0"
          className="rounded"
        />
      </CardContent>
    </Card>
  );
};

const Monitoring = () => {
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [activeTab, setActiveTab] = useState("overview");
  const [metrics, setMetrics] = useState({
    cpu: {
      value: 23,
      status: "healthy" as const,
      trend: [20, 25, 23, 28, 23, 19, 23],
    },
    memory: {
      value: 67,
      status: "warning" as const,
      trend: [60, 65, 67, 70, 68, 67, 69],
    },
    disk: {
      value: 45,
      status: "healthy" as const,
      trend: [40, 42, 45, 44, 45, 43, 45],
    },
    network: {
      value: 156,
      status: "healthy" as const,
      trend: [140, 150, 156, 160, 155, 156, 158],
    },
    requests: {
      value: 2847,
      status: "healthy" as const,
      trend: [2500, 2600, 2700, 2800, 2847, 2900, 2847],
    },
    errors: {
      value: 3,
      status: "healthy" as const,
      trend: [5, 4, 3, 2, 3, 4, 3],
    },
    latency: {
      value: 89,
      status: "healthy" as const,
      trend: [95, 90, 89, 85, 89, 92, 89],
    },
    uptime: {
      value: 99.97,
      status: "healthy" as const,
      trend: [99.9, 99.95, 99.97, 99.98, 99.97, 99.96, 99.97],
    },
  });

  const refreshMetrics = () => {
    setLastUpdate(new Date());
    // Simulate metric updates
    setMetrics((prev) => ({
      ...prev,
      cpu: { ...prev.cpu, value: Math.floor(Math.random() * 100) },
      memory: { ...prev.memory, value: Math.floor(Math.random() * 100) },
      network: { ...prev.network, value: Math.floor(Math.random() * 500) },
      requests: { ...prev.requests, value: Math.floor(Math.random() * 5000) },
    }));
  };

  useEffect(() => {
    const interval = setInterval(refreshMetrics, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <PageLayout>
      <div className="space-y-6">
        {/* Header with Live Status */}
        <PageHeader
          title="System Monitoring"
          description="Real-time infrastructure monitoring and observability"
          icon={Activity}
        />

        {/* Status Bar */}
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
                  <span className="text-sm font-medium">
                    All Systems Operational
                  </span>
                </div>
                <div className="text-sm text-muted-foreground">
                  Last updated: {lastUpdate.toLocaleTimeString()}
                </div>
                <Badge
                  variant="outline"
                  className="bg-green-50 dark:bg-green-950/20"
                >
                  Uptime: 99.97%
                </Badge>
              </div>
              <div className="flex items-center space-x-2">
                <Button variant="outline" size="sm" onClick={refreshMetrics}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh
                </Button>
                <Button variant="outline" size="sm">
                  <Settings className="h-4 w-4 mr-2" />
                  Configure
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Main Monitoring Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="infrastructure">Infrastructure</TabsTrigger>
            <TabsTrigger value="applications">Applications</TabsTrigger>
            <TabsTrigger value="network">Network</TabsTrigger>
            <TabsTrigger value="security">Security</TabsTrigger>
            <TabsTrigger value="business">Business</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              {/* Key Metrics Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <MetricCard
                  title="CPU Usage"
                  value={metrics.cpu.value}
                  unit="%"
                  change={2.3}
                  status={metrics.cpu.status}
                  icon={Cpu}
                  trend={metrics.cpu.trend}
                />
                <MetricCard
                  title="Memory Usage"
                  value={metrics.memory.value}
                  unit="%"
                  change={-1.2}
                  status={metrics.memory.status}
                  icon={MemoryStick}
                  trend={metrics.memory.trend}
                />
                <MetricCard
                  title="Network I/O"
                  value={metrics.network.value}
                  unit="MB/s"
                  change={5.8}
                  status={metrics.network.status}
                  icon={Network}
                  trend={metrics.network.trend}
                />
                <MetricCard
                  title="Request Rate"
                  value={metrics.requests.value}
                  unit="/min"
                  change={12.5}
                  status={metrics.requests.status}
                  icon={Zap}
                  trend={metrics.requests.trend}
                />
              </div>

              {/* Quick Metrics Panels */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                <RequestRatePanel />
                <ErrorRatePanel />
                <NetworkTrafficPanel />
              </div>

              {/* Main Dashboard */}
              <GrafanaDashboard
                dashboardId="platform-overview"
                title="Platform Overview Dashboard"
                description="Comprehensive system health and performance metrics"
                height={500}
                timeRange="6h"
                refresh="30s"
              />
            </motion.div>
          </TabsContent>

          {/* Infrastructure Tab */}
          <TabsContent value="infrastructure" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              {/* Infrastructure Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <MetricCard
                  title="Server Health"
                  value="8/8"
                  status="healthy"
                  icon={Server}
                  trend={[100, 100, 100, 100, 100, 100, 100]}
                />
                <MetricCard
                  title="Database"
                  value="Active"
                  change={0.2}
                  status="healthy"
                  icon={Database}
                />
                <MetricCard
                  title="Disk Space"
                  value={metrics.disk.value}
                  unit="%"
                  change={1.5}
                  status={metrics.disk.status}
                  icon={HardDrive}
                  trend={metrics.disk.trend}
                />
                <MetricCard
                  title="Load Average"
                  value="1.23"
                  change={-0.8}
                  status="healthy"
                  icon={Gauge}
                />
              </div>

              {/* Infrastructure Dashboards */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <CPUUsagePanel className="lg:col-span-1" />
                <MemoryUsagePanel className="lg:col-span-1" />
                <GrafanaPanel
                  dashboardId="infrastructure"
                  panelId={3}
                  title="Storage I/O"
                  description="Disk read/write operations and latency"
                  panelType="graph"
                  height={300}
                  timeRange="2h"
                />
                <GrafanaPanel
                  dashboardId="infrastructure"
                  panelId={4}
                  title="Container Metrics"
                  description="Container CPU, memory, and status"
                  panelType="table"
                  height={300}
                  timeRange="2h"
                />
                <GrafanaPanel
                  dashboardId="infrastructure"
                  panelId={5}
                  title="Load Balancer"
                  description="Load balancer performance and health"
                  panelType="graph"
                  height={300}
                  timeRange="2h"
                  className="lg:col-span-2"
                />
              </div>
            </motion.div>
          </TabsContent>

          {/* Applications Tab */}
          <TabsContent value="applications" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              {/* Application Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <MetricCard
                  title="Response Time"
                  value={metrics.latency.value}
                  unit="ms"
                  change={-5.2}
                  status={metrics.latency.status}
                  icon={Clock}
                  trend={metrics.latency.trend}
                />
                <MetricCard
                  title="Error Rate"
                  value={metrics.errors.value}
                  unit="errors/min"
                  change={-12.3}
                  status={metrics.errors.status}
                  icon={AlertTriangle}
                  trend={metrics.errors.trend}
                />
                <MetricCard
                  title="Active Users"
                  value="1,247"
                  change={8.7}
                  status="healthy"
                  icon={Users}
                />
                <MetricCard
                  title="Throughput"
                  value="15.6K"
                  unit="req/s"
                  change={15.4}
                  status="healthy"
                  icon={Activity}
                />
              </div>

              {/* Application Dashboards */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <GrafanaWidget
                  title="Application Performance"
                  dashboardId="applications"
                  panelId={1}
                  height={350}
                  timeRange="1h"
                />
                <GrafanaWidget
                  title="Error Tracking"
                  dashboardId="applications"
                  panelId={2}
                  height={350}
                  timeRange="1h"
                />
                <GrafanaWidget
                  title="User Activity"
                  dashboardId="applications"
                  panelId={3}
                  height={350}
                  timeRange="1h"
                />
                <GrafanaWidget
                  title="API Endpoints"
                  dashboardId="applications"
                  panelId={4}
                  height={350}
                  timeRange="1h"
                />
              </div>
            </motion.div>
          </TabsContent>

          {/* Network Tab */}
          <TabsContent value="network" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              {/* Network Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <MetricCard
                  title="Bandwidth"
                  value="2.3"
                  unit="Gbps"
                  change={12.1}
                  status="healthy"
                  icon={Wifi}
                />
                <MetricCard
                  title="Packet Loss"
                  value="0.01"
                  unit="%"
                  change={-0.5}
                  status="healthy"
                  icon={Network}
                />
                <MetricCard
                  title="Connections"
                  value="847"
                  change={5.3}
                  status="healthy"
                  icon={Globe}
                />
                <MetricCard
                  title="CDN Cache Hit"
                  value="94.2"
                  unit="%"
                  change={2.1}
                  status="healthy"
                  icon={CloudSnow}
                />
              </div>

              {/* Network Dashboards */}
              <div className="space-y-6">
                <GrafanaDashboard
                  dashboardId="network-overview"
                  title="Network Traffic Analysis"
                  description="Real-time network performance and traffic patterns"
                  height={400}
                  timeRange="3h"
                  refresh="15s"
                />

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <GrafanaWidget
                    title="Geographic Traffic"
                    dashboardId="network"
                    panelId={1}
                    height={300}
                    timeRange="1h"
                    type="heatmap"
                  />
                  <GrafanaWidget
                    title="Protocol Distribution"
                    dashboardId="network"
                    panelId={2}
                    height={300}
                    timeRange="1h"
                    type="graph"
                  />
                </div>
              </div>
            </motion.div>
          </TabsContent>

          {/* Security Tab */}
          <TabsContent value="security" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              {/* Security Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <MetricCard
                  title="Threats Blocked"
                  value="1,439"
                  change={8.2}
                  status="healthy"
                  icon={Shield}
                />
                <MetricCard
                  title="Failed Logins"
                  value="23"
                  change={-15.6}
                  status="warning"
                  icon={Target}
                />
                <MetricCard
                  title="SSL Score"
                  value="A+"
                  status="healthy"
                  icon={CheckCircle}
                />
                <MetricCard
                  title="Vulnerability Score"
                  value="95"
                  unit="/100"
                  change={2.1}
                  status="healthy"
                  icon={Eye}
                />
              </div>

              {/* Security Dashboards */}
              <div className="space-y-6">
                <GrafanaDashboard
                  dashboardId="security-overview"
                  title="Security Monitoring Dashboard"
                  description="Threat detection, anomaly analysis, and security metrics"
                  height={400}
                  timeRange="24h"
                  refresh="1m"
                />

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <GrafanaWidget
                    title="Attack Patterns"
                    dashboardId="security"
                    panelId={1}
                    height={250}
                    timeRange="6h"
                  />
                  <GrafanaWidget
                    title="Authentication Events"
                    dashboardId="security"
                    panelId={2}
                    height={250}
                    timeRange="6h"
                  />
                  <GrafanaWidget
                    title="Firewall Status"
                    dashboardId="security"
                    panelId={3}
                    height={250}
                    timeRange="6h"
                  />
                </div>
              </div>
            </motion.div>
          </TabsContent>

          {/* Business Tab */}
          <TabsContent value="business" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              {/* Business Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <MetricCard
                  title="Revenue"
                  value="$23.4K"
                  change={18.2}
                  status="healthy"
                  icon={DollarSign}
                />
                <MetricCard
                  title="Active Users"
                  value="1,847"
                  change={12.4}
                  status="healthy"
                  icon={Users}
                />
                <MetricCard
                  title="Conversion Rate"
                  value="3.2"
                  unit="%"
                  change={0.8}
                  status="healthy"
                  icon={TrendingUp}
                />
                <MetricCard
                  title="Customer Satisfaction"
                  value="4.8"
                  unit="/5"
                  change={0.2}
                  status="healthy"
                  icon={CheckCircle}
                />
              </div>

              {/* Business Dashboards */}
              <div className="space-y-6">
                <GrafanaDashboard
                  dashboardId="business-metrics"
                  title="Business Intelligence Dashboard"
                  description="Key performance indicators and business analytics"
                  height={400}
                  timeRange="7d"
                  refresh="5m"
                />

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <GrafanaWidget
                    title="Revenue Trends"
                    dashboardId="business"
                    panelId={1}
                    height={300}
                    timeRange="30d"
                  />
                  <GrafanaWidget
                    title="User Engagement"
                    dashboardId="business"
                    panelId={2}
                    height={300}
                    timeRange="30d"
                  />
                  <GrafanaWidget
                    title="Cost Analysis"
                    dashboardId="cost-overview"
                    panelId={1}
                    height={300}
                    timeRange="30d"
                  />
                  <GrafanaWidget
                    title="Performance vs Cost"
                    dashboardId="business"
                    panelId={4}
                    height={300}
                    timeRange="30d"
                  />
                </div>
              </div>
            </motion.div>
          </TabsContent>
        </Tabs>
      </div>
    </PageLayout>
  );
};

export default Monitoring;

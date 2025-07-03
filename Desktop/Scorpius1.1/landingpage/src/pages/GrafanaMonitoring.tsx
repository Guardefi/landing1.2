import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { PageLayout } from "@/components/PageLayout";
import { PageHeader } from "@/components/PageHeader";
import { GrafanaDashboard } from "@/components/GrafanaDashboard";
import { GrafanaMetrics } from "@/components/GrafanaMetrics";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Separator } from "@/components/ui/separator";
import {
  BarChart3,
  Activity,
  Server,
  Database,
  Network,
  DollarSign,
  Users,
  Shield,
  TrendingUp,
  Gauge,
  ExternalLink,
  Settings,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Clock,
} from "lucide-react";

const GrafanaMonitoring = () => {
  const [connectionStatus, setConnectionStatus] = useState<
    "connected" | "disconnected" | "checking"
  >("checking");
  const [lastRefresh, setLastRefresh] = useState(new Date());

  // Check Grafana connection status
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const grafanaUrl =
          import.meta.env.VITE_GRAFANA_URL || "http://localhost:3001";
        const response = await fetch(`${grafanaUrl}/api/health`);
        setConnectionStatus(response.ok ? "connected" : "disconnected");
      } catch {
        setConnectionStatus("disconnected");
      }
    };

    checkConnection();
    const interval = setInterval(checkConnection, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const refreshAll = () => {
    setLastRefresh(new Date());
    window.location.reload();
  };

  const openGrafanaAdmin = () => {
    const grafanaUrl =
      import.meta.env.VITE_GRAFANA_URL || "http://localhost:3001";
    window.open(grafanaUrl, "_blank");
  };

  // Dashboard configurations
  const dashboards = [
    {
      id: "platform-overview",
      title: "Platform Overview",
      description: "High-level system metrics and performance indicators",
      category: "overview",
    },
    {
      id: "mempool-monitor",
      title: "Mempool Monitor",
      description:
        "Real-time blockchain mempool activity and transaction analysis",
      category: "blockchain",
    },
    {
      id: "cost-overview",
      title: "Cost Analysis",
      description: "Infrastructure costs and resource optimization metrics",
      category: "cost",
    },
    {
      id: "security-metrics",
      title: "Security Dashboard",
      description:
        "Threat detection, security events, and vulnerability metrics",
      category: "security",
    },
    {
      id: "performance-metrics",
      title: "Performance Analytics",
      description: "Application performance, latency, and throughput analysis",
      category: "performance",
    },
    {
      id: "user-analytics",
      title: "User Analytics",
      description: "User behavior, engagement, and usage patterns",
      category: "analytics",
    },
  ];

  const getStatusIcon = () => {
    switch (connectionStatus) {
      case "connected":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "disconnected":
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-yellow-500 animate-pulse" />;
    }
  };

  const getStatusText = () => {
    switch (connectionStatus) {
      case "connected":
        return "Connected";
      case "disconnected":
        return "Disconnected";
      default:
        return "Checking...";
    }
  };

  return (
    <PageLayout>
      <div className="space-y-6">
        {/* Header */}
        <PageHeader
          title="Grafana Monitoring"
          description="Real-time system monitoring and analytics dashboards"
          icon={BarChart3}
        />

        {/* Connection Status & Controls */}
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  {getStatusIcon()}
                  <span className="text-sm font-medium">Grafana Status:</span>
                  <Badge
                    variant={
                      connectionStatus === "connected"
                        ? "default"
                        : "destructive"
                    }
                  >
                    {getStatusText()}
                  </Badge>
                </div>
                <div className="text-sm text-muted-foreground">
                  Last refresh: {lastRefresh.toLocaleTimeString()}
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Button variant="outline" size="sm" onClick={refreshAll}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh All
                </Button>
                <Button variant="outline" size="sm" onClick={openGrafanaAdmin}>
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Open Grafana
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Connection Error Alert */}
        {connectionStatus === "disconnected" && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              Unable to connect to Grafana. Please ensure Grafana is running and
              accessible at the configured URL.
            </AlertDescription>
          </Alert>
        )}

        {/* Main Dashboard Content */}
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="dashboards">Dashboards</TabsTrigger>
            <TabsTrigger value="metrics">Live Metrics</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              {/* Quick Stats */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-2">
                      <Activity className="h-4 w-4 text-blue-500" />
                      <span className="text-sm font-medium">
                        Active Dashboards
                      </span>
                    </div>
                    <div className="mt-2 text-2xl font-bold">6</div>
                    <div className="text-xs text-muted-foreground">
                      All systems operational
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-2">
                      <Server className="h-4 w-4 text-green-500" />
                      <span className="text-sm font-medium">Data Sources</span>
                    </div>
                    <div className="mt-2 text-2xl font-bold">3</div>
                    <div className="text-xs text-muted-foreground">
                      Prometheus, InfluxDB, Logs
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-2">
                      <Shield className="h-4 w-4 text-purple-500" />
                      <span className="text-sm font-medium">Alert Rules</span>
                    </div>
                    <div className="mt-2 text-2xl font-bold">24</div>
                    <div className="text-xs text-muted-foreground">
                      2 firing, 22 ok
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-2">
                      <TrendingUp className="h-4 w-4 text-orange-500" />
                      <span className="text-sm font-medium">Uptime</span>
                    </div>
                    <div className="mt-2 text-2xl font-bold">99.9%</div>
                    <div className="text-xs text-muted-foreground">
                      Last 30 days
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Main Overview Dashboard */}
              <GrafanaDashboard
                dashboardId="platform-overview"
                title="Platform Overview"
                description="Real-time system health and performance metrics"
                height={600}
                timeRange="24h"
                refresh="1m"
              />
            </motion.div>
          </TabsContent>

          {/* Dashboards Tab */}
          <TabsContent value="dashboards" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="grid grid-cols-1 lg:grid-cols-2 gap-6"
            >
              {dashboards.map((dashboard, index) => (
                <motion.div
                  key={dashboard.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                >
                  <GrafanaDashboard
                    dashboardId={dashboard.id}
                    title={dashboard.title}
                    description={dashboard.description}
                    height={400}
                    timeRange="1h"
                    refresh="30s"
                  />
                </motion.div>
              ))}
            </motion.div>
          </TabsContent>

          {/* Live Metrics Tab */}
          <TabsContent value="metrics" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <GrafanaMetrics refreshInterval={5000} />
            </motion.div>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Settings className="h-5 w-5" />
                    <span>Grafana Configuration</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium">Grafana URL</label>
                      <div className="mt-1 p-2 bg-muted rounded text-sm">
                        {import.meta.env.VITE_GRAFANA_URL ||
                          "http://localhost:3001"}
                      </div>
                    </div>
                    <div>
                      <label className="text-sm font-medium">
                        Default Theme
                      </label>
                      <div className="mt-1 p-2 bg-muted rounded text-sm">
                        Dark
                      </div>
                    </div>
                    <div>
                      <label className="text-sm font-medium">
                        Refresh Interval
                      </label>
                      <div className="mt-1 p-2 bg-muted rounded text-sm">
                        30 seconds
                      </div>
                    </div>
                    <div>
                      <label className="text-sm font-medium">
                        Default Time Range
                      </label>
                      <div className="mt-1 p-2 bg-muted rounded text-sm">
                        Last 1 hour
                      </div>
                    </div>
                  </div>

                  <Separator />

                  <div>
                    <h4 className="text-sm font-medium mb-2">
                      Available Data Sources
                    </h4>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between p-2 bg-muted rounded">
                        <span className="text-sm">Prometheus</span>
                        <Badge variant="default">Connected</Badge>
                      </div>
                      <div className="flex items-center justify-between p-2 bg-muted rounded">
                        <span className="text-sm">InfluxDB</span>
                        <Badge variant="default">Connected</Badge>
                      </div>
                      <div className="flex items-center justify-between p-2 bg-muted rounded">
                        <span className="text-sm">Elasticsearch</span>
                        <Badge variant="outline">Disconnected</Badge>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </TabsContent>
        </Tabs>
      </div>
    </PageLayout>
  );
};

export default GrafanaMonitoring;

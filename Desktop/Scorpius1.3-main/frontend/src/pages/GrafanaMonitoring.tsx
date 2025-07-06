import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { PageLayout } from "@/components/PageLayout";
import {
  GrafanaBoardGrid,
  defaultGrafanaBoards,
} from "@/components/GrafanaBoardGrid";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import {
  BarChart3,
  Activity,
  Server,
  Database,
  Network,
  Shield,
  TrendingUp,
  Gauge,
  ExternalLink,
  Settings,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Clock,
  Plus,
  Edit,
  Trash2,
  Search,
  Globe,
  DollarSign,
  Users,
  Monitor,
} from "lucide-react";

interface CustomBoard {
  id: string;
  title: string;
  description: string;
  category: string;
  url?: string;
}

const GrafanaMonitoring = () => {
  const [connectionStatus, setConnectionStatus] = useState<
    "connected" | "disconnected" | "checking"
  >("checking");
  const [lastRefresh, setLastRefresh] = useState(new Date());
  const [grafanaUrl, setGrafanaUrl] = useState(
    import.meta.env.VITE_GRAFANA_URL || "http://localhost:3000",
  );
  const [customBoards, setCustomBoards] = useState<CustomBoard[]>([]);
  const [newBoard, setNewBoard] = useState<Partial<CustomBoard>>({});
  const [showAddBoard, setShowAddBoard] = useState(false);

  // Extended board configurations with your specific dashboards
  const extendedBoards = [
    ...defaultGrafanaBoards,
    {
      id: "platform-overview",
      title: "Platform Overview",
      description: "High-level system metrics and performance indicators",
      category: "Infrastructure",
      priority: 0,
      height: 400,
    },
    {
      id: "mempool-monitor",
      title: "Mempool Monitor",
      description:
        "Real-time blockchain mempool activity and transaction analysis",
      category: "Blockchain",
      priority: 1,
      height: 400,
    },
    {
      id: "cost-overview",
      title: "Cost Analysis",
      description: "Infrastructure costs and resource optimization metrics",
      category: "Business",
      priority: 2,
      height: 400,
    },
    {
      id: "security-metrics",
      title: "Security Dashboard",
      description:
        "Threat detection, security events, and vulnerability metrics",
      category: "Security",
      priority: 3,
      height: 400,
    },
    {
      id: "user-analytics",
      title: "User Analytics",
      description: "User behavior, engagement, and usage patterns",
      category: "Business",
      priority: 7,
      height: 400,
    },
    {
      id: "api-performance",
      title: "API Performance",
      description: "API response times, error rates, and throughput metrics",
      category: "Application",
      priority: 8,
      height: 400,
    },
    {
      id: "blockchain-analytics",
      title: "Blockchain Analytics",
      description: "On-chain metrics, transaction volumes, and network health",
      category: "Blockchain",
      priority: 9,
      height: 400,
    },
    ...customBoards.map((board) => ({
      ...board,
      priority: 999,
      height: 400,
    })),
  ];

  // Check Grafana connection status
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const response = await fetch(`${grafanaUrl}/api/health`, {
          method: "GET",
          mode: "cors",
        });
        setConnectionStatus(response.ok ? "connected" : "disconnected");
      } catch {
        setConnectionStatus("disconnected");
      }
    };

    checkConnection();
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, [grafanaUrl]);

  const handleAddBoard = () => {
    if (newBoard.id && newBoard.title && newBoard.category) {
      setCustomBoards((prev) => [...prev, newBoard as CustomBoard]);
      setNewBoard({});
      setShowAddBoard(false);
    }
  };

  const handleRemoveBoard = (id: string) => {
    setCustomBoards((prev) => prev.filter((board) => board.id !== id));
  };

  const openGrafanaAdmin = () => {
    window.open(grafanaUrl, "_blank");
  };

  const systemMetrics = [
    {
      title: "Total Dashboards",
      value: extendedBoards.length,
      icon: BarChart3,
      color: "text-blue-400",
      change: "+2 this month",
    },
    {
      title: "Connection Status",
      value: connectionStatus === "connected" ? "Online" : "Offline",
      icon: connectionStatus === "connected" ? CheckCircle : AlertTriangle,
      color:
        connectionStatus === "connected" ? "text-green-400" : "text-red-400",
      change: "Last checked: " + lastRefresh.toLocaleTimeString(),
    },
    {
      title: "Data Sources",
      value: "12 Active",
      icon: Database,
      color: "text-purple-400",
      change: "All sources healthy",
    },
    {
      title: "Alerts",
      value: "3 Active",
      icon: AlertTriangle,
      color: "text-orange-400",
      change: "2 new today",
    },
  ];

  return (
    <PageLayout>
      <div className="container mx-auto px-6 py-8 space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between"
        >
          <div>
            <h1 className="text-3xl font-bold text-foreground mb-2">
              Grafana Monitoring Center
            </h1>
            <p className="text-muted-foreground">
              Comprehensive real-time dashboards and system analytics
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <Button
              variant="outline"
              onClick={openGrafanaAdmin}
              className="border-cyan-500/30 hover:bg-cyan-500/10"
            >
              <ExternalLink className="h-4 w-4 mr-2" />
              Open Grafana
            </Button>
            <Button
              variant="outline"
              onClick={() => setShowAddBoard(true)}
              className="border-green-500/30 hover:bg-green-500/10"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Dashboard
            </Button>
          </div>
        </motion.div>

        {/* Connection Status Alert */}
        {connectionStatus === "disconnected" && (
          <Alert className="border-red-500/20 bg-red-500/10">
            <AlertTriangle className="h-4 w-4 text-red-500" />
            <AlertDescription className="text-red-400">
              Unable to connect to Grafana at {grafanaUrl}. Please check your
              Grafana configuration and ensure it's running.
            </AlertDescription>
          </Alert>
        )}

        {/* System Metrics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {systemMetrics.map((metric, index) => (
              <Card
                key={metric.title}
                className="bg-background/50 backdrop-blur border-cyan-500/20"
              >
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">
                        {metric.title}
                      </p>
                      <p className={`text-2xl font-bold ${metric.color}`}>
                        {metric.value}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {metric.change}
                      </p>
                    </div>
                    <metric.icon className={`h-8 w-8 ${metric.color}`} />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </motion.div>

        {/* Configuration Panel */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="bg-background/50 backdrop-blur border-cyan-500/20">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Settings className="h-5 w-5 text-cyan-400" />
                <span>Configuration</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="grafana-url">Grafana URL</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="grafana-url"
                      value={grafanaUrl}
                      onChange={(e) => setGrafanaUrl(e.target.value)}
                      placeholder="http://localhost:3000"
                      className="border-cyan-500/20 focus:border-cyan-500"
                    />
                    <Button
                      variant="outline"
                      onClick={() => window.location.reload()}
                      className="px-3"
                    >
                      <RefreshCw className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Connection Status</Label>
                  <div className="flex items-center space-x-2 p-2 rounded-lg bg-muted/20">
                    {connectionStatus === "connected" ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : connectionStatus === "checking" ? (
                      <Clock className="h-4 w-4 text-yellow-500 animate-pulse" />
                    ) : (
                      <AlertTriangle className="h-4 w-4 text-red-500" />
                    )}
                    <span className="text-sm">
                      {connectionStatus === "connected"
                        ? "Connected"
                        : connectionStatus === "checking"
                          ? "Checking..."
                          : "Disconnected"}
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Add Dashboard Panel */}
        {showAddBoard && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Card className="bg-background/50 backdrop-blur border-green-500/20">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Plus className="h-5 w-5 text-green-400" />
                  <span>Add Custom Dashboard</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Dashboard ID</Label>
                    <Input
                      value={newBoard.id || ""}
                      onChange={(e) =>
                        setNewBoard((prev) => ({ ...prev, id: e.target.value }))
                      }
                      placeholder="e.g., my-dashboard-id"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Title</Label>
                    <Input
                      value={newBoard.title || ""}
                      onChange={(e) =>
                        setNewBoard((prev) => ({
                          ...prev,
                          title: e.target.value,
                        }))
                      }
                      placeholder="Dashboard Title"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Category</Label>
                    <Input
                      value={newBoard.category || ""}
                      onChange={(e) =>
                        setNewBoard((prev) => ({
                          ...prev,
                          category: e.target.value,
                        }))
                      }
                      placeholder="e.g., Custom"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Description</Label>
                    <Input
                      value={newBoard.description || ""}
                      onChange={(e) =>
                        setNewBoard((prev) => ({
                          ...prev,
                          description: e.target.value,
                        }))
                      }
                      placeholder="Dashboard description"
                    />
                  </div>
                </div>
                <div className="flex space-x-2">
                  <Button
                    onClick={handleAddBoard}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    Add Dashboard
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setShowAddBoard(false)}
                  >
                    Cancel
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Main Dashboard Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-foreground">
              Live Dashboards
            </h2>
            <div className="flex items-center space-x-2 text-sm text-muted-foreground">
              <Clock className="h-4 w-4" />
              <span>Last updated: {lastRefresh.toLocaleTimeString()}</span>
            </div>
          </div>

          <GrafanaBoardGrid
            boards={extendedBoards}
            grafanaUrl={grafanaUrl}
            gridCols={2}
            showControls={true}
          />
        </motion.div>

        {/* Custom Dashboards Management */}
        {customBoards.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card className="bg-background/50 backdrop-blur border-cyan-500/20">
              <CardHeader>
                <CardTitle>Custom Dashboards</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {customBoards.map((board) => (
                    <div
                      key={board.id}
                      className="flex items-center justify-between p-2 rounded border border-muted"
                    >
                      <div>
                        <span className="font-medium">{board.title}</span>
                        <span className="text-sm text-muted-foreground ml-2">
                          ({board.category})
                        </span>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleRemoveBoard(board.id)}
                        className="text-red-400 hover:bg-red-500/10"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>
    </PageLayout>
  );
};

export default GrafanaMonitoring;

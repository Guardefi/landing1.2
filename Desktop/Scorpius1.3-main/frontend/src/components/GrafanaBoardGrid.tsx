import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  ExternalLink,
  RefreshCw,
  Maximize2,
  Settings,
  AlertTriangle,
  Activity,
  Server,
  Database,
  Shield,
  TrendingUp,
  Network,
  BarChart3,
  Clock,
  CheckCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface GrafanaBoard {
  id: string;
  title: string;
  description: string;
  category: string;
  height?: number;
  timeRange?: string;
  variables?: Record<string, string>;
  priority?: number;
}

interface GrafanaBoardGridProps {
  boards: GrafanaBoard[];
  grafanaUrl?: string;
  defaultTimeRange?: string;
  showControls?: boolean;
  gridCols?: number;
  compact?: boolean;
  className?: string;
}

export const GrafanaBoardGrid: React.FC<GrafanaBoardGridProps> = ({
  boards,
  grafanaUrl = import.meta.env.VITE_GRAFANA_URL || "http://localhost:3000",
  defaultTimeRange = "1h",
  showControls = true,
  gridCols = 2,
  compact = false,
  className,
}) => {
  const [connectionStatus, setConnectionStatus] = useState<
    "connected" | "disconnected" | "checking"
  >("checking");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [timeRange, setTimeRange] = useState(defaultTimeRange);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  // Get unique categories
  const categories = [
    "all",
    ...Array.from(new Set(boards.map((board) => board.category))),
  ];

  // Filter boards by category
  const filteredBoards =
    selectedCategory === "all"
      ? boards
      : boards.filter((board) => board.category === selectedCategory);

  // Sort boards by priority
  const sortedBoards = [...filteredBoards].sort(
    (a, b) => (a.priority || 999) - (b.priority || 999),
  );

  // Check Grafana connection
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
    const interval = setInterval(checkConnection, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, [grafanaUrl]);

  const buildGrafanaUrl = (board: GrafanaBoard) => {
    const baseUrl = `${grafanaUrl}/d/${board.id}`;
    const params = new URLSearchParams({
      orgId: "1",
      kiosk: "true",
      theme: "dark",
      from: `now-${board.timeRange || timeRange}`,
      to: "now",
      refresh: "30s",
      ...(board.variables || {}),
    });

    return `${baseUrl}?${params.toString()}`;
  };

  const handleRefreshAll = () => {
    setLastRefresh(new Date());
    // Refresh all iframes
    sortedBoards.forEach((board) => {
      const iframe = document.getElementById(
        `grafana-${board.id}`,
      ) as HTMLIFrameElement;
      if (iframe) {
        iframe.src = iframe.src;
      }
    });
  };

  const openInNewTab = (board: GrafanaBoard) => {
    const fullUrl = buildGrafanaUrl(board).replace("kiosk=true", "");
    window.open(fullUrl, "_blank");
  };

  const gridColsClass =
    {
      1: "grid-cols-1",
      2: "grid-cols-1 lg:grid-cols-2",
      3: "grid-cols-1 lg:grid-cols-2 xl:grid-cols-3",
      4: "grid-cols-1 lg:grid-cols-2 xl:grid-cols-4",
    }[gridCols] || "grid-cols-1 lg:grid-cols-2";

  if (connectionStatus === "disconnected") {
    return (
      <Alert className="border-red-500/20 bg-red-500/10">
        <AlertTriangle className="h-4 w-4 text-red-500" />
        <AlertDescription className="text-red-400">
          Unable to connect to Grafana at {grafanaUrl}. Please check your
          Grafana configuration.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className={cn("w-full space-y-6", className)}>
      {/* Controls */}
      {showControls && (
        <Card className="bg-background/50 backdrop-blur border-cyan-500/20">
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <div
                    className={cn(
                      "w-2 h-2 rounded-full",
                      connectionStatus === "connected"
                        ? "bg-green-500"
                        : connectionStatus === "checking"
                          ? "bg-yellow-500"
                          : "bg-red-500",
                    )}
                  />
                  <span className="text-sm text-muted-foreground">
                    {connectionStatus === "connected"
                      ? "Connected"
                      : connectionStatus === "checking"
                        ? "Checking..."
                        : "Disconnected"}
                  </span>
                </div>
                <Badge variant="outline" className="text-xs">
                  {sortedBoards.length} dashboard
                  {sortedBoards.length !== 1 ? "s" : ""}
                </Badge>
              </div>

              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleRefreshAll}
                  className="h-8"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh All
                </Button>
              </div>
            </div>

            {/* Category Tabs */}
            <Tabs
              value={selectedCategory}
              onValueChange={setSelectedCategory}
              className="w-full"
            >
              <TabsList className="grid w-full grid-cols-2 lg:grid-cols-4 xl:grid-cols-6">
                {categories.map((category) => (
                  <TabsTrigger
                    key={category}
                    value={category}
                    className="text-xs"
                  >
                    {category === "all" ? "All" : category}
                  </TabsTrigger>
                ))}
              </TabsList>
            </Tabs>
          </CardHeader>
        </Card>
      )}

      {/* Dashboard Grid */}
      <div className={cn("grid gap-6", gridColsClass)}>
        {sortedBoards.map((board, index) => (
          <motion.div
            key={board.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
          >
            <Card className="bg-background/50 backdrop-blur border-cyan-500/20 hover:border-cyan-500/40 transition-all duration-300">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <div className="flex flex-col space-y-1">
                  <CardTitle className="text-base font-medium">
                    {board.title}
                  </CardTitle>
                  <p className="text-sm text-muted-foreground">
                    {board.description}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant="outline" className="text-xs">
                    {board.timeRange || timeRange}
                  </Badge>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => openInNewTab(board)}
                    className="h-8 w-8 p-0"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>

              <CardContent className="p-0">
                {connectionStatus === "connected" ? (
                  <div className="relative">
                    <iframe
                      id={`grafana-${board.id}`}
                      src={buildGrafanaUrl(board)}
                      width="100%"
                      height={compact ? 300 : board.height || 400}
                      frameBorder="0"
                      className="rounded-b-lg"
                      onLoad={() =>
                        console.log(`Loaded dashboard: ${board.title}`)
                      }
                      onError={() =>
                        console.error(
                          `Failed to load dashboard: ${board.title}`,
                        )
                      }
                    />
                    {/* Loading overlay */}
                    <div className="absolute inset-0 bg-background/80 backdrop-blur flex items-center justify-center rounded-b-lg transition-opacity duration-500 opacity-0 pointer-events-none">
                      <div className="flex items-center space-x-2 text-muted-foreground">
                        <RefreshCw className="h-4 w-4 animate-spin" />
                        <span>Loading dashboard...</span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="h-64 flex items-center justify-center bg-muted/20 rounded-b-lg">
                    <div className="text-center space-y-2">
                      <AlertTriangle className="h-8 w-8 text-muted-foreground mx-auto" />
                      <p className="text-sm text-muted-foreground">
                        Dashboard unavailable
                      </p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {sortedBoards.length === 0 && (
        <Card className="bg-background/50 backdrop-blur border-cyan-500/20">
          <CardContent className="p-8 text-center">
            <BarChart3 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">
              No dashboards available
            </h3>
            <p className="text-muted-foreground">
              {selectedCategory === "all"
                ? "No Grafana dashboards configured yet."
                : `No dashboards found in the "${selectedCategory}" category.`}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Last refresh info */}
      {showControls && (
        <div className="flex items-center justify-center text-xs text-muted-foreground">
          <Clock className="h-3 w-3 mr-1" />
          Last refreshed: {lastRefresh.toLocaleTimeString()}
        </div>
      )}
    </div>
  );
};

// Default dashboard configurations - customize these for your setup
export const defaultGrafanaBoards: GrafanaBoard[] = [
  {
    id: "system-overview",
    title: "System Overview",
    description: "Overall system health and performance metrics",
    category: "Infrastructure",
    priority: 1,
    height: 400,
  },
  {
    id: "application-metrics",
    title: "Application Performance",
    description: "Application response times and throughput",
    category: "Application",
    priority: 2,
    height: 400,
  },
  {
    id: "security-dashboard",
    title: "Security Monitoring",
    description: "Security events and threat detection",
    category: "Security",
    priority: 3,
    height: 400,
  },
  {
    id: "network-monitoring",
    title: "Network Analytics",
    description: "Network traffic and connectivity status",
    category: "Network",
    priority: 4,
    height: 400,
  },
  {
    id: "database-metrics",
    title: "Database Performance",
    description: "Database queries and connection metrics",
    category: "Database",
    priority: 5,
    height: 400,
  },
  {
    id: "business-metrics",
    title: "Business Intelligence",
    description: "Business KPIs and operational metrics",
    category: "Business",
    priority: 6,
    height: 400,
  },
];

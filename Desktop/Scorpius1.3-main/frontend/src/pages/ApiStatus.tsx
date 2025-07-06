import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { PageLayout } from "@/components/PageLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { apiClient } from "@/lib/api-client";
import {
  CheckCircle,
  AlertTriangle,
  Clock,
  RefreshCw,
  Server,
  Database,
  Shield,
  Search,
  Activity,
  Globe,
  BarChart3,
  Brain,
  Settings,
  Wifi,
  WifiOff,
} from "lucide-react";

interface EndpointStatus {
  name: string;
  endpoint: string;
  method: string;
  status: "healthy" | "error" | "checking";
  responseTime?: number;
  lastCheck: Date;
  error?: string;
  description: string;
  category: string;
}

const ApiStatus = () => {
  const [endpoints, setEndpoints] = useState<EndpointStatus[]>([]);
  const [isChecking, setIsChecking] = useState(false);
  const [lastFullCheck, setLastFullCheck] = useState<Date>(new Date());

  // Define all critical endpoints to test
  const endpointDefinitions = [
    // Authentication
    {
      name: "Health Check",
      endpoint: "/health",
      method: "GET",
      description: "System health status",
      category: "System",
    },
    {
      name: "System Status",
      endpoint: "/api/system/health",
      method: "GET",
      description: "Detailed system metrics",
      category: "System",
    },

    // Scanner endpoints
    {
      name: "Scanner Service",
      endpoint: "/api/scanner/health",
      method: "GET",
      description: "Scanner service health",
      category: "Scanner",
    },
    {
      name: "Vulnerability Scan",
      endpoint: "/api/scanner/scan",
      method: "POST",
      description: "Start vulnerability scan",
      category: "Scanner",
    },
    {
      name: "Scanner Results",
      endpoint: "/api/scanner/scans",
      method: "GET",
      description: "Get scan results",
      category: "Scanner",
    },

    // Honeypot endpoints
    {
      name: "Honeypot Detection",
      endpoint: "/api/honeypot/detections",
      method: "GET",
      description: "Honeypot detection service",
      category: "Security",
    },
    {
      name: "Honeypot Analysis",
      endpoint: "/api/honeypot/analyze",
      method: "POST",
      description: "Analyze contract for honeypots",
      category: "Security",
    },

    // Trading endpoints
    {
      name: "Trading Bots",
      endpoint: "/api/trading/bots",
      method: "GET",
      description: "Trading bot management",
      category: "Trading",
    },
    {
      name: "Trading Metrics",
      endpoint: "/api/trading/metrics",
      method: "GET",
      description: "Trading performance metrics",
      category: "Trading",
    },

    // Bridge endpoints
    {
      name: "Bridge Transactions",
      endpoint: "/api/bridge/transactions",
      method: "GET",
      description: "Cross-chain bridge status",
      category: "Bridge",
    },
    {
      name: "Bridge Metrics",
      endpoint: "/api/bridge/metrics",
      method: "GET",
      description: "Bridge performance metrics",
      category: "Bridge",
    },

    // Analytics endpoints
    {
      name: "Dashboard Metrics",
      endpoint: "/api/analytics/dashboard",
      method: "GET",
      description: "Dashboard analytics",
      category: "Analytics",
    },
    {
      name: "Reports",
      endpoint: "/api/analytics/reports",
      method: "GET",
      description: "Analytics reports",
      category: "Analytics",
    },

    // Mempool endpoints
    {
      name: "Mempool Data",
      endpoint: "/api/mempool/transactions",
      method: "GET",
      description: "Mempool monitoring",
      category: "Blockchain",
    },
    {
      name: "Mempool Stats",
      endpoint: "/api/mempool/stats",
      method: "GET",
      description: "Mempool statistics",
      category: "Blockchain",
    },
  ];

  const checkEndpoint = async (
    def: (typeof endpointDefinitions)[0],
  ): Promise<EndpointStatus> => {
    const startTime = Date.now();
    const status: EndpointStatus = {
      name: def.name,
      endpoint: def.endpoint,
      method: def.method,
      status: "checking",
      lastCheck: new Date(),
      description: def.description,
      category: def.category,
    };

    try {
      let response;
      if (def.method === "GET") {
        response = await apiClient.get(def.endpoint);
      } else {
        // For POST endpoints, send minimal test data
        response = await apiClient.post(def.endpoint, { test: true });
      }

      status.responseTime = Date.now() - startTime;

      if (response.success) {
        status.status = "healthy";
      } else {
        status.status = "error";
        status.error = response.error || "Unknown error";
      }
    } catch (error: any) {
      status.status = "error";
      status.responseTime = Date.now() - startTime;
      status.error = error.message || "Request failed";
    }

    return status;
  };

  const checkAllEndpoints = async () => {
    setIsChecking(true);

    try {
      const results = await Promise.all(
        endpointDefinitions.map((def) => checkEndpoint(def)),
      );

      setEndpoints(results);
      setLastFullCheck(new Date());
    } catch (error) {
      console.error("Failed to check endpoints:", error);
    } finally {
      setIsChecking(false);
    }
  };

  useEffect(() => {
    checkAllEndpoints();

    // Auto-refresh every 5 minutes
    const interval = setInterval(checkAllEndpoints, 300000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "text-green-500";
      case "error":
        return "text-red-500";
      case "checking":
        return "text-yellow-500";
      default:
        return "text-gray-500";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "healthy":
        return CheckCircle;
      case "error":
        return AlertTriangle;
      case "checking":
        return Clock;
      default:
        return Clock;
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "System":
        return Server;
      case "Scanner":
        return Search;
      case "Security":
        return Shield;
      case "Trading":
        return Brain;
      case "Bridge":
        return Globe;
      case "Analytics":
        return BarChart3;
      case "Blockchain":
        return Database;
      default:
        return Activity;
    }
  };

  const categories = Array.from(new Set(endpoints.map((e) => e.category)));
  const healthyCount = endpoints.filter((e) => e.status === "healthy").length;
  const errorCount = endpoints.filter((e) => e.status === "error").length;
  const overallHealth =
    errorCount === 0
      ? "healthy"
      : errorCount < endpoints.length / 2
        ? "degraded"
        : "error";

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
              API Status Dashboard
            </h1>
            <p className="text-muted-foreground">
              Monitor backend service health and integration status
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <Button
              onClick={checkAllEndpoints}
              disabled={isChecking}
              variant="outline"
              className="border-cyan-500/30 hover:bg-cyan-500/10"
            >
              <RefreshCw
                className={`h-4 w-4 mr-2 ${isChecking ? "animate-spin" : ""}`}
              />
              {isChecking ? "Checking..." : "Refresh All"}
            </Button>
          </div>
        </motion.div>

        {/* Overall Status */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Alert
            className={`
            ${
              overallHealth === "healthy"
                ? "border-green-500/20 bg-green-500/10"
                : overallHealth === "degraded"
                  ? "border-yellow-500/20 bg-yellow-500/10"
                  : "border-red-500/20 bg-red-500/10"
            }
          `}
          >
            <div className="flex items-center space-x-2">
              {overallHealth === "healthy" ? (
                <Wifi className="h-4 w-4 text-green-500" />
              ) : (
                <WifiOff className="h-4 w-4 text-red-500" />
              )}
              <AlertDescription
                className={`
                ${
                  overallHealth === "healthy"
                    ? "text-green-400"
                    : overallHealth === "degraded"
                      ? "text-yellow-400"
                      : "text-red-400"
                }
              `}
              >
                <strong>System Status: </strong>
                {overallHealth === "healthy"
                  ? "All systems operational"
                  : overallHealth === "degraded"
                    ? "Some services experiencing issues"
                    : "Multiple service failures detected"}
                {" • "}
                {healthyCount}/{endpoints.length} services healthy
                {" • "}
                Last checked: {lastFullCheck.toLocaleTimeString()}
              </AlertDescription>
            </div>
          </Alert>
        </motion.div>

        {/* Status Summary Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="bg-background/50 backdrop-blur border-green-500/20">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Healthy Services
                    </p>
                    <p className="text-2xl font-bold text-green-400">
                      {healthyCount}
                    </p>
                  </div>
                  <CheckCircle className="h-8 w-8 text-green-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-background/50 backdrop-blur border-red-500/20">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Failed Services
                    </p>
                    <p className="text-2xl font-bold text-red-400">
                      {errorCount}
                    </p>
                  </div>
                  <AlertTriangle className="h-8 w-8 text-red-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-background/50 backdrop-blur border-cyan-500/20">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Backend URL</p>
                    <p className="text-sm font-mono text-cyan-400">
                      {apiClient.getBaseUrl()}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {apiClient.isOnline() ? "Online" : "Offline"}
                    </p>
                  </div>
                  <Server className="h-8 w-8 text-cyan-400" />
                </div>
              </CardContent>
            </Card>
          </div>
        </motion.div>

        {/* Detailed Status by Category */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Tabs defaultValue={categories[0]} className="w-full">
            <TabsList className="grid w-full grid-cols-3 lg:grid-cols-6">
              {categories.map((category) => {
                const categoryEndpoints = endpoints.filter(
                  (e) => e.category === category,
                );
                const categoryHealthy = categoryEndpoints.filter(
                  (e) => e.status === "healthy",
                ).length;
                const categoryTotal = categoryEndpoints.length;

                return (
                  <TabsTrigger
                    key={category}
                    value={category}
                    className="text-xs"
                  >
                    {category} ({categoryHealthy}/{categoryTotal})
                  </TabsTrigger>
                );
              })}
            </TabsList>

            {categories.map((category) => {
              const categoryEndpoints = endpoints.filter(
                (e) => e.category === category,
              );
              const CategoryIcon = getCategoryIcon(category);

              return (
                <TabsContent
                  key={category}
                  value={category}
                  className="space-y-4 mt-6"
                >
                  <div className="flex items-center space-x-2 mb-4">
                    <CategoryIcon className="h-5 w-5 text-cyan-400" />
                    <h3 className="text-lg font-semibold">
                      {category} Services
                    </h3>
                  </div>

                  <div className="grid gap-4">
                    {categoryEndpoints.map((endpoint, index) => {
                      const StatusIcon = getStatusIcon(endpoint.status);

                      return (
                        <Card
                          key={index}
                          className="bg-background/50 backdrop-blur border-cyan-500/20"
                        >
                          <CardContent className="p-4">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-3">
                                <StatusIcon
                                  className={`h-5 w-5 ${getStatusColor(endpoint.status)}`}
                                />
                                <div>
                                  <h4 className="font-medium">
                                    {endpoint.name}
                                  </h4>
                                  <p className="text-sm text-muted-foreground">
                                    {endpoint.description}
                                  </p>
                                  <div className="flex items-center space-x-4 mt-1">
                                    <Badge
                                      variant="outline"
                                      className="text-xs"
                                    >
                                      {endpoint.method} {endpoint.endpoint}
                                    </Badge>
                                    {endpoint.responseTime && (
                                      <span className="text-xs text-muted-foreground">
                                        {endpoint.responseTime}ms
                                      </span>
                                    )}
                                  </div>
                                </div>
                              </div>
                              <div className="text-right">
                                <Badge
                                  variant={
                                    endpoint.status === "healthy"
                                      ? "default"
                                      : "destructive"
                                  }
                                  className="mb-1"
                                >
                                  {endpoint.status}
                                </Badge>
                                <p className="text-xs text-muted-foreground">
                                  {endpoint.lastCheck.toLocaleTimeString()}
                                </p>
                                {endpoint.error && (
                                  <p className="text-xs text-red-400 mt-1 max-w-xs truncate">
                                    {endpoint.error}
                                  </p>
                                )}
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      );
                    })}
                  </div>
                </TabsContent>
              );
            })}
          </Tabs>
        </motion.div>

        {/* Configuration Help */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card className="bg-background/50 backdrop-blur border-cyan-500/20">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Settings className="h-5 w-5 text-cyan-400" />
                <span>Configuration Help</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium mb-2">Environment Variables</h4>
                  <div className="space-y-1 font-mono text-sm">
                    <div>
                      VITE_API_BASE_URL:{" "}
                      {import.meta.env.VITE_API_BASE_URL || "Not set"}
                    </div>
                    <div>
                      VITE_WS_BASE_URL:{" "}
                      {import.meta.env.VITE_WS_BASE_URL || "Not set"}
                    </div>
                  </div>
                </div>
                <div>
                  <h4 className="font-medium mb-2">Quick Fixes</h4>
                  <ul className="text-sm space-y-1 text-muted-foreground">
                    <li>• Check if backend services are running</li>
                    <li>• Verify API base URL configuration</li>
                    <li>• Check network connectivity</li>
                    <li>• Review CORS settings</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </PageLayout>
  );
};

export default ApiStatus;

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  BarChart3,
  ExternalLink,
  RefreshCw,
  Activity,
  Server,
  Gauge,
  TrendingUp,
  TrendingDown,
} from "lucide-react";
import { Link } from "react-router-dom";
import { cn } from "@/lib/utils";

interface GrafanaWidgetProps {
  className?: string;
  compact?: boolean;
}

interface MetricData {
  label: string;
  value: number;
  unit: string;
  trend: "up" | "down" | "neutral";
  status: "healthy" | "warning" | "critical";
}

export const GrafanaWidget: React.FC<GrafanaWidgetProps> = ({
  className,
  compact = false,
}) => {
  const [metrics, setMetrics] = useState<MetricData[]>([
    {
      label: "CPU Usage",
      value: 23,
      unit: "%",
      trend: "neutral",
      status: "healthy",
    },
    { label: "Memory", value: 67, unit: "%", trend: "up", status: "warning" },
    {
      label: "Network I/O",
      value: 156,
      unit: "MB/s",
      trend: "down",
      status: "healthy",
    },
    {
      label: "Active Users",
      value: 1247,
      unit: "",
      trend: "up",
      status: "healthy",
    },
  ]);

  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  const refreshMetrics = async () => {
    setIsLoading(true);
    try {
      // Simulate API call to Grafana
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Update with mock data
      setMetrics((prev) =>
        prev.map((metric) => ({
          ...metric,
          value:
            metric.label === "CPU Usage"
              ? Math.floor(Math.random() * 100)
              : metric.label === "Memory"
                ? Math.floor(Math.random() * 100)
                : metric.label === "Network I/O"
                  ? Math.floor(Math.random() * 500)
                  : Math.floor(Math.random() * 2000),
          trend: Math.random() > 0.5 ? "up" : "down",
          status: Math.random() > 0.8 ? "warning" : "healthy",
        })),
      );

      setLastUpdate(new Date());
    } catch (error) {
      console.error("Failed to refresh metrics:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const interval = setInterval(refreshMetrics, 30000); // Auto-refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "critical":
        return "text-red-500";
      case "warning":
        return "text-yellow-500";
      default:
        return "text-green-500";
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "up":
        return <TrendingUp className="h-3 w-3 text-green-500" />;
      case "down":
        return <TrendingDown className="h-3 w-3 text-red-500" />;
      default:
        return <Activity className="h-3 w-3 text-muted-foreground" />;
    }
  };

  if (compact) {
    return (
      <Card className={cn("w-full", className)}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Live Metrics
          </CardTitle>
          <Link to="/monitoring/grafana">
            <Button variant="outline" size="sm" className="h-8 w-8 p-0">
              <ExternalLink className="h-3 w-3" />
            </Button>
          </Link>
        </CardHeader>
        <CardContent className="space-y-2">
          {metrics.slice(0, 2).map((metric, index) => (
            <div key={index} className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">
                {metric.label}
              </span>
              <div className="flex items-center gap-1">
                <span
                  className={cn(
                    "text-xs font-medium",
                    getStatusColor(metric.status),
                  )}
                >
                  {metric.value}
                  {metric.unit}
                </span>
                {getTrendIcon(metric.trend)}
              </div>
            </div>
          ))}
          <div className="text-xs text-muted-foreground pt-1">
            Updated: {lastUpdate.toLocaleTimeString()}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <div className="flex items-center space-x-2">
          <BarChart3 className="h-5 w-5 text-blue-500" />
          <CardTitle className="text-lg font-semibold">
            System Metrics
          </CardTitle>
          <Badge variant="outline" className="text-xs">
            Live
          </Badge>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={refreshMetrics}
            disabled={isLoading}
            className="h-8"
          >
            <RefreshCw
              className={cn("h-3 w-3 mr-1", isLoading && "animate-spin")}
            />
            Refresh
          </Button>
          <Link to="/monitoring/grafana">
            <Button variant="outline" size="sm" className="h-8">
              <ExternalLink className="h-3 w-3 mr-1" />
              Full Dashboard
            </Button>
          </Link>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {metrics.map((metric, index) => (
            <div key={index} className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">{metric.label}</span>
                <div className="flex items-center space-x-1">
                  <span
                    className={cn(
                      "text-lg font-bold",
                      getStatusColor(metric.status),
                    )}
                  >
                    {typeof metric.value === "number"
                      ? metric.value.toLocaleString()
                      : metric.value}
                    {metric.unit}
                  </span>
                  {getTrendIcon(metric.trend)}
                </div>
              </div>
              {metric.label.includes("Usage") && (
                <Progress
                  value={metric.value}
                  className="h-2"
                  indicatorClassName={
                    metric.status === "critical"
                      ? "bg-red-500"
                      : metric.status === "warning"
                        ? "bg-yellow-500"
                        : "bg-green-500"
                  }
                />
              )}
            </div>
          ))}
        </div>

        <div className="flex items-center justify-between pt-2 border-t">
          <div className="flex items-center space-x-4 text-xs text-muted-foreground">
            <span>Last updated: {lastUpdate.toLocaleTimeString()}</span>
            <span>•</span>
            <span>Auto-refresh: 30s</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 rounded-full bg-green-500"></div>
              <span className="text-xs text-muted-foreground">
                Grafana Connected
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default GrafanaWidget;

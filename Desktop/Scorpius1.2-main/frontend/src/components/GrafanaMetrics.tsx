import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import {
  Activity,
  Server,
  Database,
  Cpu,
  MemoryStick,
  HardDrive,
  Network,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
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
  className,
}) => {
  const getStatusColor = () => {
    switch (status) {
      case "critical":
        return "text-red-500 border-red-200 dark:border-red-800";
      case "warning":
        return "text-yellow-500 border-yellow-200 dark:border-yellow-800";
      default:
        return "text-green-500 border-green-200 dark:border-green-800";
    }
  };

  const getTrendIcon = () => {
    if (change === undefined) return null;
    return change > 0 ? (
      <TrendingUp className="h-3 w-3 text-green-500" />
    ) : (
      <TrendingDown className="h-3 w-3 text-red-500" />
    );
  };

  return (
    <Card className={cn("border-l-4", getStatusColor(), className)}>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Icon className={cn("h-4 w-4", getStatusColor().split(" ")[0])} />
            <span className="text-sm font-medium text-muted-foreground">
              {title}
            </span>
          </div>
          {status !== "healthy" && (
            <AlertTriangle className="h-4 w-4 text-yellow-500" />
          )}
        </div>
        <div className="mt-2 flex items-baseline space-x-2">
          <span className="text-2xl font-bold">
            {typeof value === "number" ? value.toLocaleString() : value}
          </span>
          {unit && (
            <span className="text-sm text-muted-foreground">{unit}</span>
          )}
        </div>
        {change !== undefined && (
          <div className="mt-1 flex items-center space-x-1">
            {getTrendIcon()}
            <span className="text-xs text-muted-foreground">
              {Math.abs(change)}% {changeLabel || "vs last hour"}
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

interface GrafanaMetricsProps {
  className?: string;
  refreshInterval?: number;
}

export const GrafanaMetrics: React.FC<GrafanaMetricsProps> = ({
  className,
  refreshInterval = 30000, // 30 seconds
}) => {
  const [metrics, setMetrics] = useState({
    cpu: { value: 0, status: "healthy" as const },
    memory: { value: 0, status: "healthy" as const },
    disk: { value: 0, status: "healthy" as const },
    network: { value: 0, status: "healthy" as const },
    uptime: { value: "0d 0h 0m", status: "healthy" as const },
    activeConnections: { value: 0, status: "healthy" as const },
    throughput: { value: 0, status: "healthy" as const },
    errors: { value: 0, status: "healthy" as const },
  });

  const [lastUpdate, setLastUpdate] = useState(new Date());

  // Mock data for demonstration - replace with actual Grafana API calls
  const fetchMetrics = async () => {
    try {
      // Simulate fetching from Grafana API
      // const response = await fetch(`${grafanaUrl}/api/datasources/proxy/1/api/v1/query_range?...`);

      // For now, generate mock data
      const newMetrics = {
        cpu: {
          value: Math.floor(Math.random() * 100),
          status: Math.random() > 0.8 ? "warning" : ("healthy" as const),
        },
        memory: {
          value: Math.floor(Math.random() * 100),
          status: Math.random() > 0.9 ? "critical" : ("healthy" as const),
        },
        disk: {
          value: Math.floor(Math.random() * 100),
          status: "healthy" as const,
        },
        network: {
          value: Math.floor(Math.random() * 1000),
          status: "healthy" as const,
        },
        uptime: {
          value: "5d 12h 43m",
          status: "healthy" as const,
        },
        activeConnections: {
          value: Math.floor(Math.random() * 500),
          status: "healthy" as const,
        },
        throughput: {
          value: Math.floor(Math.random() * 10000),
          status: "healthy" as const,
        },
        errors: {
          value: Math.floor(Math.random() * 10),
          status: Math.random() > 0.7 ? "warning" : ("healthy" as const),
        },
      };

      setMetrics(newMetrics);
      setLastUpdate(new Date());
    } catch (error) {
      console.error("Failed to fetch metrics:", error);
    }
  };

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  return (
    <div className={cn("space-y-6", className)}>
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">System Metrics</h3>
        <Badge variant="outline" className="text-xs">
          Last update: {lastUpdate.toLocaleTimeString()}
        </Badge>
      </div>

      {/* Resource Metrics */}
      <div>
        <h4 className="text-sm font-medium text-muted-foreground mb-3">
          Resource Usage
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="CPU Usage"
            value={metrics.cpu.value}
            unit="%"
            change={Math.random() > 0.5 ? 2.3 : -1.2}
            status={metrics.cpu.status}
            icon={Cpu}
          />
          <MetricCard
            title="Memory Usage"
            value={metrics.memory.value}
            unit="%"
            change={Math.random() > 0.5 ? 1.5 : -0.8}
            status={metrics.memory.status}
            icon={MemoryStick}
          />
          <MetricCard
            title="Disk Usage"
            value={metrics.disk.value}
            unit="%"
            change={0.3}
            status={metrics.disk.status}
            icon={HardDrive}
          />
          <MetricCard
            title="Network I/O"
            value={metrics.network.value}
            unit="MB/s"
            change={Math.random() > 0.5 ? 5.2 : -2.1}
            status={metrics.network.status}
            icon={Network}
          />
        </div>
      </div>

      <Separator />

      {/* Application Metrics */}
      <div>
        <h4 className="text-sm font-medium text-muted-foreground mb-3">
          Application Performance
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="Uptime"
            value={metrics.uptime.value}
            status={metrics.uptime.status}
            icon={Server}
          />
          <MetricCard
            title="Active Connections"
            value={metrics.activeConnections.value}
            change={Math.random() > 0.5 ? 8.1 : -3.4}
            status={metrics.activeConnections.status}
            icon={Activity}
          />
          <MetricCard
            title="Throughput"
            value={metrics.throughput.value}
            unit="req/s"
            change={Math.random() > 0.5 ? 15.2 : -7.8}
            status={metrics.throughput.status}
            icon={Database}
          />
          <MetricCard
            title="Error Rate"
            value={metrics.errors.value}
            unit="errors/min"
            change={Math.random() > 0.5 ? -12.5 : 4.3}
            status={metrics.errors.status}
            icon={AlertTriangle}
          />
        </div>
      </div>
    </div>
  );
};

export default GrafanaMetrics;

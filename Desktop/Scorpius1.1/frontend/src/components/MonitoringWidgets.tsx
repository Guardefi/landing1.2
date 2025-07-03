import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Activity,
  Server,
  Database,
  Network,
  Cpu,
  MemoryStick,
  HardDrive,
  Users,
  Zap,
  Clock,
  Shield,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  TrendingDown,
  ExternalLink,
  RefreshCw,
  Monitor,
  Eye,
  Target,
  Globe,
  BarChart3,
  Container,
  Wifi,
} from "lucide-react";
import { Link } from "react-router-dom";
import { cn } from "@/lib/utils";

interface LiveMetricProps {
  icon: React.ElementType;
  label: string;
  value: string | number;
  unit?: string;
  status: "healthy" | "warning" | "critical";
  trend?: "up" | "down" | "stable";
  trendValue?: number;
  className?: string;
}

const LiveMetric: React.FC<LiveMetricProps> = ({
  icon: Icon,
  label,
  value,
  unit,
  status,
  trend,
  trendValue,
  className,
}) => {
  const getStatusColor = () => {
    switch (status) {
      case "critical":
        return "text-red-500";
      case "warning":
        return "text-yellow-500";
      default:
        return "text-green-500";
    }
  };

  const getTrendIcon = () => {
    switch (trend) {
      case "up":
        return <TrendingUp className="h-3 w-3 text-green-500" />;
      case "down":
        return <TrendingDown className="h-3 w-3 text-red-500" />;
      default:
        return <Activity className="h-3 w-3 text-muted-foreground" />;
    }
  };

  return (
    <div
      className={cn(
        "flex items-center justify-between p-3 rounded-lg border bg-card",
        className,
      )}
    >
      <div className="flex items-center space-x-3">
        <Icon className={cn("h-4 w-4", getStatusColor())} />
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium">{label}</span>
            <div
              className={cn(
                "w-2 h-2 rounded-full",
                status === "healthy"
                  ? "bg-green-500"
                  : status === "warning"
                    ? "bg-yellow-500"
                    : "bg-red-500",
              )}
            />
          </div>
          <div className="flex items-center space-x-1 mt-1">
            <span className={cn("text-lg font-bold", getStatusColor())}>
              {typeof value === "number" ? value.toLocaleString() : value}
            </span>
            {unit && (
              <span className="text-xs text-muted-foreground">{unit}</span>
            )}
          </div>
        </div>
      </div>
      <div className="flex items-center space-x-1">
        {getTrendIcon()}
        {trendValue && (
          <span className="text-xs text-muted-foreground">
            {trendValue > 0 ? "+" : ""}
            {trendValue}%
          </span>
        )}
      </div>
    </div>
  );
};

interface SystemOverviewProps {
  className?: string;
}

export const SystemOverview: React.FC<SystemOverviewProps> = ({
  className,
}) => {
  const [metrics, setMetrics] = useState({
    cpu: {
      value: 23,
      status: "healthy" as const,
      trend: "stable" as const,
      trendValue: 2.1,
    },
    memory: {
      value: 67,
      status: "warning" as const,
      trend: "up" as const,
      trendValue: 8.3,
    },
    disk: {
      value: 45,
      status: "healthy" as const,
      trend: "stable" as const,
      trendValue: 0.5,
    },
    network: {
      value: 156,
      status: "healthy" as const,
      trend: "up" as const,
      trendValue: 12.4,
    },
  });

  const [lastUpdate, setLastUpdate] = useState(new Date());

  const refreshMetrics = () => {
    setMetrics({
      cpu: {
        value: Math.floor(Math.random() * 100),
        status: Math.random() > 0.8 ? "warning" : "healthy",
        trend: Math.random() > 0.5 ? "up" : "down",
        trendValue: parseFloat((Math.random() * 10 - 5).toFixed(1)),
      },
      memory: {
        value: Math.floor(Math.random() * 100),
        status: Math.random() > 0.7 ? "warning" : "healthy",
        trend: Math.random() > 0.5 ? "up" : "down",
        trendValue: parseFloat((Math.random() * 10 - 5).toFixed(1)),
      },
      disk: {
        value: Math.floor(Math.random() * 100),
        status: "healthy",
        trend: "stable",
        trendValue: parseFloat((Math.random() * 2 - 1).toFixed(1)),
      },
      network: {
        value: Math.floor(Math.random() * 500),
        status: "healthy",
        trend: Math.random() > 0.5 ? "up" : "down",
        trendValue: parseFloat((Math.random() * 20 - 10).toFixed(1)),
      },
    });
    setLastUpdate(new Date());
  };

  useEffect(() => {
    const interval = setInterval(refreshMetrics, 15000); // Update every 15 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle className="text-lg font-semibold flex items-center space-x-2 flex-1 min-w-0">
          <Monitor className="h-5 w-5 text-blue-500 flex-shrink-0" />
          <span className="truncate">System Overview</span>
          <Badge variant="outline" className="text-xs flex-shrink-0">
            Live
          </Badge>
        </CardTitle>
        <div className="flex items-center space-x-1 flex-shrink-0">
          <Button
            variant="outline"
            size="sm"
            onClick={refreshMetrics}
            className="text-xs px-2"
          >
            <RefreshCw className="h-3 w-3" />
            <span className="hidden sm:ml-1 sm:inline">Refresh</span>
          </Button>
          <Link to="/monitoring/health">
            <Button variant="outline" size="sm" className="text-xs px-2">
              <ExternalLink className="h-3 w-3" />
              <span className="hidden sm:ml-1 sm:inline">Details</span>
            </Button>
          </Link>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <LiveMetric
          icon={Cpu}
          label="CPU Usage"
          value={metrics.cpu.value}
          unit="%"
          status={metrics.cpu.status}
          trend={metrics.cpu.trend}
          trendValue={metrics.cpu.trendValue}
        />
        <LiveMetric
          icon={MemoryStick}
          label="Memory"
          value={metrics.memory.value}
          unit="%"
          status={metrics.memory.status}
          trend={metrics.memory.trend}
          trendValue={metrics.memory.trendValue}
        />
        <LiveMetric
          icon={HardDrive}
          label="Disk Usage"
          value={metrics.disk.value}
          unit="%"
          status={metrics.disk.status}
          trend={metrics.disk.trend}
          trendValue={metrics.disk.trendValue}
        />
        <LiveMetric
          icon={Network}
          label="Network I/O"
          value={metrics.network.value}
          unit="MB/s"
          status={metrics.network.status}
          trend={metrics.network.trend}
          trendValue={metrics.network.trendValue}
        />

        <div className="pt-2 border-t text-xs text-muted-foreground flex justify-between">
          <span>Last updated: {lastUpdate.toLocaleTimeString()}</span>
          <span>Auto-refresh: 15s</span>
        </div>
      </CardContent>
    </Card>
  );
};

interface ApplicationStatusProps {
  className?: string;
}

export const ApplicationStatus: React.FC<ApplicationStatusProps> = ({
  className,
}) => {
  const services = [
    {
      name: "API Gateway",
      status: "healthy",
      uptime: "99.9%",
      responseTime: "45ms",
    },
    {
      name: "Database",
      status: "healthy",
      uptime: "99.8%",
      responseTime: "12ms",
    },
    {
      name: "Cache Layer",
      status: "warning",
      uptime: "98.5%",
      responseTime: "89ms",
    },
    {
      name: "Queue Service",
      status: "healthy",
      uptime: "99.7%",
      responseTime: "23ms",
    },
    {
      name: "File Storage",
      status: "healthy",
      uptime: "99.9%",
      responseTime: "156ms",
    },
    {
      name: "Search Engine",
      status: "healthy",
      uptime: "99.4%",
      responseTime: "67ms",
    },
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "healthy":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "warning":
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
    }
  };

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle className="text-lg font-semibold flex items-center space-x-2">
          <Server className="h-5 w-5 text-green-500" />
          <span>Service Status</span>
        </CardTitle>
        <Badge variant="outline" className="bg-green-50 dark:bg-green-950/20">
          {services.filter((s) => s.status === "healthy").length}/
          {services.length} Healthy
        </Badge>
      </CardHeader>
      <CardContent className="space-y-3">
        {services.map((service, index) => (
          <motion.div
            key={service.name}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            className="flex items-center justify-between p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
          >
            <div className="flex items-center space-x-3">
              {getStatusIcon(service.status)}
              <div>
                <div className="font-medium">{service.name}</div>
                <div className="text-xs text-muted-foreground">
                  Uptime: {service.uptime}
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm font-medium">{service.responseTime}</div>
              <div className="text-xs text-muted-foreground">avg response</div>
            </div>
          </motion.div>
        ))}

        <div className="pt-2 border-t">
          <Link to="/monitoring/health">
            <Button variant="outline" size="sm" className="w-full">
              <BarChart3 className="h-4 w-4 mr-2" />
              View Detailed Metrics
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
};

interface SecurityMonitorProps {
  className?: string;
}

export const SecurityMonitor: React.FC<SecurityMonitorProps> = ({
  className,
}) => {
  const [securityMetrics, setSecurityMetrics] = useState({
    threatsBlocked: 1439,
    attacksDetected: 23,
    vulnerabilities: 2,
    securityScore: 95,
  });

  const [recentEvents] = useState([
    {
      type: "blocked",
      message: "SQL injection attempt blocked",
      time: "2 min ago",
      severity: "high",
    },
    {
      type: "alert",
      message: "Unusual login pattern detected",
      time: "5 min ago",
      severity: "medium",
    },
    {
      type: "blocked",
      message: "DDoS attack mitigated",
      time: "12 min ago",
      severity: "high",
    },
    {
      type: "info",
      message: "Security scan completed",
      time: "18 min ago",
      severity: "low",
    },
  ]);

  const getEventIcon = (type: string) => {
    switch (type) {
      case "blocked":
        return <Shield className="h-4 w-4 text-red-500" />;
      case "alert":
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      default:
        return <CheckCircle className="h-4 w-4 text-blue-500" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high":
        return "text-red-500";
      case "medium":
        return "text-yellow-500";
      default:
        return "text-blue-500";
    }
  };

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle className="text-lg font-semibold flex items-center space-x-2">
          <Shield className="h-5 w-5 text-purple-500" />
          <span>Security Monitor</span>
        </CardTitle>
        <Badge variant="outline" className="bg-purple-50 dark:bg-purple-950/20">
          Score: {securityMetrics.securityScore}/100
        </Badge>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Security Metrics */}
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center p-3 rounded-lg border bg-red-50 dark:bg-red-950/20">
            <div className="text-2xl font-bold text-red-600">
              {securityMetrics.threatsBlocked.toLocaleString()}
            </div>
            <div className="text-xs text-muted-foreground">Threats Blocked</div>
          </div>
          <div className="text-center p-3 rounded-lg border bg-green-50 dark:bg-green-950/20">
            <div className="text-2xl font-bold text-green-600">
              {securityMetrics.vulnerabilities}
            </div>
            <div className="text-xs text-muted-foreground">Open Issues</div>
          </div>
        </div>

        {/* Recent Security Events */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium">Recent Events</h4>
          {recentEvents.slice(0, 3).map((event, index) => (
            <div
              key={index}
              className="flex items-center space-x-3 p-2 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
            >
              {getEventIcon(event.type)}
              <div className="flex-1 min-w-0">
                <div className="text-xs font-medium truncate">
                  {event.message}
                </div>
                <div
                  className={cn("text-xs", getSeverityColor(event.severity))}
                >
                  {event.severity.toUpperCase()} • {event.time}
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="pt-2 border-t">
          <Link to="/security/elite">
            <Button variant="outline" size="sm" className="w-full">
              <Eye className="h-4 w-4 mr-2" />
              View Security Dashboard
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
};

interface NetworkStatusProps {
  className?: string;
}

export const NetworkStatus: React.FC<NetworkStatusProps> = ({ className }) => {
  const [networkData, setNetworkData] = useState({
    bandwidth: "2.3 Gbps",
    latency: "12ms",
    packetLoss: "0.01%",
    connections: 847,
    regions: [
      { name: "US East", status: "healthy", latency: "8ms", load: 65 },
      { name: "EU West", status: "healthy", latency: "15ms", load: 78 },
      { name: "Asia Pacific", status: "warning", latency: "45ms", load: 89 },
    ],
  });

  const getRegionStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "border-green-500 bg-green-50 dark:bg-green-950/20";
      case "warning":
        return "border-yellow-500 bg-yellow-50 dark:bg-yellow-950/20";
      default:
        return "border-red-500 bg-red-50 dark:bg-red-950/20";
    }
  };

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle className="text-lg font-semibold flex items-center space-x-2">
          <Globe className="h-5 w-5 text-cyan-500" />
          <span>Network Status</span>
        </CardTitle>
        <Badge variant="outline" className="bg-cyan-50 dark:bg-cyan-950/20">
          Global
        </Badge>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Network Metrics */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Bandwidth</span>
              <span className="text-sm font-medium">
                {networkData.bandwidth}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Latency</span>
              <span className="text-sm font-medium text-green-600">
                {networkData.latency}
              </span>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Packet Loss</span>
              <span className="text-sm font-medium text-green-600">
                {networkData.packetLoss}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Connections</span>
              <span className="text-sm font-medium">
                {networkData.connections.toLocaleString()}
              </span>
            </div>
          </div>
        </div>

        {/* Regional Status */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium">Regional Status</h4>
          {networkData.regions.map((region, index) => (
            <div
              key={region.name}
              className={cn(
                "p-3 rounded-lg border",
                getRegionStatusColor(region.status),
              )}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <Wifi className="h-4 w-4" />
                  <span className="text-sm font-medium">{region.name}</span>
                </div>
                <span className="text-xs text-muted-foreground">
                  {region.latency}
                </span>
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span>Load</span>
                  <span>{region.load}%</span>
                </div>
                <Progress value={region.load} className="h-1" />
              </div>
            </div>
          ))}
        </div>

        <div className="pt-2 border-t">
          <Link to="/monitoring/health">
            <Button variant="outline" size="sm" className="w-full">
              <Network className="h-4 w-4 mr-2" />
              Network Details
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
};

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  ExternalLink,
  RefreshCw,
  Maximize2,
  Settings,
  AlertTriangle,
  BarChart3,
  LineChart,
  PieChart,
  Activity,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface GrafanaPanelProps {
  dashboardId: string;
  panelId: number;
  title: string;
  description?: string;
  grafanaUrl?: string;
  height?: number;
  width?: string;
  theme?: "light" | "dark";
  timeRange?: string;
  refresh?: string;
  variables?: Record<string, string>;
  panelType?:
    | "graph"
    | "singlestat"
    | "table"
    | "heatmap"
    | "gauge"
    | "bargauge";
  showHeader?: boolean;
  className?: string;
}

export const GrafanaPanel: React.FC<GrafanaPanelProps> = ({
  dashboardId,
  panelId,
  title,
  description,
  grafanaUrl = import.meta.env.VITE_GRAFANA_URL || "http://localhost:3001",
  height = 300,
  width = "100%",
  theme = "dark",
  timeRange = "1h",
  refresh = "30s",
  variables = {},
  panelType = "graph",
  showHeader = true,
  className,
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  // Build Grafana panel URL
  const buildPanelUrl = () => {
    const baseUrl = `${grafanaUrl}/d-solo/${dashboardId}`;
    const params = new URLSearchParams({
      orgId: "1",
      panelId: panelId.toString(),
      theme: theme,
      from: `now-${timeRange}`,
      to: "now",
      refresh: refresh,
      ...variables,
    });

    return `${baseUrl}?${params.toString()}`;
  };

  const handleRefresh = () => {
    setLastRefresh(new Date());
    const iframe = document.getElementById(
      `grafana-panel-${dashboardId}-${panelId}`,
    ) as HTMLIFrameElement;
    if (iframe) {
      iframe.src = iframe.src;
    }
  };

  const openInNewTab = () => {
    const fullUrl = `${grafanaUrl}/d/${dashboardId}?panelId=${panelId}&fullscreen`;
    window.open(fullUrl, "_blank");
  };

  const getPanelIcon = () => {
    switch (panelType) {
      case "singlestat":
      case "gauge":
      case "bargauge":
        return <Activity className="h-4 w-4" />;
      case "table":
        return <BarChart3 className="h-4 w-4" />;
      case "heatmap":
        return <PieChart className="h-4 w-4" />;
      default:
        return <LineChart className="h-4 w-4" />;
    }
  };

  useEffect(() => {
    setIsLoading(true);
    setIsError(false);

    // Simulate loading time
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, [dashboardId, panelId, grafanaUrl, theme, timeRange]);

  if (!showHeader) {
    return (
      <div className={cn("relative", className)} style={{ width, height }}>
        {isError ? (
          <Alert
            variant="destructive"
            className="h-full flex items-center justify-center"
          >
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>Failed to load panel</AlertDescription>
          </Alert>
        ) : (
          <>
            {isLoading && (
              <div className="absolute inset-0 flex items-center justify-center bg-background/80 backdrop-blur-sm z-10">
                <div className="flex items-center space-x-2">
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  <span className="text-sm text-muted-foreground">
                    Loading...
                  </span>
                </div>
              </div>
            )}
            <iframe
              id={`grafana-panel-${dashboardId}-${panelId}`}
              src={buildPanelUrl()}
              width="100%"
              height="100%"
              frameBorder="0"
              className="rounded"
              onLoad={() => setIsLoading(false)}
              onError={() => {
                setIsLoading(false);
                setIsError(true);
              }}
            />
          </>
        )}
      </div>
    );
  }

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <div className="flex flex-col space-y-1">
          <CardTitle className="text-base font-medium flex items-center space-x-2">
            {getPanelIcon()}
            <span>{title}</span>
          </CardTitle>
          {description && (
            <p className="text-sm text-muted-foreground">{description}</p>
          )}
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="text-xs">
            {timeRange}
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            className="h-8 w-8 p-0"
          >
            <RefreshCw className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={openInNewTab}
            className="h-8 w-8 p-0"
          >
            <ExternalLink className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-2">
        {isError ? (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              Failed to load Grafana panel. Please check your connection.
              <Button
                variant="outline"
                size="sm"
                onClick={handleRefresh}
                className="ml-2"
              >
                Retry
              </Button>
            </AlertDescription>
          </Alert>
        ) : (
          <div className="relative">
            {isLoading && (
              <div className="absolute inset-0 flex items-center justify-center bg-background/80 backdrop-blur-sm z-10">
                <div className="flex items-center space-x-2">
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  <span className="text-sm text-muted-foreground">
                    Loading panel...
                  </span>
                </div>
              </div>
            )}
            <iframe
              id={`grafana-panel-${dashboardId}-${panelId}`}
              src={buildPanelUrl()}
              width="100%"
              height={height}
              frameBorder="0"
              className="rounded-md"
              onLoad={() => setIsLoading(false)}
              onError={() => {
                setIsLoading(false);
                setIsError(true);
              }}
            />
          </div>
        )}
        <div className="flex justify-between items-center mt-2 text-xs text-muted-foreground">
          <span>Panel ID: {panelId}</span>
          <span>Auto-refresh: {refresh}</span>
        </div>
      </CardContent>
    </Card>
  );
};

// Specific panel components for common use cases
export const CPUUsagePanel: React.FC<{ className?: string }> = ({
  className,
}) => (
  <GrafanaPanel
    dashboardId="system-metrics"
    panelId={1}
    title="CPU Usage"
    description="Real-time CPU utilization across all nodes"
    panelType="graph"
    timeRange="2h"
    refresh="15s"
    height={250}
    className={className}
  />
);

export const MemoryUsagePanel: React.FC<{ className?: string }> = ({
  className,
}) => (
  <GrafanaPanel
    dashboardId="system-metrics"
    panelId={2}
    title="Memory Usage"
    description="Memory consumption and availability"
    panelType="graph"
    timeRange="2h"
    refresh="15s"
    height={250}
    className={className}
  />
);

export const NetworkTrafficPanel: React.FC<{ className?: string }> = ({
  className,
}) => (
  <GrafanaPanel
    dashboardId="network-metrics"
    panelId={1}
    title="Network Traffic"
    description="Inbound and outbound network traffic"
    panelType="graph"
    timeRange="1h"
    refresh="30s"
    height={250}
    className={className}
  />
);

export const RequestRatePanel: React.FC<{ className?: string }> = ({
  className,
}) => (
  <GrafanaPanel
    dashboardId="application-metrics"
    panelId={3}
    title="Request Rate"
    description="HTTP requests per second"
    panelType="singlestat"
    timeRange="5m"
    refresh="10s"
    height={150}
    className={className}
  />
);

export const ErrorRatePanel: React.FC<{ className?: string }> = ({
  className,
}) => (
  <GrafanaPanel
    dashboardId="application-metrics"
    panelId={4}
    title="Error Rate"
    description="Application error percentage"
    panelType="gauge"
    timeRange="1h"
    refresh="30s"
    height={200}
    className={className}
  />
);

export const ResponseTimePanel: React.FC<{ className?: string }> = ({
  className,
}) => (
  <GrafanaPanel
    dashboardId="application-metrics"
    panelId={5}
    title="Response Time"
    description="Average API response time"
    panelType="graph"
    timeRange="1h"
    refresh="30s"
    height={250}
    className={className}
  />
);

export default GrafanaPanel;

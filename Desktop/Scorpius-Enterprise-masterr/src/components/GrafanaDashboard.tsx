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
} from "lucide-react";
import { cn } from "@/lib/utils";

interface GrafanaDashboardProps {
  dashboardId: string;
  title: string;
  description?: string;
  grafanaUrl?: string;
  height?: number;
  theme?: "light" | "dark";
  timeRange?: string;
  refresh?: string;
  variables?: Record<string, string>;
  className?: string;
}

export const GrafanaDashboard: React.FC<GrafanaDashboardProps> = ({
  dashboardId,
  title,
  description,
  grafanaUrl = import.meta.env.VITE_GRAFANA_URL || "http://localhost:3001",
  height = 500,
  theme = "dark",
  timeRange = "1h",
  refresh = "30s",
  variables = {},
  className,
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  // Build Grafana URL with parameters
  const buildGrafanaUrl = () => {
    const baseUrl = `${grafanaUrl}/d/${dashboardId}`;
    const params = new URLSearchParams({
      orgId: "1",
      kiosk: "true",
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
      `grafana-${dashboardId}`,
    ) as HTMLIFrameElement;
    if (iframe) {
      iframe.src = iframe.src;
    }
  };

  const openInNewTab = () => {
    const fullUrl = buildGrafanaUrl().replace("kiosk=true", "");
    window.open(fullUrl, "_blank");
  };

  useEffect(() => {
    setIsLoading(true);
    setIsError(false);
  }, [dashboardId, grafanaUrl, theme, timeRange]);

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <div className="flex flex-col space-y-1">
          <CardTitle className="text-base font-medium">{title}</CardTitle>
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
              Failed to load Grafana dashboard. Please check your Grafana
              connection.
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
                    Loading dashboard...
                  </span>
                </div>
              </div>
            )}
            <iframe
              id={`grafana-${dashboardId}`}
              src={buildGrafanaUrl()}
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
          <span>Last updated: {lastRefresh.toLocaleTimeString()}</span>
          <span>Auto-refresh: {refresh}</span>
        </div>
      </CardContent>
    </Card>
  );
};

export default GrafanaDashboard;

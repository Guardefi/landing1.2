import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import {
  RefreshCw,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";

interface ServiceStatus {
  name: string;
  url: string;
  status: "online" | "offline" | "checking" | "error";
  responseTime?: number;
  lastChecked?: Date;
  error?: string;
}

const BACKEND_SERVICES = [
  { name: "Main API Gateway", url: "/api/health", port: "8000" },
  { name: "Scanner Service", url: "/api/scanner/health", port: "8001" },
  { name: "Honeypot Service", url: "/api/honeypot/health", port: "8002" },
  { name: "Mempool Service", url: "/api/mempool/health", port: "8003" },
  { name: "Bridge Service", url: "/api/bridge/health", port: "8004" },
  { name: "Bytecode Service", url: "/api/bytecode/health", port: "8005" },
  { name: "Wallet Guard", url: "/api/wallet/health", port: "8006" },
  { name: "Time Machine", url: "/api/time-machine/health", port: "8007" },
  { name: "Quantum Service", url: "/api/quantum/health", port: "8008" },
];

export const BackendServiceStatus: React.FC = () => {
  const [services, setServices] = useState<ServiceStatus[]>(
    BACKEND_SERVICES.map((service) => ({
      ...service,
      status: "checking" as const,
    })),
  );
  const [isChecking, setIsChecking] = useState(false);

  const checkService = async (
    service: (typeof BACKEND_SERVICES)[0],
  ): Promise<ServiceStatus> => {
    const startTime = Date.now();

    try {
      await apiClient.get(service.url);
      const responseTime = Date.now() - startTime;

      return {
        ...service,
        status: "online",
        responseTime,
        lastChecked: new Date(),
      };
    } catch (error: any) {
      return {
        ...service,
        status: "offline",
        lastChecked: new Date(),
        error: error.message || "Connection failed",
      };
    }
  };

  const checkAllServices = async () => {
    setIsChecking(true);

    // Set all to checking state
    setServices((prev) =>
      prev.map((s) => ({ ...s, status: "checking" as const })),
    );

    try {
      const results = await Promise.all(
        BACKEND_SERVICES.map((service) => checkService(service)),
      );
      setServices(results);
    } catch (error) {
      console.error("Error checking services:", error);
    } finally {
      setIsChecking(false);
    }
  };

  useEffect(() => {
    checkAllServices();

    // Check every 30 seconds
    const interval = setInterval(checkAllServices, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: ServiceStatus["status"]) => {
    switch (status) {
      case "online":
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "offline":
        return <XCircle className="w-4 h-4 text-red-500" />;
      case "error":
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case "checking":
        return <Clock className="w-4 h-4 text-blue-500 animate-spin" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: ServiceStatus["status"]) => {
    const variants = {
      online: "default",
      offline: "destructive",
      error: "secondary",
      checking: "outline",
    } as const;

    return (
      <Badge variant={variants[status] || "outline"}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const onlineCount = services.filter((s) => s.status === "online").length;
  const totalCount = services.length;

  return (
    <Card className="w-full">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-lg font-semibold">
          Backend Services Status
        </CardTitle>
        <div className="flex items-center space-x-2">
          <Badge
            variant={onlineCount === totalCount ? "default" : "destructive"}
          >
            {onlineCount}/{totalCount} Online
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={checkAllServices}
            disabled={isChecking}
          >
            <RefreshCw
              className={`w-4 h-4 mr-2 ${isChecking ? "animate-spin" : ""}`}
            />
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid gap-3">
          {services.map((service) => (
            <div
              key={service.name}
              className="flex items-center justify-between p-3 border rounded-lg"
            >
              <div className="flex items-center space-x-3">
                {getStatusIcon(service.status)}
                <div>
                  <div className="font-medium">{service.name}</div>
                  <div className="text-sm text-muted-foreground">
                    Port {service.port} • {service.url}
                  </div>
                  {service.error && (
                    <div className="text-xs text-red-500 mt-1">
                      Error: {service.error}
                    </div>
                  )}
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {service.responseTime && (
                  <span className="text-xs text-muted-foreground">
                    {service.responseTime}ms
                  </span>
                )}
                {getStatusBadge(service.status)}
              </div>
            </div>
          ))}
        </div>

        {onlineCount < totalCount && (
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 text-yellow-600" />
              <div className="text-sm text-yellow-800">
                Some backend services are offline. Make sure all services are
                running:
              </div>
            </div>
            <div className="mt-2 text-xs text-yellow-700 font-mono">
              {services
                .filter((s) => s.status === "offline")
                .map((s) => `• ${s.name} (Port ${s.port})`)
                .join("\n")}
            </div>
          </div>
        )}

        {service.lastChecked && (
          <div className="mt-3 text-xs text-muted-foreground">
            Last checked: {services[0]?.lastChecked?.toLocaleTimeString()}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default BackendServiceStatus;

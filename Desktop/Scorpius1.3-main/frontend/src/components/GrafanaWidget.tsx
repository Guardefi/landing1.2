import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart3 } from "lucide-react";

interface GrafanaWidgetProps {
  title?: string;
  description?: string;
  url?: string;
}

export const GrafanaWidget: React.FC<GrafanaWidgetProps> = ({
  title = "Grafana Dashboard",
  description = "Real-time metrics and monitoring",
  url,
}) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          {title}  
        </CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        {url ? (
          <iframe
            src={url}
            width="100%"
            height="300"
            frameBorder="0"
            title="Grafana Dashboard"
            className="rounded-md"
          />
        ) : (
          <div className="flex items-center justify-center h-48 bg-muted rounded-md">
            <p className="text-muted-foreground">Grafana dashboard will load here</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { RefreshCw, Activity } from "lucide-react";
import { LucideIcon } from "lucide-react";

interface ActivityItem {
  id: string;
  type: string;
  icon: LucideIcon;
  iconColor: string;
  message: string;
  time: string;
  severity: "info" | "warning" | "error" | "success";
}

interface ActivityFeedProps {
  title?: string;
  description?: string;
  activities: ActivityItem[];
  maxHeight?: string;
}

export const ActivityFeed = ({
  title = "Live Activity Stream",
  description = "Real-time system events and alerts",
  activities,
  maxHeight = "max-h-64",
}: ActivityFeedProps) => {
  const getSeverityVariant = (severity: ActivityItem["severity"]) => {
    switch (severity) {
      case "error":
        return "destructive";
      case "warning":
        return "default";
      case "success":
        return "secondary";
      default:
        return "secondary";
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="h-5 w-5" />
              <span>{title}</span>
            </CardTitle>
            <p className="text-sm text-muted-foreground mt-1">{description}</p>
          </div>
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className={`space-y-3 ${maxHeight} overflow-y-auto`}>
          {activities.map((activity) => (
            <div
              key={activity.id}
              className="flex items-start space-x-3 p-3 rounded-lg border"
            >
              <div className={`p-1 rounded ${activity.iconColor}`}>
                <activity.icon className="h-4 w-4" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium">{activity.message}</p>
                <p className="text-xs text-muted-foreground">{activity.time}</p>
              </div>
              <Badge variant={getSeverityVariant(activity.severity)}>
                {activity.severity}
              </Badge>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface MetricsCardProps {
  title: string;
  value: string | number;
  change?: string;
  period?: string;
  icon: LucideIcon;
  iconColor?: string;
  variant?: "default" | "positive" | "negative" | "warning";
  description?: string;
  onClick?: () => void;
}

export const MetricsCard = ({
  title,
  value,
  change,
  period,
  icon: Icon,
  iconColor = "text-primary",
  variant = "default",
  description,
  onClick,
}: MetricsCardProps) => {
  const getVariantStyles = () => {
    switch (variant) {
      case "positive":
        return "border-green-200 dark:border-green-800 bg-gradient-to-br from-green-50 to-green-100/50 dark:from-green-900/20 dark:to-green-800/10";
      case "negative":
        return "border-red-200 dark:border-red-800 bg-gradient-to-br from-red-50 to-red-100/50 dark:from-red-900/20 dark:to-red-800/10";
      case "warning":
        return "border-amber-200 dark:border-amber-800 bg-gradient-to-br from-amber-50 to-amber-100/50 dark:from-amber-900/20 dark:to-amber-800/10";
      default:
        return "border-border bg-gradient-to-br from-background to-muted/50";
    }
  };

  const getChangeColor = () => {
    if (!change) return "";
    if (change.startsWith("+")) return "text-green-600 dark:text-green-400";
    if (change.startsWith("-")) return "text-red-600 dark:text-red-400";
    return "text-muted-foreground";
  };

  return (
    <Card
      className={cn(
        "transition-all duration-200 hover:shadow-md cursor-pointer",
        getVariantStyles(),
        onClick && "hover:scale-105",
      )}
      onClick={onClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium text-foreground/80">
            {title}
          </CardTitle>
          <Icon className={cn("h-4 w-4", iconColor)} />
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <span className="text-2xl font-bold">{value}</span>
            {change && (
              <Badge
                variant="secondary"
                className={cn("text-xs", getChangeColor())}
              >
                {change}
              </Badge>
            )}
          </div>
          <div className="flex items-center justify-between">
            {period && (
              <span className="text-xs text-muted-foreground">{period}</span>
            )}
            {description && (
              <span className="text-xs text-muted-foreground">
                {description}
              </span>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

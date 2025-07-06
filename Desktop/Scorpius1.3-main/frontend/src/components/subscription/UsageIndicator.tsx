import React from "react";
import { useSubscription } from "../../contexts/SubscriptionContext";
import {
  getUsagePercentage,
  formatUsage,
  getUsageStatus,
  getRemainingUsage,
} from "../../lib/subscription-utils";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../ui/card";
import { Progress } from "../ui/progress";
import { Badge } from "../ui/badge";
import { AlertTriangle, CheckCircle, XCircle, Clock } from "lucide-react";

interface UsageIndicatorProps {
  type: "smartContracts" | "apiCalls";
  title: string;
  className?: string;
}

export function UsageIndicator({
  type,
  title,
  className,
}: UsageIndicatorProps) {
  const { subscription } = useSubscription();

  if (!subscription) {
    return (
      <Card className={className}>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-gray-500">Loading...</div>
        </CardContent>
      </Card>
    );
  }

  const percentage = getUsagePercentage(
    subscription.tier,
    subscription.usage,
    type,
  );
  const status = getUsageStatus(subscription.tier, subscription.usage, type);
  const remaining = getRemainingUsage(
    subscription.tier,
    subscription.usage,
    type,
  );
  const current = subscription.usage[type];
  const limit = require("../../lib/subscription-utils").getTierInfo(
    subscription.tier,
  ).limits[type];

  const getStatusIcon = () => {
    switch (status) {
      case "low":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "medium":
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case "high":
        return <AlertTriangle className="h-4 w-4 text-orange-500" />;
      case "exceeded":
        return <XCircle className="h-4 w-4 text-red-500" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case "low":
        return "bg-green-500";
      case "medium":
        return "bg-yellow-500";
      case "high":
        return "bg-orange-500";
      case "exceeded":
        return "bg-red-500";
    }
  };

  const getStatusBadge = () => {
    switch (status) {
      case "low":
        return (
          <Badge variant="outline" className="text-green-700 border-green-200">
            Good
          </Badge>
        );
      case "medium":
        return (
          <Badge
            variant="outline"
            className="text-yellow-700 border-yellow-200"
          >
            Moderate
          </Badge>
        );
      case "high":
        return (
          <Badge
            variant="outline"
            className="text-orange-700 border-orange-200"
          >
            High Usage
          </Badge>
        );
      case "exceeded":
        return <Badge variant="destructive">Limit Exceeded</Badge>;
    }
  };

  return (
    <Card className={className}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium">{title}</CardTitle>
          <div className="flex items-center gap-1">
            {getStatusIcon()}
            {getStatusBadge()}
          </div>
        </div>
        <CardDescription className="text-xs">
          {formatUsage(current, limit)}
        </CardDescription>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="space-y-3">
          <Progress
            value={Math.min(percentage, 100)}
            className="h-2"
            // @ts-ignore - custom progress bar color
            style={
              {
                "--progress-background": getStatusColor(),
              } as React.CSSProperties
            }
          />

          <div className="flex justify-between text-xs text-gray-500">
            <span>{percentage.toFixed(1)}% used</span>
            <span>
              {limit === -1
                ? "Unlimited remaining"
                : `${remaining.toLocaleString()} remaining`}
            </span>
          </div>

          {status === "exceeded" && (
            <div className="text-xs text-red-600 mt-2">
              You've exceeded your monthly limit. Upgrade your plan for more
              usage.
            </div>
          )}

          {status === "high" && (
            <div className="text-xs text-orange-600 mt-2">
              You're approaching your monthly limit. Consider upgrading to avoid
              interruption.
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export function UsageDashboard() {
  const { subscription } = useSubscription();

  if (!subscription) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="text-center text-gray-500">
              Loading usage data...
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const daysUntilRenewal = Math.ceil(
    (new Date(subscription.currentPeriodEnd).getTime() - new Date().getTime()) /
      (1000 * 60 * 60 * 24),
  );

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <UsageIndicator type="smartContracts" title="Smart Contract Scans" />
        <UsageIndicator type="apiCalls" title="API Calls" />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Billing Period</CardTitle>
          <CardDescription>Current billing period information</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Current Tier:</span>
              <Badge variant="outline">{subscription.tier}</Badge>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Days until renewal:</span>
              <span className="font-medium">{daysUntilRenewal} days</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Period end:</span>
              <span className="font-medium">
                {new Date(subscription.currentPeriodEnd).toLocaleDateString()}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Status:</span>
              <Badge
                variant={
                  subscription.status === "active" ? "default" : "destructive"
                }
              >
                {subscription.status}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

import React from "react";
import { useSubscription } from "../../contexts/SubscriptionContext";
import { TierType } from "../../types/subscription";
import { canUpgradeTo } from "../../lib/subscription-utils";
import { Button } from "../ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../ui/card";
import { Lock, Zap, Crown } from "lucide-react";

interface FeatureGateProps {
  feature: string;
  requiredTier?: TierType;
  children: React.ReactNode;
  fallback?: React.ReactNode;
  showUpgradePrompt?: boolean;
}

export function FeatureGate({
  feature,
  requiredTier,
  children,
  fallback,
  showUpgradePrompt = true,
}: FeatureGateProps) {
  const { subscription, checkFeatureAccess, upgradeToTier } = useSubscription();

  if (!subscription) {
    return fallback || <div>Loading subscription...</div>;
  }

  const hasAccess = checkFeatureAccess(feature);

  if (hasAccess) {
    return <>{children}</>;
  }

  if (fallback) {
    return <>{fallback}</>;
  }

  if (!showUpgradePrompt) {
    return null;
  }

  const getUpgradeTarget = (): TierType => {
    if (requiredTier) return requiredTier;
    if (subscription.tier === "PRO") return "ELITE";
    return "ENTERPRISE";
  };

  const targetTier = getUpgradeTarget();
  const canUpgrade = canUpgradeTo(subscription.tier, targetTier);

  const getTierIcon = (tier: TierType) => {
    switch (tier) {
      case "PRO":
        return <Zap className="h-5 w-5" />;
      case "ELITE":
        return <Crown className="h-5 w-5" />;
      case "ENTERPRISE":
        return <Crown className="h-5 w-5 text-yellow-500" />;
    }
  };

  const handleUpgrade = async () => {
    try {
      await upgradeToTier(targetTier);
    } catch (error) {
      console.error("Upgrade failed:", error);
    }
  };

  return (
    <Card className="border-dashed border-2 border-gray-300 bg-gray-50/50">
      <CardHeader className="text-center pb-4">
        <div className="mx-auto w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mb-3">
          <Lock className="h-6 w-6 text-gray-500" />
        </div>
        <CardTitle className="text-lg">Premium Feature</CardTitle>
        <CardDescription>
          This feature requires {targetTier} tier or higher
        </CardDescription>
      </CardHeader>
      <CardContent className="text-center space-y-4">
        <div className="flex items-center justify-center gap-2 text-sm text-gray-600">
          {getTierIcon(targetTier)}
          <span>Upgrade to {targetTier} Tier</span>
        </div>

        {canUpgrade && (
          <Button onClick={handleUpgrade} className="w-full" size="sm">
            Upgrade Now
          </Button>
        )}

        <p className="text-xs text-gray-500">
          Your current tier: {subscription.tier}
        </p>
      </CardContent>
    </Card>
  );
}

interface UsageGateProps {
  usageType: "smartContracts" | "apiCalls";
  children: React.ReactNode;
  fallback?: React.ReactNode;
  showUpgradePrompt?: boolean;
}

export function UsageGate({
  usageType,
  children,
  fallback,
  showUpgradePrompt = true,
}: UsageGateProps) {
  const { subscription, checkUsageLimit, upgradeToTier } = useSubscription();

  if (!subscription) {
    return fallback || <div>Loading subscription...</div>;
  }

  const hasReachedLimit = checkUsageLimit(usageType);

  if (!hasReachedLimit) {
    return <>{children}</>;
  }

  if (fallback) {
    return <>{fallback}</>;
  }

  if (!showUpgradePrompt) {
    return null;
  }

  const getUpgradeTarget = (): TierType => {
    if (subscription.tier === "PRO") return "ELITE";
    return "ENTERPRISE";
  };

  const targetTier = getUpgradeTarget();
  const canUpgrade = canUpgradeTo(subscription.tier, targetTier);

  const getUsageTypeLabel = () => {
    switch (usageType) {
      case "smartContracts":
        return "smart contract scans";
      case "apiCalls":
        return "API calls";
    }
  };

  const handleUpgrade = async () => {
    try {
      await upgradeToTier(targetTier);
    } catch (error) {
      console.error("Upgrade failed:", error);
    }
  };

  return (
    <Card className="border-dashed border-2 border-orange-300 bg-orange-50/50">
      <CardHeader className="text-center pb-4">
        <div className="mx-auto w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mb-3">
          <Lock className="h-6 w-6 text-orange-500" />
        </div>
        <CardTitle className="text-lg">Usage Limit Reached</CardTitle>
        <CardDescription>
          You've reached your monthly limit for {getUsageTypeLabel()}
        </CardDescription>
      </CardHeader>
      <CardContent className="text-center space-y-4">
        <div className="text-sm text-gray-600">
          Upgrade to {targetTier} for higher limits
        </div>

        {canUpgrade && (
          <Button
            onClick={handleUpgrade}
            className="w-full"
            size="sm"
            variant="outline"
          >
            Upgrade to {targetTier}
          </Button>
        )}

        <p className="text-xs text-gray-500">Limits reset monthly</p>
      </CardContent>
    </Card>
  );
}

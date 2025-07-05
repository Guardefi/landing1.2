import React from "react";
import { useSubscription } from "../../contexts/SubscriptionContext";
import {
  getUpgradeRecommendation,
  shouldShowUpgradePrompt,
} from "../../lib/subscription-utils";
import { TierType } from "../../types/subscription";
import { Button } from "../ui/button";
import { Alert, AlertDescription } from "../ui/alert";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../ui/card";
import { Badge } from "../ui/badge";
import { ArrowUp, X, Zap, Crown, Star } from "lucide-react";

interface UpgradePromptProps {
  onDismiss?: () => void;
  className?: string;
  variant?: "inline" | "banner" | "modal";
}

export function UpgradePrompt({
  onDismiss,
  className,
  variant = "inline",
}: UpgradePromptProps) {
  const { subscription, upgradeToTier } = useSubscription();

  if (
    !subscription ||
    !shouldShowUpgradePrompt(subscription.tier, subscription.usage)
  ) {
    return null;
  }

  const recommendedTier = getUpgradeRecommendation(
    subscription.tier,
    subscription.usage,
  );

  if (!recommendedTier) {
    return null;
  }

  const handleUpgrade = async () => {
    try {
      await upgradeToTier(recommendedTier);
      onDismiss?.();
    } catch (error) {
      console.error("Upgrade failed:", error);
    }
  };

  const getTierIcon = (tier: TierType) => {
    switch (tier) {
      case "PRO":
        return <Zap className="h-5 w-5 text-blue-500" />;
      case "ELITE":
        return <Crown className="h-5 w-5 text-purple-500" />;
      case "ENTERPRISE":
        return <Star className="h-5 w-5 text-yellow-500" />;
    }
  };

  const getTierPrice = (tier: TierType) => {
    const { TIER_DEFINITIONS } = require("../../types/subscription");
    return TIER_DEFINITIONS[tier].price;
  };

  if (variant === "banner") {
    return (
      <Alert className={`border-orange-200 bg-orange-50 ${className}`}>
        <ArrowUp className="h-4 w-4 text-orange-600" />
        <AlertDescription className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-orange-800">
              You're approaching your usage limits. Upgrade to {recommendedTier}{" "}
              for more capacity.
            </span>
            {getTierIcon(recommendedTier)}
            <Badge
              variant="outline"
              className="text-orange-700 border-orange-300"
            >
              ${getTierPrice(recommendedTier)}/month
            </Badge>
          </div>
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              onClick={handleUpgrade}
              className="bg-orange-600 hover:bg-orange-700"
            >
              Upgrade Now
            </Button>
            {onDismiss && (
              <Button
                size="sm"
                variant="ghost"
                onClick={onDismiss}
                className="text-orange-600 hover:text-orange-700"
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        </AlertDescription>
      </Alert>
    );
  }

  if (variant === "modal") {
    return (
      <Card className={`max-w-md mx-auto ${className}`}>
        <CardHeader className="text-center">
          <div className="mx-auto w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mb-3">
            <ArrowUp className="h-6 w-6 text-orange-600" />
          </div>
          <CardTitle>Time to Upgrade!</CardTitle>
          <CardDescription>
            You're running low on your monthly limits
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center">
            <div className="flex items-center justify-center gap-2 mb-2">
              {getTierIcon(recommendedTier)}
              <span className="font-semibold">{recommendedTier} Tier</span>
            </div>
            <div className="text-2xl font-bold text-orange-600">
              ${getTierPrice(recommendedTier)}/month
            </div>
          </div>

          <div className="space-y-2 text-sm text-gray-600">
            <div>✓ Higher usage limits</div>
            <div>✓ Advanced features</div>
            <div>✓ Priority support</div>
          </div>

          <div className="flex gap-2">
            <Button onClick={handleUpgrade} className="flex-1">
              Upgrade Now
            </Button>
            {onDismiss && (
              <Button variant="outline" onClick={onDismiss} className="flex-1">
                Later
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  // Default inline variant
  return (
    <Card className={`border-orange-200 bg-orange-50/50 ${className}`}>
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center flex-shrink-0">
            <ArrowUp className="h-4 w-4 text-orange-600" />
          </div>

          <div className="flex-1 space-y-2">
            <div className="font-medium text-orange-800">
              Upgrade Recommended
            </div>
            <div className="text-sm text-orange-700">
              You're approaching your usage limits. Upgrade to {recommendedTier}{" "}
              for more capacity and advanced features.
            </div>

            <div className="flex items-center gap-2">
              <Button
                size="sm"
                onClick={handleUpgrade}
                className="bg-orange-600 hover:bg-orange-700"
              >
                Upgrade to {recommendedTier}
              </Button>
              <Badge
                variant="outline"
                className="text-orange-700 border-orange-300"
              >
                ${getTierPrice(recommendedTier)}/month
              </Badge>
            </div>
          </div>

          {onDismiss && (
            <Button
              size="sm"
              variant="ghost"
              onClick={onDismiss}
              className="text-orange-600 hover:text-orange-700 flex-shrink-0"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

interface UsageLimitReachedProps {
  type: "smartContracts" | "apiCalls";
  onUpgrade?: () => void;
  className?: string;
}

export function UsageLimitReached({
  type,
  onUpgrade,
  className,
}: UsageLimitReachedProps) {
  const { subscription, upgradeToTier } = useSubscription();

  if (!subscription) return null;

  const handleUpgrade = async () => {
    const targetTier = subscription.tier === "PRO" ? "ELITE" : "ENTERPRISE";
    try {
      await upgradeToTier(targetTier);
      onUpgrade?.();
    } catch (error) {
      console.error("Upgrade failed:", error);
    }
  };

  const getTypeLabel = () => {
    switch (type) {
      case "smartContracts":
        return "smart contract scans";
      case "apiCalls":
        return "API calls";
    }
  };

  return (
    <Alert className={`border-red-200 bg-red-50 ${className}`}>
      <X className="h-4 w-4 text-red-600" />
      <AlertDescription className="space-y-2">
        <div className="font-medium text-red-800">Monthly limit reached</div>
        <div className="text-sm text-red-700">
          You've used all your {getTypeLabel()} for this month. Upgrade your
          plan to continue using this feature.
        </div>
        <Button
          size="sm"
          onClick={handleUpgrade}
          className="bg-red-600 hover:bg-red-700"
        >
          Upgrade Plan
        </Button>
      </AlertDescription>
    </Alert>
  );
}

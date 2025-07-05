import React from "react";
import { TierType, Tier } from "../../types/subscription";
import { formatPrice } from "../../lib/subscription-utils";
import { useSubscription } from "../../contexts/SubscriptionContext";
import { Button } from "../ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../ui/card";
import { Badge } from "../ui/badge";
import { Check, Zap, Crown, Star } from "lucide-react";

interface TierCardProps {
  tier: Tier;
  isCurrentTier?: boolean;
  onUpgrade?: (tier: TierType) => void;
  isLoading?: boolean;
}

export function TierCard({
  tier,
  isCurrentTier,
  onUpgrade,
  isLoading,
}: TierCardProps) {
  const { subscription } = useSubscription();

  const getTierIcon = () => {
    switch (tier.id) {
      case "PRO":
        return <Zap className="h-6 w-6 text-blue-500" />;
      case "ELITE":
        return <Crown className="h-6 w-6 text-purple-500" />;
      case "ENTERPRISE":
        return <Star className="h-6 w-6 text-yellow-500" />;
    }
  };

  const getTierBadge = () => {
    if (isCurrentTier) {
      return (
        <Badge variant="default" className="bg-green-500">
          Current Plan
        </Badge>
      );
    }
    if (tier.highlighted) {
      return (
        <Badge variant="secondary" className="bg-purple-100 text-purple-700">
          Most Popular
        </Badge>
      );
    }
    return null;
  };

  const canUpgradeToTier = () => {
    if (!subscription || isCurrentTier) return false;

    const tiers: TierType[] = ["PRO", "ELITE", "ENTERPRISE"];
    const currentIndex = tiers.indexOf(subscription.tier);
    const targetIndex = tiers.indexOf(tier.id);

    return targetIndex > currentIndex;
  };

  const handleUpgrade = () => {
    if (onUpgrade && canUpgradeToTier()) {
      onUpgrade(tier.id);
    }
  };

  return (
    <Card
      className={`relative ${tier.highlighted ? "ring-2 ring-purple-500 shadow-lg" : ""} ${isCurrentTier ? "ring-2 ring-green-500" : ""}`}
    >
      {tier.highlighted && (
        <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
          <Badge className="bg-purple-500 text-white px-3 py-1">
            Most Popular
          </Badge>
        </div>
      )}

      <CardHeader className="text-center pb-6">
        <div className="flex items-center justify-center gap-3 mb-2">
          {getTierIcon()}
          <CardTitle className="text-2xl">{tier.name}</CardTitle>
        </div>

        <div className="space-y-1">
          <div className="text-4xl font-bold">
            {formatPrice(tier.price)}
            <span className="text-lg font-normal text-gray-500">/month</span>
          </div>
          {getTierBadge()}
        </div>

        <CardDescription className="text-sm">{tier.target}</CardDescription>
      </CardHeader>

      <CardContent className="space-y-6">
        <p className="text-sm text-gray-600 text-center">{tier.description}</p>

        <div className="space-y-3">
          {tier.features.map((feature, index) => (
            <div key={index} className="flex items-start gap-3">
              <Check className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-gray-700">{feature}</span>
            </div>
          ))}
        </div>

        <div className="pt-4">
          {isCurrentTier ? (
            <Button disabled className="w-full">
              Current Plan
            </Button>
          ) : canUpgradeToTier() ? (
            <Button
              onClick={handleUpgrade}
              disabled={isLoading}
              className="w-full"
              variant={tier.highlighted ? "default" : "outline"}
            >
              {isLoading ? "Processing..." : `Upgrade to ${tier.name}`}
            </Button>
          ) : (
            <Button disabled className="w-full" variant="outline">
              Contact Sales
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

interface TierComparisonProps {
  currentTier?: TierType;
  onUpgrade?: (tier: TierType) => void;
  isLoading?: boolean;
}

export function TierComparison({
  currentTier,
  onUpgrade,
  isLoading,
}: TierComparisonProps) {
  const { TIER_DEFINITIONS } = require("../../types/subscription");

  const tiers = Object.values(TIER_DEFINITIONS) as Tier[];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-7xl mx-auto">
      {tiers.map((tier) => (
        <TierCard
          key={tier.id}
          tier={tier}
          isCurrentTier={currentTier === tier.id}
          onUpgrade={onUpgrade}
          isLoading={isLoading}
        />
      ))}
    </div>
  );
}

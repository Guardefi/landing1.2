import React, { createContext, useContext, useState, useEffect } from "react";
import { TierType, Subscription, DEFAULT_USAGE } from "../types/subscription";
import { getTierInfo, hasReachedLimit } from "../lib/subscription-utils";
import { apiClient } from "../lib/api-client";
import { useAuth } from "./AuthContext";

interface SubscriptionContextType {
  subscription: Subscription | null;
  loading: boolean;
  error: string | null;
  refreshSubscription: () => Promise<void>;
  updateUsage: (
    type: "smartContracts" | "apiCalls",
    increment?: number,
  ) => Promise<void>;
  checkFeatureAccess: (feature: string) => boolean;
  checkUsageLimit: (type: "smartContracts" | "apiCalls") => boolean;
  upgradeToTier: (tier: TierType) => Promise<void>;
  cancelSubscription: () => Promise<void>;
}

const SubscriptionContext = createContext<SubscriptionContextType | undefined>(
  undefined,
);

export function useSubscription() {
  const context = useContext(SubscriptionContext);
  if (context === undefined) {
    throw new Error(
      "useSubscription must be used within a SubscriptionProvider",
    );
  }
  return context;
}

interface SubscriptionProviderProps {
  children: React.ReactNode;
}

export function SubscriptionProvider({ children }: SubscriptionProviderProps) {
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user, isAuthenticated } = useAuth();

  const refreshSubscription = async () => {
    if (!isAuthenticated || !user) {
      setSubscription(null);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.get<any>("/subscription");
      
      // Normalize tier name to match frontend expectations
      const normalizeTier = (tier: string): TierType => {
        const lowerTier = tier.toLowerCase();
        if (lowerTier === "enterprise" || lowerTier === "admin") return "ENTERPRISE";
        if (lowerTier === "elite") return "ELITE";
        return "PRO"; // Default to PRO for free/pro users
      };
      
      // Handle API response structure
      const subscriptionData = response.data || response;
      
      // Normalize the subscription data
      const normalizedSubscription: Subscription = {
        ...subscriptionData,
        tier: normalizeTier(subscriptionData.tier || "pro")
      };
      
      setSubscription(normalizedSubscription);
    } catch (err) {
      console.error("Failed to fetch subscription:", err);

      // Create default PRO subscription for new users
      const defaultSubscription: Subscription = {
        id: "temp-" + Date.now(),
        userId: user.id,
        tier: "PRO",
        status: "active",
        currentPeriodStart: new Date().toISOString(),
        currentPeriodEnd: new Date(
          Date.now() + 30 * 24 * 60 * 60 * 1000,
        ).toISOString(),
        cancelAtPeriodEnd: false,
        usage: { ...DEFAULT_USAGE },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      setSubscription(defaultSubscription);
      setError("Using default subscription - please set up billing");
    } finally {
      setLoading(false);
    }
  };

  const updateUsage = async (
    type: "smartContracts" | "apiCalls",
    increment: number = 1,
  ) => {
    if (!subscription) return;

    try {
      const updatedUsage = {
        ...subscription.usage,
        [type]: subscription.usage[type] + increment,
      };

      const response = await apiClient.put<Subscription>(
        "/subscription/usage",
        {
          [type]: updatedUsage[type],
        },
      );

      const responseData = (response as any).data || response;
      setSubscription(responseData);
    } catch (err) {
      console.error("Failed to update usage:", err);

      // Update locally if API fails
      setSubscription((prev) => {
        if (!prev) return null;
        return {
          ...prev,
          usage: {
            ...prev.usage,
            [type]: prev.usage[type] + increment,
          },
        };
      });
    }
  };

  const checkFeatureAccess = (feature: string): boolean => {
    if (!subscription) return false;

    const { limits } = getTierInfo(subscription.tier);
    return limits.features.includes(feature) || limits.features.includes("all");
  };

  const checkUsageLimit = (type: "smartContracts" | "apiCalls"): boolean => {
    if (!subscription) return false;

    return hasReachedLimit(subscription.tier, subscription.usage, type);
  };

  const upgradeToTier = async (tier: TierType) => {
    if (!subscription) return;

    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.post<Subscription>(
        "/subscription/upgrade",
        {
          tier,
        },
      );

      const responseData = (response as any).data || response;
      setSubscription(responseData);
    } catch (err) {
      console.error("Failed to upgrade subscription:", err);
      setError("Failed to upgrade subscription. Please try again.");
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const cancelSubscription = async () => {
    if (!subscription) return;

    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.post<Subscription>(
        "/subscription/cancel",
      );
      const responseData = (response as any).data || response;
      setSubscription(responseData);
    } catch (err) {
      console.error("Failed to cancel subscription:", err);
      setError("Failed to cancel subscription. Please try again.");
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshSubscription();
  }, [isAuthenticated, user]);

  const value: SubscriptionContextType = {
    subscription,
    loading,
    error,
    refreshSubscription,
    updateUsage,
    checkFeatureAccess,
    checkUsageLimit,
    upgradeToTier,
    cancelSubscription,
  };

  return (
    <SubscriptionContext.Provider value={value}>
      {children}
    </SubscriptionContext.Provider>
  );
}

import React, { useState } from "react";
import { useSubscription } from "../contexts/SubscriptionContext";
import { TierComparison } from "../components/subscription/TierCard";
import { UsageDashboard } from "../components/subscription/UsageIndicator";
import { UpgradePrompt } from "../components/subscription/UpgradePrompt";
import { TierType } from "../types/subscription";
import { formatPrice, getDaysUntilRenewal } from "../lib/subscription-utils";
import { Button } from "../components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "../components/ui/tabs";
import { Alert, AlertDescription } from "../components/ui/alert";
import {
  CreditCard,
  Download,
  AlertCircle,
  CheckCircle,
  Clock,
  Settings,
  BarChart3,
  Crown,
} from "lucide-react";

export default function Subscription() {
  const {
    subscription,
    loading,
    error,
    upgradeToTier,
    cancelSubscription,
    refreshSubscription,
  } = useSubscription();

  const [upgradeLoading, setUpgradeLoading] = useState(false);
  const [cancelLoading, setCancelLoading] = useState(false);

  const handleUpgrade = async (tier: TierType) => {
    setUpgradeLoading(true);
    try {
      await upgradeToTier(tier);
    } catch (error) {
      console.error("Upgrade failed:", error);
    } finally {
      setUpgradeLoading(false);
    }
  };

  const handleCancel = async () => {
    setCancelLoading(true);
    try {
      await cancelSubscription();
    } catch (error) {
      console.error("Cancel failed:", error);
    } finally {
      setCancelLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">
              Loading subscription details...
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Alert className="max-w-md mx-auto">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {error}
              <Button
                onClick={refreshSubscription}
                variant="outline"
                size="sm"
                className="ml-2"
              >
                Retry
              </Button>
            </AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  if (!subscription) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <p className="text-gray-600">No subscription found.</p>
            <Button onClick={refreshSubscription} className="mt-4">
              Refresh
            </Button>
          </div>
        </div>
      </div>
    );
  }

  const daysUntilRenewal = getDaysUntilRenewal(subscription);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Subscription</h1>
              <p className="text-gray-600 mt-1">
                Manage your plan and monitor usage
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Badge
                variant={
                  subscription.status === "active" ? "default" : "destructive"
                }
                className="text-sm"
              >
                {subscription.status}
              </Badge>
              <Button onClick={refreshSubscription} variant="outline" size="sm">
                Refresh
              </Button>
            </div>
          </div>
        </div>

        {/* Upgrade Prompt */}
        <UpgradePrompt variant="banner" className="mb-6" />

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="plans" className="flex items-center gap-2">
              <Crown className="h-4 w-4" />
              Plans
            </TabsTrigger>
            <TabsTrigger value="billing" className="flex items-center gap-2">
              <CreditCard className="h-4 w-4" />
              Billing
            </TabsTrigger>
            <TabsTrigger value="settings" className="flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Settings
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Current Plan Overview */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Crown className="h-5 w-5" />
                  Current Plan: {subscription.tier}
                </CardTitle>
                <CardDescription>
                  Your subscription details and usage summary
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="space-y-2">
                    <div className="text-sm text-gray-600">Monthly Cost</div>
                    <div className="text-2xl font-bold">
                      {formatPrice(
                        require("../types/subscription").TIER_DEFINITIONS[
                          subscription.tier
                        ].price,
                      )}
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="text-sm text-gray-600">Next Billing</div>
                    <div className="text-lg font-medium">
                      {daysUntilRenewal} days
                    </div>
                    <div className="text-xs text-gray-500">
                      {new Date(
                        subscription.currentPeriodEnd,
                      ).toLocaleDateString()}
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="text-sm text-gray-600">Account Status</div>
                    <div className="flex items-center gap-2">
                      {subscription.status === "active" ? (
                        <>
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          <span className="text-green-700 font-medium">
                            Active
                          </span>
                        </>
                      ) : (
                        <>
                          <AlertCircle className="h-4 w-4 text-red-500" />
                          <span className="text-red-700 font-medium">
                            {subscription.status}
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Usage Dashboard */}
            <UsageDashboard />
          </TabsContent>

          <TabsContent value="plans" className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Choose Your Plan</h2>
              <p className="text-gray-600 mb-6">
                Upgrade or downgrade your subscription at any time
              </p>

              <TierComparison
                currentTier={subscription.tier}
                onUpgrade={handleUpgrade}
                isLoading={upgradeLoading}
              />
            </div>
          </TabsContent>

          <TabsContent value="billing" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Billing Information */}
              <Card>
                <CardHeader>
                  <CardTitle>Billing Information</CardTitle>
                  <CardDescription>
                    Your current billing details
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Current Plan:</span>
                    <span className="font-medium">{subscription.tier}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Monthly Cost:</span>
                    <span className="font-medium">
                      {formatPrice(
                        require("../types/subscription").TIER_DEFINITIONS[
                          subscription.tier
                        ].price,
                      )}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Next Billing:</span>
                    <span className="font-medium">
                      {new Date(
                        subscription.currentPeriodEnd,
                      ).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Payment Method:</span>
                    <span className="font-medium">**** 4242</span>
                  </div>
                </CardContent>
              </Card>

              {/* Billing Actions */}
              <Card>
                <CardHeader>
                  <CardTitle>Billing Actions</CardTitle>
                  <CardDescription>
                    Manage your subscription and billing
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Button variant="outline" className="w-full justify-start">
                    <CreditCard className="h-4 w-4 mr-2" />
                    Update Payment Method
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Download className="h-4 w-4 mr-2" />
                    Download Invoices
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Clock className="h-4 w-4 mr-2" />
                    View Billing History
                  </Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="settings" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Subscription Settings</CardTitle>
                <CardDescription>
                  Manage your subscription preferences
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">Auto-renewal</div>
                      <div className="text-sm text-gray-600">
                        Automatically renew your subscription each month
                      </div>
                    </div>
                    <Badge
                      variant={
                        subscription.cancelAtPeriodEnd
                          ? "destructive"
                          : "default"
                      }
                    >
                      {subscription.cancelAtPeriodEnd ? "Disabled" : "Enabled"}
                    </Badge>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">Usage Alerts</div>
                      <div className="text-sm text-gray-600">
                        Get notified when approaching usage limits
                      </div>
                    </div>
                    <Badge variant="default">Enabled</Badge>
                  </div>
                </div>

                <div className="pt-6 border-t border-gray-200">
                  <div className="space-y-4">
                    <div>
                      <h3 className="font-medium text-red-900 mb-2">
                        Danger Zone
                      </h3>
                      <p className="text-sm text-gray-600 mb-4">
                        These actions cannot be undone. Please proceed with
                        caution.
                      </p>
                    </div>

                    <Button
                      variant="destructive"
                      onClick={handleCancel}
                      disabled={cancelLoading || subscription.cancelAtPeriodEnd}
                    >
                      {cancelLoading ? "Cancelling..." : "Cancel Subscription"}
                    </Button>

                    {subscription.cancelAtPeriodEnd && (
                      <Alert>
                        <AlertCircle className="h-4 w-4" />
                        <AlertDescription>
                          Your subscription will be cancelled at the end of the
                          current billing period (
                          {new Date(
                            subscription.currentPeriodEnd,
                          ).toLocaleDateString()}
                          ).
                        </AlertDescription>
                      </Alert>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

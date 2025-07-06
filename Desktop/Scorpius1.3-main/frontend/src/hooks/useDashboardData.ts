import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { useState, useEffect } from "react";
import { toast } from "sonner";

// Dashboard data hook for real-time updates
export const useDashboardData = () => {
  const queryClient = useQueryClient();

  // System Health & Status
  const {
    data: systemHealth,
    isLoading: healthLoading,
    error: healthError,
  } = useQuery({
    queryKey: ["system-health"],
    queryFn: () => apiClient.healthCheck(),
    refetchInterval: 5000,
    retry: 2,
  });

  // Analytics & Metrics
  const { data: dashboardMetrics, isLoading: metricsLoading } = useQuery({
    queryKey: ["dashboard-metrics"],
    queryFn: () => apiClient.getDashboardMetrics(),
    refetchInterval: 30000,
  });

  // Security Metrics
  const { data: securityMetrics, isLoading: securityLoading } = useQuery({
    queryKey: ["security-metrics"],
    queryFn: () => apiClient.getSecurityMetrics(),
    refetchInterval: 10000,
  });

  // Performance Metrics
  const { data: performanceMetrics, isLoading: performanceLoading } = useQuery({
    queryKey: ["performance-metrics"],
    queryFn: () => apiClient.getPerformanceMetrics(),
    refetchInterval: 15000,
  });

  // Recent Scanner Results
  const { data: recentScans, isLoading: scansLoading } = useQuery({
    queryKey: ["recent-scans"],
    queryFn: () => apiClient.getRecentScans(5),
    refetchInterval: 30000,
  });

  // Bridge Status
  const { data: bridgeStatus, isLoading: bridgeLoading } = useQuery({
    queryKey: ["bridge-status"],
    queryFn: () => apiClient.getBridgeStatus(),
    refetchInterval: 10000,
  });

  // Mempool Stats
  const { data: mempoolStats, isLoading: mempoolLoading } = useQuery({
    queryKey: ["mempool-stats"],
    queryFn: () => apiClient.getMempoolStats(),
    refetchInterval: 5000,
  });

  // Current Usage Stats
  const { data: usageStats, isLoading: usageLoading } = useQuery({
    queryKey: ["usage-stats"],
    queryFn: () => apiClient.getCurrentUsage(),
    refetchInterval: 60000,
  });

  // Subscription Info
  const { data: subscriptionInfo, isLoading: subscriptionLoading } = useQuery({
    queryKey: ["subscription-info"],
    queryFn: () => apiClient.getSubscriptionInfo(),
    refetchInterval: 300000, // 5 minutes
  });

  // Refresh all data
  const refreshAll = async () => {
    try {
      await queryClient.invalidateQueries();
      toast.success("Dashboard data refreshed");
    } catch (error) {
      toast.error("Failed to refresh dashboard data");
    }
  };

  // Calculate overall loading state
  const isLoading =
    healthLoading || metricsLoading || securityLoading || performanceLoading;

  // Calculate connection status
  const isConnected = !healthError && systemHealth?.status === "healthy";

  return {
    // Data
    systemHealth,
    dashboardMetrics,
    securityMetrics,
    performanceMetrics,
    recentScans,
    bridgeStatus,
    mempoolStats,
    usageStats,
    subscriptionInfo,

    // Loading states
    isLoading,
    healthLoading,
    metricsLoading,
    securityLoading,
    performanceLoading,
    scansLoading,
    bridgeLoading,
    mempoolLoading,
    usageLoading,
    subscriptionLoading,

    // Connection status
    isConnected,
    healthError,

    // Actions
    refreshAll,
  };
};

// Scanner operations hook
export const useScannerOperations = () => {
  const queryClient = useQueryClient();

  // Initiate scan mutation
  const scanMutation = useMutation({
    mutationFn: ({ address, options }: { address: string; options?: any }) =>
      apiClient.scanContract(address, options),
    onSuccess: () => {
      toast.success("Scan initiated successfully");
      queryClient.invalidateQueries({ queryKey: ["recent-scans"] });
    },
    onError: () => {
      toast.error("Failed to initiate scan");
    },
  });

  // Upload and scan mutation
  const uploadScanMutation = useMutation({
    mutationFn: (file: File) => apiClient.uploadAndScan(file),
    onSuccess: () => {
      toast.success("File uploaded and scan initiated");
      queryClient.invalidateQueries({ queryKey: ["recent-scans"] });
    },
    onError: () => {
      toast.error("Failed to upload and scan file");
    },
  });

  return {
    scanContract: scanMutation.mutate,
    uploadAndScan: uploadScanMutation.mutate,
    isScanning: scanMutation.isPending || uploadScanMutation.isPending,
    scanError: scanMutation.error || uploadScanMutation.error,
  };
};

// Bridge operations hook
export const useBridgeOperations = () => {
  const queryClient = useQueryClient();

  // Bridge transfer mutation
  const transferMutation = useMutation({
    mutationFn: ({
      fromChain,
      toChain,
      amount,
      token,
    }: {
      fromChain: string;
      toChain: string;
      amount: string;
      token: string;
    }) => apiClient.initiateBridgeTransfer(fromChain, toChain, amount, token),
    onSuccess: () => {
      toast.success("Bridge transfer initiated");
      queryClient.invalidateQueries({ queryKey: ["bridge-transactions"] });
    },
    onError: () => {
      toast.error("Failed to initiate bridge transfer");
    },
  });

  // Get quote mutation
  const quoteMutation = useMutation({
    mutationFn: ({
      fromChain,
      toChain,
      amount,
      token,
    }: {
      fromChain: string;
      toChain: string;
      amount: string;
      token: string;
    }) => apiClient.getBridgeQuote(fromChain, toChain, amount, token),
    onSuccess: (quote) => {
      toast.success(
        `Quote received: ${quote.estimatedFee} ${quote.feeCurrency}`,
      );
    },
    onError: () => {
      toast.error("Failed to get bridge quote");
    },
  });

  return {
    initiateBridgeTransfer: transferMutation.mutate,
    getBridgeQuote: quoteMutation.mutate,
    isTransferring: transferMutation.isPending,
    isGettingQuote: quoteMutation.isPending,
    transferError: transferMutation.error,
    quoteError: quoteMutation.error,
  };
};

// Honeypot detection hook
export const useHoneypotOperations = () => {
  const queryClient = useQueryClient();

  // Detect honeypot mutation
  const detectMutation = useMutation({
    mutationFn: (address: string) => apiClient.detectHoneypot(address),
    onSuccess: () => {
      toast.success("Honeypot detection initiated");
      queryClient.invalidateQueries({ queryKey: ["honeypot-detections"] });
    },
    onError: () => {
      toast.error("Failed to initiate honeypot detection");
    },
  });

  // Analyze honeypot mutation
  const analyzeMutation = useMutation({
    mutationFn: (address: string) => apiClient.analyzeHoneypot(address),
    onSuccess: () => {
      toast.success("Honeypot analysis completed");
      queryClient.invalidateQueries({ queryKey: ["honeypot-detections"] });
    },
    onError: () => {
      toast.error("Failed to analyze honeypot");
    },
  });

  return {
    detectHoneypot: detectMutation.mutate,
    analyzeHoneypot: analyzeMutation.mutate,
    isDetecting: detectMutation.isPending,
    isAnalyzing: analyzeMutation.isPending,
    detectError: detectMutation.error,
    analyzeError: analyzeMutation.error,
  };
};

// Wallet operations hook
export const useWalletOperations = () => {
  const queryClient = useQueryClient();

  // Check wallet mutation
  const checkMutation = useMutation({
    mutationFn: (address: string) => apiClient.checkWallet(address),
    onSuccess: () => {
      toast.success("Wallet check completed");
    },
    onError: () => {
      toast.error("Failed to check wallet");
    },
  });

  // Revoke approval mutation
  const revokeMutation = useMutation({
    mutationFn: ({
      address,
      tokenContract,
      spender,
    }: {
      address: string;
      tokenContract: string;
      spender: string;
    }) => apiClient.revokeApproval(address, tokenContract, spender),
    onSuccess: () => {
      toast.success("Approval revoked successfully");
      queryClient.invalidateQueries({ queryKey: ["wallet-approvals"] });
    },
    onError: () => {
      toast.error("Failed to revoke approval");
    },
  });

  return {
    checkWallet: checkMutation.mutate,
    revokeApproval: revokeMutation.mutate,
    isChecking: checkMutation.isPending,
    isRevoking: revokeMutation.isPending,
    checkError: checkMutation.error,
    revokeError: revokeMutation.error,
  };
};

export default {
  useDashboardData,
  useScannerOperations,
  useBridgeOperations,
  useHoneypotOperations,
  useWalletOperations,
};

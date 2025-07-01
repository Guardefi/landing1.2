import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, useCallback, useRef } from "react";
import { toast } from "sonner";
import apiClient from "@/lib/api";
import {
  cacheKeys,
  createOptimisticUpdate,
  invalidateRelatedQueries,
} from "@/lib/react-query";
import useWebSocket from "./useWebSocket";

// =============================================================================
// TYPES
// =============================================================================

interface ScanWorkflowData {
  scanId: string;
  contractAddress?: string;
  sourceCode?: string;
  plugins?: string[];
  priority?: "low" | "medium" | "high" | "critical";
}

interface ScanProgress {
  scanId: string;
  status: "queued" | "scanning" | "completed" | "failed";
  progress: number;
  currentStage: string;
  completedStages: string[];
  totalStages: number;
  estimatedCompletion?: string;
  findings?: any[];
}

interface HoneypotAnalysisData {
  address: string;
  priority?: "low" | "medium" | "high";
  includeSimulation?: boolean;
  reportFormat?: "json" | "pdf" | "both";
}

interface NotificationPreferences {
  email: boolean;
  push: boolean;
  sms: boolean;
  webhook?: string;
  severityFilter: "all" | "medium" | "high" | "critical";
}

// =============================================================================
// 1. WALLET SCAN → BYTECODE SERVICE → RESULTS STREAM → UI DASHBOARD UPDATE
// =============================================================================

export function useWalletScanWorkflow() {
  const queryClient = useQueryClient();
  const [currentScan, setCurrentScan] = useState<ScanProgress | null>(null);
  const scanTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // WebSocket for real-time progress updates
  const { sendJsonMessage, isConnected } = useWebSocket("scanner", {
    onMessage: (message) => {
      if (
        message.type === "scan_progress" &&
        message.data?.scan_id === currentScan?.scanId
      ) {
        setCurrentScan((prev) => (prev ? { ...prev, ...message.data } : null));

        // Update dashboard metrics
        queryClient.invalidateQueries({ queryKey: cacheKeys.dashboardMetrics });
      }

      if (
        message.type === "scan_completed" &&
        message.data?.scan_id === currentScan?.scanId
      ) {
        const scanId = message.data.scan_id;

        // Update scan results
        invalidateRelatedQueries.onScanComplete(scanId);

        // Show completion notification
        toast.success("Scan completed successfully", {
          description: `Found ${message.data.findings_count || 0} potential issues`,
          action: {
            label: "View Results",
            onClick: () => window.open(`/scanner/results/${scanId}`, "_blank"),
          },
        });

        // Clear current scan
        setCurrentScan(null);

        // Clear timeout
        if (scanTimeoutRef.current) {
          clearTimeout(scanTimeoutRef.current);
          scanTimeoutRef.current = null;
        }
      }
    },
  });

  // Start wallet scan mutation
  const startScanMutation = useMutation({
    mutationFn: async (data: ScanWorkflowData) => {
      const response = await apiClient.post("/api/scanner/scan", data);
      if (!response.success) {
        throw new Error(response.error || "Failed to start scan");
      }
      return response.data;
    },
    onSuccess: (data) => {
      const scanProgress: ScanProgress = {
        scanId: data.scan_id,
        status: "queued",
        progress: 0,
        currentStage: "Initializing",
        completedStages: [],
        totalStages: data.total_stages || 5,
      };

      setCurrentScan(scanProgress);

      // Subscribe to updates
      if (isConnected) {
        sendJsonMessage({ type: "subscribe", scan_id: data.scan_id });
      }

      // Set a timeout for scan completion (30 minutes)
      scanTimeoutRef.current = setTimeout(
        () => {
          toast.error("Scan timeout", {
            description:
              "The scan is taking longer than expected. Please check the results page.",
          });
          setCurrentScan(null);
        },
        30 * 60 * 1000,
      );

      toast.info("Scan started", {
        description: "Your wallet scan has been queued and will begin shortly.",
      });
    },
    ...createOptimisticUpdate({
      queryKey: cacheKeys.scanHistory(),
      updater: (oldData: any[]) => [
        ...(oldData || []),
        {
          id: `temp-${Date.now()}`,
          status: "queued",
          created_at: new Date().toISOString(),
        },
      ],
    }),
  });

  // Get scan results
  const getScanResults = useCallback(async (scanId: string) => {
    const response = await apiClient.get(`/api/scanner/scan/${scanId}/results`);
    return response.data;
  }, []);

  // Cancel scan
  const cancelScan = useCallback(async (scanId: string) => {
    await apiClient.post(`/api/scanner/scan/${scanId}/cancel`);
    setCurrentScan(null);
    if (scanTimeoutRef.current) {
      clearTimeout(scanTimeoutRef.current);
      scanTimeoutRef.current = null;
    }
    toast.info("Scan cancelled");
  }, []);

  return {
    startScan: startScanMutation.mutate,
    isStarting: startScanMutation.isPending,
    currentScan,
    getScanResults,
    cancelScan,
    error: startScanMutation.error,
  };
}

// =============================================================================
// 2. HONEYPOT ANALYSIS → NOTIFICATION + PDF REPORT
// =============================================================================

export function useHoneypotAnalysisWorkflow() {
  const queryClient = useQueryClient();
  const [currentAnalysis, setCurrentAnalysis] = useState<{
    analysisId: string;
    address: string;
    status: "analyzing" | "completed" | "failed";
    progress: number;
  } | null>(null);

  // WebSocket for real-time updates
  const { sendJsonMessage, isConnected } = useWebSocket("honeypot", {
    onMessage: (message) => {
      if (
        message.type === "analysis_progress" &&
        currentAnalysis?.analysisId === message.data?.analysis_id
      ) {
        setCurrentAnalysis((prev) =>
          prev ? { ...prev, ...message.data } : null,
        );
      }

      if (
        message.type === "analysis_completed" &&
        currentAnalysis?.analysisId === message.data?.analysis_id
      ) {
        const {
          analysis_id,
          address,
          is_honeypot,
          confidence_score,
          report_url,
        } = message.data;

        // Update cache
        invalidateRelatedQueries.onHoneypotDetection(address);

        // Show notification with results
        const severity = is_honeypot ? "error" : "success";
        const title = is_honeypot ? "Honeypot Detected!" : "Token Appears Safe";
        const description = `Confidence: ${Math.round(confidence_score * 100)}%`;

        toast[severity](title, {
          description,
          action: report_url
            ? {
                label: "Download Report",
                onClick: () => window.open(report_url, "_blank"),
              }
            : undefined,
        });

        // Clear current analysis
        setCurrentAnalysis(null);
      }
    },
  });

  // Start honeypot analysis
  const startAnalysisMutation = useMutation({
    mutationFn: async (data: HoneypotAnalysisData) => {
      const response = await apiClient.post("/api/honeypot/analyze", data);
      if (!response.success) {
        throw new Error(response.error || "Failed to start analysis");
      }
      return response.data;
    },
    onSuccess: (data) => {
      setCurrentAnalysis({
        analysisId: data.analysis_id,
        address: data.address,
        status: "analyzing",
        progress: 0,
      });

      // Subscribe to updates
      if (isConnected) {
        sendJsonMessage({ type: "subscribe", analysis_id: data.analysis_id });
      }

      toast.info("Analysis started", {
        description: `Analyzing ${data.address} for honeypot patterns...`,
      });
    },
    ...createOptimisticUpdate({
      queryKey: cacheKeys.honeypotHistory(),
      updater: (oldData: any[]) => [
        ...(oldData || []),
        {
          id: `temp-${Date.now()}`,
          address: "pending",
          status: "analyzing",
          created_at: new Date().toISOString(),
        },
      ],
    }),
  });

  // Get analysis history
  const { data: analysisHistory, isLoading: isLoadingHistory } = useQuery({
    queryKey: cacheKeys.honeypotHistory(),
    queryFn: () => apiClient.get("/api/honeypot/history"),
  });

  // Download report
  const downloadReport = useCallback(
    async (analysisId: string, format: "pdf" | "json" = "pdf") => {
      const response = await apiClient.get(
        `/api/honeypot/analysis/${analysisId}/report?format=${format}`,
        {
          skipAuth: false,
        },
      );

      if (response.success && response.data?.download_url) {
        window.open(response.data.download_url, "_blank");
      }
    },
    [],
  );

  return {
    startAnalysis: startAnalysisMutation.mutate,
    isStarting: startAnalysisMutation.isPending,
    currentAnalysis,
    analysisHistory: analysisHistory?.data || [],
    isLoadingHistory,
    downloadReport,
    error: startAnalysisMutation.error,
  };
}

// =============================================================================
// 3. TRADING BOT WORKFLOW
// =============================================================================

export function useTradingBotWorkflow() {
  const queryClient = useQueryClient();

  // Start trading bot
  const startBotMutation = useMutation({
    mutationFn: async (botId: string) => {
      const response = await apiClient.post(`/api/trading/bots/${botId}/start`);
      if (!response.success) {
        throw new Error(response.error || "Failed to start bot");
      }
      return response.data;
    },
    onSuccess: (data, botId) => {
      invalidateRelatedQueries.onTradingBotUpdate(botId);
      toast.success("Trading bot started", {
        description: "Your bot is now actively trading.",
      });
    },
    ...createOptimisticUpdate({
      queryKey: cacheKeys.tradingBots,
      updater: (oldData: any[]) =>
        oldData?.map((bot) =>
          bot.id === arguments[0] ? { ...bot, status: "starting" } : bot,
        ) || [],
    }),
  });

  // Stop trading bot
  const stopBotMutation = useMutation({
    mutationFn: async (botId: string) => {
      const response = await apiClient.post(`/api/trading/bots/${botId}/stop`);
      if (!response.success) {
        throw new Error(response.error || "Failed to stop bot");
      }
      return response.data;
    },
    onSuccess: (data, botId) => {
      invalidateRelatedQueries.onTradingBotUpdate(botId);
      toast.info("Trading bot stopped", {
        description: "Your bot has been safely stopped.",
      });
    },
    ...createOptimisticUpdate({
      queryKey: cacheKeys.tradingBots,
      updater: (oldData: any[]) =>
        oldData?.map((bot) =>
          bot.id === arguments[0] ? { ...bot, status: "stopping" } : bot,
        ) || [],
    }),
  });

  // Create trading bot
  const createBotMutation = useMutation({
    mutationFn: async (config: any) => {
      const response = await apiClient.post("/api/trading/bots", config);
      if (!response.success) {
        throw new Error(response.error || "Failed to create bot");
      }
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: cacheKeys.tradingBots });
      toast.success("Trading bot created", {
        description: "Your new bot is ready to start trading.",
      });
    },
  });

  return {
    startBot: startBotMutation.mutate,
    stopBot: stopBotMutation.mutate,
    createBot: createBotMutation.mutate,
    isStarting: startBotMutation.isPending,
    isStopping: stopBotMutation.isPending,
    isCreating: createBotMutation.isPending,
  };
}

// =============================================================================
// 4. BRIDGE TRANSACTION WORKFLOW
// =============================================================================

export function useBridgeWorkflow() {
  const queryClient = useQueryClient();

  // WebSocket for transaction updates
  const { sendJsonMessage } = useWebSocket("bridge", {
    onMessage: (message) => {
      if (message.type === "transaction_update") {
        invalidateRelatedQueries.onBridgeTransaction();

        const { status, transaction_hash, amount, from_chain, to_chain } =
          message.data;

        if (status === "completed") {
          toast.success("Bridge transaction completed", {
            description: `${amount} bridged from ${from_chain} to ${to_chain}`,
            action: {
              label: "View Transaction",
              onClick: () =>
                window.open(`/bridge/tx/${transaction_hash}`, "_blank"),
            },
          });
        } else if (status === "failed") {
          toast.error("Bridge transaction failed", {
            description: "Please check the transaction details and try again.",
          });
        }
      }
    },
  });

  // Initiate bridge transaction
  const bridgeMutation = useMutation({
    mutationFn: async (params: {
      amount: string;
      tokenAddress: string;
      fromChain: string;
      toChain: string;
      recipientAddress: string;
      slippageTolerance?: number;
    }) => {
      const response = await apiClient.post("/api/bridge/transfer", params);
      if (!response.success) {
        throw new Error(response.error || "Failed to initiate bridge");
      }
      return response.data;
    },
    onSuccess: (data) => {
      // Subscribe to transaction updates
      sendJsonMessage({
        type: "subscribe",
        transaction_id: data.transaction_id,
      });

      toast.info("Bridge transaction initiated", {
        description: "Your transaction has been submitted to the bridge.",
      });
    },
  });

  return {
    initiateBridge: bridgeMutation.mutate,
    isInitiating: bridgeMutation.isPending,
    error: bridgeMutation.error,
  };
}

// =============================================================================
// 5. NOTIFICATION WORKFLOW
// =============================================================================

export function useNotificationWorkflow() {
  const queryClient = useQueryClient();

  // Update notification preferences
  const updatePreferencesMutation = useMutation({
    mutationFn: async (preferences: NotificationPreferences) => {
      const response = await apiClient.put(
        "/api/notifications/preferences",
        preferences,
      );
      if (!response.success) {
        throw new Error(response.error || "Failed to update preferences");
      }
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: cacheKeys.notificationSettings,
      });
      toast.success("Notification preferences updated");
    },
  });

  // Mark notification as read
  const markAsReadMutation = useMutation({
    mutationFn: async (notificationId: string) => {
      const response = await apiClient.put(
        `/api/notifications/${notificationId}/read`,
      );
      if (!response.success) {
        throw new Error(response.error || "Failed to mark as read");
      }
      return response.data;
    },
    ...createOptimisticUpdate({
      queryKey: cacheKeys.notifications,
      updater: (oldData: any[]) =>
        oldData?.map((notification) =>
          notification.id === arguments[0]
            ? { ...notification, read: true, read_at: new Date().toISOString() }
            : notification,
        ) || [],
    }),
  });

  // Mark all as read
  const markAllAsReadMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.put("/api/notifications/read-all");
      if (!response.success) {
        throw new Error(response.error || "Failed to mark all as read");
      }
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: cacheKeys.notifications });
      toast.success("All notifications marked as read");
    },
  });

  return {
    updatePreferences: updatePreferencesMutation.mutate,
    markAsRead: markAsReadMutation.mutate,
    markAllAsRead: markAllAsReadMutation.mutate,
    isUpdatingPreferences: updatePreferencesMutation.isPending,
    isMarkingAsRead: markAsReadMutation.isPending,
    isMarkingAllAsRead: markAllAsReadMutation.isPending,
  };
}

// =============================================================================
// 6. SYSTEM MONITORING WORKFLOW
// =============================================================================

export function useSystemMonitoringWorkflow() {
  const queryClient = useQueryClient();

  // WebSocket for real-time system updates
  useWebSocket("system", {
    onMessage: (message) => {
      if (message.type === "system_alert") {
        const { severity, title, description, component } = message.data;

        queryClient.invalidateQueries({ queryKey: cacheKeys.systemHealth });

        if (severity === "critical") {
          toast.error(title, { description });
        } else if (severity === "warning") {
          toast.warning(title, { description });
        }
      }

      if (message.type === "metrics_update") {
        queryClient.invalidateQueries({ queryKey: cacheKeys.systemMetrics });
      }
    },
  });

  // Restart service
  const restartServiceMutation = useMutation({
    mutationFn: async (serviceName: string) => {
      const response = await apiClient.post(
        `/api/system/services/${serviceName}/restart`,
      );
      if (!response.success) {
        throw new Error(response.error || "Failed to restart service");
      }
      return response.data;
    },
    onSuccess: (data, serviceName) => {
      queryClient.invalidateQueries({ queryKey: cacheKeys.systemHealth });
      toast.success(`Service ${serviceName} restarted successfully`);
    },
  });

  return {
    restartService: restartServiceMutation.mutate,
    isRestarting: restartServiceMutation.isPending,
  };
}

// =============================================================================
// EXPORT ALL WORKFLOWS
// =============================================================================

export {
  useWalletScanWorkflow,
  useHoneypotAnalysisWorkflow,
  useTradingBotWorkflow,
  useBridgeWorkflow,
  useNotificationWorkflow,
  useSystemMonitoringWorkflow,
};

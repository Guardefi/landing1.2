// Export all hooks from this file
export { useToast } from "./use-toast";
export { useIsMobile } from "./use-mobile";
export { useWebSocket } from "./useWebSocket";
export { useSSE } from "./useSSE";

import apiClient, { ApiResponse } from "../lib/api";
import { useMutation, useQuery, UseMutationOptions } from "@tanstack/react-query";
import type { LicenseInfo } from "@/lib/api/types";
import { useEffect, useState, useRef, useCallback } from "react";
import { queryClient } from "../lib/react-query";
import { useWebSocket as useWebSocketHook } from "./useWebSocket"; // local import for hook usage

// API Hooks
export const useLogin = () =>
  useMutation<
    { token: string },
    Error,
    { email: string; password: string; remember_me?: boolean }
  >({
    mutationFn: (creds) =>
      apiClient.post<{ token: string }>("/auth/login", creds),
  });

export const useBiometricLogin = () => {
  // Placeholder implementation
  return {
    login: async () => ({ success: true }),
    isAvailable: false,
    isLoading: false,
  };
};

export const useSystemStatus = () =>
  useQuery({
    queryKey: ["system-status"],
    queryFn: () => apiClient.get("/health"),
    refetchInterval: 30_000,
  });

// --- LICENSE VERIFICATION HOOK (MERGED) ---
interface LicenseVerificationPayload {
  license_key: string;
  license_file?: File;
}

export const useLicenseVerification = (
  options?: UseMutationOptions<ApiResponse<LicenseInfo>, Error, LicenseVerificationPayload>
) =>
  useMutation<ApiResponse<LicenseInfo>, Error, LicenseVerificationPayload>({
    mutationFn: ({ license_key }) =>
      apiClient.post<ApiResponse<LicenseInfo>>("/license/verify", { license_key }),
    ...options,
  });
// -------------------------------------------

export const useMempool = () => {
  const { data, isLoading, error } = useQuery({
    queryKey: ["mempool-initial"],
    queryFn: () => apiClient.get("/api/mempool/latest"),
    staleTime: 10_000,
  });

  // Live updates via WS
  const { sendJsonMessage } = useWebSocketHook("ws/mempool", {
    onMessage: (e) => {
      try {
        const tx = JSON.parse(e.data);
        // Push to React Query cache list
        queryClient.setQueryData<any[]>(["mempool-stream"], (old = []) => [
          tx,
          ...old.slice(0, 999),
        ]);
      } catch (_) {}
    },
  });

  useEffect(() => {
    // Optionally request backfill or ping
    sendJsonMessage({ type: "ping" });
  }, [sendJsonMessage]);

  const transactions =
    useQuery({
      queryKey: ["mempool-stream"],
      queryFn: () => [],
    }).data ?? [];

  return {
    transactions: [...(data ?? []), ...transactions],
    isLoading,
    error,
  };
};

export const useSecurityMonitoring = () => {
  // Placeholder implementation
  return {
    threats: [],
    isLoading: false,
    error: null,
    refresh: () => {},
  };
};

export const useScannerAPI = () => {
  // Placeholder implementation
  return {
    scan: async (contract: string) => ({ results: [] }),
    isLoading: false,
    error: null,
  };
};

export const useHoneypotDetection = () =>
  useQuery({
    queryKey: ["honeypot-detections"],
    queryFn: () => apiClient.get("/api/scanner/api/v1/honeypot/detections"),
    enabled: false, // placeholder until backend ready
  });

interface HoneypotAnalyzePayload {
  address: string;
}
export const useHoneypotAnalyzer = () => {
  return useMutation<any, Error, HoneypotAnalyzePayload>({
    mutationFn: ({ address }) =>
      apiClient.post("/api/scanner/api/v1/honeypot/analyze", { address }),
  });
};

export const useTradingEngine = () => {
  const [bots, setBots] = useState<any[]>([]);
  const [metrics, setMetrics] = useState<any>({});
  const [isConnected, setIsConnected] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch MEV bot status and strategies
  const fetchBotData = useCallback(async () => {
    try {
      // Get bot status
      const statusResponse = await apiClient.get("/api/mev-bot/status");
      
      // Get strategies
      const strategiesResponse = await apiClient.get("/api/mev-bot/strategies");
      
      // Get performance metrics
      const performanceResponse = await apiClient.get("/api/mev-bot/performance");
      
      if (statusResponse?.data && strategiesResponse?.data && performanceResponse?.data) {
        // Transform strategies into bot format for frontend
        const strategiesData = strategiesResponse.data as Record<string, any>;
        const transformedBots = Object.entries(strategiesData).map(([key, strategy]: [string, any]) => ({
          id: key,
          name: strategy.name,
          strategy: key,
          status: strategy.is_active ? "active" : "idle",
          profit: strategy.stats?.total_profit || 0,
          trades: strategy.stats?.total_opportunities || 0,
          gasUsed: strategy.stats?.total_gas_used || 0,
          winRate: strategy.stats?.success_rate || 0,
          config: strategy.config
        }));
        
        setBots(transformedBots);
        const performanceData = performanceResponse.data as any;
        setMetrics({
          totalProfit: performanceData.total_profit_eth || 0,
          totalTrades: performanceData.total_executions || 0,
          totalOpportunities: performanceData.total_opportunities || 0,
          successRate: performanceData.success_rate || 0,
          uptimeHours: performanceData.uptime_hours || 0,
          strategiesActive: performanceData.strategies_active || 0
        });
        
        setIsConnected(true);
        setError(null);
      }
    } catch (err: any) {
      console.error("Error fetching MEV bot data:", err);
      setError(err.message || "Failed to connect to MEV bot");
      setIsConnected(false);
    }
  }, []);

  // Start a bot/strategy
  const startBot = useCallback(async (strategyId: string) => {
    try {
      const response = await apiClient.post("/api/mev-bot/strategy/toggle", {
        strategy_type: strategyId,
        enabled: true
      });
      
      const responseData = response?.data as any;
      if (responseData?.success) {
        await fetchBotData(); // Refresh data
        return { success: true };
      }
      throw new Error(responseData?.message || "Failed to start strategy");
    } catch (err: any) {
      setError(err.message || "Failed to start bot");
      return { success: false, error: err.message };
    }
  }, [fetchBotData]);

  // Stop a bot/strategy
  const stopBot = useCallback(async (strategyId: string) => {
    try {
      const response = await apiClient.post("/api/mev-bot/strategy/toggle", {
        strategy_type: strategyId,
        enabled: false
      });
      
      const responseData = response?.data as any;
      if (responseData?.success) {
        await fetchBotData(); // Refresh data
        return { success: true };
      }
      throw new Error(responseData?.message || "Failed to stop strategy");
    } catch (err: any) {
      setError(err.message || "Failed to stop bot");
      return { success: false, error: err.message };
    }
  }, [fetchBotData]);

  // Create a new bot (start the entire MEV bot)
  const createBot = useCallback(async (config: any) => {
    try {
      const response = await apiClient.post("/api/mev-bot/start");
      
      const responseData = response?.data as any;
      if (responseData?.message) {
        await fetchBotData(); // Refresh data
        return { success: true };
      }
      throw new Error("Failed to start MEV bot");
    } catch (err: any) {
      setError(err.message || "Failed to create bot");
      return { success: false, error: err.message };
    }
  }, [fetchBotData]);

  // Get latest opportunities
  const getOpportunities = useCallback(async (limit = 10) => {
    try {
      const response = await apiClient.get(`/api/mev-bot/opportunities?limit=${limit}`);
      return response?.data || [];
    } catch (err: any) {
      console.error("Error fetching opportunities:", err);
      return [];
    }
  }, []);

  // Get recent executions
  const getExecutions = useCallback(async (limit = 10) => {
    try {
      const response = await apiClient.get(`/api/mev-bot/executions?limit=${limit}`);
      return response?.data || [];
    } catch (err: any) {
      console.error("Error fetching executions:", err);
      return [];
    }
  }, []);

  // Fetch data on component mount and set up polling
  useEffect(() => {
    fetchBotData();
    
    const interval = setInterval(fetchBotData, 5000); // Poll every 5 seconds
    
    return () => clearInterval(interval);
  }, [fetchBotData]);

  return {
    bots,
    metrics,
    isConnected,
    error,
    startBot,
    stopBot,
    createBot,
    getOpportunities,
    getExecutions,
    refreshData: fetchBotData
  };
};

export const useWalletCheck = () =>
  useMutation<any, Error, { address: string }>({
    mutationFn: (payload) => apiClient.post("/api/wallet/check", payload),
  });

export const useWalletRevoke = () =>
  useMutation<
    any,
    Error,
    { address: string; token_contract: string; spender: string }
  >({
    mutationFn: (payload) => apiClient.post("/api/wallet/revoke", payload),
  });

export const useTeamChat = () => {
  // Placeholder implementation
  return {
    messages: [],
    send: async (message: string) => ({ success: true }),
    isLoading: false,
    error: null,
  };
};

export const useNotifications = () => {
  // Placeholder implementation
  return {
    notifications: [],
    markAsRead: async (id: string) => ({ success: true }),
    isLoading: false,
    error: null,
  };
};

export const useVulnerabilityScanner = () => {
  interface ScanPayload {
    target: string;
    options?: { scanType?: string; plugins?: string[] };
  }

  const currentScanIdRef = useRef<string | null>(null);
  const [scanResult, setScanResult] = useState<any | null>(null);
  const [progress, setProgress] = useState<number>(0);

  // Mutation to start scan via address / contract
  const {
    mutateAsync: _startScan,
    isPending: isStarting,
    error: startError,
  } = useMutation<{ scan_id: string; status: string }, Error, ScanPayload>({
    mutationFn: ({ target, options }) =>
      apiClient.post<{ scan_id: string; status: string }>(
        "/api/scanner/api/v1/scan",
        {
          target_type: "contract_address",
          target_identifier: target,
          scan_type: options?.scanType ?? "full",
          plugins: options?.plugins ?? undefined,
        },
        { headers: { Authorization: "Bearer scorpius-api-token" } },
      ),
    onSuccess: (data) => {
      currentScanIdRef.current = data.scan_id;
    },
  });

  // Mutation to upload file and start scan
  const {
    mutateAsync: _uploadScan,
    isPending: isUploading,
    error: uploadError,
  } = useMutation<{ scan_id: string; status: string }, Error, File>({
    mutationFn: (file) => {
      const formData = new FormData();
      formData.append("file", file);
      // backend expects target_type=file? Provide wrapper endpoint /scan with multipart
      return apiClient.post<{ scan_id: string; status: string }>(
        "/api/scanner/api/v1/scan",
        formData,
        {
          headers: {
            Authorization: "Bearer scorpius-api-token",
            "Content-Type": "multipart/form-data",
          },
        },
      );
    },
    onSuccess: (data) => {
      currentScanIdRef.current = data.scan_id;
    },
  });

  // WebSocket for progress updates
  useWebSocketHook("ws/scanner", {
    onMessage: (e) => {
      try {
        const msg = JSON.parse(e.data);
        if (
          msg.event === "scan_progress" &&
          msg.scan_id === currentScanIdRef.current
        ) {
          if (msg.progress !== undefined) {
            setProgress(msg.progress);
          }
          if (msg.status === "completed") {
            // Fetch final results
            apiClient
              .get(`/api/scanner/api/v1/scan/${msg.scan_id}/results`, {
                headers: { Authorization: "Bearer scorpius-api-token" },
              })
              .then((res) => setScanResult(res));
          }
        }
      } catch {}
    },
  });

  return {
    startScan: (
      target: string,
      opts?: { scanType?: string; plugins?: string[] },
    ) => _startScan({ target, options: opts }),
    uploadAndScan: (file: File) => _uploadScan(file),
    scanResult,
    progress,
    isScanning: isStarting || isUploading,
    error: startError || uploadError,
  };
};

export const useScannerResults = (limit = 10) =>
  useQuery({
    queryKey: ["scanner-results", limit],
    queryFn: () =>
      apiClient.get(`/api/scanner/api/v1/scans?limit=${limit}`, {
        headers: { Authorization: "Bearer scorpius-api-token" },
      }),
    refetchInterval: 60_000,
  });

// Honeypot hooks -----------------------------------------------------------
export const useHoneypotDetector = () => {
  interface DetectPayload {
    address: string;
  }

  const currentIdRef = useRef<string | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const [result, setResult] = useState<any | null>(null);

  const {
    mutateAsync: _startDetect,
    isPending,
    error,
  } = useMutation<
    { detection_id: string; status: string },
    Error,
    DetectPayload
  >({
    mutationFn: ({ address }) =>
      apiClient.post(
        "/api/honeypot/detect",
        { address },
        {
          headers: { Authorization: "Bearer scorpius-api-token" },
        },
      ),
    onSuccess: (data) => {
      currentIdRef.current = data.detection_id;
    },
  });

  // WebSocket subscription
  useWebSocketHook("ws/honeypot", {
    onMessage: (e) => {
      try {
        const msg = JSON.parse(e.data);
        if (msg.detection_id === currentIdRef.current) {
          if (msg.progress !== undefined) setProgress(msg.progress);
          if (msg.status === "completed") {
            apiClient
              .get(`/api/honeypot/${msg.detection_id}/results`, {
                headers: { Authorization: "Bearer scorpius-api-token" },
              })
              .then((res) => setResult(res));
          }
        }
      } catch {}
    },
  });

  return {
    startDetection: (address: string) => _startDetect({ address }),
    progress,
    result,
    isDetecting: isPending,
    error,
  };
};

export const useHoneypotResults = (limit = 10) =>
  useQuery({
    queryKey: ["honeypot-results", limit],
    queryFn: () =>
      apiClient.get(`/api/honeypot/history?limit=${limit}`, {
        headers: { Authorization: "Bearer scorpius-api-token" },
      }),
    refetchInterval: 60_000,
  });

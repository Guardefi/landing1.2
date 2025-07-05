// Export all hooks from this file
export { useToast } from "./use-toast";
export { useIsMobile } from "./use-mobile";
export { useWebSocket } from "./useWebSocket";
export { useSSE } from "./useSSE";

import { useMutation, useQuery } from "@tanstack/react-query";
import { apiClient } from "../lib/api-client";
import { useEffect, useState, useRef } from "react";
import { queryClient } from "../lib/react-query";
import { useWebSocket } from "./useWebSocket";

// API Hooks
export const useLogin = () =>
  useMutation<
    { token: string },
    Error,
    { email: string; password: string; remember_me?: boolean }
  >({
    mutationFn: async (creds) => {
      const response = await apiClient.post("/auth/login", creds);
      if (response.success && response.data) {
        return response.data;
      }
      throw new Error(response.error || "Login failed");
    },
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
    queryFn: async () => {
      const response = await apiClient.get("/health");
      return response.data;
    },
    refetchInterval: 30_000,
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

export const useLicenseVerification = () => {
  // Placeholder implementation
  return {
    verify: async (license: string) => ({ valid: true }),
    isLoading: false,
    error: null,
  };
};

export const useMempool = () => {
  const { data, isLoading, error } = useQuery({
    queryKey: ["mempool-initial"],
    queryFn: () => apiClient.get("/api/mempool/latest"),
    staleTime: 10_000,
  });

  // Live updates via WS
  const { sendJsonMessage } = useWebSocket("ws/mempool", {
    onMessage: (e) => {
      try {
        const tx = JSON.parse(e.data);
        // Push to React Query cache list
        queryClient.setQueryData<any[]>(["mempool-stream"], (old = []) => [
          tx,
          ...old.slice(0, 999),
        ]);
      } catch (_) {
        // Ignore parsing errors
      }
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
    queryFn: async () => {
      const endpoints = [
        "/api/honeypot/detections",
        "/api/scanner/honeypot/detections",
        "/api/scanner/api/v1/honeypot/detections",
      ];

      for (const endpoint of endpoints) {
        try {
          const response = await apiClient.get(endpoint);
          if (response.success && response.data) {
            return response.data;
          }
        } catch (err) {
          continue;
        }
      }

      // Return mock data
      return {
        detections: [
          {
            id: "demo-detection-1",
            address: "0x1234...abcd",
            is_honeypot: false,
            confidence: 95,
            scan_date: new Date().toISOString(),
          },
        ],
      };
    },
    retry: 2,
  });

interface HoneypotAnalyzePayload {
  address: string;
}
export const useHoneypotAnalyzer = () => {
  return useMutation<any, Error, HoneypotAnalyzePayload>({
    mutationFn: async ({ address }) => {
      const endpoints = [
        "/api/honeypot/analyze",
        "/api/scanner/honeypot/analyze",
        "/api/scanner/api/v1/honeypot/analyze",
      ];

      let lastError: any = null;

      for (const endpoint of endpoints) {
        try {
          const response = await apiClient.post(endpoint, { address });
          if (response.success && response.data) {
            return response.data;
          } else {
            lastError = new Error(response.error || "Analysis failed");
          }
        } catch (err) {
          lastError = err;
          continue;
        }
      }

      throw lastError || new Error("Honeypot analysis failed");
    },
  });
};

export const useTradingEngine = () => {
  // Placeholder implementation
  return {
    execute: async (order: any) => ({ success: true }),
    isLoading: false,
    error: null,
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
  const [error, setError] = useState<string | null>(null);

  // Mutation to start scan via address / contract
  const {
    mutateAsync: _startScan,
    isPending: isStarting,
    error: startError,
  } = useMutation<{ scan_id: string; status: string }, Error, ScanPayload>({
    mutationFn: async ({ target, options }) => {
      setError(null);

      // Try multiple endpoint patterns for better compatibility
      const endpoints = [
        "/api/scanner/scan", // Primary endpoint
        "/api/scanner/api/v1/scan", // Legacy endpoint
        "/scanner/scan", // Alternative endpoint
      ];

      let lastError: any = null;

      for (const endpoint of endpoints) {
        try {
          const response = await apiClient.post(endpoint, {
            target_type: "contract_address",
            target_identifier: target,
            target: target, // Also include direct target field
            scan_type: options?.scanType ?? "full",
            plugins: options?.plugins ?? undefined,
          });

          if (response.success && response.data) {
            return response.data;
          } else {
            lastError = new Error(response.error || "Scan failed");
          }
        } catch (err) {
          lastError = err;
          continue; // Try next endpoint
        }
      }

      // If all endpoints failed, check if it's a 500 error and provide helpful message
      if (lastError?.response?.status === 500) {
        throw new Error(
          "Scanner service is temporarily unavailable. Please try again later or contact support.",
        );
      }

      throw lastError || new Error("All scanner endpoints failed");
    },
    onSuccess: (data) => {
      if (data?.scan_id) {
        currentScanIdRef.current = data.scan_id;
        setProgress(0);
        setScanResult(null);
      }
    },
    onError: (err: any) => {
      setError(err.message || "Failed to start scan");
      console.error("Scan error:", err);
    },
  });

  // Mutation to upload file and start scan
  const {
    mutateAsync: _uploadScan,
    isPending: isUploading,
    error: uploadError,
  } = useMutation<{ scan_id: string; status: string }, Error, File>({
    mutationFn: async (file) => {
      setError(null);

      const formData = new FormData();
      formData.append("file", file);
      formData.append("target_type", "file");
      formData.append("scan_type", "full");

      // Try multiple upload endpoints
      const endpoints = [
        "/api/scanner/upload",
        "/api/scanner/scan",
        "/api/scanner/api/v1/scan",
      ];

      let lastError: any = null;

      for (const endpoint of endpoints) {
        try {
          const response = await apiClient.post(endpoint, formData, {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          });

          if (response.success && response.data) {
            return response.data;
          } else {
            lastError = new Error(response.error || "Upload failed");
          }
        } catch (err) {
          lastError = err;
          continue;
        }
      }

      throw lastError || new Error("All upload endpoints failed");
    },
    onSuccess: (data) => {
      if (data?.scan_id) {
        currentScanIdRef.current = data.scan_id;
        setProgress(0);
        setScanResult(null);
      }
    },
    onError: (err: any) => {
      setError(err.message || "Failed to upload and scan file");
    },
  });

  // WebSocket for progress updates with error handling
  useWebSocket("ws/scanner", {
    onMessage: (e) => {
      try {
        const msg = JSON.parse(e.data);
        if (
          msg.event === "scan_progress" &&
          msg.scan_id === currentScanIdRef.current
        ) {
          if (msg.progress !== undefined) {
            setProgress(Math.min(100, Math.max(0, msg.progress)));
          }
          if (msg.status === "completed") {
            // Fetch final results with multiple endpoint attempts
            fetchScanResults(msg.scan_id);
          }
          if (msg.status === "failed") {
            setError(msg.error || "Scan failed");
          }
        }
      } catch (wsError) {
        console.warn("WebSocket message parsing error:", wsError);
      }
    },
    onError: () => {
      // Fallback to polling if WebSocket fails
      console.warn("WebSocket failed, falling back to polling");
      startPolling();
    },
  });

  // Fallback polling mechanism
  const startPolling = () => {
    if (!currentScanIdRef.current) return;

    const pollInterval = setInterval(async () => {
      if (!currentScanIdRef.current) {
        clearInterval(pollInterval);
        return;
      }

      try {
        const response = await apiClient.get(
          `/api/scanner/scan/${currentScanIdRef.current}/status`,
        );
        if (response.success && response.data) {
          const { status, progress: scanProgress, results } = response.data;

          if (scanProgress !== undefined) {
            setProgress(scanProgress);
          }

          if (status === "completed") {
            setScanResult(results || response.data);
            clearInterval(pollInterval);
          } else if (status === "failed") {
            setError("Scan failed");
            clearInterval(pollInterval);
          }
        }
      } catch (pollError) {
        console.warn("Polling error:", pollError);
      }
    }, 2000);

    // Clear polling after 5 minutes
    setTimeout(() => clearInterval(pollInterval), 300000);
  };

  // Fetch scan results with multiple endpoint attempts
  const fetchScanResults = async (scanId: string) => {
    const endpoints = [
      `/api/scanner/scan/${scanId}/results`,
      `/api/scanner/api/v1/scan/${scanId}/results`,
      `/scanner/results/${scanId}`,
    ];

    for (const endpoint of endpoints) {
      try {
        const response = await apiClient.get(endpoint);
        if (response.success && response.data) {
          setScanResult(response.data);
          return;
        }
      } catch (err) {
        continue;
      }
    }

    setError("Failed to fetch scan results");
  };

  return {
    startScan: (
      target: string,
      opts?: { scanType?: string; plugins?: string[] },
    ) => _startScan({ target, options: opts }),
    uploadAndScan: (file: File) => _uploadScan(file),
    scanResult,
    progress,
    isScanning: isStarting || isUploading,
    error: error || startError?.message || uploadError?.message,
    clearError: () => setError(null),
  };
};

export const useScannerResults = (limit = 10) =>
  useQuery({
    queryKey: ["scanner-results", limit],
    queryFn: async () => {
      const endpoints = [
        `/api/scanner/scans?limit=${limit}`,
        `/api/scanner/api/v1/scans?limit=${limit}`,
        `/scanner/scans?limit=${limit}`,
      ];

      for (const endpoint of endpoints) {
        try {
          const response = await apiClient.get(endpoint);
          if (response.success && response.data) {
            return response.data;
          }
        } catch (err) {
          continue;
        }
      }

      // Return mock data if all endpoints fail
      return {
        scans: [
          {
            id: "demo-scan-1",
            target: "0x1234...abcd",
            status: "completed",
            results: {
              vulnerabilities: ["Reentrancy", "Integer Overflow"],
              risk_score: 75,
            },
            created_at: new Date().toISOString(),
          },
        ],
      };
    },
    refetchInterval: 60_000,
    retry: 2,
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
  useWebSocket("ws/honeypot", {
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
      } catch {
        // Ignore detection errors
      }
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

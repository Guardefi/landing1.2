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
    queryFn: async () => {
      try {
        return await apiClient.getMempoolData();
      } catch (err) {
        console.error("Failed to fetch mempool data:", err);
        return { transactions: [] };
      }
    },
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
    transactions: [...(data?.transactions ?? []), ...transactions],
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
      try {
        const response = await apiClient.getHoneypotDetections();
        return response;
      } catch (err) {
        console.error("Failed to fetch honeypot detections:", err);

        // Return mock data if backend is unavailable
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
      }
    },
    retry: 2,
  });

interface HoneypotAnalyzePayload {
  address: string;
}
export const useHoneypotAnalyzer = () => {
  return useMutation<any, Error, HoneypotAnalyzePayload>({
    mutationFn: async ({ address }) => {
      try {
        const response = await apiClient.analyzeHoneypot(address);
        return response;
      } catch (err: any) {
        console.error("Honeypot analysis error:", err);

        if (err.response?.status === 404) {
          throw new Error(
            "Honeypot service not available. Please ensure backend services are running.",
          );
        }

        throw new Error(err.message || "Honeypot analysis failed");
      }
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

      try {
        // Use the enhanced API client method
        const response = await apiClient.scanContract(target, options);

        if (response && (response.scan_id || response.id)) {
          return {
            scan_id: response.scan_id || response.id,
            status: response.status || "started",
          };
        }

        throw new Error("Invalid response from scanner service");
      } catch (err: any) {
        console.error("Scanner API Error:", err);

        if (err.response?.status === 500) {
          throw new Error(
            "Scanner service is temporarily unavailable. Please try again later or contact support.",
          );
        }

        if (err.response?.status === 404) {
          throw new Error(
            "Scanner service not found. Please ensure the backend services are running.",
          );
        }

        throw new Error(err.message || "Failed to start vulnerability scan");
      }
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

      try {
        // Use the enhanced API client method
        const response = await apiClient.uploadAndScan(file, {
          scanType: "full",
        });

        if (response && (response.scan_id || response.id)) {
          return {
            scan_id: response.scan_id || response.id,
            status: response.status || "started",
          };
        }

        throw new Error("Invalid response from scanner service");
      } catch (err: any) {
        console.error("Scanner Upload Error:", err);

        if (err.response?.status === 413) {
          throw new Error("File too large. Please upload a smaller file.");
        }

        if (err.response?.status === 415) {
          throw new Error(
            "Unsupported file type. Please upload a Solidity (.sol) file.",
          );
        }

        throw new Error(err.message || "Failed to upload and scan file");
      }
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

  // Fetch scan results using enhanced API client
  const fetchScanResults = async (scanId: string) => {
    try {
      const response = await apiClient.getScanResults(scanId);
      setScanResult(response);
    } catch (err: any) {
      console.error("Failed to fetch scan results:", err);
      setError("Failed to fetch scan results");
    }
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
      try {
        const response = await apiClient.getRecentScans(limit);
        return response;
      } catch (err) {
        console.error("Failed to fetch scanner results:", err);

        // Return mock data if backend is unavailable (for development)
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
      }
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

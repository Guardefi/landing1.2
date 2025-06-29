// Export all hooks from this file
export { useToast } from './use-toast';
export { useIsMobile } from './use-mobile';
export { useWebSocket } from './useWebSocket';
export { useSSE } from './useSSE';

import { useMutation, useQuery } from '@tanstack/react-query';
import apiClient from '../lib/api';
import { useEffect, useState, useRef } from 'react';
import { queryClient } from '../lib/react-query';
import { useWebSocket } from './useWebSocket'; // local import for hook usage

// API Hooks
export const useLogin = () =>
  useMutation<{ token: string }, Error, { email: string; password: string; remember_me?: boolean }>({
    mutationFn: (creds) => apiClient.post<{ token: string }>('/auth/login', creds),
  });

export const useBiometricLogin = () => {
  // Placeholder implementation
  return {
    login: async () => ({ success: true }),
    isAvailable: false,
    isLoading: false
  };
};

export const useSystemStatus = () =>
  useQuery({
    queryKey: ['system-status'],
    queryFn: () => apiClient.get('/health'),
    refetchInterval: 30_000,
  });

export const useLicenseVerification = () => {
  // Placeholder implementation
  return {
    verify: async (license: string) => ({ valid: true }),
    isLoading: false,
    error: null
  };
};

export const useMempool = () => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['mempool-initial'],
    queryFn: () => apiClient.get('/api/mempool/latest'),
    staleTime: 10_000,
  });

  // Live updates via WS
  const { sendJsonMessage } = useWebSocket('ws/mempool', {
    onMessage: (e) => {
      try {
        const tx = JSON.parse(e.data);
        // Push to React Query cache list
        queryClient.setQueryData<any[]>(['mempool-stream'], (old = []) => [tx, ...old.slice(0, 999)]);
      } catch (_) {}
    },
  });

  useEffect(() => {
    // Optionally request backfill or ping
    sendJsonMessage({ type: 'ping' });
  }, [sendJsonMessage]);

  const transactions = useQuery({
    queryKey: ['mempool-stream'],
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
    refresh: () => {}
  };
};

export const useScannerAPI = () => {
  // Placeholder implementation
  return {
    scan: async (contract: string) => ({ results: [] }),
    isLoading: false,
    error: null
  };
};

export const useHoneypotDetection = () =>
  useQuery({
    queryKey: ['honeypot-detections'],
    queryFn: () => apiClient.get('/api/scanner/api/v1/honeypot/detections'),
    enabled: false, // placeholder until backend ready
  });

interface HoneypotAnalyzePayload { address: string }
export const useHoneypotAnalyzer = () => {
  return useMutation<any, Error, HoneypotAnalyzePayload>({
    mutationFn: ({ address }) =>
      apiClient.post('/api/scanner/api/v1/honeypot/analyze', { address }),
  });
};

export const useTradingEngine = () => {
  // Placeholder implementation
  return {
    execute: async (order: any) => ({ success: true }),
    isLoading: false,
    error: null
  };
};

export const useWalletCheck = () =>
  useMutation<any, Error, { address: string }>({
    mutationFn: (payload) => apiClient.post('/api/wallet/check', payload),
  });

export const useWalletRevoke = () =>
  useMutation<any, Error, { address: string; token_contract: string; spender: string }>({
    mutationFn: (payload) => apiClient.post('/api/wallet/revoke', payload),
  });

export const useTeamChat = () => {
  // Placeholder implementation
  return {
    messages: [],
    send: async (message: string) => ({ success: true }),
    isLoading: false,
    error: null
  };
};

export const useNotifications = () => {
  // Placeholder implementation
  return {
    notifications: [],
    markAsRead: async (id: string) => ({ success: true }),
    isLoading: false,
    error: null
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
  const { mutateAsync: _startScan, isPending: isStarting, error: startError } = useMutation<
    { scan_id: string; status: string },
    Error,
    ScanPayload
  >({
    mutationFn: ({ target, options }) =>
      apiClient.post<{ scan_id: string; status: string }>(
        '/api/scanner/api/v1/scan',
        {
          target_type: 'contract_address',
          target_identifier: target,
          scan_type: options?.scanType ?? 'full',
          plugins: options?.plugins ?? undefined,
        },
        { headers: { Authorization: 'Bearer scorpius-api-token' } },
      ),
    onSuccess: (data) => {
      currentScanIdRef.current = data.scan_id;
    },
  });

  // Mutation to upload file and start scan
  const { mutateAsync: _uploadScan, isPending: isUploading, error: uploadError } = useMutation<
    { scan_id: string; status: string },
    Error,
    File
  >({
    mutationFn: (file) => {
      const formData = new FormData();
      formData.append('file', file);
      // backend expects target_type=file? Provide wrapper endpoint /scan with multipart
      return apiClient.post<{ scan_id: string; status: string }>(
        '/api/scanner/api/v1/scan',
        formData,
        {
          headers: { Authorization: 'Bearer scorpius-api-token', 'Content-Type': 'multipart/form-data' },
        },
      );
    },
    onSuccess: (data) => {
      currentScanIdRef.current = data.scan_id;
    },
  });

  // WebSocket for progress updates
  useWebSocket('ws/scanner', {
    onMessage: (e) => {
      try {
        const msg = JSON.parse(e.data);
        if (msg.event === 'scan_progress' && msg.scan_id === currentScanIdRef.current) {
          if (msg.progress !== undefined) {
            setProgress(msg.progress);
          }
          if (msg.status === 'completed') {
            // Fetch final results
            apiClient
              .get(`/api/scanner/api/v1/scan/${msg.scan_id}/results`, {
                headers: { Authorization: 'Bearer scorpius-api-token' },
              })
              .then((res) => setScanResult(res));
          }
        }
      } catch {}
    },
  });

  return {
    startScan: (target: string, opts?: { scanType?: string; plugins?: string[] }) =>
      _startScan({ target, options: opts }),
    uploadAndScan: (file: File) => _uploadScan(file),
    scanResult,
    progress,
    isScanning: isStarting || isUploading,
    error: startError || uploadError,
  };
};

export const useScannerResults = (limit = 10) =>
  useQuery({
    queryKey: ['scanner-results', limit],
    queryFn: () =>
      apiClient.get(`/api/scanner/api/v1/scans?limit=${limit}`, {
        headers: { Authorization: 'Bearer scorpius-api-token' },
      }),
    refetchInterval: 60_000,
  });

// Honeypot hooks -----------------------------------------------------------
export const useHoneypotDetector = () => {
  interface DetectPayload { address: string }

  const currentIdRef = useRef<string | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const [result, setResult] = useState<any | null>(null);

  const { mutateAsync: _startDetect, isPending, error } = useMutation<
    { detection_id: string; status: string },
    Error,
    DetectPayload
  >({
    mutationFn: ({ address }) =>
      apiClient.post('/api/honeypot/detect', { address }, {
        headers: { Authorization: 'Bearer scorpius-api-token' },
      }),
    onSuccess: (data) => {
      currentIdRef.current = data.detection_id;
    },
  });

  // WebSocket subscription
  useWebSocket('ws/honeypot', {
    onMessage: (e) => {
      try {
        const msg = JSON.parse(e.data);
        if (msg.detection_id === currentIdRef.current) {
          if (msg.progress !== undefined) setProgress(msg.progress);
          if (msg.status === 'completed') {
            apiClient.get(`/api/honeypot/${msg.detection_id}/results`, {
              headers: { Authorization: 'Bearer scorpius-api-token' },
            }).then((res) => setResult(res));
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
    queryKey: ['honeypot-results', limit],
    queryFn: () =>
      apiClient.get(`/api/honeypot/history?limit=${limit}`, {
        headers: { Authorization: 'Bearer scorpius-api-token' },
      }),
    refetchInterval: 60_000,
  }); 
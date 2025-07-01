/**
 * Scanner API Hook
 * Connects the Scanner frontend to the backend API
 */

import { useState, useCallback } from 'react';

export interface ScanRequest {
  target: string;
  rpc_url?: string;
  block_number?: number;
  plugins?: string[];
  enable_simulation?: boolean;
}

export interface ScanResponse {
  scan_id: string;
  status: string;
  message: string;
}

export interface ScanResult {
  scan_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  target: string;
  findings: Array<{
    id: string;
    severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
    title: string;
    description: string;
    file?: string;
    line?: number;
    confidence: number;
  }>;
  metadata: {
    scan_time: number;
    engine: string;
    plugins_used: string[];
    total_findings: number;
  };
  created_at: string;
  completed_at?: string;
}

export interface ScannerHealth {
  status: string;
  external_scanner: boolean;
  active_scans: number;
  total_scans: number;
}

export interface ScanPlugin {
  name: string;
  description: string;
  category: string;
}

export interface ScanListItem {
  scan_id: string;
  target: string;
  status: string;
  created_at: string;
  findings_count: number;
}

const API_BASE = 'http://localhost:8000/api/scanner';

export const useScannerAPI = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getHeaders = () => ({
    'Content-Type': 'application/json',
    // Add auth token if available
    ...(localStorage.getItem('scorpius_token') && {
      Authorization: `Bearer ${localStorage.getItem('scorpius_token')}`,
    }),
  });

  const handleApiResponse = async (response: Response) => {
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} - ${response.statusText}`);
    }
    return response.json();
  };

  // Get scanner health status
  const getHealth = useCallback(async (): Promise<ScannerHealth> => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE}/health`, {
        headers: getHeaders(),
      });

      return await handleApiResponse(response);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to get scanner health';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Get available plugins
  const getPlugins = useCallback(async (): Promise<ScanPlugin[]> => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE}/plugins`, {
        headers: getHeaders(),
      });

      return await handleApiResponse(response);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get plugins';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Start a new scan
  const startScan = useCallback(
    async (scanRequest: ScanRequest): Promise<ScanResponse> => {
      try {
        setIsLoading(true);
        setError(null);

        const response = await fetch(`${API_BASE}/scan`, {
          method: 'POST',
          headers: getHeaders(),
          body: JSON.stringify(scanRequest),
        });

        return await handleApiResponse(response);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : 'Failed to start scan';
        setError(errorMessage);
        throw new Error(errorMessage);
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  // Get scan results
  const getScanResults = useCallback(async (scanId: string): Promise<ScanResult> => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE}/scan/${scanId}`, {
        headers: getHeaders(),
      });

      return await handleApiResponse(response);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to get scan results';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Get all scans
  const getAllScans = useCallback(async (): Promise<ScanListItem[]> => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE}/scans`, {
        headers: getHeaders(),
      });

      return await handleApiResponse(response);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get scans';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Stop a running scan
  const stopScan = useCallback(async (scanId: string): Promise<{ message: string }> => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE}/scan/${scanId}`, {
        method: 'DELETE',
        headers: getHeaders(),
      });

      return await handleApiResponse(response);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to stop scan';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    isLoading,
    error,
    getHealth,
    getPlugins,
    startScan,
    getScanResults,
    getAllScans,
    stopScan,
  };
};

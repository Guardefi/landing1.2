import { useState, useEffect, useCallback } from 'react';
import { useRealtimeData } from '@/services/websocket';
import { fallbackData } from '@/services/fallbackData';

// Generic hook for API data with loading states and fallback support
export const useAPIData = <T>(
  apiCall: () => Promise<T>,
  dependencies: any[] = [],
  realTimeChannel?: string,
  fallbackDataKey?: keyof typeof fallbackData,
) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isUsingFallback, setIsUsingFallback] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiCall();
      setData(result);
      setIsUsingFallback(false);
    } catch (err) {
      console.warn(
        'API Error, attempting to use fallback data:',
        err instanceof Error ? err.message : 'Unknown error',
      );

      // Try to use fallback data if available
      if (fallbackDataKey && fallbackData[fallbackDataKey]) {
        setData(fallbackData[fallbackDataKey] as T);
        setIsUsingFallback(true);
        setError(null); // Clear error when using fallback
      } else {
        setError(err instanceof Error ? err.message : 'An error occurred');
        setIsUsingFallback(false);
      }
    } finally {
      setLoading(false);
    }
  }, dependencies);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Subscribe to real-time updates if channel provided
  useEffect(() => {
    if (realTimeChannel && !isUsingFallback) {
      const unsubscribe = useRealtimeData[
        realTimeChannel as keyof typeof useRealtimeData
      ]?.((newData: T) => {
        setData(newData);
      });
      return unsubscribe;
    }
  }, [realTimeChannel, isUsingFallback]);

  return { data, loading, error, isUsingFallback, refetch: fetchData };
};

// Specific hooks for different data types
export const useDashboardStats = () => {
  return useAPIData(
    async () => {
      const response = await fetch('/api/dashboard/stats');
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    },
    [],
    'dashboardStats',
    'dashboardStats',
  );
};

export const useMEVStrategies = () => {
  return useAPIData(
    async () => {
      const response = await fetch('/api/mev/strategies');
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    },
    [],
    'mevOpportunities',
    'mevOpportunities',
  );
};

export const useMempoolData = () => {
  return useAPIData(
    async () => {
      const response = await fetch('/api/mempool/live');
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    },
    [],
    'mempoolData',
    'mempoolData',
  );
};

export const useSecurityAlerts = () => {
  return useAPIData(
    async () => {
      const response = await fetch('/api/mempool/alerts');
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    },
    [],
    'securityAlerts',
    'securityThreats',
  );
};

export const useSystemHealth = () => {
  return useAPIData(
    async () => {
      const response = await fetch('/api/system/health');
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    },
    [],
    'systemHealth',
    'systemHealth',
  );
};

export const useContractScan = (contractAddress: string | null) => {
  return useAPIData(
    async () => {
      if (!contractAddress) return null;
      const response = await fetch('/api/scanner/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contract_address: contractAddress }),
      });
      return response.json();
    },
    [contractAddress],
    'scanResults',
  );
};

// Hook for mutations (POST, PUT, DELETE operations)
export const useAPIMutation = <T, P>(mutationFn: (params: P) => Promise<T>) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const mutate = useCallback(
    async (params: P): Promise<T | null> => {
      try {
        setLoading(true);
        setError(null);
        const result = await mutationFn(params);
        return result;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Mutation failed';
        setError(errorMessage);
        console.error('Mutation Error:', err);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [mutationFn],
  );

  return { mutate, loading, error };
};

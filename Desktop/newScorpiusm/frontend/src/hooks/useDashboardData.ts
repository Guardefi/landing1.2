/**
 * Dashboard Data Hook
 * Connects to the backend API to fetch real system stats with fallback to mock data
 */

import { useState, useEffect, useRef } from 'react';
import { fallbackData } from '@/services/fallbackData';

export interface DashboardData {
  timestamp: string;
  cpu: number;
  mem: number;
  mem_available_gb: number;
  mem_total_gb: number;
  disk: {
    total_gb: number;
    used_gb: number;
    free_gb: number;
    percent: number;
  };
  network: {
    bytes_sent: number;
    bytes_recv: number;
    packets_sent: number;
    packets_recv: number;
  };
  uptime_seconds: number;
  history: {
    cpu: Array<{ timestamp: string; value: number }>;
    memory: Array<{ timestamp: string; value: number }>;
  };
}

// Transform fallback data to match expected interface
const generateMockDashboardData = (): DashboardData => {
  const health = fallbackData.systemHealth;
  return {
    timestamp: new Date().toISOString(),
    cpu: health.cpu_usage,
    mem: health.memory_usage,
    mem_available_gb: 8 - (health.memory_usage / 100) * 8,
    mem_total_gb: 8,
    disk: {
      total_gb: 100,
      used_gb: health.storage_usage,
      free_gb: 100 - health.storage_usage,
      percent: health.storage_usage,
    },
    network: {
      bytes_sent: Math.floor(Math.random() * 1000000),
      bytes_recv: Math.floor(Math.random() * 1000000),
      packets_sent: Math.floor(Math.random() * 10000),
      packets_recv: Math.floor(Math.random() * 10000),
    },
    uptime_seconds: 72 * 3600 + 15 * 60, // 72h 15m in seconds
    history: {
      cpu: Array.from({ length: 10 }, (_, i) => ({
        timestamp: new Date(Date.now() - (9 - i) * 60000).toISOString(),
        value: Math.floor(Math.random() * 30) + 20,
      })),
      memory: Array.from({ length: 10 }, (_, i) => ({
        timestamp: new Date(Date.now() - (9 - i) * 60000).toISOString(),
        value: Math.floor(Math.random() * 40) + 40,
      })),
    },
  };
};

export const useDashboardData = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isUsingFallback, setIsUsingFallback] = useState(false);
  const failureCount = useRef(0);
  const maxConsecutiveFailures = 3;

  const fetchData = async () => {
    try {
      setLoading(true);

      // Only try API if we haven't had too many consecutive failures
      if (failureCount.current < maxConsecutiveFailures) {
        const response = await fetch('http://localhost:8000/api/dashboard/stats', {
          timeout: 5000, // 5 second timeout
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        setData(result);
        setError(null);
        setIsUsingFallback(false);
        failureCount.current = 0; // Reset failure count on success
        return;
      }
    } catch (err) {
      failureCount.current += 1;

      // Only log error on first few failures to avoid spam
      if (failureCount.current <= 2) {
        console.warn(
          'Dashboard API unavailable, using fallback data:',
          err instanceof Error ? err.message : 'Unknown error',
        );
      }
    }

    // Use fallback data
    setData(generateMockDashboardData());
    setIsUsingFallback(true);
    setError(null); // Clear error when using fallback
    setLoading(false);
  };

  useEffect(() => {
    fetchData();

    // Set up periodic refresh with dynamic interval based on failures
    const getRefreshInterval = () => {
      if (failureCount.current >= maxConsecutiveFailures) {
        return 60000; // 1 minute when using fallback
      }
      return 30000; // 30 seconds when API is working
    };

    const setupInterval = () => {
      const interval = setInterval(() => {
        fetchData();
      }, getRefreshInterval());

      return interval;
    };

    const interval = setupInterval();

    return () => clearInterval(interval);
  }, []);

  return {
    data,
    loading,
    error,
    isUsingFallback,
    refresh: fetchData,
  };
};

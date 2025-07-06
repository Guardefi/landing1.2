import { useState, useEffect } from "react";
import { StorageManager } from "@/lib/storage";

interface Stats {
  scanStats: {
    threatsDetected: number;
    totalScans: number;
    criticalIssues: number;
  };
  tradingStats: {
    totalProfit: number;
    successfulTrades: number;
    totalTrades: number;
  };
}

export const usePersistedStats = () => {
  const [stats, setStats] = useState<Stats>({
    scanStats: {
      threatsDetected: 0,
      totalScans: 0,
      criticalIssues: 0,
    },
    tradingStats: {
      totalProfit: 0,
      successfulTrades: 0,
      totalTrades: 0,
    },
  });

  const [isAvailable, setIsAvailable] = useState(false);

  useEffect(() => {
    // Load stats from storage
    const scanStats = StorageManager.getScanStats();
    const tradingStats = StorageManager.getTradingStats();

    setStats({
      scanStats: {
        threatsDetected: scanStats.vulnerabilitiesFound || 0,
        totalScans: scanStats.totalScans || 0,
        criticalIssues: scanStats.criticalIssues || 0,
      },
      tradingStats: {
        totalProfit: tradingStats.profitLoss || 0,
        successfulTrades: tradingStats.successfulTrades || 0,
        totalTrades: tradingStats.totalTrades || 0,
      },
    });

    setIsAvailable(true);
  }, []);

  const refreshStats = () => {
    const scanStats = StorageManager.getScanStats();
    const tradingStats = StorageManager.getTradingStats();

    setStats({
      scanStats: {
        threatsDetected: scanStats.vulnerabilitiesFound || 0,
        totalScans: scanStats.totalScans || 0,
        criticalIssues: scanStats.criticalIssues || 0,
      },
      tradingStats: {
        totalProfit: tradingStats.profitLoss || 0,
        successfulTrades: tradingStats.successfulTrades || 0,
        totalTrades: tradingStats.totalTrades || 0,
      },
    });
  };

  return { 
    stats, 
    isAvailable, 
    refreshStats 
  };
};

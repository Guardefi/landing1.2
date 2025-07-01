import { useState, useEffect } from "react";
import {
  StorageManager,
  ScanStats,
  TradingStats,
  MempoolStats,
  ReportStats,
} from "@/lib/storage";

export interface AllStats {
  scanStats: ScanStats;
  tradingStats: TradingStats;
  mempoolStats: MempoolStats;
  reportStats: ReportStats;
}

export const usePersistedStats = () => {
  const [stats, setStats] = useState<AllStats>(() => ({
    scanStats: StorageManager.getScanStats(),
    tradingStats: StorageManager.getTradingStats(),
    mempoolStats: StorageManager.getMempoolStats(),
    reportStats: StorageManager.getReportStats(),
  }));

  const refreshStats = () => {
    setStats({
      scanStats: StorageManager.getScanStats(),
      tradingStats: StorageManager.getTradingStats(),
      mempoolStats: StorageManager.getMempoolStats(),
      reportStats: StorageManager.getReportStats(),
    });
  };

  // Listen for storage changes
  useEffect(() => {
    const handleStorageChange = () => {
      refreshStats();
    };

    window.addEventListener("storage", handleStorageChange);

    // Custom event for internal storage updates
    window.addEventListener("scorpius-stats-updated", handleStorageChange);

    return () => {
      window.removeEventListener("storage", handleStorageChange);
      window.removeEventListener("scorpius-stats-updated", handleStorageChange);
    };
  }, []);

  const incrementScan = (scanData: ScanStats["scanHistory"][0]) => {
    StorageManager.incrementScanCount(scanData);
    refreshStats();
    window.dispatchEvent(new CustomEvent("scorpius-stats-updated"));
  };

  const incrementTrading = (profit: number, value: number) => {
    StorageManager.incrementTradingStats(profit, value);
    refreshStats();
    window.dispatchEvent(new CustomEvent("scorpius-stats-updated"));
  };

  const incrementMempool = () => {
    StorageManager.incrementMempoolActivity();
    refreshStats();
    window.dispatchEvent(new CustomEvent("scorpius-stats-updated"));
  };

  const incrementReport = (generationTime: number) => {
    StorageManager.incrementReportGeneration(generationTime);
    refreshStats();
    window.dispatchEvent(new CustomEvent("scorpius-stats-updated"));
  };

  return {
    stats,
    refreshStats,
    incrementScan,
    incrementTrading,
    incrementMempool,
    incrementReport,

    // Individual getters for convenience
    scanStats: stats.scanStats,
    tradingStats: stats.tradingStats,
    mempoolStats: stats.mempoolStats,
    reportStats: stats.reportStats,
  };
};

export default usePersistedStats;

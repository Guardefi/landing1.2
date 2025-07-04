import { storageService, StorageData } from "../services/storageService";

// Extend these interfaces if you want extra fields from the feature branch
export interface ScanStats {
  id?: string; // optional, for backward compatibility
  contractAddress?: string;
  timestamp?: string;
  findings: number;
  riskScore?: number;
  totalScans: number;
  vulnerabilitiesFound: number;
  criticalIssues: number;
  threatsDetected: number;
  contractsAnalyzed: number;
  lastScanDate?: string | null;
}

export interface TradingStats {
  totalProfit: number;
  successfulTrades: number;
  totalTrades: number;
  attacksPrevented: number;
  valueSaved: number;
  lastTradeDate?: string | null;
}

// Add these only if you use them elsewhere in your app
export interface MempoolStats {
  transactionsMonitored: number;
  averageGasPrice: number;
  totalValue: number;
  contractsTracked: number;
  threatsDetected: number;
  lastActivityDate: string | null;
}

export interface ReportStats {
  totalReports: number;
  reportsToday: number;
  averageGenerationTime: number;
  totalDownloads: number;
  lastReportDate: string | null;
}

export interface SystemConfig {
  openaiApiKey: string;
  anthropicApiKey: string;
  slitherApiKey: string;
  mythxApiKey: string;
  mantecoreApiKey: string;
  mythrilApiKey: string;
  ethereumRpc: string;
  polygonRpc: string;
  bscRpc: string;
  arbitrumRpc: string;
  optimismRpc: string;
  avalancheRpc: string;
  privateKey: string;
  walletAddress: string;
  emailNotifications: boolean;
  emailAddress: string;
  slackWebhook: string;
  slackChannel: string;
  telegramBotToken: string;
  telegramChatId: string;
  discordWebhook: string;
  autoScan: boolean;
  realTimeMonitoring: boolean;
  advancedLogging: boolean;
  apiRateLimit: number;
  maxConcurrentScans: number;
}

interface StatsPayload {
  scanStats: ScanStats;
  tradingStats: TradingStats;
  // Optionally: mempoolStats: MempoolStats; reportStats: ReportStats;
}

const STATS_KEY = "scorpius_stats";
const CONFIG_KEY = "scorpius_config";

const DEFAULT_STATS: StatsPayload = {
  scanStats: {
    findings: 0,
    riskScore: 0,
    totalScans: 0,
    vulnerabilitiesFound: 0,
    criticalIssues: 0,
    threatsDetected: 0,
    contractsAnalyzed: 0,
    lastScanDate: null,
  },
  tradingStats: {
    totalProfit: 0,
    successfulTrades: 0,
    totalTrades: 0,
    attacksPrevented: 0,
    valueSaved: 0,
    lastTradeDate: null,
  },
};

const DEFAULT_CONFIG: SystemConfig = {
  openaiApiKey: "",
  anthropicApiKey: "",
  slitherApiKey: "",
  mythxApiKey: "",
  mantecoreApiKey: "",
  mythrilApiKey: "",
  ethereumRpc: "",
  polygonRpc: "",
  bscRpc: "",
  arbitrumRpc: "",
  optimismRpc: "",
  avalancheRpc: "",
  privateKey: "",
  walletAddress: "",
  emailNotifications: false,
  emailAddress: "",
  slackWebhook: "",
  slackChannel: "",
  telegramBotToken: "",
  telegramChatId: "",
  discordWebhook: "",
  autoScan: false,
  realTimeMonitoring: false,
  advancedLogging: false,
  apiRateLimit: 100,
  maxConcurrentScans: 3,
};

class StorageManagerClass {
  private static loadStats(): StatsPayload {
    try {
      const raw = localStorage.getItem(STATS_KEY);
      if (raw) return { ...DEFAULT_STATS, ...JSON.parse(raw) };
    } catch {}
    return { ...DEFAULT_STATS };
  }

  private static saveStats(payload: StatsPayload) {
    localStorage.setItem(STATS_KEY, JSON.stringify(payload));
  }

  static getScanStats(): ScanStats {
    return this.loadStats().scanStats;
  }

  static incrementScanCount(scan: Partial<ScanStats>): void {
    const stats = this.loadStats();
    stats.scanStats.totalScans += 1;
    stats.scanStats.contractsAnalyzed += 1;
    const findings = scan.findings || 0;
    stats.scanStats.vulnerabilitiesFound += findings;
    stats.scanStats.lastScanDate = scan.timestamp || new Date().toISOString();
    if (findings > 0) stats.scanStats.threatsDetected += 1;
    if ((scan.riskScore || 0) >= 8) stats.scanStats.criticalIssues += 1;
    this.saveStats(stats);
    try {
      storageService.addItem("scanner" as keyof StorageData, "scanHistory", scan);
    } catch {}
  }

  static getTradingStats(): TradingStats {
    return this.loadStats().tradingStats;
  }

  static incrementTradingStats(trade: Partial<TradingStats>): void {
    const stats = this.loadStats();
    stats.tradingStats.totalTrades += 1;
    if (trade.totalProfit && trade.totalProfit > 0) {
      stats.tradingStats.successfulTrades += 1;
      stats.tradingStats.totalProfit += trade.totalProfit;
    }
    if (trade.attacksPrevented) {
      stats.tradingStats.attacksPrevented += trade.attacksPrevented;
    }
    if (trade.valueSaved) {
      stats.tradingStats.valueSaved += trade.valueSaved;
    }
    stats.tradingStats.lastTradeDate = new Date().toISOString();
    this.saveStats(stats);
  }

  static getSystemConfig(): SystemConfig {
    try {
      const raw = localStorage.getItem(CONFIG_KEY);
      if (raw) return { ...DEFAULT_CONFIG, ...JSON.parse(raw) };
    } catch {}
    return { ...DEFAULT_CONFIG };
  }

  static setSystemConfig(config: Partial<SystemConfig>): void {
    const current = this.getSystemConfig();
    const updated = { ...current, ...config };
    localStorage.setItem(CONFIG_KEY, JSON.stringify(updated));
  }

  static exportData(): any {
    return {
      stats: this.loadStats(),
      config: this.getSystemConfig(),
      timestamp: new Date().toISOString(),
    };
  }

  static importData(data: any): boolean {
    try {
      if (data.stats) {
        this.saveStats(data.stats);
      }
      if (data.config) {
        this.setSystemConfig(data.config);
      }
      return true;
    } catch {
      return false;
    }
  }

  static clearAll(): void {
    localStorage.removeItem(STATS_KEY);
    localStorage.removeItem(CONFIG_KEY);
  }
}

export const StorageManager = StorageManagerClass;

export const loadInitialConfig = (): SystemConfig => {
  const config = StorageManager.getSystemConfig();
  // Ensure config is saved to localStorage
  StorageManager.setSystemConfig(config);
  return config;
};

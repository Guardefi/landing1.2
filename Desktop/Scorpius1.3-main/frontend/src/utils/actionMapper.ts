import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";

// Comprehensive mapping of UI actions to API endpoints
export class ActionMapper {
  // Scanner Actions
  static async scanContract(address: string, options?: any) {
    try {
      const result = await apiClient.scanContract(address, options);
      toast.success("Contract scan initiated");
      return result;
    } catch (error) {
      toast.error("Failed to initiate contract scan");
      throw error;
    }
  }

  static async uploadAndScanFile(file: File) {
    try {
      const result = await apiClient.uploadAndScan(file);
      toast.success("File uploaded and scan initiated");
      return result;
    } catch (error) {
      toast.error("Failed to upload and scan file");
      throw error;
    }
  }

  static async getScanResults(scanId: string) {
    try {
      return await apiClient.getScanResults(scanId);
    } catch (error) {
      toast.error("Failed to fetch scan results");
      throw error;
    }
  }

  // Honeypot Actions
  static async detectHoneypot(address: string) {
    try {
      const result = await apiClient.detectHoneypot(address);
      toast.success("Honeypot detection initiated");
      return result;
    } catch (error) {
      toast.error("Failed to detect honeypot");
      throw error;
    }
  }

  static async analyzeHoneypot(address: string) {
    try {
      const result = await apiClient.analyzeHoneypot(address);
      toast.success("Honeypot analysis completed");
      return result;
    } catch (error) {
      toast.error("Failed to analyze honeypot");
      throw error;
    }
  }

  // Bridge Actions
  static async initiateBridgeTransfer(
    fromChain: string,
    toChain: string,
    amount: string,
    token: string,
  ) {
    try {
      const result = await apiClient.initiateBridgeTransfer(
        fromChain,
        toChain,
        amount,
        token,
      );
      toast.success("Bridge transfer initiated");
      return result;
    } catch (error) {
      toast.error("Failed to initiate bridge transfer");
      throw error;
    }
  }

  static async getBridgeQuote(
    fromChain: string,
    toChain: string,
    amount: string,
    token: string,
  ) {
    try {
      const result = await apiClient.getBridgeQuote(
        fromChain,
        toChain,
        amount,
        token,
      );
      toast.success(`Quote: ${result.estimatedFee} ${result.feeCurrency}`);
      return result;
    } catch (error) {
      toast.error("Failed to get bridge quote");
      throw error;
    }
  }

  static async getBridgeStatus() {
    try {
      return await apiClient.getBridgeStatus();
    } catch (error) {
      toast.error("Failed to fetch bridge status");
      throw error;
    }
  }

  // Wallet Actions
  static async checkWallet(address: string) {
    try {
      const result = await apiClient.checkWallet(address);
      toast.success("Wallet check completed");
      return result;
    } catch (error) {
      toast.error("Failed to check wallet");
      throw error;
    }
  }

  static async revokeApproval(
    address: string,
    tokenContract: string,
    spender: string,
  ) {
    try {
      const result = await apiClient.revokeApproval(
        address,
        tokenContract,
        spender,
      );
      toast.success("Approval revoked successfully");
      return result;
    } catch (error) {
      toast.error("Failed to revoke approval");
      throw error;
    }
  }

  static async getWalletApprovals(address: string) {
    try {
      return await apiClient.getWalletApprovals(address);
    } catch (error) {
      toast.error("Failed to fetch wallet approvals");
      throw error;
    }
  }

  // Mempool Actions
  static async getMempoolData() {
    try {
      return await apiClient.getMempoolData();
    } catch (error) {
      toast.error("Failed to fetch mempool data");
      throw error;
    }
  }

  static async getMempoolStats() {
    try {
      return await apiClient.getMempoolStats();
    } catch (error) {
      toast.error("Failed to fetch mempool statistics");
      throw error;
    }
  }

  static async getMEVOpportunities() {
    try {
      return await apiClient.getMEVOpportunities();
    } catch (error) {
      toast.error("Failed to fetch MEV opportunities");
      throw error;
    }
  }

  // Bytecode Actions
  static async analyzeBytecode(bytecode: string) {
    try {
      const result = await apiClient.analyzeBytecode(bytecode);
      toast.success("Bytecode analysis completed");
      return result;
    } catch (error) {
      toast.error("Failed to analyze bytecode");
      throw error;
    }
  }

  static async compareBytecode(bytecode1: string, bytecode2: string) {
    try {
      const result = await apiClient.compareBytecode(bytecode1, bytecode2);
      toast.success("Bytecode comparison completed");
      return result;
    } catch (error) {
      toast.error("Failed to compare bytecode");
      throw error;
    }
  }

  // Time Machine Actions
  static async createSnapshot(blockNumber?: number) {
    try {
      const result = await apiClient.createSnapshot(blockNumber);
      toast.success("Snapshot created successfully");
      return result;
    } catch (error) {
      toast.error("Failed to create snapshot");
      throw error;
    }
  }

  static async restoreSnapshot(snapshotId: string) {
    try {
      const result = await apiClient.restoreSnapshot(snapshotId);
      toast.success("Snapshot restored successfully");
      return result;
    } catch (error) {
      toast.error("Failed to restore snapshot");
      throw error;
    }
  }

  static async simulateTransaction(txData: any, snapshotId?: string) {
    try {
      const result = await apiClient.simulateTransaction(txData, snapshotId);
      toast.success("Transaction simulation completed");
      return result;
    } catch (error) {
      toast.error("Failed to simulate transaction");
      throw error;
    }
  }

  // Analytics Actions
  static async getAnalytics(timeRange?: string) {
    try {
      return await apiClient.getAnalytics(timeRange);
    } catch (error) {
      toast.error("Failed to fetch analytics data");
      throw error;
    }
  }

  static async getDashboardMetrics() {
    try {
      return await apiClient.getDashboardMetrics();
    } catch (error) {
      toast.error("Failed to fetch dashboard metrics");
      throw error;
    }
  }

  static async getSecurityMetrics() {
    try {
      return await apiClient.getSecurityMetrics();
    } catch (error) {
      toast.error("Failed to fetch security metrics");
      throw error;
    }
  }

  static async getPerformanceMetrics() {
    try {
      return await apiClient.getPerformanceMetrics();
    } catch (error) {
      toast.error("Failed to fetch performance metrics");
      throw error;
    }
  }

  // Settings Actions
  static async getSettings() {
    try {
      return await apiClient.getSettings();
    } catch (error) {
      toast.error("Failed to fetch settings");
      throw error;
    }
  }

  static async updateSettings(settings: any) {
    try {
      const result = await apiClient.updateSettings(settings);
      toast.success("Settings updated successfully");
      return result;
    } catch (error) {
      toast.error("Failed to update settings");
      throw error;
    }
  }

  static async getSystemConfig() {
    try {
      return await apiClient.getSystemConfig();
    } catch (error) {
      toast.error("Failed to fetch system configuration");
      throw error;
    }
  }

  static async updateSystemConfig(config: any) {
    try {
      const result = await apiClient.updateSystemConfig(config);
      toast.success("System configuration updated successfully");
      return result;
    } catch (error) {
      toast.error("Failed to update system configuration");
      throw error;
    }
  }

  // Subscription Actions
  static async getUsageStats() {
    try {
      return await apiClient.getUsageStats();
    } catch (error) {
      toast.error("Failed to fetch usage statistics");
      throw error;
    }
  }

  static async getCurrentUsage() {
    try {
      return await apiClient.getCurrentUsage();
    } catch (error) {
      toast.error("Failed to fetch current usage");
      throw error;
    }
  }

  static async getSubscriptionInfo() {
    try {
      return await apiClient.getSubscriptionInfo();
    } catch (error) {
      toast.error("Failed to fetch subscription information");
      throw error;
    }
  }

  static async upgradeSubscription(plan: string) {
    try {
      const result = await apiClient.upgradeSubscription(plan);
      toast.success("Subscription upgraded successfully");
      return result;
    } catch (error) {
      toast.error("Failed to upgrade subscription");
      throw error;
    }
  }

  // Quantum Actions
  static async getQuantumAnalytics() {
    try {
      return await apiClient.getQuantumAnalytics();
    } catch (error) {
      toast.error("Failed to fetch quantum analytics");
      throw error;
    }
  }

  static async runQuantumSimulation(parameters: any) {
    try {
      const result = await apiClient.runQuantumSimulation(parameters);
      toast.success("Quantum simulation completed");
      return result;
    } catch (error) {
      toast.error("Failed to run quantum simulation");
      throw error;
    }
  }

  // Health Check Actions
  static async checkSystemHealth() {
    try {
      return await apiClient.healthCheck();
    } catch (error) {
      toast.error("Failed to check system health");
      throw error;
    }
  }

  // Data Export Actions
  static async exportData(type: string, format: string = "json") {
    try {
      const response = await apiClient.get(
        `/api/export/${type}?format=${format}`,
      );

      // Create download
      const blob = new Blob([JSON.stringify(response, null, 2)], {
        type: format === "json" ? "application/json" : "text/csv",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${type}-export-${new Date().toISOString()}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      toast.success("Data exported successfully");
      return response;
    } catch (error) {
      toast.error("Failed to export data");
      throw error;
    }
  }

  // Bulk Actions
  static async refreshAllData() {
    try {
      const promises = [
        this.getDashboardMetrics(),
        this.getSecurityMetrics(),
        this.getPerformanceMetrics(),
        this.checkSystemHealth(),
      ];

      await Promise.allSettled(promises);
      toast.success("All data refreshed successfully");
    } catch (error) {
      toast.error("Failed to refresh all data");
      throw error;
    }
  }
}

// Action validation helper
export const validateAction = (actionName: string, data: any): boolean => {
  switch (actionName) {
    case "scanContract":
      return !!data.address && typeof data.address === "string";
    case "initiateBridgeTransfer":
      return !!(data.fromChain && data.toChain && data.amount && data.token);
    case "checkWallet":
      return !!data.address && typeof data.address === "string";
    case "revokeApproval":
      return !!(data.address && data.tokenContract && data.spender);
    default:
      return true;
  }
};

// Generic action executor with validation
export const executeAction = async (
  actionName: string,
  data: any,
): Promise<any> => {
  if (!validateAction(actionName, data)) {
    toast.error("Invalid action parameters");
    throw new Error("Invalid action parameters");
  }

  const actionMap: Record<string, Function> = {
    scanContract: (d: any) => ActionMapper.scanContract(d.address, d.options),
    uploadAndScanFile: (d: any) => ActionMapper.uploadAndScanFile(d.file),
    detectHoneypot: (d: any) => ActionMapper.detectHoneypot(d.address),
    analyzeHoneypot: (d: any) => ActionMapper.analyzeHoneypot(d.address),
    initiateBridgeTransfer: (d: any) =>
      ActionMapper.initiateBridgeTransfer(
        d.fromChain,
        d.toChain,
        d.amount,
        d.token,
      ),
    getBridgeQuote: (d: any) =>
      ActionMapper.getBridgeQuote(d.fromChain, d.toChain, d.amount, d.token),
    checkWallet: (d: any) => ActionMapper.checkWallet(d.address),
    revokeApproval: (d: any) =>
      ActionMapper.revokeApproval(d.address, d.tokenContract, d.spender),
    analyzeBytecode: (d: any) => ActionMapper.analyzeBytecode(d.bytecode),
    compareBytecode: (d: any) =>
      ActionMapper.compareBytecode(d.bytecode1, d.bytecode2),
    createSnapshot: (d: any) => ActionMapper.createSnapshot(d.blockNumber),
    restoreSnapshot: (d: any) => ActionMapper.restoreSnapshot(d.snapshotId),
    simulateTransaction: (d: any) =>
      ActionMapper.simulateTransaction(d.txData, d.snapshotId),
    upgradeSubscription: (d: any) => ActionMapper.upgradeSubscription(d.plan),
    runQuantumSimulation: (d: any) =>
      ActionMapper.runQuantumSimulation(d.parameters),
    exportData: (d: any) => ActionMapper.exportData(d.type, d.format),
    refreshAllData: () => ActionMapper.refreshAllData(),
  };

  const actionFn = actionMap[actionName];
  if (!actionFn) {
    toast.error("Unknown action");
    throw new Error(`Unknown action: ${actionName}`);
  }

  return await actionFn(data);
};

export default ActionMapper;

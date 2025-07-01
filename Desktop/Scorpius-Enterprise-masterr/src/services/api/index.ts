/**
 * Comprehensive API Services for Scorpius Dashboard
 * Handles all backend integrations with proper error handling and typing
 */

import { useState, useEffect, useCallback } from "react";

// Base configuration
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || "ws://localhost:8000";

// ============================================================================
// TYPE DEFINITIONS FOR ALL 12 MODULES
// ============================================================================

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination?: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// 1. Wallet Guard Types
export interface WalletRiskScore {
  address: string;
  risk_score: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  last_updated: string;
  factors: {
    suspicious_transactions: number;
    blacklisted_interactions: number;
    honeypot_interactions: number;
    rugpull_exposure: number;
  };
}

export interface TokenAllowance {
  token_address: string;
  token_name: string;
  token_symbol: string;
  spender: string;
  spender_name?: string;
  amount: string;
  unlimited: boolean;
  last_updated: string;
}

export interface ApprovalHistory {
  transaction_hash: string;
  timestamp: string;
  token_address: string;
  spender: string;
  amount: string;
  action: "APPROVE" | "REVOKE";
  status: "CONFIRMED" | "PENDING" | "FAILED";
}

// 2. Honeypot Radar Types
export interface HoneypotScanResult {
  token_address: string;
  is_honeypot: boolean;
  confidence_score: number;
  scan_timestamp: string;
  detection_methods: string[];
  risk_factors: {
    cant_sell_all: boolean;
    modifiable_taxes: boolean;
    hidden_owner: boolean;
    selfdestruct_risk: boolean;
    external_functions: boolean;
  };
  simulation_results?: {
    buy_tax: number;
    sell_tax: number;
    liquidity_locked: boolean;
    max_sell_amount?: string;
  };
}

export interface HoneypotStats {
  total_scans: number;
  honeypots_detected: number;
  accuracy_rate: number;
  false_positives: number;
  updated_at: string;
}

// 3. Vulnerability Scanner Types
export interface ScanSubmission {
  scan_id: string;
  contract_address?: string;
  source_code?: string;
  submission_time: string;
  status: "QUEUED" | "SCANNING" | "COMPLETED" | "FAILED";
}

export interface ScanProgress {
  scan_id: string;
  status: "QUEUED" | "SCANNING" | "COMPLETED" | "FAILED";
  progress_percentage: number;
  current_stage: string;
  estimated_completion?: string;
  stages_completed: string[];
  total_stages: number;
}

export interface VulnerabilityFinding {
  id: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  title: string;
  description: string;
  file_path?: string;
  line_number?: number;
  category: string;
  plugin: string;
  confidence: number;
  remediation?: string;
  cwe_id?: string;
  references?: string[];
}

export interface ScanResults {
  scan_id: string;
  contract_address?: string;
  completion_time: string;
  total_findings: number;
  severity_breakdown: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  findings: VulnerabilityFinding[];
  plugins_used: string[];
  scan_duration_seconds: number;
}

export interface ScanPlugin {
  name: string;
  version: string;
  description: string;
  enabled: boolean;
  detection_types: string[];
}

// 4. MEV Bot Types
export interface MEVBotStatus {
  bot_id: string;
  status: "ACTIVE" | "INACTIVE" | "ERROR" | "MAINTENANCE";
  health_score: number;
  capital_deployed: string;
  available_capital: string;
  total_transactions: number;
  successful_transactions: number;
  failed_transactions: number;
  uptime_percentage: number;
  last_activity: string;
  gas_price_strategy: string;
  target_profit_margin: number;
}

export interface MEVTrade {
  trade_id: string;
  timestamp: string;
  type: "ARBITRAGE" | "SANDWICH" | "LIQUIDATION" | "FRONTRUN";
  tokens_involved: string[];
  profit_eth: string;
  profit_usd: string;
  gas_used: string;
  gas_price: string;
  transaction_hash: string;
  block_number: number;
  success: boolean;
}

export interface MEVTarget {
  pair_address: string;
  token_a: string;
  token_b: string;
  exchange: string;
  liquidity_usd: string;
  volume_24h: string;
  opportunity_score: number;
  last_opportunity: string;
  active: boolean;
}

// 5. Time Machine Types
export interface SimulationResult {
  simulation_id: string;
  transaction_hash: string;
  block_number: number;
  timestamp: string;
  original_result: {
    success: boolean;
    gas_used: string;
    return_data?: string;
  };
  simulated_result: {
    success: boolean;
    gas_used: string;
    return_data?: string;
    state_changes: any[];
  };
  variable_diffs: VariableDiff[];
  execution_time_ms: number;
}

export interface VariableDiff {
  variable_name: string;
  storage_slot?: string;
  original_value: string;
  simulated_value: string;
  value_type: "uint256" | "address" | "bool" | "bytes" | "string";
  change_type: "ADDED" | "MODIFIED" | "REMOVED";
}

// 6. Dashboard Metrics Types
export interface SystemHealth {
  overall_status: "HEALTHY" | "DEGRADED" | "CRITICAL";
  services: {
    name: string;
    status: "UP" | "DOWN" | "DEGRADED";
    response_time_ms: number;
    last_check: string;
  }[];
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  network_latency: number;
}

export interface ThreatMetrics {
  active_threats: number;
  threats_blocked_24h: number;
  honeypots_detected_24h: number;
  vulnerable_contracts_found: number;
  critical_vulnerabilities: number;
  risk_score_distribution: {
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
}

export interface ProfitMetrics {
  total_profit_usd: string;
  profit_24h: string;
  profit_7d: string;
  profit_30d: string;
  successful_trades: number;
  total_trades: number;
  roi_percentage: number;
  best_trade_profit: string;
}

export interface CrossChainVolume {
  total_volume_usd: string;
  volume_24h: string;
  transactions_24h: number;
  popular_routes: {
    from_chain: string;
    to_chain: string;
    volume: string;
    count: number;
  }[];
  bridge_utilization: number;
}

// 7. Security Findings Types
export interface SecurityFinding {
  id: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  title: string;
  description: string;
  category: string;
  source: string;
  timestamp: string;
  affected_systems: string[];
  status:
    | "NEW"
    | "ACKNOWLEDGED"
    | "IN_PROGRESS"
    | "RESOLVED"
    | "FALSE_POSITIVE";
  cve_id?: string;
  cvss_score?: number;
  remediation_steps?: string[];
}

export interface SecurityLog {
  id: string;
  timestamp: string;
  level: "DEBUG" | "INFO" | "WARN" | "ERROR" | "CRITICAL";
  source: string;
  message: string;
  metadata?: any;
  user_id?: string;
  ip_address?: string;
  user_agent?: string;
}

export interface SecurityIncident {
  id: string;
  title: string;
  description: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  status: "ACTIVE" | "INVESTIGATING" | "RESOLVED";
  timestamp: string;
  affected_users?: number;
  estimated_loss?: string;
  remediation_actions: string[];
}

// 8. Bug Bounty Types
export interface BountyListing {
  id: string;
  title: string;
  description: string;
  reward_amount: string;
  difficulty: "EASY" | "MEDIUM" | "HARD" | "EXPERT";
  category: string;
  target_contract?: string;
  deadline?: string;
  status: "ACTIVE" | "COMPLETED" | "EXPIRED";
  submissions_count: number;
  created_at: string;
}

export interface BountySubmission {
  id: string;
  bounty_id: string;
  title: string;
  description: string;
  proof_of_concept?: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  status: "SUBMITTED" | "UNDER_REVIEW" | "ACCEPTED" | "REJECTED" | "DUPLICATE";
  submitted_at: string;
  reward_amount?: string;
  feedback?: string;
}

export interface UserBountyStatus {
  user_id: string;
  total_submissions: number;
  accepted_submissions: number;
  total_rewards_earned: string;
  reputation_score: number;
  rank: number;
  active_submissions: BountySubmission[];
  recent_rewards: {
    amount: string;
    bounty_title: string;
    date: string;
  }[];
}

// 9. Scheduler Types
export interface ScheduledJob {
  id: string;
  name: string;
  description?: string;
  type: string;
  schedule: string; // cron expression
  enabled: boolean;
  last_run?: string;
  next_run: string;
  status: "SCHEDULED" | "RUNNING" | "COMPLETED" | "FAILED" | "CANCELLED";
  parameters?: any;
  created_at: string;
  success_count: number;
  failure_count: number;
}

// 10. Monitoring & Alerts Types
export interface AlertConfig {
  id: string;
  name: string;
  type:
    | "GAS_PRICE"
    | "MEV_OPPORTUNITY"
    | "SECURITY_THREAT"
    | "SYSTEM_HEALTH"
    | "CUSTOM";
  conditions: {
    metric: string;
    operator: ">" | "<" | "=" | "!=" | ">=" | "<=";
    threshold: number | string;
    time_window?: string;
  }[];
  actions: {
    type: "EMAIL" | "WEBHOOK" | "SLACK" | "TELEGRAM";
    target: string;
    message_template?: string;
  }[];
  enabled: boolean;
  created_at: string;
  last_triggered?: string;
  trigger_count: number;
}

export interface AlertEvent {
  id: string;
  alert_id: string;
  alert_name: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  message: string;
  timestamp: string;
  status: "ACTIVE" | "ACKNOWLEDGED" | "RESOLVED";
  metadata?: any;
  acknowledged_by?: string;
  acknowledged_at?: string;
  resolved_at?: string;
}

// 11. Reports Types
export interface ReportGeneration {
  report_id: string;
  type: "SECURITY" | "FINANCIAL" | "SYSTEM" | "CUSTOM";
  title: string;
  date_range: {
    start: string;
    end: string;
  };
  parameters?: any;
  status: "GENERATING" | "COMPLETED" | "FAILED";
  created_at: string;
  completed_at?: string;
  file_size?: number;
  download_url?: string;
}

export interface ReportData {
  report_id: string;
  title: string;
  type: string;
  generated_at: string;
  summary: {
    total_scans: number;
    vulnerabilities_found: number;
    threats_blocked: number;
    profit_generated: string;
  };
  sections: {
    title: string;
    content: any;
    charts?: any[];
  }[];
}

// ============================================================================
// CORE API CLIENT
// ============================================================================

class ApiClient {
  private baseURL: string;
  private defaultHeaders: HeadersInit;
  private token: string | null = null;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
    this.defaultHeaders = {
      "Content-Type": "application/json",
      Accept: "application/json",
    };

    // Load token from localStorage
    this.token = localStorage.getItem("auth_token");
    if (this.token) {
      this.setAuthToken(this.token);
    }
  }

  setAuthToken(token: string) {
    this.token = token;
    localStorage.setItem("auth_token", token);
    this.defaultHeaders = {
      ...this.defaultHeaders,
      Authorization: `Bearer ${token}`,
    };
  }

  clearAuthToken() {
    this.token = null;
    localStorage.removeItem("auth_token");
    const { Authorization, ...headers } = this.defaultHeaders as any;
    this.defaultHeaders = headers;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseURL}${endpoint}`;
      const response = await fetch(url, {
        ...options,
        headers: {
          ...this.defaultHeaders,
          ...options.headers,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.detail || data.error || `HTTP ${response.status}`,
        };
      }

      return {
        success: true,
        data,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Network error",
      };
    }
  }

  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: "GET" });
  }

  async post<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: "DELETE" });
  }
}

const apiClient = new ApiClient();

// ============================================================================
// WEBSOCKET MANAGER
// ============================================================================

class WebSocketManager {
  private connections: Map<string, WebSocket> = new Map();
  private reconnectAttempts: Map<string, number> = new Map();
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000;

  connect(
    endpoint: string,
    onMessage: (data: any) => void,
    onError?: (error: Event) => void,
    onClose?: (event: CloseEvent) => void,
  ): WebSocket | null {
    try {
      const url = `${WS_BASE_URL}${endpoint}`;
      const ws = new WebSocket(url);

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage(data);
        } catch (error) {
          console.error("Failed to parse WebSocket message:", error);
        }
      };

      ws.onerror = (error) => {
        console.error(`WebSocket error for ${endpoint}:`, error);
        onError?.(error);
      };

      ws.onclose = (event) => {
        console.log(`WebSocket closed for ${endpoint}:`, event.code);
        this.connections.delete(endpoint);

        // Attempt to reconnect
        this.attemptReconnect(endpoint, onMessage, onError, onClose);
        onClose?.(event);
      };

      ws.onopen = () => {
        console.log(`WebSocket connected to ${endpoint}`);
        this.reconnectAttempts.set(endpoint, 0);
      };

      this.connections.set(endpoint, ws);
      return ws;
    } catch (error) {
      console.error(
        `Failed to create WebSocket connection to ${endpoint}:`,
        error,
      );
      return null;
    }
  }

  private attemptReconnect(
    endpoint: string,
    onMessage: (data: any) => void,
    onError?: (error: Event) => void,
    onClose?: (event: CloseEvent) => void,
  ) {
    const attempts = this.reconnectAttempts.get(endpoint) || 0;

    if (attempts < this.maxReconnectAttempts) {
      setTimeout(
        () => {
          console.log(
            `Attempting to reconnect to ${endpoint} (attempt ${attempts + 1})`,
          );
          this.reconnectAttempts.set(endpoint, attempts + 1);
          this.connect(endpoint, onMessage, onError, onClose);
        },
        this.reconnectDelay * Math.pow(2, attempts),
      ); // Exponential backoff
    }
  }

  disconnect(endpoint: string) {
    const ws = this.connections.get(endpoint);
    if (ws) {
      ws.close();
      this.connections.delete(endpoint);
      this.reconnectAttempts.delete(endpoint);
    }
  }

  disconnectAll() {
    this.connections.forEach((ws, endpoint) => {
      ws.close();
    });
    this.connections.clear();
    this.reconnectAttempts.clear();
  }

  send(endpoint: string, data: any) {
    const ws = this.connections.get(endpoint);
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data));
    }
  }
}

export const wsManager = new WebSocketManager();

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

// Scanner Types
export interface ScanResult {
  id: string;
  contractAddress: string;
  vulnerabilities: Vulnerability[];
  score: number;
  status: "pending" | "scanning" | "completed" | "failed";
  createdAt: string;
  completedAt?: string;
}

export interface Vulnerability {
  id: string;
  type: string;
  severity: "low" | "medium" | "high" | "critical";
  description: string;
  location?: string;
  recommendation?: string;
}

// Mempool Types
export interface Transaction {
  hash: string;
  from: string;
  to: string;
  value: string;
  gasPrice: string;
  gasLimit: number;
  timestamp: string;
  status: "pending" | "confirmed" | "failed";
}

export interface MempoolStats {
  totalTransactions: number;
  avgGasPrice: number;
  pendingCount: number;
  throughput: number;
}

// Security Types
export interface ThreatEvent {
  id: string;
  type: string;
  severity: "low" | "medium" | "high" | "critical";
  description: string;
  source: string;
  timestamp: string;
  status: "active" | "mitigated" | "investigating";
}

export interface SecurityMetrics {
  threatLevel: number;
  activeThreats: number;
  mitigatedThreats: number;
  detectionRate: number;
  responseTime: number;
}

// Trading Types
export interface TradingBot {
  id: string;
  name: string;
  strategy: string;
  status: "active" | "paused" | "stopped";
  pnl: number;
  trades: number;
  successRate: number;
}

export interface TradingMetrics {
  totalPnl: number;
  totalTrades: number;
  winRate: number;
  activeBots: number;
}

// Bridge Types
export interface BridgeTransaction {
  id: string;
  sourceChain: string;
  targetChain: string;
  amount: string;
  status: "pending" | "completed" | "failed";
  timestamp: string;
}

export interface BridgeMetrics {
  totalVolume: number;
  successRate: number;
  avgTime: number;
  activeTransactions: number;
}

// ============================================================================
// API SERVICES
// ============================================================================

// Scanner Service
export class ScannerService {
  static async startScan(
    contractAddress: string,
    options?: any,
  ): Promise<ApiResponse<ScanResult>> {
    return apiClient.post("/api/scanner/scan", { contractAddress, ...options });
  }

  static async getScanResults(
    scanId: string,
  ): Promise<ApiResponse<ScanResult>> {
    return apiClient.get(`/api/scanner/results/${scanId}`);
  }

  static async getRecentScans(limit = 10): Promise<ApiResponse<ScanResult[]>> {
    return apiClient.get(`/api/scanner/recent?limit=${limit}`);
  }

  static async uploadContract(
    file: File,
  ): Promise<ApiResponse<{ scanId: string }>> {
    const formData = new FormData();
    formData.append("file", file);

    return fetch(`${API_BASE_URL}/api/scanner/upload`, {
      method: "POST",
      body: formData,
    }).then((res) => res.json());
  }
}

// Mempool Service
export class MempoolService {
  static async getTransactions(
    limit = 50,
  ): Promise<ApiResponse<Transaction[]>> {
    return apiClient.get(`/api/mempool/transactions?limit=${limit}`);
  }

  static async getStats(): Promise<ApiResponse<MempoolStats>> {
    return apiClient.get("/api/mempool/stats");
  }

  static async addContract(address: string): Promise<ApiResponse<any>> {
    return apiClient.post("/api/mempool/contracts", { address });
  }

  static async removeContract(address: string): Promise<ApiResponse<any>> {
    return apiClient.delete(`/api/mempool/contracts/${address}`);
  }
}

// Security Service
export class SecurityService {
  static async getThreats(limit = 20): Promise<ApiResponse<ThreatEvent[]>> {
    return apiClient.get(`/api/security/threats?limit=${limit}`);
  }

  static async getMetrics(): Promise<ApiResponse<SecurityMetrics>> {
    return apiClient.get("/api/security/metrics");
  }

  static async mitigateThreat(threatId: string): Promise<ApiResponse<any>> {
    return apiClient.post(`/api/security/threats/${threatId}/mitigate`);
  }
}

// Trading Service
export class TradingService {
  static async getBots(): Promise<ApiResponse<TradingBot[]>> {
    return apiClient.get("/api/trading/bots");
  }

  static async getMetrics(): Promise<ApiResponse<TradingMetrics>> {
    return apiClient.get("/api/trading/metrics");
  }

  static async startBot(botId: string): Promise<ApiResponse<any>> {
    return apiClient.post(`/api/trading/bots/${botId}/start`);
  }

  static async stopBot(botId: string): Promise<ApiResponse<any>> {
    return apiClient.post(`/api/trading/bots/${botId}/stop`);
  }

  static async createBot(config: any): Promise<ApiResponse<TradingBot>> {
    return apiClient.post("/api/trading/bots", config);
  }
}

// Bridge Service
export class BridgeService {
  static async getTransactions(
    limit = 20,
  ): Promise<ApiResponse<BridgeTransaction[]>> {
    return apiClient.get(`/api/bridge/transactions?limit=${limit}`);
  }

  static async getMetrics(): Promise<ApiResponse<BridgeMetrics>> {
    return apiClient.get("/api/bridge/metrics");
  }

  static async initiateBridge(
    params: any,
  ): Promise<ApiResponse<BridgeTransaction>> {
    return apiClient.post("/api/bridge/transfer", params);
  }
}

// Honeypot Service
export class HoneypotService {
  static async getDetections(limit = 20): Promise<ApiResponse<any[]>> {
    return apiClient.get(`/api/honeypot/detections?limit=${limit}`);
  }

  static async analyzeContract(address: string): Promise<ApiResponse<any>> {
    return apiClient.post("/api/honeypot/analyze", { address });
  }

  static async getStats(): Promise<ApiResponse<any>> {
    return apiClient.get("/api/honeypot/stats");
  }
}

// System Service
export class SystemService {
  static async getHealth(): Promise<ApiResponse<any>> {
    return apiClient.get("/api/system/health");
  }

  static async getMetrics(): Promise<ApiResponse<any>> {
    return apiClient.get("/api/system/metrics");
  }

  static async getLogs(
    service?: string,
    limit = 100,
  ): Promise<ApiResponse<any[]>> {
    const params = new URLSearchParams();
    if (service) params.append("service", service);
    params.append("limit", limit.toString());

    return apiClient.get(`/api/system/logs?${params}`);
  }
}

// Analytics Service
export class AnalyticsService {
  static async getDashboardMetrics(): Promise<ApiResponse<any>> {
    return apiClient.get("/api/analytics/dashboard");
  }

  static async getChartData(
    type: string,
    timeframe = "24h",
  ): Promise<ApiResponse<any>> {
    return apiClient.get(
      `/api/analytics/charts/${type}?timeframe=${timeframe}`,
    );
  }

  static async getReports(limit = 10): Promise<ApiResponse<any[]>> {
    return apiClient.get(`/api/analytics/reports?limit=${limit}`);
  }

  static async generateReport(config: any): Promise<ApiResponse<any>> {
    return apiClient.post("/api/analytics/reports", config);
  }
}

// Export all services
export { ApiClient, WebSocketManager, apiClient };

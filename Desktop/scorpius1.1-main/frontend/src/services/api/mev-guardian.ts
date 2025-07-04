/**
 * MEV Guardian Service API Client
 * Handles blockchain MEV protection, threat detection, and attack simulation
 */

// Base configuration
const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || "http://localhost:8000";

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface SystemStatus {
  status: string;
  mode: "guardian" | "attack" | "hybrid";
  uptime_seconds: number;
  version: string;
  timestamp: string;
}

export interface GuardianStatus {
  is_active: boolean;
  active_detectors: number;
  threats_detected_total: number;
  threats_detected_last_hour: number;
  simulations_executed_total: number;
  honeypots_identified_total: number;
  active_simulations: number;
}

export interface AttackStatus {
  is_active: boolean;
  active_strategies: string[];
  opportunities_found_total: number;
  opportunities_found_last_hour: number;
  successful_executions: number;
  failed_executions: number;
  total_profit_eth: number;
}

export interface ThreatDetection {
  id: string;
  threat_type: string;
  severity: "low" | "medium" | "high" | "critical";
  confidence: number;
  title: string;
  description: string;
  detected_at: string;
  chain_id: number;
  affected_protocols: string[];
  potential_loss_usd?: number;
}

export interface SimulationRequest {
  attack_type: string;
  target_protocol: string;
  chain_id?: number;
  fork_block?: number;
  parameters?: Record<string, any>;
}

export interface SimulationResponse {
  id: string;
  status: "queued" | "running" | "completed" | "failed";
  attack_type: string;
  target_protocol: string;
  success?: boolean;
  profit_extracted?: number;
  gas_cost?: number;
  duration_seconds?: number;
  created_at: string;
  error_message?: string;
}

export interface HoneypotDetection {
  id: string;
  contract_address: string;
  chain_id: number;
  honeypot_type: string;
  confidence: number;
  risk_score: number;
  detected_at: string;
  estimated_victims: number;
  total_funds_trapped?: number;
}

export interface MEVOpportunity {
  id: string;
  strategy_type: string;
  chain_id: number;
  estimated_profit: number;
  confidence_score: number;
  discovered_at: string;
  executed: boolean;
  net_profit: number;
}

export interface MEVStrategy {
  type: string;
  name: string;
  description: string;
  enabled: boolean;
  profit_threshold: number;
  max_gas_price: number;
  success_rate: number;
  total_executions: number;
  total_profit: number;
}

export interface StrategyToggleRequest {
  strategy_type: string;
  enabled: boolean;
}

export interface SystemMetrics {
  guardian_metrics: {
    active_monitors: number;
    threats_per_hour: number;
    detection_accuracy: number;
    honeypots_found: number;
  };
  attack_metrics: {
    active_strategies: number;
    opportunities_per_hour: number;
    success_rate: number;
    total_profit_eth: number;
  };
  system_metrics: {
    cpu_usage: number;
    memory_usage: number;
    network_latency: number;
    transactions_processed: number;
  };
  timestamp: string;
}

export interface MevResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
}

// ============================================================================
// MEV GUARDIAN SERVICE CLASS
// ============================================================================

export class MevGuardianService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Get service health status
   */
  async getHealth(): Promise<MevResponse> {
    const response = await fetch(`${this.baseUrl}/api/mev/health`);
    return await response.json();
  }

  /**
   * Get system status and configuration
   */
  async getSystemStatus(): Promise<MevResponse<SystemStatus>> {
    const response = await fetch(`${this.baseUrl}/api/mev/api/v1/system/status`);
    return await response.json();
  }

  /**
   * Get system performance metrics
   */
  async getSystemMetrics(): Promise<MevResponse<SystemMetrics>> {
    const response = await fetch(`${this.baseUrl}/api/mev/api/v1/system/metrics`);
    return await response.json();
  }

  /**
   * Switch between guardian, attack, or hybrid mode
   */
  async switchMode(mode: "guardian" | "attack" | "hybrid"): Promise<MevResponse> {
    const response = await fetch(`${this.baseUrl}/api/mev/api/v1/system/mode`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ mode }),
    });
    return await response.json();
  }

  // ============================================================================
  // GUARDIAN MODE ENDPOINTS
  // ============================================================================

  /**
   * Get guardian system status
   */
  async getGuardianStatus(): Promise<MevResponse<GuardianStatus>> {
    const response = await fetch(`${this.baseUrl}/api/mev/api/v1/guardian/status`);
    return await response.json();
  }

  /**
   * Get recent threat detections
   */
  async getThreats(
    hours: number = 24,
    severity?: string,
    threat_type?: string
  ): Promise<MevResponse<ThreatDetection[]>> {
    const params = new URLSearchParams();
    params.append('hours', hours.toString());
    if (severity) params.append('severity', severity);
    if (threat_type) params.append('threat_type', threat_type);

    const response = await fetch(`${this.baseUrl}/api/mev/api/v1/guardian/threats?${params}`);
    return await response.json();
  }

  /**
   * Create a new attack simulation
   */
  async createSimulation(request: SimulationRequest): Promise<MevResponse<SimulationResponse>> {
    const response = await fetch(`${this.baseUrl}/api/mev/api/v1/guardian/simulate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    return await response.json();
  }

  /**
   * Get simulation history
   */
  async getSimulations(): Promise<MevResponse<SimulationResponse[]>> {
    const response = await fetch(`${this.baseUrl}/api/mev/api/v1/guardian/simulations`);
    return await response.json();
  }

  /**
   * Get specific simulation details
   */
  async getSimulation(simulationId: string): Promise<MevResponse<SimulationResponse>> {
    const response = await fetch(`${this.baseUrl}/api/mev/api/v1/guardian/simulations/${simulationId}`);
    return await response.json();
  }

  /**
   * Get honeypot detections
   */
  async getHoneypots(): Promise<MevResponse<HoneypotDetection[]>> {
    const response = await fetch(`${this.baseUrl}/api/mev/api/v1/guardian/honeypots`);
    return await response.json();
  }

  // ============================================================================
  // ATTACK MODE ENDPOINTS
  // ============================================================================

  /**
   * Get attack system status
   */
  async getAttackStatus(): Promise<MevResponse<AttackStatus>> {
    const response = await fetch(`${this.baseUrl}/api/mev/api/v1/mev/status`);
    return await response.json();
  }

  /**
   * Get MEV strategies configuration
   */
  async getStrategies(): Promise<MevResponse<MEVStrategy[]>> {
    const response = await fetch(`${this.baseUrl}/api/mev/api/v1/mev/strategies`);
    return await response.json();
  }

  /**
   * Toggle MEV strategy enable/disable
   */
  async toggleStrategy(strategyType: string, enabled: boolean): Promise<MevResponse> {
    const response = await fetch(`${this.baseUrl}/api/mev/api/v1/mev/strategies/${strategyType}/toggle`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ strategy_type: strategyType, enabled }),
    });
    return await response.json();
  }

  /**
   * Get MEV opportunities
   */
  async getOpportunities(): Promise<MevResponse<MEVOpportunity[]>> {
    const response = await fetch(`${this.baseUrl}/api/mev/api/v1/mev/opportunities`);
    return await response.json();
  }

  /**
   * Get MEV execution history
   */
  async getExecutions(): Promise<MevResponse<any[]>> {
    const response = await fetch(`${this.baseUrl}/api/mev/api/v1/mev/executions`);
    return await response.json();
  }

  // ============================================================================
  // UTILITY METHODS
  // ============================================================================

  /**
   * Get threat severity color
   */
  getThreatSeverityColor(severity: string): string {
    switch (severity) {
      case 'critical': return 'text-red-400';
      case 'high': return 'text-orange-400';
      case 'medium': return 'text-yellow-400';
      case 'low': return 'text-green-400';
      default: return 'text-gray-400';
    }
  }

  /**
   * Format ETH amount with proper decimals
   */
  formatEthAmount(amount: number): string {
    if (amount === 0) return '0 ETH';
    if (amount < 0.001) return `${(amount * 1000).toFixed(3)} mETH`;
    if (amount < 1) return `${amount.toFixed(4)} ETH`;
    return `${amount.toFixed(2)} ETH`;
  }

  /**
   * Format USD amount
   */
  formatUsdAmount(amount: number): string {
    if (amount === 0) return '$0';
    if (amount < 1) return `$${amount.toFixed(4)}`;
    if (amount < 1000) return `$${amount.toFixed(2)}`;
    if (amount < 1000000) return `$${(amount / 1000).toFixed(1)}K`;
    return `$${(amount / 1000000).toFixed(1)}M`;
  }

  /**
   * Get strategy status color
   */
  getStrategyStatusColor(enabled: boolean): string {
    return enabled ? 'text-green-400' : 'text-gray-400';
  }

  /**
   * Format timestamp to relative time
   */
  formatRelativeTime(timestamp: string): string {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now.getTime() - time.getTime();
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  }
}

// Export singleton instance
export const mevGuardianService = new MevGuardianService();
export default mevGuardianService;

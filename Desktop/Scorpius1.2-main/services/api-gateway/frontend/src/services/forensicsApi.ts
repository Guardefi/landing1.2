/**
 * Blockchain Forensics API Service
 *
 * Provides comprehensive blockchain forensics and investigation capabilities
 * including AI-powered analysis, pattern detection, and compliance monitoring.
 */

// Types and Enums matching the Python backend
export enum ForensicsEventType {
  SUSPICIOUS_TRANSACTION = 'suspicious_transaction',
  MONEY_LAUNDERING = 'money_laundering',
  MIXER_USAGE = 'mixer_usage',
  EXCHANGE_DEPOSIT = 'exchange_deposit',
  HIGH_FREQUENCY_TRADING = 'high_frequency_trading',
  SMART_CONTRACT_EXPLOIT = 'smart_contract_exploit',
  PHISHING_SCAM = 'phishing_scam',
  PONZI_SCHEME = 'ponzi_scheme',
  FLASH_LOAN_ATTACK = 'flash_loan_attack',
  FRONT_RUNNING = 'front_running',
}

export enum RiskLevel {
  LOW = 1,
  MEDIUM = 2,
  HIGH = 3,
  CRITICAL = 4,
}

export enum ComplianceStandard {
  AML = 'anti_money_laundering',
  KYC = 'know_your_customer',
  FATF = 'financial_action_task_force',
  OFAC = 'office_foreign_assets_control',
  EU_5AMLD = 'eu_5th_anti_money_laundering_directive',
  TRAVEL_RULE = 'travel_rule',
}

// Interfaces matching Python backend dataclasses
export interface ForensicsAlert {
  id: string;
  event_type: ForensicsEventType;
  risk_level: RiskLevel;
  confidence: number;
  description: string;
  transaction_hashes: string[];
  addresses_involved: string[];
  timestamp: string;
  evidence: Record<string, any>;
  compliance_violations: ComplianceStandard[];
  follow_up_required: boolean;
  investigator_notes: string;
}

export interface TransactionPattern {
  pattern_type: string;
  description: string;
  addresses: string[];
  transactions: string[];
  time_span: number; // timedelta in seconds
  frequency: number;
  total_value: number;
  risk_indicators: string[];
  confidence: number;
}

export interface AddressProfile {
  address: string;
  label?: string;
  category?: string;
  risk_score: number;
  transaction_count: number;
  total_volume: number;
  first_seen?: string;
  last_seen?: string;
  connected_addresses: string[];
  known_services: string[];
  compliance_flags: string[];
  behavioral_patterns: Record<string, any>;
}

export interface InvestigationCase {
  case_id: string;
  title: string;
  description: string;
  investigator: string;
  status: string;
  priority: RiskLevel;
  created_at: string;
  updated_at: string;
  alerts: string[];
  evidence: Record<string, any>;
  timeline: Array<{
    timestamp: string;
    action: string;
    type: string;
    description: string;
  }>;
  suspects: string[];
  tags: string[];
  notes: string;
}

export interface TransactionAnomaly {
  transaction_hash: string;
  anomaly_score: number;
  anomaly_type: string;
  features: Record<string, number>;
  explanation: string;
}

export interface ComplianceViolation {
  type: string;
  standard: string;
  description: string;
  severity: string;
}

export interface AddressInvestigationRequest {
  address: string;
  depth?: number;
}

export interface AddressInvestigationResult {
  address: string;
  investigation_id: string;
  profile: AddressProfile;
  risk_score: number;
  anomalies: TransactionAnomaly[];
  compliance_issues: ComplianceViolation[];
  patterns: TransactionPattern[];
  alerts: string[];
  investigation_time: number;
  timestamp: string;
}

export interface CaseCreationRequest {
  title: string;
  description: string;
  investigator: string;
  priority?: RiskLevel;
}

export interface EvidenceRequest {
  case_id: string;
  evidence_type: string;
  evidence_data: Record<string, any>;
}

export interface InvestigationReport {
  case_id: string;
  title: string;
  investigator: string;
  status: string;
  priority: number;
  created_at: string;
  updated_at: string;
  summary: {
    total_alerts: number;
    total_addresses: number;
    total_transactions: number;
    average_risk_level: number;
    compliance_violations: number;
  };
  alerts: ForensicsAlert[];
  evidence: Record<string, any>;
  timeline: Array<{
    timestamp: string;
    action: string;
    type: string;
    description: string;
  }>;
  recommendations: string[];
  next_steps: string[];
}

export interface ForensicsStatistics {
  total_investigations: number;
  alerts_generated: number;
  patterns_detected: number;
  compliance_violations: number;
  average_investigation_time: number;
  active_cases: number;
  total_cases: number;
  total_alerts: number;
  high_risk_alerts: number;
  address_profiles: number;
  known_addresses: number;
  alert_distribution: Record<string, number>;
  risk_distribution: Record<string, number>;
  compliance_violations_by_standard: Record<string, number>;
}

// API Service Class
export class ForensicsApiService {
  private baseUrl: string;
  private timeout: number;

  constructor() {
    this.baseUrl = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';
    this.timeout = parseInt(import.meta.env.VITE_API_TIMEOUT || '30000');
  }

  /**
   * Make HTTP request to forensics API
   */
  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {},
  ): Promise<T> {
    const url = `${this.baseUrl}/forensics${endpoint}`;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error('Request timeout');
      }
      throw error;
    }
  }

  // Address Investigation
  async investigateAddress(
    request: AddressInvestigationRequest,
  ): Promise<AddressInvestigationResult> {
    return this.makeRequest<AddressInvestigationResult>('/investigate-address', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getAddressProfile(address: string): Promise<AddressProfile> {
    return this.makeRequest<AddressProfile>(`/address/${address}/profile`);
  }

  async getAddressRiskScore(
    address: string,
  ): Promise<{ address: string; risk_score: number }> {
    return this.makeRequest<{ address: string; risk_score: number }>(
      `/address/${address}/risk-score`,
    );
  }

  // Case Management
  async createInvestigationCase(
    request: CaseCreationRequest,
  ): Promise<{ case_id: string }> {
    return this.makeRequest<{ case_id: string }>('/cases', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getInvestigationCase(caseId: string): Promise<InvestigationCase> {
    return this.makeRequest<InvestigationCase>(`/cases/${caseId}`);
  }

  async getAllCases(): Promise<InvestigationCase[]> {
    return this.makeRequest<InvestigationCase[]>('/cases');
  }

  async updateCaseStatus(
    caseId: string,
    status: string,
  ): Promise<{ success: boolean }> {
    return this.makeRequest<{ success: boolean }>(`/cases/${caseId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });
  }

  async addEvidenceToCase(request: EvidenceRequest): Promise<{ success: boolean }> {
    return this.makeRequest<{ success: boolean }>(
      `/cases/${request.case_id}/evidence`,
      {
        method: 'POST',
        body: JSON.stringify({
          evidence_type: request.evidence_type,
          evidence_data: request.evidence_data,
        }),
      },
    );
  }

  async generateInvestigationReport(caseId: string): Promise<InvestigationReport> {
    return this.makeRequest<InvestigationReport>(`/cases/${caseId}/report`);
  }

  // Alert Management
  async getAllAlerts(): Promise<ForensicsAlert[]> {
    return this.makeRequest<ForensicsAlert[]>('/alerts');
  }

  async getAlert(alertId: string): Promise<ForensicsAlert> {
    return this.makeRequest<ForensicsAlert>(`/alerts/${alertId}`);
  }

  async getHighRiskAlerts(): Promise<ForensicsAlert[]> {
    return this.makeRequest<ForensicsAlert[]>('/alerts/high-risk');
  }

  async markAlertAsReviewed(alertId: string): Promise<{ success: boolean }> {
    return this.makeRequest<{ success: boolean }>(`/alerts/${alertId}/reviewed`, {
      method: 'POST',
    });
  }

  async addInvestigatorNotes(
    alertId: string,
    notes: string,
  ): Promise<{ success: boolean }> {
    return this.makeRequest<{ success: boolean }>(`/alerts/${alertId}/notes`, {
      method: 'POST',
      body: JSON.stringify({ notes }),
    });
  }

  // Pattern Detection
  async detectTransactionPatterns(addresses: string[]): Promise<TransactionPattern[]> {
    return this.makeRequest<TransactionPattern[]>('/patterns/detect', {
      method: 'POST',
      body: JSON.stringify({ addresses }),
    });
  }

  async getKnownPatterns(): Promise<TransactionPattern[]> {
    return this.makeRequest<TransactionPattern[]>('/patterns');
  }

  async analyzeTransactionAnomalies(
    transactions: any[],
  ): Promise<TransactionAnomaly[]> {
    return this.makeRequest<TransactionAnomaly[]>('/anomalies/analyze', {
      method: 'POST',
      body: JSON.stringify({ transactions }),
    });
  }

  // Compliance
  async checkCompliance(address: string): Promise<ComplianceViolation[]> {
    return this.makeRequest<ComplianceViolation[]>(`/compliance/check/${address}`);
  }

  async getComplianceViolations(): Promise<ComplianceViolation[]> {
    return this.makeRequest<ComplianceViolation[]>('/compliance/violations');
  }

  async checkSanctionsList(
    address: string,
  ): Promise<{ is_sanctioned: boolean; details?: any }> {
    return this.makeRequest<{ is_sanctioned: boolean; details?: any }>(
      `/compliance/sanctions/${address}`,
    );
  }

  // Statistics and Reporting
  async getForensicsStatistics(): Promise<ForensicsStatistics> {
    return this.makeRequest<ForensicsStatistics>('/statistics');
  }

  async getInvestigationMetrics(): Promise<{
    daily_investigations: Array<{ date: string; count: number }>;
    risk_score_distribution: Array<{ range: string; count: number }>;
    alert_trends: Array<{ date: string; alerts: number }>;
    pattern_detection_rates: Array<{
      pattern_type: string;
      detection_rate: number;
    }>;
  }> {
    return this.makeRequest<{
      daily_investigations: Array<{ date: string; count: number }>;
      risk_score_distribution: Array<{ range: string; count: number }>;
      alert_trends: Array<{ date: string; alerts: number }>;
      pattern_detection_rates: Array<{
        pattern_type: string;
        detection_rate: number;
      }>;
    }>('/metrics');
  }

  async exportInvestigationData(params: {
    start_date?: string;
    end_date?: string;
    include_alerts?: boolean;
    include_cases?: boolean;
    format?: 'json' | 'csv';
  }): Promise<Blob> {
    const queryParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        queryParams.append(key, value.toString());
      }
    });

    const response = await fetch(`${this.baseUrl}/forensics/export?${queryParams}`, {
      method: 'GET',
      headers: {
        Accept: params.format === 'csv' ? 'text/csv' : 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Export failed: ${response.status}`);
    }

    return response.blob();
  }

  // AI Analysis
  async runAIAnalysis(data: {
    addresses?: string[];
    transactions?: any[];
    analysis_type:
      | 'anomaly_detection'
      | 'pattern_recognition'
      | 'risk_assessment'
      | 'full_analysis';
  }): Promise<{
    analysis_id: string;
    results: any;
    confidence: number;
    recommendations: string[];
  }> {
    return this.makeRequest<{
      analysis_id: string;
      results: any;
      confidence: number;
      recommendations: string[];
    }>('/ai/analyze', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getAIAnalysisStatus(analysisId: string): Promise<{
    status: 'pending' | 'running' | 'completed' | 'failed';
    progress: number;
    results?: any;
  }> {
    return this.makeRequest<{
      status: 'pending' | 'running' | 'completed' | 'failed';
      progress: number;
      results?: any;
    }>(`/ai/analysis/${analysisId}/status`);
  }

  // Network Analysis
  async analyzeTransactionNetwork(params: {
    root_address: string;
    depth: number;
    min_value?: number;
    time_range?: { start: string; end: string };
  }): Promise<{
    nodes: Array<{
      id: string;
      label: string;
      risk_score: number;
      category: string;
    }>;
    edges: Array<{
      source: string;
      target: string;
      value: number;
      transactions: string[];
    }>;
    clusters: Array<{ id: string; nodes: string[]; risk_level: string }>;
    insights: string[];
  }> {
    return this.makeRequest<{
      nodes: Array<{
        id: string;
        label: string;
        risk_score: number;
        category: string;
      }>;
      edges: Array<{
        source: string;
        target: string;
        value: number;
        transactions: string[];
      }>;
      clusters: Array<{ id: string; nodes: string[]; risk_level: string }>;
      insights: string[];
    }>('/network/analyze', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  // Real-time Monitoring
  async startRealTimeMonitoring(params: {
    addresses: string[];
    alert_thresholds: Record<string, number>;
    notification_channels: string[];
  }): Promise<{ monitoring_id: string }> {
    return this.makeRequest<{ monitoring_id: string }>('/monitoring/start', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async stopRealTimeMonitoring(monitoringId: string): Promise<{ success: boolean }> {
    return this.makeRequest<{ success: boolean }>(`/monitoring/${monitoringId}/stop`, {
      method: 'POST',
    });
  }

  async getMonitoringStatus(): Promise<
    Array<{
      monitoring_id: string;
      status: string;
      addresses_count: number;
      alerts_generated: number;
      started_at: string;
    }>
  > {
    return this.makeRequest<
      Array<{
        monitoring_id: string;
        status: string;
        addresses_count: number;
        alerts_generated: number;
        started_at: string;
      }>
    >('/monitoring/status');
  }
}

// Export singleton instance
export const forensicsApiService = new ForensicsApiService();

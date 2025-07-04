/**
 * Reporting Service API Client
 * Handles report generation, management, and download for the Scorpius platform
 */

// Base configuration
const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || "http://localhost:8000";

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  type: "security" | "compliance" | "audit" | "executive";
  formats: string[];
  theme: string;
  lastUsed?: Date;
  popularity: number;
  fields: Record<string, any>;
}

export interface ReportCapabilities {
  name: string;
  version: string;
  description: string;
  supported_formats: string[];
  supported_themes: string[];
  templates: ReportTemplate[];
  max_file_size: string;
  digital_signing: boolean;
  watermarking: boolean;
  compression: boolean;
  features: string[];
}

export interface ReportGenerationRequest {
  scan_id: string;
  template_id?: string;
  formats: string[];
  theme?: string;
  title?: string;
  description?: string;
  include_signature?: boolean;
  include_watermark?: boolean;
  compression?: boolean;
  webhook_url?: string;
  metadata?: Record<string, any>;
}

export interface ReportGenerationResponse {
  report_id: string;
  status: "queued" | "generating" | "completed" | "failed";
  message: string;
  estimated_completion?: string;
  formats: string[];
}

export interface ReportStatus {
  report_id: string;
  status: "queued" | "generating" | "completed" | "failed";
  progress: number;
  current_stage: string;
  estimated_completion?: string;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface GeneratedReport {
  id: string;
  title: string;
  description?: string;
  scan_id: string;
  template_id: string;
  format: string;
  theme: string;
  status: "generating" | "completed" | "failed" | "signed";
  created_at: string;
  completed_at?: string;
  file_size?: number;
  download_count: number;
  signed_by?: string;
  watermarked: boolean;
  compressed: boolean;
  metadata?: Record<string, any>;
  findings?: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    total: number;
  };
  download_url?: string;
  expires_at?: string;
}

export interface ReportResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  timestamp: string;
}

// ============================================================================
// REPORTING SERVICE CLASS
// ============================================================================

export class ReportingService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Get service health status
   */
  async getHealth(): Promise<ReportResponse> {
    const response = await fetch(`${this.baseUrl}/api/reporting/health`);
    return await response.json();
  }

  /**
   * Get service capabilities and supported features
   */
  async getCapabilities(): Promise<ReportResponse<ReportCapabilities>> {
    const response = await fetch(`${this.baseUrl}/api/reporting/capabilities`);
    return await response.json();
  }

  /**
   * Get available report templates
   */
  async getTemplates(): Promise<ReportResponse<{ templates: ReportTemplate[] }>> {
    const response = await fetch(`${this.baseUrl}/api/reporting/templates`);
    return await response.json();
  }

  /**
   * Generate a new report
   */
  async generateReport(request: ReportGenerationRequest): Promise<ReportResponse<ReportGenerationResponse>> {
    const response = await fetch(`${this.baseUrl}/api/reporting/reports/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    return await response.json();
  }

  /**
   * Get report generation status
   */
  async getReportStatus(reportId: string): Promise<ReportResponse<ReportStatus>> {
    const response = await fetch(`${this.baseUrl}/api/reporting/reports/${reportId}/status`);
    return await response.json();
  }

  /**
   * Get list of generated reports
   */
  async getReports(
    limit: number = 50,
    offset: number = 0,
    scanId?: string,
    status?: string
  ): Promise<ReportResponse<{ reports: GeneratedReport[]; total: number }>> {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());
    if (scanId) params.append('scan_id', scanId);
    if (status) params.append('status', status);

    const response = await fetch(`${this.baseUrl}/api/reporting/reports?${params}`);
    return await response.json();
  }

  /**
   * Get specific report details
   */
  async getReport(reportId: string): Promise<ReportResponse<GeneratedReport>> {
    const response = await fetch(`${this.baseUrl}/api/reporting/reports/${reportId}`);
    return await response.json();
  }

  /**
   * Download report file
   */
  async downloadReport(reportId: string): Promise<Response> {
    const response = await fetch(`${this.baseUrl}/api/reporting/reports/${reportId}/download`);
    return response;
  }

  /**
   * Get available scans for reporting
   */
  async getScans(
    limit: number = 50,
    offset: number = 0
  ): Promise<ReportResponse<{ scans: Array<{
    scan_id: string;
    contract_name?: string;
    contract_address?: string;
    scan_date: string;
    status: string;
    findings: {
      critical: number;
      high: number;
      medium: number;
      low: number;
      total: number;
    };
    risk_score: number;
  }>; total: number }>> {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());

    const response = await fetch(`${this.baseUrl}/api/reporting/scans?${params}`);
    return await response.json();
  }

  /**
   * Helper method to download and save report file
   */
  async downloadAndSaveReport(reportId: string, filename?: string): Promise<void> {
    const response = await this.downloadReport(reportId);
    if (!response.ok) {
      throw new Error(`Download failed: ${response.statusText}`);
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || `report-${reportId}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }

  /**
   * Helper method to poll report status until completion
   */
  async pollReportStatus(
    reportId: string,
    onProgress?: (status: ReportStatus) => void,
    pollInterval: number = 2000
  ): Promise<ReportStatus> {
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const response = await this.getReportStatus(reportId);
          if (!response.success || !response.data) {
            reject(new Error('Failed to get report status'));
            return;
          }

          const status = response.data;
          onProgress?.(status);

          if (status.status === 'completed') {
            resolve(status);
          } else if (status.status === 'failed') {
            reject(new Error(status.error_message || 'Report generation failed'));
          } else {
            setTimeout(poll, pollInterval);
          }
        } catch (error) {
          reject(error);
        }
      };

      poll();
    });
  }
}

// Export singleton instance
export const reportingService = new ReportingService();
export default reportingService;

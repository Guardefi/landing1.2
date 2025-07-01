/**
 * Scanner API Service
 * Connects the Scanner frontend to the backend scanner endpoints
 */

export interface ScanRequest {
  target: string;
  rpc_url?: string;
  block_number?: number;
  plugins?: string[];
  enable_simulation?: boolean;
}

export interface ScanResponse {
  scan_id: string;
  status: string;
  message: string;
}

export interface ScanStatus {
  scan_id: string;
  status: string;
  progress?: number;
  findings?: any[];
  error?: string;
  created_at: string;
  updated_at: string;
}

export interface ScannerHealth {
  status: string;
  external_scanner: boolean;
  active_scans: number;
  total_scans: number;
}

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';

export class ScannerAPI {
  private static async request<T>(
    endpoint: string,
    options: RequestInit = {},
  ): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Scanner API Error: ${response.status} - ${error}`);
    }

    return response.json();
  }

  // Health check
  static async getHealth(): Promise<ScannerHealth> {
    return this.request<ScannerHealth>('/scanner/health');
  }

  // Start a new scan
  static async startScan(request: ScanRequest): Promise<ScanResponse> {
    return this.request<ScanResponse>('/scanner/scan', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Get scan status
  static async getScanStatus(scanId: string): Promise<ScanStatus> {
    return this.request<ScanStatus>(`/scanner/scan/${scanId}`);
  }

  // Get all scans
  static async getAllScans(): Promise<ScanStatus[]> {
    return this.request<ScanStatus[]>('/scanner/scans');
  }

  // Delete a scan
  static async deleteScan(scanId: string): Promise<void> {
    await this.request(`/scanner/scan/${scanId}`, {
      method: 'DELETE',
    });
  }

  // Get available plugins
  static async getPlugins(): Promise<string[]> {
    return this.request<string[]>('/scanner/plugins');
  }
}

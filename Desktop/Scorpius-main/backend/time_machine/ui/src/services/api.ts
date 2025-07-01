import { 
  TimelineEvent, 
  ReplayJob, 
  Branch, 
  AnalysisResult, 
  AnalysisPlugin,
  JobStatusUpdate,
  WebSocketMessage 
} from '../types';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000/api';
const WS_BASE = process.env.REACT_APP_WS_BASE || 'ws://localhost:8000';

class ApiService {
  // Job management
  async getJobs(): Promise<ReplayJob[]> {
    const response = await fetch(`${API_BASE}/jobs`);
    if (!response.ok) throw new Error('Failed to fetch jobs');
    return response.json();
  }

  async createJob(config: {
    start_block: number;
    end_block: number;
    vm_type: string;
    config?: Record<string, any>;
  }): Promise<ReplayJob> {
    const response = await fetch(`${API_BASE}/replay`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });
    if (!response.ok) throw new Error('Failed to create job');
    return response.json();
  }

  async getJob(jobId: string): Promise<ReplayJob> {
    const response = await fetch(`${API_BASE}/jobs/${jobId}`);
    if (!response.ok) throw new Error('Failed to fetch job');
    return response.json();
  }

  async cancelJob(jobId: string): Promise<void> {
    const response = await fetch(`${API_BASE}/jobs/${jobId}/cancel`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to cancel job');
  }

  // Branch management
  async getBranches(): Promise<Branch[]> {
    const response = await fetch(`${API_BASE}/branches`);
    if (!response.ok) throw new Error('Failed to fetch branches');
    return response.json();
  }

  async createBranch(config: {
    name: string;
    description: string;
    base_snapshot_id: string;
  }): Promise<Branch> {
    const response = await fetch(`${API_BASE}/branches`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });
    if (!response.ok) throw new Error('Failed to create branch');
    return response.json();
  }

  async deleteBranch(branchId: string): Promise<void> {
    const response = await fetch(`${API_BASE}/branches/${branchId}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete branch');
  }

  // Plugin management
  async getPlugins(): Promise<AnalysisPlugin[]> {
    const response = await fetch(`${API_BASE}/plugins`);
    if (!response.ok) throw new Error('Failed to fetch plugins');
    return response.json();
  }

  async runAnalysis(config: {
    plugin_id: string;
    session_id?: string;
    job_id?: string;
    config?: Record<string, any>;
  }): Promise<AnalysisResult> {
    const response = await fetch(`${API_BASE}/analysis`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });
    if (!response.ok) throw new Error('Failed to run analysis');
    return response.json();
  }

  async getAnalysisResults(sessionId?: string, jobId?: string): Promise<AnalysisResult[]> {
    const params = new URLSearchParams();
    if (sessionId) params.append('session_id', sessionId);
    if (jobId) params.append('job_id', jobId);
    
    const response = await fetch(`${API_BASE}/analysis?${params}`);
    if (!response.ok) throw new Error('Failed to fetch analysis results');
    return response.json();
  }

  // Diff operations
  async generateDiff(config: {
    left_snapshot_id: string;
    right_snapshot_id: string;
    format?: string;
    include_metadata?: boolean;
  }): Promise<any> {
    const response = await fetch(`${API_BASE}/diff`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });
    if (!response.ok) throw new Error('Failed to generate diff');
    return response.json();
  }

  // WebSocket connections
  connectTimelineStream(onEvent: (event: TimelineEvent) => void): WebSocket | null {
    try {
      const ws = new WebSocket(`${WS_BASE}/timeline`);
      
      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          if (message.type === 'timeline_event') {
            onEvent(message.data);
          }
        } catch (err) {
          console.error('Failed to parse timeline message:', err);
        }
      };

      ws.onerror = (error) => {
        console.error('Timeline WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('Timeline WebSocket connection closed');
      };

      return ws;
    } catch (err) {
      console.error('Failed to connect to timeline stream:', err);
      return null;
    }
  }

  connectJobStatus(onUpdate: (update: JobStatusUpdate) => void): WebSocket | null {
    try {
      const ws = new WebSocket(`${WS_BASE}/job-status`);
      
      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          if (message.type === 'job_status') {
            onUpdate(message.data);
          }
        } catch (err) {
          console.error('Failed to parse job status message:', err);
        }
      };

      ws.onerror = (error) => {
        console.error('Job status WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('Job status WebSocket connection closed');
      };

      return ws;
    } catch (err) {
      console.error('Failed to connect to job status stream:', err);
      return null;
    }
  }

  connectAnalysisResults(onResult: (result: AnalysisResult) => void): WebSocket | null {
    try {
      const ws = new WebSocket(`${WS_BASE}/analysis-status`);
      
      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          if (message.type === 'analysis_result') {
            onResult(message.data);
          }
        } catch (err) {
          console.error('Failed to parse analysis result message:', err);
        }
      };

      ws.onerror = (error) => {
        console.error('Analysis results WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('Analysis results WebSocket connection closed');
      };

      return ws;
    } catch (err) {
      console.error('Failed to connect to analysis results stream:', err);
      return null;
    }
  }

  // Engine stats
  async getEngineStats(): Promise<any> {
    const response = await fetch(`${API_BASE}/engine/stats`);
    if (!response.ok) throw new Error('Failed to fetch engine stats');
    return response.json();
  }

  // Cleanup operations
  async cleanup(config: {
    older_than_days?: number;
    job_status?: string;
    dry_run?: boolean;
  }): Promise<any> {
    const response = await fetch(`${API_BASE}/engine/cleanup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });
    if (!response.ok) throw new Error('Failed to perform cleanup');
    return response.json();
  }

  // Snapshot management
  async getSnapshots(): Promise<any[]> {
    const response = await fetch(`${API_BASE}/snapshots`);
    if (!response.ok) throw new Error('Failed to fetch snapshots');
    return response.json();
  }
}

export const api = new ApiService();

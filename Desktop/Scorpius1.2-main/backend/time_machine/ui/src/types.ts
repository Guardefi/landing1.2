// Type definitions for Time Machine UI

export interface TimelineEvent {
  id: string;
  timestamp: string;
  event_type: string;
  description: string;
  metadata: Record<string, any>;
  session_id?: string;
  job_id?: string;
}

export interface ReplayJob {
  id: string;
  status: string;
  start_block: number;
  end_block: number;
  vm_type: string;
  created_at: string;
  completed_at?: string;
  error?: string;
  progress?: number;
  config: Record<string, any>;
}

export interface Branch {
  id: string;
  name: string;
  description: string;
  created_at: string;
  base_snapshot_id: string;
  head_snapshot_id: string;
  author: string;
  tags: string[];
  is_active: boolean;
}

export interface Snapshot {
  id: string;
  job_id: string;
  block_number: number;
  state_root: string;
  created_at: string;
  size_bytes: number;
  compression_ratio: number;
  metadata: Record<string, any>;
}

export interface Patch {
  id: string;
  name: string;
  description: string;
  patch_type: 'state' | 'code' | 'storage' | 'balance';
  target_address?: string;
  operations: PatchOperation[];
  created_at: string;
  author: string;
  is_macro: boolean;
}

export interface PatchOperation {
  op_type: 'set' | 'delete' | 'increment' | 'append';
  path: string;
  value?: any;
  condition?: string;
}

export interface ForensicSession {
  id: string;
  name: string;
  description: string;
  created_at: string;
  status: 'active' | 'completed' | 'archived';
  base_snapshot_id: string;
  current_snapshot_id: string;
  manipulations: StateManipulation[];
}

export interface StateManipulation {
  id: string;
  session_id: string;
  patch_id: string;
  applied_at: string;
  result_snapshot_id: string;
  notes?: string;
}

export interface AnalysisPlugin {
  id: string;
  name: string;
  version: string;
  description: string;
  author: string;
  plugin_type: 'transaction' | 'state' | 'gas' | 'security' | 'defi';
  config_schema: Record<string, any>;
  is_enabled: boolean;
}

export interface AnalysisResult {
  id: string;
  plugin_id: string;
  session_id?: string;
  job_id?: string;
  created_at: string;
  completed_at?: string;
  status: 'running' | 'completed' | 'failed';
  results: Record<string, any>;
  metadata: Record<string, any>;
  score?: number;
  alerts?: Alert[];
}

export interface Alert {
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  details?: Record<string, any>;
}

export interface WebSocketMessage {
  type: 'timeline_event' | 'job_status' | 'analysis_result';
  data: any;
}

export interface JobStatusUpdate {
  job_id: string;
  status: string;
  progress?: number;
  error?: string;
}

export interface ApiError {
  detail: string;
  code?: string;
  context?: Record<string, any>;
}

/**
 * Plugin Management API Service
 * Handles individual plugin toggle functionality and configuration
 */

export interface PluginConfig {
  [key: string]: any;
}

export interface PluginStatus {
  name: string;
  enabled: boolean;
  initialized: boolean;
  version: string;
  description: string;
  capabilities: Record<string, any>;
  last_used?: string;
  total_scans: number;
  success_rate: number;
  config: PluginConfig;
}

export interface PluginToggleRequest {
  enabled: boolean;
}

export interface PluginConfigRequest {
  config: PluginConfig;
}

export interface PluginToggleResponse {
  plugin_name: string;
  enabled: boolean;
  status: string;
  message: string;
}

export interface PluginListResponse {
  plugins: PluginStatus[];
  total_count: number;
  enabled_count: number;
}

export interface EnabledPluginsResponse {
  enabled_plugins: string[];
  count: number;
  timestamp: string;
}

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';

export class PluginManagementAPI {
  private static async request<T>(
    endpoint: string,
    options: RequestInit = {},
  ): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer scorpius-api-token',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Plugin Management API Error: ${response.status} - ${error}`);
    }

    return response.json();
  }

  // Get all plugin statuses
  static async getAllPlugins(): Promise<PluginListResponse> {
    return this.request<PluginListResponse>('/v1/plugin-management/plugins');
  }

  // Get specific plugin status
  static async getPluginStatus(pluginName: string): Promise<PluginStatus> {
    return this.request<PluginStatus>(`/v1/plugin-management/plugins/${pluginName}/status`);
  }

  // Toggle plugin on/off
  static async togglePlugin(
    pluginName: string,
    enabled: boolean,
  ): Promise<PluginToggleResponse> {
    return this.request<PluginToggleResponse>(
      `/v1/plugin-management/plugins/${pluginName}/toggle`,
      {
        method: 'POST',
        body: JSON.stringify({ enabled }),
      },
    );
  }

  // Update plugin configuration
  static async updatePluginConfig(
    pluginName: string,
    config: PluginConfig,
  ): Promise<any> {
    return this.request(`/v1/plugin-management/plugins/${pluginName}/config`, {
      method: 'PUT',
      body: JSON.stringify({ config }),
    });
  }

  // Test plugin functionality
  static async testPlugin(pluginName: string): Promise<any> {
    return this.request(`/v1/plugin-management/plugins/${pluginName}/test`, {
      method: 'POST',
    });
  }

  // Get list of enabled plugins
  static async getEnabledPlugins(): Promise<EnabledPluginsResponse> {
    return this.request<EnabledPluginsResponse>('/v1/plugin-management/plugins/enabled');
  }

  // Bulk toggle plugins
  static async bulkTogglePlugins(
    pluginToggles: Record<string, boolean>,
  ): Promise<PluginToggleResponse[]> {
    const promises = Object.entries(pluginToggles).map(([pluginName, enabled]) =>
      this.togglePlugin(pluginName, enabled),
    );

    return Promise.all(promises);
  }

  // Get plugin capabilities by name
  static async getPluginCapabilities(pluginName: string): Promise<Record<string, any>> {
    const status = await this.getPluginStatus(pluginName);
    return status.capabilities;
  }

  // Check if plugin supports specific scan type
  static async pluginSupportsScansType(
    pluginName: string,
    scanType: 'static' | 'dynamic' | 'symbolic',
  ): Promise<boolean> {
    try {
      const capabilities = await this.getPluginCapabilities(pluginName);
      
      switch (scanType) {
        case 'static':
          return capabilities.static_analysis || false;
        case 'dynamic':
          return capabilities.dynamic_analysis || false;
        case 'symbolic':
          return capabilities.symbolic_execution || false;
        default:
          return false;
      }
    } catch (error) {
      console.error(`Error checking plugin capabilities: ${error}`);
      return false;
    }
  }

  // Get recommended plugins for scan type
  static async getRecommendedPlugins(
    scanType: 'quick' | 'deep' | 'comprehensive',
  ): Promise<string[]> {
    try {
      const allPlugins = await this.getAllPlugins();
      const enabledPlugins = allPlugins.plugins.filter(p => p.enabled);

      switch (scanType) {
        case 'quick':
          // For quick scans, use fast static analysis tools
          return enabledPlugins
            .filter(p => 
              p.capabilities.static_analysis && 
              !p.capabilities.symbolic_execution
            )
            .map(p => p.name);

        case 'deep':
          // For deep scans, use both static and symbolic execution
          return enabledPlugins
            .filter(p => 
              p.capabilities.static_analysis || 
              p.capabilities.symbolic_execution
            )
            .map(p => p.name);

        case 'comprehensive':
          // For comprehensive scans, use all available enabled plugins
          return enabledPlugins.map(p => p.name);

        default:
          return [];
      }
    } catch (error) {
      console.error(`Error getting recommended plugins: ${error}`);
      return [];
    }
  }
}

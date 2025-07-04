/**
 * Settings Service API Client
 * Handles configuration management for the Scorpius platform
 */

// Base configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export interface ConfigCategory {
  name: string;
  description: string;
  icon: string;
  order: number;
}

export interface ConfigVariable {
  key: string;
  value?: string;
  default_value?: string;
  description: string;
  category: string;
  is_public: boolean;
  is_required: boolean;
  is_secret: boolean;
  data_type: string;
  validation_pattern?: string;
  options?: string[];
  has_value?: boolean;
}

export interface SettingsSchema {
  categories: ConfigCategory[];
  variables: ConfigVariable[];
}

export interface SettingsResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  timestamp: string;
}

export interface ValidationResult {
  key: string;
  category: string;
  required: boolean;
  has_value: boolean;
  valid: boolean;
  issues: string[];
}

export interface ValidationSummary {
  total_variables: number;
  valid_variables: number;
  invalid_variables: number;
  error_count: number;
  warning_count: number;
}

export interface ConfigUpdate {
  updates: Record<string, any>;
}

export class SettingsService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Get service health status
   */
  async getHealth(): Promise<SettingsResponse> {
    const response = await fetch(`${this.baseUrl}/api/settings/health`);
    return await response.json();
  }

  /**
   * Get service capabilities
   */
  async getCapabilities(): Promise<SettingsResponse> {
    const response = await fetch(`${this.baseUrl}/api/settings/capabilities`);
    return await response.json();
  }

  /**
   * Get complete configuration schema
   */
  async getSchema(): Promise<SettingsResponse<SettingsSchema>> {
    const response = await fetch(`${this.baseUrl}/api/settings/schema`);
    return await response.json();
  }

  /**
   * Get configuration categories
   */
  async getCategories(): Promise<SettingsResponse<{ categories: ConfigCategory[] }>> {
    const response = await fetch(`${this.baseUrl}/api/settings/categories`);
    return await response.json();
  }

  /**
   * Get configuration variables
   */
  async getVariables(
    category?: string,
    publicOnly: boolean = false
  ): Promise<SettingsResponse<{ variables: ConfigVariable[] }>> {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (publicOnly) params.append('public_only', 'true');
    
    const response = await fetch(`${this.baseUrl}/api/settings/variables?${params}`);
    return await response.json();
  }

  /**
   * Get specific configuration variable
   */
  async getVariable(key: string): Promise<SettingsResponse<{ variable: ConfigVariable }>> {
    const response = await fetch(`${this.baseUrl}/api/settings/variables/${key}`);
    return await response.json();
  }

  /**
   * Update specific configuration variable
   */
  async updateVariable(key: string, value: any): Promise<SettingsResponse> {
    const response = await fetch(`${this.baseUrl}/api/settings/variables/${key}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ value }),
    });
    return await response.json();
  }

  /**
   * Delete configuration variable
   */
  async deleteVariable(key: string): Promise<SettingsResponse> {
    const response = await fetch(`${this.baseUrl}/api/settings/variables/${key}`, {
      method: 'DELETE',
    });
    return await response.json();
  }

  /**
   * Update multiple configuration variables
   */
  async updateMultipleVariables(updates: Record<string, any>): Promise<SettingsResponse> {
    const response = await fetch(`${this.baseUrl}/api/settings/variables`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ updates }),
    });
    return await response.json();
  }

  /**
   * Export current configuration (public values only)
   */
  async exportConfiguration(): Promise<SettingsResponse> {
    const response = await fetch(`${this.baseUrl}/api/settings/export`);
    return await response.json();
  }

  /**
   * Create environment blueprint
   */
  async createBlueprint(): Promise<SettingsResponse<{ blueprint: string }>> {
    const response = await fetch(`${this.baseUrl}/api/settings/blueprint`, {
      method: 'POST',
    });
    return await response.json();
  }

  /**
   * Validate current configuration
   */
  async validateConfiguration(): Promise<SettingsResponse<{
    validation_results: ValidationResult[];
    summary: ValidationSummary;
    errors: string[];
    warnings: string[];
  }>> {
    const response = await fetch(`${this.baseUrl}/api/settings/validate`);
    return await response.json();
  }

  /**
   * Get variables by category (helper method)
   */
  async getVariablesByCategory(): Promise<Record<string, ConfigVariable[]>> {
    const response = await this.getVariables();
    if (!response.success || !response.data) {
      return {};
    }

    const variablesByCategory: Record<string, ConfigVariable[]> = {};
    response.data.variables.forEach(variable => {
      if (!variablesByCategory[variable.category]) {
        variablesByCategory[variable.category] = [];
      }
      variablesByCategory[variable.category].push(variable);
    });

    return variablesByCategory;
  }

  /**
   * Get public variables only (safe for frontend)
   */
  async getPublicVariables(): Promise<SettingsResponse<{ variables: ConfigVariable[] }>> {
    return this.getVariables(undefined, true);
  }

  /**
   * Download .env blueprint file
   */
  async downloadBlueprint(): Promise<void> {
    const response = await this.createBlueprint();
    if (response.success && response.data?.blueprint) {
      const blob = new Blob([response.data.blueprint], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = '.env';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }
  }

  /**
   * Get configuration summary
   */
  async getConfigurationSummary(): Promise<{
    categories: ConfigCategory[];
    variablesByCategory: Record<string, ConfigVariable[]>;
    validationSummary?: ValidationSummary;
  }> {
    const [schemaResponse, validationResponse] = await Promise.allSettled([
      this.getSchema(),
      this.validateConfiguration(),
    ]);

    const categories: ConfigCategory[] = 
      schemaResponse.status === 'fulfilled' && schemaResponse.value.success
        ? schemaResponse.value.data?.categories || []
        : [];

    const variablesByCategory: Record<string, ConfigVariable[]> = 
      schemaResponse.status === 'fulfilled' && schemaResponse.value.success
        ? schemaResponse.value.data?.variables.reduce((acc, variable) => {
            if (!acc[variable.category]) {
              acc[variable.category] = [];
            }
            acc[variable.category].push(variable);
            return acc;
          }, {} as Record<string, ConfigVariable[]>) || {}
        : {};

    const validationSummary: ValidationSummary | undefined = 
      validationResponse.status === 'fulfilled' && validationResponse.value.success
        ? validationResponse.value.data?.summary
        : undefined;

    return {
      categories,
      variablesByCategory,
      validationSummary,
    };
  }
}

// Export singleton instance
export const settingsService = new SettingsService(); 
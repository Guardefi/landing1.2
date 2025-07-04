export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

class ApiClient {
  private token: string | null;
  constructor(private baseUrl: string = API_BASE_URL) {
    this.token = localStorage.getItem("auth_token");
  }

  setAuthToken(token: string) {
    this.token = token;
    localStorage.setItem("auth_token", token);
  }

  clearAuthToken() {
    this.token = null;
    localStorage.removeItem("auth_token");
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    try {
      const res = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          ...(this.token ? { Authorization: `Bearer ${this.token}` } : {}),
          ...options.headers,
        },
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        return { success: false, error: data.error || res.statusText };
      }
      return { success: true, data };
    } catch (err) {
      return { success: false, error: (err as Error).message };
    }
  }

  get<T>(endpoint: string) {
    return this.request<T>(endpoint, { method: "GET" });
  }
  post<T>(endpoint: string, body?: any) {
    return this.request<T>(endpoint, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    });
  }
  put<T>(endpoint: string, body?: any) {
    return this.request<T>(endpoint, {
      method: "PUT",
      body: body ? JSON.stringify(body) : undefined,
    });
  }
  delete<T>(endpoint: string) {
    return this.request<T>(endpoint, { method: "DELETE" });
  }
}

const apiClient = new ApiClient();
export default apiClient;
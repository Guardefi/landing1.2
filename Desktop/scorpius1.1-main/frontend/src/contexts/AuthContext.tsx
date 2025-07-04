import React, {
  createContext,
  useContext,
  useReducer,
  useEffect,
  useCallback,
  useMemo,
  ReactNode,
} from "react";
import { z } from "zod";
import apiClient from "@/lib/api";

// =============================================================================
// TYPES AND SCHEMAS
// =============================================================================

const UserSchema = z.object({
  id: z.string(),
  email: z.string().email(),
  username: z.string(),
  firstName: z.string().optional(),
  lastName: z.string().optional(),
  avatar: z.string().url().optional(),
  roles: z.array(z.string()),
  permissions: z.array(z.string()),
  isActive: z.boolean(),
  isVerified: z.boolean(),
  lastLogin: z.string().optional(),
  createdAt: z.string(),
  updatedAt: z.string(),
  settings: z.record(z.any()).optional(),
  subscription: z
    .object({
      tier: z.enum(["free", "pro", "enterprise"]),
      expiresAt: z.string().optional(),
      features: z.array(z.string()),
    })
    .optional(),
});

export type User = z.infer<typeof UserSchema>;

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  sessionExpiry: number | null;
  lastActivity: number;
  requiresTwoFactor: boolean;
  loginAttempts: number;
  isLocked: boolean;
  lockoutExpiry: number | null;
}

export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
  twoFactorCode?: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  firstName?: string;
  lastName?: string;
  acceptTerms: boolean;
  marketingOptIn?: boolean;
}

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  user: any;
}

interface AuthTokens {
  access_token: string;
  refresh_token: string;
  expires_in: number;
}

export interface AuthContextValue extends AuthState {
  login: (credentials: LoginCredentials) => Promise<{
    success: boolean;
    error?: string;
    requiresTwoFactor?: boolean;
  }>;
  register: (
    data: RegisterData,
  ) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  refreshToken: () => Promise<boolean>;
  updateUser: (updates: Partial<User>) => Promise<boolean>;
  checkPermission: (permission: string) => boolean;
  hasRole: (role: string) => boolean;
  hasAnyRole: (roles: string[]) => boolean;
  updateActivity: () => void;
  resetPassword: (
    email: string,
  ) => Promise<{ success: boolean; error?: string }>;
  confirmPasswordReset: (
    token: string,
    newPassword: string,
  ) => Promise<{ success: boolean; error?: string }>;
  verifyLicense: (key: string) => Promise<{ success: boolean; error?: string }>;
  verifyEmail: (token: string) => Promise<{ success: boolean; error?: string }>;
  enable2FA: () => Promise<{
    success: boolean;
    qrCode?: string;
    backupCodes?: string[];
    error?: string;
  }>;
  disable2FA: (code: string) => Promise<{ success: boolean; error?: string }>;
  updateSettings: (settings: Record<string, any>) => Promise<boolean>;
}

// =============================================================================
// ACTION TYPES
// =============================================================================

type AuthAction =
  | { type: "SET_LOADING"; payload: boolean }
  | { type: "SET_USER"; payload: User | null }
  | { type: "SET_ERROR"; payload: string | null }
  | { type: "SET_AUTHENTICATED"; payload: boolean }
  | { type: "SET_SESSION_EXPIRY"; payload: number | null }
  | { type: "UPDATE_ACTIVITY" }
  | { type: "SET_TWO_FACTOR_REQUIRED"; payload: boolean }
  | { type: "INCREMENT_LOGIN_ATTEMPTS" }
  | { type: "RESET_LOGIN_ATTEMPTS" }
  | {
      type: "SET_LOCKED";
      payload: { isLocked: boolean; lockoutExpiry?: number };
    }
  | { type: "UPDATE_USER"; payload: Partial<User> };

// =============================================================================
// REDUCER
// =============================================================================

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
  sessionExpiry: null,
  lastActivity: Date.now(),
  requiresTwoFactor: false,
  loginAttempts: 0,
  isLocked: false,
  lockoutExpiry: null,
};

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case "SET_LOADING":
      return { ...state, isLoading: action.payload };

    case "SET_USER":
      return {
        ...state,
        user: action.payload,
        isAuthenticated: !!action.payload,
        error: null,
      };

    case "SET_ERROR":
      return { ...state, error: action.payload, isLoading: false };

    case "SET_AUTHENTICATED":
      return { ...state, isAuthenticated: action.payload };

    case "SET_SESSION_EXPIRY":
      return { ...state, sessionExpiry: action.payload };

    case "UPDATE_ACTIVITY":
      return { ...state, lastActivity: Date.now() };

    case "SET_TWO_FACTOR_REQUIRED":
      return { ...state, requiresTwoFactor: action.payload };

    case "INCREMENT_LOGIN_ATTEMPTS":
      const newAttempts = state.loginAttempts + 1;
      const shouldLock = newAttempts >= 5;
      return {
        ...state,
        loginAttempts: newAttempts,
        isLocked: shouldLock,
        lockoutExpiry: shouldLock ? Date.now() + 15 * 60 * 1000 : null, // 15 minutes
      };

    case "RESET_LOGIN_ATTEMPTS":
      return {
        ...state,
        loginAttempts: 0,
        isLocked: false,
        lockoutExpiry: null,
      };

    case "SET_LOCKED":
      return {
        ...state,
        isLocked: action.payload.isLocked,
        lockoutExpiry: action.payload.lockoutExpiry || null,
      };

    case "UPDATE_USER":
      return {
        ...state,
        user: state.user ? { ...state.user, ...action.payload } : null,
      };

    default:
      return state;
  }
}

// =============================================================================
// CONTEXT CREATION
// =============================================================================

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// =============================================================================
// PROVIDER COMPONENT
// =============================================================================

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // =============================================================================
  // UTILITY FUNCTIONS
  // =============================================================================

  const setError = (error: string | null) => {
    dispatch({ type: "SET_ERROR", payload: error });
  };

  const setLoading = (loading: boolean) => {
    dispatch({ type: "SET_LOADING", payload: loading });
  };

  const updateActivity = useCallback(() => {
    dispatch({ type: "UPDATE_ACTIVITY" });
  }, []);

  // =============================================================================
  // AUTHENTICATION FUNCTIONS
  // =============================================================================

  const login = useCallback(
    async (credentials: LoginCredentials) => {
      if (
        state.isLocked &&
        state.lockoutExpiry &&
        Date.now() < state.lockoutExpiry
      ) {
        const remainingTime = Math.ceil(
          (state.lockoutExpiry - Date.now()) / 1000 / 60,
        );
        return {
          success: false,
          error: `Account locked. Try again in ${remainingTime} minutes.`,
        };
      }

      setLoading(true);
      setError(null);

      try {
        const response = await apiClient.post<LoginResponse>("/auth/login", {
          email: credentials.email,
          password: credentials.password,
          remember_me: credentials.rememberMe ?? false,
        });

        if (!response.success || !response.data) {
          throw new Error(response.error || "Login failed");
        }

        const { access_token, refresh_token, expires_in, user } = response.data;

        const userData: User = UserSchema.parse({
          ...user,
        });

        apiClient.setAuthToken(access_token);
        localStorage.setItem("refresh_token", refresh_token);
        localStorage.setItem("user", JSON.stringify(userData));

        dispatch({ type: "SET_USER", payload: userData });
        dispatch({ type: "RESET_LOGIN_ATTEMPTS" });
        dispatch({
          type: "SET_SESSION_EXPIRY",
          payload: Date.now() + expires_in * 1000,
        });

        return { success: true };
      } catch (error) {
        dispatch({ type: "INCREMENT_LOGIN_ATTEMPTS" });
        const errorMessage =
          error instanceof Error ? error.message : "Login failed";
        setError(errorMessage);
        return { success: false, error: errorMessage };
      } finally {
        setLoading(false);
      }
    },
    [state.isLocked, state.lockoutExpiry],
  );

  const register = useCallback(async (data: RegisterData) => {
    setLoading(true);
    setError(null);

    try {
      // For now, simulate successful registration
      // TODO: Implement actual registration API call when backend is ready
      const mockUser: User = {
        id: "new-user-" + Date.now(),
        email: data.email,
        username: data.username,
        firstName: data.firstName || "",
        lastName: data.lastName || "",
        roles: ["user"],
        permissions: ["read"],
        isActive: true,
        isVerified: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        subscription: {
          tier: "free",
          features: [],
        },
      };

      dispatch({ type: "SET_USER", payload: mockUser });
      return { success: true };
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Registration failed";
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    apiClient.post("/auth/logout").catch(() => {});
    apiClient.clearAuthToken();
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    dispatch({ type: "SET_USER", payload: null });
    dispatch({ type: "SET_SESSION_EXPIRY", payload: null });
    dispatch({ type: "SET_TWO_FACTOR_REQUIRED", payload: false });
    dispatch({ type: "RESET_LOGIN_ATTEMPTS" });
  }, []);

  const refreshToken = useCallback(async (): Promise<boolean> => {
    try {
      const response = await apiClient.post<AuthTokens>("/auth/refresh");
      return response.success;
    } catch (error) {
      logout();
      return false;
    }
  }, [logout]);

  const loadUserProfile = async () => {
    try {
      // First try to load from localStorage (for mock auth)
      const storedUser = localStorage.getItem("user");
      if (storedUser) {
        try {
          const user = JSON.parse(storedUser);
          const validatedUser = UserSchema.parse(user);
          dispatch({ type: "SET_USER", payload: validatedUser });
          return;
        } catch (parseError) {
          console.error("Failed to parse stored user:", parseError);
          localStorage.removeItem("user");
          localStorage.removeItem("auth_token");
        }
      }

      // If no stored user, try to get from API
      const profileRes = await apiClient.get<User>("/auth/me");
      if (!profileRes.success || !profileRes.data) return;
      const userData = profileRes.data;

      // Transform API response to User schema format if needed
      const user: User = {
        id: userData.id || "mock-user",
        email: userData.email || "user@example.com",
        username: userData.name || userData.username || "user",
        firstName: userData.firstName || userData.name?.split(" ")[0] || "",
        lastName: userData.lastName || userData.name?.split(" ")[1] || "",
        roles: [userData.role || "user"],
        permissions:
          userData.role === "admin" ? ["read", "write", "admin"] : ["read"],
        isActive: true,
        isVerified: true,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        subscription: {
          tier: userData.tier || "free",
          features:
            userData.tier === "enterprise" ? ["advanced-analytics"] : [],
        },
      };

      const validatedUser = UserSchema.parse(user);
      dispatch({ type: "SET_USER", payload: validatedUser });
    } catch (error) {
      console.error("Failed to load user profile:", error);
      throw error;
    }
  };

  // =============================================================================
  // USER MANAGEMENT FUNCTIONS
  // =============================================================================

  const updateUser = useCallback(
    async (updates: Partial<User>): Promise<boolean> => {
      try {
        const response = await apiClient.put<User>("/auth/me", updates);

        if (response.success && response.data) {
          const validatedUser = UserSchema.parse(response.data);
          dispatch({ type: "SET_USER", payload: validatedUser });
          return true;
        }
        return false;
      } catch (error) {
        console.error("Failed to update user:", error);
        return false;
      }
    },
    [],
  );

  const updateSettings = useCallback(
    async (settings: Record<string, any>): Promise<boolean> => {
      try {
        const response = await apiClient.put("/auth/settings", { settings });

        if (response.success) {
          dispatch({ type: "UPDATE_USER", payload: { settings } });
          return true;
        }
        return false;
      } catch (error) {
        console.error("Failed to update settings:", error);
        return false;
      }
    },
    [],
  );

  // =============================================================================
  // PERMISSION AND ROLE FUNCTIONS
  // =============================================================================

  const checkPermission = useCallback(
    (permission: string): boolean => {
      return state.user?.permissions?.includes(permission) ?? false;
    },
    [state.user?.permissions],
  );

  const hasRole = useCallback(
    (role: string): boolean => {
      return state.user?.roles?.includes(role) ?? false;
    },
    [state.user?.roles],
  );

  const hasAnyRole = useCallback(
    (roles: string[]): boolean => {
      return roles.some((role) => hasRole(role));
    },
    [hasRole],
  );

  // =============================================================================
  // PASSWORD AND 2FA FUNCTIONS
  // =============================================================================

  const resetPassword = useCallback(async (email: string) => {
    try {
      const response = await apiClient.post("/auth/reset-password", { email });
      return { success: response.success, error: response.error };
    } catch (error) {
      return { success: false, error: "Failed to send reset email" };
    }
  }, []);

  const confirmPasswordReset = useCallback(
    async (token: string, newPassword: string) => {
      try {
        const response = await apiClient.post("/auth/confirm-reset", {
          token,
          password: newPassword,
        });
        return { success: response.success, error: response.error };
      } catch (error) {
        return { success: false, error: "Failed to reset password" };
      }
    },
    [],
  );

  const verifyLicense = useCallback(async (key: string) => {
    try {
      const response = await apiClient.post("/license/verify", {
        license_key: key,
      });
      return { success: response.success, error: response.error };
    } catch (error) {
      return { success: false, error: "License verification failed" };
    }
  }, []);

  const verifyEmail = useCallback(async (token: string) => {
    try {
      const response = await apiClient.post("/auth/verify-email", { token });

      if (response.success) {
        dispatch({ type: "UPDATE_USER", payload: { isVerified: true } });
      }

      return { success: response.success, error: response.error };
    } catch (error) {
      return { success: false, error: "Email verification failed" };
    }
  }, []);

  const enable2FA = useCallback(async () => {
    try {
      const response = await apiClient.post<{
        qr_code: string;
        backup_codes: string[];
      }>("/auth/2fa/enable");
      return {
        success: response.success,
        qrCode: response.data?.qr_code,
        backupCodes: response.data?.backup_codes,
        error: response.error,
      };
    } catch (error) {
      return { success: false, error: "Failed to enable 2FA" };
    }
  }, []);

  const disable2FA = useCallback(async (code: string) => {
    try {
      const response = await apiClient.post("/auth/2fa/disable", { code });
      return { success: response.success, error: response.error };
    } catch (error) {
      return { success: false, error: "Failed to disable 2FA" };
    }
  }, []);

  // =============================================================================
  // EFFECTS
  // =============================================================================

  // Initialize authentication state
  useEffect(() => {
    const initAuth = async () => {
      try {
        const token = localStorage.getItem("auth_token");
        const storedUser = localStorage.getItem("user");

        if (token && storedUser) {
          try {
            const user = JSON.parse(storedUser);
            const validatedUser = UserSchema.parse(user);
            dispatch({ type: "SET_USER", payload: validatedUser });
          } catch (error) {
            console.error("Failed to parse stored user:", error);
            localStorage.removeItem("auth_token");
            localStorage.removeItem("user");
          }
        }
      } catch (error) {
        console.error("Auth initialization failed:", error);
      } finally {
        setLoading(false);
      }
    };

    initAuth();

    // Fallback timeout to ensure loading never gets stuck
    const timeout = setTimeout(() => {
      setLoading(false);
    }, 3000);

    return () => clearTimeout(timeout);
  }, []);

  // Activity tracking
  useEffect(() => {
    const handleActivity = () => updateActivity();
    const events = [
      "mousedown",
      "mousemove",
      "keypress",
      "scroll",
      "touchstart",
    ];

    events.forEach((event) => {
      document.addEventListener(event, handleActivity, { passive: true });
    });

    return () => {
      events.forEach((event) => {
        document.removeEventListener(event, handleActivity);
      });
    };
  }, []);

  // Session timeout handling
  useEffect(() => {
    if (!state.sessionExpiry || !state.isAuthenticated) return;

    const checkSession = () => {
      if (Date.now() >= state.sessionExpiry!) {
        logout();
      }
    };

    const interval = setInterval(checkSession, 60000); // Check every minute
    return () => clearInterval(interval);
  }, [state.sessionExpiry, state.isAuthenticated]);

  // Lockout timer
  useEffect(() => {
    if (!state.isLocked || !state.lockoutExpiry) return;

    const timer = setTimeout(() => {
      dispatch({ type: "SET_LOCKED", payload: { isLocked: false } });
    }, state.lockoutExpiry - Date.now());

    return () => clearTimeout(timer);
  }, [state.isLocked, state.lockoutExpiry]);

  // =============================================================================
  // CONTEXT VALUE
  // =============================================================================

  const contextValue: AuthContextValue = useMemo(
    () => ({
      ...state,
      login,
      register,
      logout,
      refreshToken,
      updateUser,
      checkPermission,
      hasRole,
      hasAnyRole,
      updateActivity,
      resetPassword,
      confirmPasswordReset,
      verifyLicense,
      verifyEmail,
      enable2FA,
      disable2FA,
      updateSettings,
    }),
    [
      state,
      login,
      register,
      logout,
      refreshToken,
      updateUser,
      checkPermission,
      hasRole,
      hasAnyRole,
      updateActivity,
      resetPassword,
      confirmPasswordReset,
      verifyLicense,
      verifyEmail,
      enable2FA,
      disable2FA,
      updateSettings,
    ],
  );

  return (
    <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>
  );
}

// =============================================================================
// HOOK
// =============================================================================

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

export default AuthContext;

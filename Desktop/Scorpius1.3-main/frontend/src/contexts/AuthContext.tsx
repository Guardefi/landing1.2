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
import { authApi, apiClient } from "@/lib/api";

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
      tier: z.enum(["PRO", "ELITE", "ENTERPRISE"]),
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

    case "INCREMENT_LOGIN_ATTEMPTS": {
      const newAttempts = state.loginAttempts + 1;
      const shouldLock = newAttempts >= 5;
      return {
        ...state,
        loginAttempts: newAttempts,
        isLocked: shouldLock,
        lockoutExpiry: shouldLock ? Date.now() + 15 * 60 * 1000 : null, // 15 minutes
      };
    }

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
        const response = await authApi.login({
          email: credentials.email,
          password: credentials.password,
        });

        // Transform the API response to match our User schema
        const fullName = response.user.full_name || response.user.name || "";
        const nameParts = fullName.split(" ");
        
        // Normalize tier name to match frontend expectations
        const normalizeTier = (tier: string): "PRO" | "ELITE" | "ENTERPRISE" => {
          const lowerTier = tier.toLowerCase();
          if (lowerTier === "enterprise" || lowerTier === "admin") return "ENTERPRISE";
          if (lowerTier === "elite") return "ELITE";
          return "PRO"; // Default to PRO for free/pro users
        };
        
        const user: User = {
          id: response.user.id || `user-${Date.now()}`,
          email: response.user.email,
          username:
            response.user.username ||
            fullName ||
            response.user.email.split("@")[0],
          firstName: nameParts[0] || "",
          lastName: nameParts[1] || "",
          roles: [response.user.role || "user"],
          permissions:
            response.user.role === "admin"
              ? ["read", "write", "admin"]
              : ["read"],
          isActive: true,
          isVerified: true,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          subscription: {
            tier: normalizeTier(response.user.tier || "pro"),
            features:
              response.user.tier === "enterprise"
                ? ["advanced-analytics", "priority-support"]
                : [],
          },
        };

        // Store the auth token and user info
        localStorage.setItem("auth_token", response.access_token);
        localStorage.setItem("user", JSON.stringify(user));

        // Set user in context
        dispatch({ type: "SET_USER", payload: user });
        dispatch({ type: "RESET_LOGIN_ATTEMPTS" });

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
      const response = await authApi.register({
        email: data.email,
        password: data.password,
        name:
          `${data.firstName || ""} ${data.lastName || ""}`.trim() ||
          data.username,
        confirmPassword: data.password, // Assuming validation is done in the form
      });

      // Transform the API response to match our User schema
      const fullName = response.user.full_name || response.user.name || "";
      const nameParts = fullName.split(" ");
      const user: User = {
        id: response.user.id || `user-${Date.now()}`,
        email: response.user.email,
        username:
          response.user.username ||
          fullName ||
          response.user.email.split("@")[0],
        firstName: data.firstName || nameParts[0] || "",
        lastName: data.lastName || nameParts[1] || "",
        roles: [response.user.role || "user"],
        permissions:
          response.user.role === "admin"
            ? ["read", "write", "admin"]
            : ["read"],
        isActive: true,
        isVerified: false, // User needs to verify email
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        subscription: {
          tier: response.user.tier === "enterprise" ? "ENTERPRISE" : "PRO",
          features: [],
        },
      };

      // Set user in context
      dispatch({ type: "SET_USER", payload: user });

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
    authApi.logout().catch(console.error);
    localStorage.removeItem("auth_token");
    localStorage.removeItem("user");
    dispatch({ type: "SET_USER", payload: null });
    dispatch({ type: "SET_SESSION_EXPIRY", payload: null });
    dispatch({ type: "SET_TWO_FACTOR_REQUIRED", payload: false });
    dispatch({ type: "RESET_LOGIN_ATTEMPTS" });
  }, []);

  const refreshToken = useCallback(async (): Promise<boolean> => {
    try {
      // For now, just check if we have a valid token
      const token = localStorage.getItem("auth_token");
      return !!token;
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

      // If no stored user, try to get from API (mock)
      const userData = await authApi.getProfile();

      // Transform API response to User schema format if needed
      const fullName = userData.full_name || userData.name || "";
      const nameParts = fullName.split(" ");
      const user: User = {
        id: userData.id || "mock-user",
        email: userData.email || "user@example.com",
        username:
          userData.username ||
          fullName ||
          userData.email?.split("@")[0] ||
          "user",
        firstName: userData.firstName || nameParts[0] || "",
        lastName: userData.lastName || nameParts[1] || "",
        roles: [userData.role || "user"],
        permissions:
          userData.role === "admin" ? ["read", "write", "admin"] : ["read"],
        isActive: true,
        isVerified: true,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        subscription: {
          tier: userData.tier === "enterprise" ? "ENTERPRISE" : "PRO",
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

  // Initialize authentication state - Conservative approach
  useEffect(() => {
    const initAuth = async () => {
      try {
        const token = localStorage.getItem("auth_token");
        const storedUser = localStorage.getItem("user");

        // Only restore session if both token and user data exist and are valid
        if (token && storedUser) {
          try {
            const user = JSON.parse(storedUser);
            const validatedUser = UserSchema.parse(user);

            // Verify token is still valid before auto-login
            try {
              await authApi.getProfile();
              // If API call succeeds, restore the session
              dispatch({ type: "SET_USER", payload: validatedUser });
            } catch (apiError) {
              // Token is invalid, clear storage and require fresh login
              console.log("Token expired or invalid, clearing session");
              localStorage.removeItem("auth_token");
              localStorage.removeItem("user");
            }
          } catch (parseError) {
            console.error("Failed to parse stored user:", parseError);
            localStorage.removeItem("auth_token");
            localStorage.removeItem("user");
          }
        }
        // If no valid session, user will see login page
      } catch (error) {
        console.error("Auth initialization failed:", error);
        // Clear any partial session data on error
        localStorage.removeItem("auth_token");
        localStorage.removeItem("user");
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

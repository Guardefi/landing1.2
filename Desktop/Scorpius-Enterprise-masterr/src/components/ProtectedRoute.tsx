import React, {
  ReactNode,
  useEffect,
  useState,
  useCallback,
  useMemo,
} from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { Loader2, Shield, AlertTriangle, Clock } from "lucide-react";

// Move this outside the component to prevent recreation
const SUBSCRIPTION_TIERS = { free: 0, pro: 1, enterprise: 2 } as const;

// =============================================================================
// TYPES
// =============================================================================

export interface ProtectedRouteProps {
  children: ReactNode;
  roles?: string[];
  permissions?: string[];
  requireAll?: boolean; // If true, user must have ALL roles/permissions, otherwise ANY
  fallback?: ReactNode;
  redirectTo?: string;
  requireVerification?: boolean;
  requireSubscription?: boolean;
  minSubscriptionTier?: "free" | "pro" | "enterprise";
  onUnauthorized?: (reason: string) => void;
}

export interface AccessCheckResult {
  hasAccess: boolean;
  reason?: string;
  code?:
    | "LOADING"
    | "UNAUTHENTICATED"
    | "INSUFFICIENT_ROLES"
    | "INSUFFICIENT_PERMISSIONS"
    | "UNVERIFIED"
    | "INSUFFICIENT_SUBSCRIPTION"
    | "ACCOUNT_LOCKED";
}

// =============================================================================
// ACCESS VERIFICATION COMPONENT
// =============================================================================

function AccessDeniedFallback({
  reason,
  code,
}: {
  reason: string;
  code?: string;
}) {
  const getIcon = () => {
    switch (code) {
      case "LOADING":
        return <Loader2 className="h-8 w-8 animate-spin text-blue-500" />;
      case "ACCOUNT_LOCKED":
        return <Shield className="h-8 w-8 text-red-500" />;
      case "UNVERIFIED":
        return <AlertTriangle className="h-8 w-8 text-yellow-500" />;
      case "INSUFFICIENT_SUBSCRIPTION":
        return <Clock className="h-8 w-8 text-purple-500" />;
      default:
        return <Shield className="h-8 w-8 text-gray-500" />;
    }
  };

  const getTitle = () => {
    switch (code) {
      case "LOADING":
        return "Loading...";
      case "UNAUTHENTICATED":
        return "Authentication Required";
      case "INSUFFICIENT_ROLES":
      case "INSUFFICIENT_PERMISSIONS":
        return "Access Denied";
      case "UNVERIFIED":
        return "Email Verification Required";
      case "INSUFFICIENT_SUBSCRIPTION":
        return "Upgrade Required";
      case "ACCOUNT_LOCKED":
        return "Account Locked";
      default:
        return "Access Restricted";
    }
  };

  const getDescription = () => {
    switch (code) {
      case "LOADING":
        return "Please wait while we verify your access...";
      case "UNAUTHENTICATED":
        return "Please log in to access this page.";
      case "INSUFFICIENT_ROLES":
        return "You do not have the required role to access this resource.";
      case "INSUFFICIENT_PERMISSIONS":
        return "You do not have the required permissions to access this resource.";
      case "UNVERIFIED":
        return "Please verify your email address to access this feature.";
      case "INSUFFICIENT_SUBSCRIPTION":
        return "This feature requires a higher subscription tier.";
      case "ACCOUNT_LOCKED":
        return "Your account has been temporarily locked. Please contact support.";
      default:
        return reason;
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-white shadow-lg">
            {getIcon()}
          </div>

          <h2 className="mt-6 text-3xl font-bold tracking-tight text-gray-900">
            {getTitle()}
          </h2>

          <p className="mt-2 text-sm text-gray-600">{getDescription()}</p>

          <div className="mt-6">
            {code === "UNAUTHENTICATED" && (
              <a
                href="/login"
                className="inline-flex items-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                Sign In
              </a>
            )}

            {code === "UNVERIFIED" && (
              <div className="space-y-3">
                <button
                  type="button"
                  className="inline-flex items-center rounded-md border border-transparent bg-yellow-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:ring-offset-2"
                  onClick={() => {
                    // Trigger resend verification email
                    window.location.href = "/verify-email";
                  }}
                >
                  Resend Verification Email
                </button>
              </div>
            )}

            {code === "INSUFFICIENT_SUBSCRIPTION" && (
              <a
                href="/subscription/upgrade"
                className="inline-flex items-center rounded-md border border-transparent bg-purple-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
              >
                Upgrade Subscription
              </a>
            )}

            {code === "ACCOUNT_LOCKED" && (
              <a
                href="/support"
                className="inline-flex items-center rounded-md border border-transparent bg-red-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
              >
                Contact Support
              </a>
            )}

            {![
              "UNAUTHENTICATED",
              "UNVERIFIED",
              "INSUFFICIENT_SUBSCRIPTION",
              "ACCOUNT_LOCKED",
            ].includes(code || "") && (
              <button
                type="button"
                className="inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                onClick={() => window.history.back()}
              >
                Go Back
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// MAIN PROTECTED ROUTE COMPONENT
// =============================================================================

export function ProtectedRoute({
  children,
  roles = [],
  permissions = [],
  requireAll = false,
  fallback,
  redirectTo = "/login",
  requireVerification = false,
  requireSubscription = false,
  minSubscriptionTier = "free",
  onUnauthorized,
}: ProtectedRouteProps) {
  const auth = useAuth();
  const location = useLocation();
  const [accessCheck, setAccessCheck] = useState<AccessCheckResult>({
    hasAccess: false,
    code: "LOADING",
  });

  // Stable callback for unauthorized handling
  const handleUnauthorized = useCallback(
    (reason: string) => {
      if (onUnauthorized) {
        onUnauthorized(reason);
      }
    },
    [onUnauthorized],
  );

  // Note: SUBSCRIPTION_TIERS is now defined outside the component

  // Create stable references for arrays to prevent unnecessary re-renders
  const stableRoles = useMemo(() => roles, [JSON.stringify(roles)]);
  const stablePermissions = useMemo(
    () => permissions,
    [JSON.stringify(permissions)],
  );
  const stableUserRoles = useMemo(
    () => auth.user?.roles,
    [JSON.stringify(auth.user?.roles)],
  );
  const stableUserPermissions = useMemo(
    () => auth.user?.permissions,
    [JSON.stringify(auth.user?.permissions)],
  );

  const checkAccess = React.useCallback((): AccessCheckResult => {
    // Loading state
    if (auth.isLoading) {
      return { hasAccess: false, reason: "Loading...", code: "LOADING" };
    }

    // Account locked check
    if (auth.isLocked) {
      return {
        hasAccess: false,
        reason: "Account is locked",
        code: "ACCOUNT_LOCKED",
      };
    }

    // Authentication check
    if (!auth.isAuthenticated || !auth.user) {
      return {
        hasAccess: false,
        reason: "User not authenticated",
        code: "UNAUTHENTICATED",
      };
    }

    // Email verification check
    if (requireVerification && !auth.user.isVerified) {
      return {
        hasAccess: false,
        reason: "Email verification required",
        code: "UNVERIFIED",
      };
    }

    // Subscription check
    if (requireSubscription && auth.user.subscription) {
      const userTier = SUBSCRIPTION_TIERS[auth.user.subscription.tier];
      const requiredTier = SUBSCRIPTION_TIERS[minSubscriptionTier];

      if (userTier < requiredTier) {
        return {
          hasAccess: false,
          reason: `Subscription tier ${minSubscriptionTier} or higher required`,
          code: "INSUFFICIENT_SUBSCRIPTION",
        };
      }

      // Check subscription expiry
      if (auth.user.subscription.expiresAt) {
        const expiryDate = new Date(auth.user.subscription.expiresAt);
        if (expiryDate < new Date()) {
          return {
            hasAccess: false,
            reason: "Subscription has expired",
            code: "INSUFFICIENT_SUBSCRIPTION",
          };
        }
      }
    }

    // Role check
    if (stableRoles.length > 0) {
      const userRoles = stableUserRoles || [];
      const hasRequiredRoles = requireAll
        ? stableRoles.every((role) => userRoles.includes(role))
        : stableRoles.some((role) => userRoles.includes(role));

      if (!hasRequiredRoles) {
        return {
          hasAccess: false,
          reason: `Required roles: ${stableRoles.join(", ")}`,
          code: "INSUFFICIENT_ROLES",
        };
      }
    }

    // Permission check
    if (stablePermissions.length > 0) {
      const userPermissions = stableUserPermissions || [];
      const hasRequiredPermissions = requireAll
        ? stablePermissions.every((permission) =>
            userPermissions.includes(permission),
          )
        : stablePermissions.some((permission) =>
            userPermissions.includes(permission),
          );

      if (!hasRequiredPermissions) {
        return {
          hasAccess: false,
          reason: `Required permissions: ${stablePermissions.join(", ")}`,
          code: "INSUFFICIENT_PERMISSIONS",
        };
      }
    }

    return { hasAccess: true };
  }, [
    auth.isLoading,
    auth.isAuthenticated,
    auth.isLocked,
    auth.user?.id,
    auth.user?.isVerified,
    auth.user?.subscription?.tier,
    auth.user?.subscription?.expiresAt,
    stableUserRoles,
    stableUserPermissions,
    stableRoles,
    stablePermissions,
    requireAll,
    requireVerification,
    requireSubscription,
    minSubscriptionTier,
  ]);

  // Update access check when dependencies change
  useEffect(() => {
    const result = checkAccess();
    setAccessCheck(result);

    if (!result.hasAccess && result.reason) {
      handleUnauthorized(result.reason);
    }
  }, [checkAccess, handleUnauthorized]);

  // Loading state
  if (accessCheck.code === "LOADING") {
    return (
      fallback || <AccessDeniedFallback reason="Loading..." code="LOADING" />
    );
  }

  // Access denied
  if (!accessCheck.hasAccess) {
    // Redirect to login for unauthenticated users
    if (accessCheck.code === "UNAUTHENTICATED") {
      return (
        <Navigate
          to={redirectTo}
          state={{ from: location.pathname + location.search }}
          replace
        />
      );
    }

    // Show fallback or default access denied page
    return (
      fallback || (
        <AccessDeniedFallback
          reason={accessCheck.reason || "Access denied"}
          code={accessCheck.code}
        />
      )
    );
  }

  // Access granted
  return <>{children}</>;
}

// =============================================================================
// CONVENIENCE COMPONENTS
// =============================================================================

export function AdminRoute({
  children,
  ...props
}: Omit<ProtectedRouteProps, "roles">) {
  return (
    <ProtectedRoute roles={["admin"]} {...props}>
      {children}
    </ProtectedRoute>
  );
}

export function ModeratorRoute({
  children,
  ...props
}: Omit<ProtectedRouteProps, "roles">) {
  return (
    <ProtectedRoute
      roles={["admin", "moderator"]}
      requireAll={false}
      {...props}
    >
      {children}
    </ProtectedRoute>
  );
}

export function ProRoute({
  children,
  ...props
}: Omit<ProtectedRouteProps, "minSubscriptionTier" | "requireSubscription">) {
  return (
    <ProtectedRoute
      requireSubscription={true}
      minSubscriptionTier="pro"
      {...props}
    >
      {children}
    </ProtectedRoute>
  );
}

export function EnterpriseRoute({
  children,
  ...props
}: Omit<ProtectedRouteProps, "minSubscriptionTier" | "requireSubscription">) {
  return (
    <ProtectedRoute
      requireSubscription={true}
      minSubscriptionTier="enterprise"
      {...props}
    >
      {children}
    </ProtectedRoute>
  );
}

export function VerifiedRoute({
  children,
  ...props
}: Omit<ProtectedRouteProps, "requireVerification">) {
  return (
    <ProtectedRoute requireVerification={true} {...props}>
      {children}
    </ProtectedRoute>
  );
}

// =============================================================================
// PERMISSION CHECK HOOK
// =============================================================================

export function usePermissions() {
  const auth = useAuth();

  const can = React.useCallback(
    (permission: string) => {
      return auth.checkPermission(permission);
    },
    [auth.checkPermission],
  );

  const hasRole = React.useCallback(
    (role: string) => {
      return auth.hasRole(role);
    },
    [auth.hasRole],
  );

  const hasAnyRole = React.useCallback(
    (roles: string[]) => {
      return auth.hasAnyRole(roles);
    },
    [auth.hasAnyRole],
  );

  const hasAllRoles = React.useCallback(
    (roles: string[]) => {
      return roles.every((role) => auth.hasRole(role));
    },
    [auth.hasRole],
  );

  return {
    can,
    hasRole,
    hasAnyRole,
    hasAllRoles,
    user: auth.user,
    isAuthenticated: auth.isAuthenticated,
  };
}

export default ProtectedRoute;

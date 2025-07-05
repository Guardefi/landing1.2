/**
 * Error Boundary and Loading States for API Integration
 * Provides graceful error handling and loading UI components
 */

import React, { Component, ReactNode } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  AlertTriangle,
  RefreshCw,
  Wifi,
  WifiOff,
  Activity,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

// ============================================================================
// ERROR BOUNDARY
// ============================================================================

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: any;
}

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: (
    error: Error,
    errorInfo: any,
    resetError: () => void,
  ) => ReactNode;
  onError?: (error: Error, errorInfo: any) => void;
}

export class ErrorBoundary extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    this.setState({
      error,
      errorInfo,
    });

    // Call onError callback if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Log error in development
    if (import.meta.env.MODE === "development") {
      console.error("ErrorBoundary caught an error:", error, errorInfo);
    }
  }

  resetError = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback(
          this.state.error!,
          this.state.errorInfo,
          this.resetError,
        );
      }

      return (
        <DefaultErrorFallback
          error={this.state.error!}
          resetError={this.resetError}
        />
      );
    }

    return this.props.children;
  }
}

// ============================================================================
// DEFAULT ERROR FALLBACK
// ============================================================================

interface ErrorFallbackProps {
  error: Error;
  resetError: () => void;
  className?: string;
}

export function DefaultErrorFallback({
  error,
  resetError,
  className,
}: ErrorFallbackProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn("p-6", className)}
    >
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription className="mt-2">
          <div className="space-y-3">
            <p className="font-medium">Something went wrong:</p>
            <p className="text-sm opacity-90">{error.message}</p>
            <Button
              onClick={resetError}
              variant="outline"
              size="sm"
              className="mt-3"
            >
              <RefreshCw className="h-3 w-3 mr-2" />
              Try Again
            </Button>
          </div>
        </AlertDescription>
      </Alert>
    </motion.div>
  );
}

// ============================================================================
// LOADING STATES
// ============================================================================

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  className?: string;
  message?: string;
}

export function LoadingSpinner({
  size = "md",
  className,
  message,
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: "h-4 w-4",
    md: "h-6 w-6",
    lg: "h-8 w-8",
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className={cn("flex items-center justify-center space-x-2", className)}
    >
      <Loader2
        className={cn("animate-spin text-cyan-500", sizeClasses[size])}
      />
      {message && (
        <span className="text-sm text-muted-foreground">{message}</span>
      )}
    </motion.div>
  );
}

interface SkeletonProps {
  className?: string;
  width?: string;
  height?: string;
  style?: React.CSSProperties;
}

export function Skeleton({ className, width, height, style }: SkeletonProps) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-muted", className)}
      style={{ width, height, ...style }}
    />
  );
}

// ============================================================================
// MODULE LOADING WRAPPER
// ============================================================================

interface ModuleLoadingWrapperProps {
  loading: boolean;
  error: any;
  children: ReactNode;
  moduleName: string;
  retryAction?: () => void;
  className?: string;
}

export function ModuleLoadingWrapper({
  loading,
  error,
  children,
  moduleName,
  retryAction,
  className,
}: ModuleLoadingWrapperProps) {
  if (loading) {
    return (
      <Card className={cn("min-h-64", className)}>
        <CardContent className="flex items-center justify-center h-64">
          <div className="text-center space-y-4">
            <LoadingSpinner size="lg" />
            <div>
              <p className="text-sm font-medium">Loading {moduleName}</p>
              <p className="text-xs text-muted-foreground">
                Connecting to backend services...
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={cn("min-h-64", className)}>
        <CardContent className="flex items-center justify-center h-64">
          <div className="text-center space-y-4 max-w-md">
            <div className="p-3 rounded-full bg-red-500/10 w-fit mx-auto">
              <AlertTriangle className="h-6 w-6 text-red-500" />
            </div>
            <div>
              <p className="text-sm font-medium">Failed to load {moduleName}</p>
              <p className="text-xs text-muted-foreground mt-1">{error}</p>
            </div>
            {retryAction && (
              <Button onClick={retryAction} variant="outline" size="sm">
                <RefreshCw className="h-3 w-3 mr-2" />
                Retry
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  return <>{children}</>;
}

// ============================================================================
// CONNECTION STATUS INDICATOR
// ============================================================================

interface ConnectionStatusProps {
  isConnected: boolean;
  serviceName: string;
  className?: string;
}

export function ConnectionStatus({
  isConnected,
  serviceName,
  className,
}: ConnectionStatusProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className={cn("flex items-center space-x-2 text-xs", className)}
    >
      <motion.div
        animate={{ scale: isConnected ? [1, 1.2, 1] : 1 }}
        transition={{ repeat: isConnected ? Infinity : 0, duration: 2 }}
        className={cn(
          "w-2 h-2 rounded-full",
          isConnected ? "bg-green-500" : "bg-red-500",
        )}
      />
      <div className="flex items-center space-x-1">
        {isConnected ? (
          <Wifi className="h-3 w-3 text-green-500" />
        ) : (
          <WifiOff className="h-3 w-3 text-red-500" />
        )}
        <span className={isConnected ? "text-green-600" : "text-red-600"}>
          {serviceName} {isConnected ? "Connected" : "Disconnected"}
        </span>
      </div>
    </motion.div>
  );
}

// ============================================================================
// DATA TABLE LOADING STATE
// ============================================================================

interface TableSkeletonProps {
  rows?: number;
  columns?: number;
  className?: string;
}

export function TableSkeleton({
  rows = 5,
  columns = 4,
  className,
}: TableSkeletonProps) {
  return (
    <div className={cn("space-y-3", className)}>
      {/* Header */}
      <div className="flex space-x-4">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={i} className="h-4 flex-1" />
        ))}
      </div>

      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="flex space-x-4">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton
              key={colIndex}
              className={cn(
                "h-6 flex-1",
                colIndex === 0 && "max-w-16", // First column smaller for IDs
                colIndex === columns - 1 && "max-w-20", // Last column for actions
              )}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

// ============================================================================
// METRICS CARD LOADING STATE
// ============================================================================

interface MetricsSkeletonProps {
  cards?: number;
  className?: string;
}

export function MetricsSkeleton({
  cards = 4,
  className,
}: MetricsSkeletonProps) {
  return (
    <div
      className={cn(
        "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4",
        className,
      )}
    >
      {Array.from({ length: cards }).map((_, i) => (
        <Card key={i}>
          <CardHeader className="pb-2">
            <Skeleton className="h-4 w-2/3" />
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Skeleton className="h-8 w-1/2" />
              <Skeleton className="h-3 w-3/4" />
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

// ============================================================================
// CHART LOADING STATE
// ============================================================================

export function ChartSkeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "w-full h-64 relative overflow-hidden rounded-lg bg-muted",
        className,
      )}
    >
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full animate-shimmer" />
      <div className="p-4 space-y-3">
        <Skeleton className="h-4 w-1/4" />
        <div className="space-y-2">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="flex items-end space-x-1 h-8">
              {Array.from({ length: 12 }).map((_, j) => (
                <Skeleton
                  key={j}
                  className="flex-1"
                  style={{ height: `${Math.random() * 100 + 20}%` }}
                />
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// ACTIVITY FEED LOADING STATE
// ============================================================================

export function ActivityFeedSkeleton({
  items = 5,
  className,
}: {
  items?: number;
  className?: string;
}) {
  return (
    <div className={cn("space-y-4", className)}>
      {Array.from({ length: items }).map((_, i) => (
        <div key={i} className="flex items-start space-x-3">
          <Skeleton className="h-8 w-8 rounded-full" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
          </div>
          <Skeleton className="h-3 w-16" />
        </div>
      ))}
    </div>
  );
}

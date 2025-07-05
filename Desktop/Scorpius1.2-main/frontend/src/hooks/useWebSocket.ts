import { useEffect, useRef, useState, useCallback, useMemo } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";

// =============================================================================
// TYPES AND INTERFACES
// =============================================================================

export interface WebSocketMessage {
  type: string;
  event?: string;
  data?: any;
  timestamp?: number;
  id?: string;
}

export interface WebSocketOptions {
  url?: string;
  protocols?: string | string[];
  reconnect?: boolean;
  maxRetries?: number;
  backoffFactor?: number;
  backoffMaxDelay?: number;
  heartbeatInterval?: number;
  heartbeatTimeout?: number;
  onMessage?: (message: WebSocketMessage) => void;
  onOpen?: (event: Event) => void;
  onClose?: (event: CloseEvent) => void;
  onError?: (event: Event) => void;
  onReconnect?: (attempt: number) => void;
  filter?: (message: WebSocketMessage) => boolean;
  transform?: (data: any) => any;
  enableCircuitBreaker?: boolean;
  circuitBreakerThreshold?: number;
  circuitBreakerTimeout?: number;
}

export interface WebSocketState {
  readyState: number;
  isConnected: boolean;
  isConnecting: boolean;
  isReconnecting: boolean;
  reconnectAttempts: number;
  lastError: Error | null;
  lastMessage: WebSocketMessage | null;
  circuitBreakerOpen: boolean;
  connectionId: string | null;
  latency: number | null;
}

// =============================================================================
// CIRCUIT BREAKER CLASS
// =============================================================================

class CircuitBreaker {
  private failureCount = 0;
  private lastFailureTime: number | null = null;
  private state: "CLOSED" | "OPEN" | "HALF_OPEN" = "CLOSED";

  constructor(
    private threshold: number = 5,
    private timeout: number = 60000, // 1 minute
  ) {}

  public canExecute(): boolean {
    if (this.state === "CLOSED") {
      return true;
    }

    if (this.state === "OPEN") {
      if (Date.now() - (this.lastFailureTime || 0) >= this.timeout) {
        this.state = "HALF_OPEN";
        return true;
      }
      return false;
    }

    // HALF_OPEN state
    return true;
  }

  public onSuccess(): void {
    this.failureCount = 0;
    this.state = "CLOSED";
    this.lastFailureTime = null;
  }

  public onFailure(): void {
    this.failureCount++;
    this.lastFailureTime = Date.now();

    if (this.failureCount >= this.threshold) {
      this.state = "OPEN";
    }
  }

  public getState(): string {
    return this.state;
  }

  public isOpen(): boolean {
    return this.state === "OPEN";
  }
}

// =============================================================================
// WEBSOCKET MANAGER CLASS
// =============================================================================

class WebSocketManager {
  private ws: WebSocket | null = null;
  private reconnectTimeoutId: NodeJS.Timeout | null = null;
  private heartbeatIntervalId: NodeJS.Timeout | null = null;
  private heartbeatTimeoutId: NodeJS.Timeout | null = null;
  private circuitBreaker: CircuitBreaker | null = null;
  private lastPingTime: number | null = null;

  constructor(
    private url: string,
    private options: WebSocketOptions,
    private setState: React.Dispatch<React.SetStateAction<WebSocketState>>,
  ) {
    if (options.enableCircuitBreaker) {
      this.circuitBreaker = new CircuitBreaker(
        options.circuitBreakerThreshold,
        options.circuitBreakerTimeout,
      );
    }
  }

  public connect(): void {
    if (this.circuitBreaker && !this.circuitBreaker.canExecute()) {
      console.warn(
        "WebSocket circuit breaker is open, skipping connection attempt",
      );
      this.setState((prev) => ({ ...prev, circuitBreakerOpen: true }));
      this.scheduleReconnect();
      return;
    }

    try {
      this.setState((prev) => ({
        ...prev,
        isConnecting: true,
        lastError: null,
        circuitBreakerOpen: false,
      }));

      this.ws = new WebSocket(this.url, this.options.protocols);
      this.setupEventListeners();
    } catch (error) {
      console.error("Failed to create WebSocket connection:", error);
      this.handleError(error as Error);
    }
  }

  private setupEventListeners(): void {
    if (!this.ws) return;

    this.ws.onopen = (event) => {
      console.log("WebSocket connected:", this.url);

      this.setState((prev) => ({
        ...prev,
        readyState: this.ws!.readyState,
        isConnected: true,
        isConnecting: false,
        isReconnecting: false,
        reconnectAttempts: 0,
        connectionId: this.generateConnectionId(),
        lastError: null,
      }));

      if (this.circuitBreaker) {
        this.circuitBreaker.onSuccess();
      }

      this.startHeartbeat();
      this.options.onOpen?.(event);
    };

    this.ws.onmessage = (event) => {
      try {
        const rawData = JSON.parse(event.data);
        const message: WebSocketMessage = {
          type: rawData.type || "message",
          event: rawData.event,
          data: this.options.transform
            ? this.options.transform(rawData.data)
            : rawData.data,
          timestamp: rawData.timestamp || Date.now(),
          id: rawData.id,
        };

        // Handle heartbeat responses
        if (message.type === "pong" && this.lastPingTime) {
          const latency = Date.now() - this.lastPingTime;
          this.setState((prev) => ({ ...prev, latency }));
          this.lastPingTime = null;
          return;
        }

        // Apply filter if provided
        if (this.options.filter && !this.options.filter(message)) {
          return;
        }

        this.setState((prev) => ({ ...prev, lastMessage: message }));
        this.options.onMessage?.(message);
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error);
      }
    };

    this.ws.onclose = (event) => {
      console.log("WebSocket closed:", event.code, event.reason);

      this.setState((prev) => ({
        ...prev,
        readyState: WebSocket.CLOSED,
        isConnected: false,
        isConnecting: false,
        connectionId: null,
      }));

      this.stopHeartbeat();
      this.options.onClose?.(event);

      // Don't reconnect if closed intentionally
      if (event.code !== 1000 && this.options.reconnect) {
        this.scheduleReconnect();
      }
    };

    this.ws.onerror = (event) => {
      console.error("WebSocket error:", event);

      const error = new Error("WebSocket connection error");
      this.handleError(error);
      this.options.onError?.(event);
    };
  }

  private handleError(error: Error): void {
    this.setState((prev) => ({
      ...prev,
      lastError: error,
      isConnecting: false,
    }));

    if (this.circuitBreaker) {
      this.circuitBreaker.onFailure();
    }
  }

  private scheduleReconnect(): void {
    if (!this.options.reconnect) return;

    this.setState((prev) => {
      const newAttempts = prev.reconnectAttempts + 1;

      if (newAttempts > (this.options.maxRetries || 5)) {
        console.error("Max reconnection attempts reached");
        return { ...prev, isReconnecting: false };
      }

      const delay = Math.min(
        Math.pow(this.options.backoffFactor || 1.5, newAttempts - 1) * 1000,
        this.options.backoffMaxDelay || 30000,
      );

      console.log(
        `Attempting to reconnect in ${delay}ms (attempt ${newAttempts})`,
      );

      this.reconnectTimeoutId = setTimeout(() => {
        this.setState((p) => ({ ...p, isReconnecting: true }));
        this.options.onReconnect?.(newAttempts);
        this.connect();
      }, delay);

      return {
        ...prev,
        reconnectAttempts: newAttempts,
        isReconnecting: true,
      };
    });
  }

  private startHeartbeat(): void {
    if (!this.options.heartbeatInterval) return;

    this.heartbeatIntervalId = setInterval(() => {
      this.ping();
    }, this.options.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatIntervalId) {
      clearInterval(this.heartbeatIntervalId);
      this.heartbeatIntervalId = null;
    }
    if (this.heartbeatTimeoutId) {
      clearTimeout(this.heartbeatTimeoutId);
      this.heartbeatTimeoutId = null;
    }
  }

  private ping(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.lastPingTime = Date.now();
      this.sendMessage({ type: "ping", timestamp: this.lastPingTime });

      // Set timeout for pong response
      if (this.options.heartbeatTimeout) {
        this.heartbeatTimeoutId = setTimeout(() => {
          console.warn("Heartbeat timeout, closing connection");
          this.ws?.close();
        }, this.options.heartbeatTimeout);
      }
    }
  }

  private generateConnectionId(): string {
    return `ws_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  public sendMessage(message: WebSocketMessage): boolean {
    if (this.ws?.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(message));
        return true;
      } catch (error) {
        console.error("Failed to send WebSocket message:", error);
        return false;
      }
    }
    return false;
  }

  public disconnect(): void {
    if (this.reconnectTimeoutId) {
      clearTimeout(this.reconnectTimeoutId);
      this.reconnectTimeoutId = null;
    }

    this.stopHeartbeat();

    if (this.ws) {
      this.ws.close(1000, "Client disconnect");
      this.ws = null;
    }

    this.setState((prev) => ({
      ...prev,
      readyState: WebSocket.CLOSED,
      isConnected: false,
      isConnecting: false,
      isReconnecting: false,
      connectionId: null,
    }));
  }

  public getReadyState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED;
  }
}

// =============================================================================
// MAIN HOOK
// =============================================================================

export function useWebSocket(
  channel: string,
  options: WebSocketOptions = {},
): WebSocketState & {
  sendMessage: (message: Omit<WebSocketMessage, "timestamp">) => boolean;
  sendJsonMessage: (data: any) => boolean;
  disconnect: () => void;
  reconnect: () => void;
} {
  const baseUrl =
    options.url || import.meta.env.VITE_WS_BASE_URL || "ws://localhost:8000";
  const fullUrl = `${baseUrl.replace(/\/$/, "")}/ws/${channel.replace(/^\//, "")}`;

  const [state, setState] = useState<WebSocketState>({
    readyState: WebSocket.CLOSED,
    isConnected: false,
    isConnecting: false,
    isReconnecting: false,
    reconnectAttempts: 0,
    lastError: null,
    lastMessage: null,
    circuitBreakerOpen: false,
    connectionId: null,
    latency: null,
  });

  const managerRef = useRef<WebSocketManager | null>(null);

  // Create manager instance
  const manager = useMemo(() => {
    return new WebSocketManager(fullUrl, options, setState);
  }, [fullUrl, JSON.stringify(options)]);

  useEffect(() => {
    managerRef.current = manager;
    manager.connect();

    return () => {
      manager.disconnect();
    };
  }, [manager]);

  // Public interface
  const sendMessage = useCallback(
    (message: Omit<WebSocketMessage, "timestamp">) => {
      const fullMessage: WebSocketMessage = {
        ...message,
        timestamp: Date.now(),
      };
      return managerRef.current?.sendMessage(fullMessage) ?? false;
    },
    [],
  );

  const sendJsonMessage = useCallback(
    (data: any) => {
      return sendMessage({ type: "message", data });
    },
    [sendMessage],
  );

  const disconnect = useCallback(() => {
    managerRef.current?.disconnect();
  }, []);

  const reconnect = useCallback(() => {
    setState((prev) => ({ ...prev, reconnectAttempts: 0 }));
    managerRef.current?.connect();
  }, []);

  return {
    ...state,
    sendMessage,
    sendJsonMessage,
    disconnect,
    reconnect,
  };
}

// =============================================================================
// ADDITIONAL HOOKS
// =============================================================================

// Hook for subscribing to specific event types
export function useWebSocketSubscription(
  channel: string,
  eventType: string,
  onMessage: (data: any) => void,
  options?: Omit<WebSocketOptions, "onMessage" | "filter">,
) {
  return useWebSocket(channel, {
    ...options,
    filter: (message) =>
      message.type === eventType || message.event === eventType,
    onMessage: (message) => onMessage(message.data),
  });
}

// Hook for WebSocket with React Query integration
export function useWebSocketQuery<T>(
  channel: string,
  queryKey: string[],
  options?: WebSocketOptions,
) {
  const queryClient = useQueryClient();

  const { isConnected, sendJsonMessage } = useWebSocket(channel, {
    ...options,
    onMessage: (message) => {
      // Invalidate related queries when data changes
      if (message.type === "data_update" || message.type === "invalidate") {
        queryClient.invalidateQueries({ queryKey });
      }

      // Update query data directly for real-time updates
      if (message.type === "data" && message.data) {
        queryClient.setQueryData(queryKey, message.data);
      }

      options?.onMessage?.(message);
    },
  });

  // Subscribe to query updates on connection
  useEffect(() => {
    if (isConnected) {
      sendJsonMessage({ type: "subscribe", query: queryKey });
    }
  }, [isConnected, queryKey, sendJsonMessage]);

  return { isConnected };
}

export default useWebSocket;

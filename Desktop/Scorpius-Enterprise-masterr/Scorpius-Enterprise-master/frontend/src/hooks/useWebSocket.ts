// WebSocket hook with auto-reconnect and backoff
import { useEffect, useRef, useState, useCallback } from 'react';

interface UseWebSocketOptions {
  url?: string; // override default base URL
  protocols?: string | string[];
  reconnect?: boolean;
  maxRetries?: number;
  backoffFactor?: number; // multiplier, e.g., 1.5
  onMessage?: (ev: MessageEvent) => void;
  onOpen?: (ev: Event) => void;
  onClose?: (ev: CloseEvent) => void;
  onError?: (ev: Event) => void;
}

export function useWebSocket(channel: string, opts: UseWebSocketOptions = {}) {
  const {
    url = import.meta.env.VITE_WS_BASE_URL ?? 'ws://localhost:8000',
    protocols,
    reconnect = true,
    maxRetries = 5,
    backoffFactor = 1.5,
    onMessage,
    onOpen,
    onClose,
    onError,
  } = opts;

  const [readyState, setReadyState] = useState<WebSocket['readyState']>(WebSocket.CLOSED);
  const wsRef = useRef<WebSocket | null>(null);
  const retriesRef = useRef(0);

  const fullUrl = `${url.replace(/\/$/, '')}/${channel.replace(/^\//, '')}`;

  const connect = useCallback(() => {
    wsRef.current = new WebSocket(fullUrl, protocols);

    wsRef.current.onopen = (e) => {
      retriesRef.current = 0;
      setReadyState(wsRef.current?.readyState ?? WebSocket.OPEN);
      onOpen?.(e);
    };

    wsRef.current.onmessage = (e) => {
      onMessage?.(e);
    };

    wsRef.current.onclose = (e) => {
      setReadyState(WebSocket.CLOSED);
      onClose?.(e);

      if (reconnect && retriesRef.current < maxRetries) {
        const timeout = Math.pow(backoffFactor, retriesRef.current) * 1000;
        retriesRef.current += 1;
        setTimeout(connect, timeout);
      }
    };

    wsRef.current.onerror = (e) => {
      onError?.(e);
    };
  }, [fullUrl, protocols, reconnect, maxRetries, backoffFactor, onMessage, onOpen, onClose, onError]);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
    };
  }, [connect]);

  const sendJsonMessage = useCallback((data: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  return {
    readyState,
    sendJsonMessage,
  };
} 
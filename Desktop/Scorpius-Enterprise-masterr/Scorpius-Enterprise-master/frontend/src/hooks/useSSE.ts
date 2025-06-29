// Simple EventSource hook for Server-Sent Events
import { useEffect, useRef, useState } from 'react';

export function useSSE<T = MessageEvent>(url: string, onMessage?: (ev: MessageEvent) => void) {
  const [isConnected, setIsConnected] = useState(false);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    esRef.current = new EventSource(url, { withCredentials: true });

    esRef.current.onopen = () => setIsConnected(true);
    esRef.current.onmessage = (e) => onMessage?.(e);
    esRef.current.onerror = () => {
      setIsConnected(false);
    };

    return () => {
      esRef.current?.close();
    };
  }, [url, onMessage]);

  return isConnected;
} 
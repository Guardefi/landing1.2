import { useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';

interface RealtimeData {
  systemStatus?: any;
  threats?: any[];
  tradingMetrics?: any;
  bridgeStats?: any;
  analyticsData?: any;
}

export function useRealtimeConnection() {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [connected, setConnected] = useState(false);
  const [data, setData] = useState<RealtimeData>({});

  useEffect(() => {
    // Connect to your backend WebSocket server
    const socketConnection = io('http://localhost:8000', {
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    socketConnection.on('connect', () => {
      setConnected(true);
      console.log('🔗 Connected to Scorpius X real-time feed');
    });

    socketConnection.on('disconnect', () => {
      setConnected(false);
      console.log('🔌 Disconnected from real-time feed');
    });

    // Listen for different data streams from your backend
    socketConnection.on('system_status', statusData => {
      setData(prev => ({ ...prev, systemStatus: statusData }));
    });

    socketConnection.on('threats', threatData => {
      setData(prev => ({ ...prev, threats: threatData }));
    });

    socketConnection.on('trading_metrics', tradingData => {
      setData(prev => ({ ...prev, tradingMetrics: tradingData }));
    });

    socketConnection.on('bridge_stats', bridgeData => {
      setData(prev => ({ ...prev, bridgeStats: bridgeData }));
    });

    socketConnection.on('analytics', analyticsData => {
      setData(prev => ({ ...prev, analyticsData: analyticsData }));
    });

    setSocket(socketConnection);

    return () => {
      socketConnection.disconnect();
    };
  }, []);

  return { socket, connected, data };
}

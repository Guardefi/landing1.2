# React + Vite Dashboard Integration Guide

This guide shows how to integrate the Scorpius Enterprise FastAPI backend with a modern React + Vite frontend dashboard.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Python 3.8+ (for backend)

### 1. Start the Scorpius API Backend

```bash
# Install Python dependencies
pip install -r requirements.enterprise.txt

# Start the FastAPI server
python -m scorpius.api.main
# OR using uvicorn directly
uvicorn scorpius.api.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **REST API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws/dashboard

### 2. Create React + Vite Frontend

```bash
# Create new Vite + React project
npm create vite@latest scorpius-dashboard -- --template react-ts
cd scorpius-dashboard

# Install additional dependencies for dashboard
npm install axios recharts lucide-react @radix-ui/react-alert-dialog
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

## 🔌 API Integration Examples

### REST API Client Setup

```typescript
// src/lib/api.ts
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';
const AUTH_TOKEN = 'demo-token'; // Replace with real auth

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Authorization': `Bearer ${AUTH_TOKEN}`,
    'Content-Type': 'application/json',
  },
});

// API Types
export interface DashboardStats {
  total_encryptions_today: number;
  total_scans_today: number;
  active_threats: number;
  system_health_score: number;
  uptime_seconds: number;
  last_updated: string;
}

export interface ThreatAlert {
  id: string;
  level: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  detected_at: string;
  source: string;
  status: string;
}

// API Functions
export const api = {
  // Health & Status
  getHealth: () => apiClient.get('/health'),
  getStatus: () => apiClient.get('/status'),
  
  // Dashboard
  getDashboardStats: () => apiClient.get<DashboardStats>('/dashboard/stats'),
  getActivity: (limit = 50) => apiClient.get(`/dashboard/activity?limit=${limit}`),
  getSystemResources: () => apiClient.get('/dashboard/resources'),
  getAlerts: (limit = 20) => apiClient.get<ThreatAlert[]>(`/dashboard/alerts?limit=${limit}`),
  
  // Security
  performScan: (target: string, scanType = 'quick') => 
    apiClient.post('/security/scan', { target, scan_type: scanType }),
  getThreats: (limit = 100) => apiClient.get(`/security/threats?limit=${limit}`),
  
  // Quantum Operations
  quantumEncrypt: (message: string, algorithm = 'lattice_based') => 
    apiClient.post('/quantum/encrypt', { message, algorithm }),
  generateKeys: (algorithm = 'lattice_based') => 
    apiClient.post('/quantum/generate-keys', { algorithm }),
  
  // Analytics
  getMetrics: (timeframe = '1h') => 
    apiClient.get(`/analytics/metrics?timeframe=${timeframe}`),
  generateReport: (reportType: string, timeframe = '24h') => 
    apiClient.post('/analytics/reports', { report_type: reportType, timeframe }),
};
```

### WebSocket Integration

```typescript
// src/lib/websocket.ts
export class ScorpiusWebSocket {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 5000;

  constructor(
    private url: string,
    private onMessage: (data: any) => void,
    private onError?: (error: Event) => void
  ) {}

  connect() {
    try {
      this.ws = new WebSocket(this.url);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected to', this.url);
        this.reconnectAttempts = 0;
        
        // Subscribe to events
        this.send({
          type: 'subscribe',
          events: ['security_scan', 'quantum_operation', 'threat_notification']
        });
      };

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.onMessage(data);
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.reconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        if (this.onError) this.onError(error);
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
    }
  }

  private reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => {
        console.log(`Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        this.connect();
      }, this.reconnectInterval);
    }
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// Usage Hook
import { useEffect, useRef, useState } from 'react';

export const useScorpiusWebSocket = () => {
  const [realTimeData, setRealTimeData] = useState<any[]>([]);
  const wsRef = useRef<ScorpiusWebSocket | null>(null);

  useEffect(() => {
    wsRef.current = new ScorpiusWebSocket(
      'ws://localhost:8000/ws/dashboard',
      (data) => {
        setRealTimeData(prev => [...prev.slice(-99), data]); // Keep last 100 messages
      },
      (error) => console.error('WebSocket error:', error)
    );

    wsRef.current.connect();

    return () => {
      wsRef.current?.disconnect();
    };
  }, []);

  return {
    realTimeData,
    sendMessage: (data: any) => wsRef.current?.send(data)
  };
};
```

## 📊 Dashboard Components

### Main Dashboard Component

```tsx
// src/components/Dashboard.tsx
import React, { useEffect, useState } from 'react';
import { Shield, Activity, Zap, AlertTriangle } from 'lucide-react';
import { api, DashboardStats, ThreatAlert } from '../lib/api';
import { useScorpiusWebSocket } from '../lib/websocket';

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [alerts, setAlerts] = useState<ThreatAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const { realTimeData } = useScorpiusWebSocket();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, alertsRes] = await Promise.all([
          api.getDashboardStats(),
          api.getAlerts(5)
        ]);
        
        setStats(statsRes.data);
        setAlerts(alertsRes.data);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Encryptions Today"
          value={stats?.total_encryptions_today || 0}
          icon={<Shield className="h-6 w-6" />}
          color="blue"
        />
        <StatCard
          title="Security Scans"
          value={stats?.total_scans_today || 0}
          icon={<Activity className="h-6 w-6" />}
          color="green"
        />
        <StatCard
          title="Active Threats"
          value={stats?.active_threats || 0}
          icon={<AlertTriangle className="h-6 w-6" />}
          color="red"
        />
        <StatCard
          title="System Health"
          value={`${stats?.system_health_score || 0}%`}
          icon={<Zap className="h-6 w-6" />}
          color="purple"
        />
      </div>

      {/* Real-time Updates */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Real-time Activity</h2>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {realTimeData.slice(-10).map((item, index) => (
            <div key={index} className="text-sm border-l-4 border-blue-400 pl-3 py-1">
              <span className="font-medium">{item.type}</span>
              <span className="text-gray-500 ml-2">{item.timestamp}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Alerts */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Recent Alerts</h2>
        <div className="space-y-3">
          {alerts.map((alert) => (
            <AlertCard key={alert.id} alert={alert} />
          ))}
        </div>
      </div>
    </div>
  );
};

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: 'blue' | 'green' | 'red' | 'purple';
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color }) => {
  const colorClasses = {
    blue: 'bg-blue-500 text-white',
    green: 'bg-green-500 text-white',
    red: 'bg-red-500 text-white',
    purple: 'bg-purple-500 text-white',
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-2xl font-bold">{value}</p>
        </div>
        <div className={`p-3 rounded-full ${colorClasses[color]}`}>
          {icon}
        </div>
      </div>
    </div>
  );
};

const AlertCard: React.FC<{ alert: ThreatAlert }> = ({ alert }) => {
  const levelColors = {
    low: 'border-green-400 bg-green-50',
    medium: 'border-yellow-400 bg-yellow-50',
    high: 'border-orange-400 bg-orange-50',
    critical: 'border-red-400 bg-red-50',
  };

  return (
    <div className={`border-l-4 p-3 rounded ${levelColors[alert.level]}`}>
      <div className="flex justify-between items-start">
        <div>
          <h3 className="font-medium">{alert.title}</h3>
          <p className="text-sm text-gray-600">{alert.description}</p>
          <p className="text-xs text-gray-500 mt-1">
            {new Date(alert.detected_at).toLocaleString()}
          </p>
        </div>
        <span className={`px-2 py-1 rounded text-xs font-medium bg-${alert.level === 'critical' ? 'red' : alert.level === 'high' ? 'orange' : alert.level === 'medium' ? 'yellow' : 'green'}-100`}>
          {alert.level.toUpperCase()}
        </span>
      </div>
    </div>
  );
};
```

## 🛠️ Security Operations Component

```tsx
// src/components/SecurityOperations.tsx
import React, { useState } from 'react';
import { api } from '../lib/api';

export const SecurityOperations: React.FC = () => {
  const [scanTarget, setScanTarget] = useState('');
  const [scanResults, setScanResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleScan = async () => {
    if (!scanTarget) return;
    
    setLoading(true);
    try {
      const response = await api.performScan(scanTarget, 'comprehensive');
      setScanResults(response.data);
    } catch (error) {
      console.error('Scan failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Security Scan</h2>
        <div className="flex gap-4">
          <input
            type="text"
            value={scanTarget}
            onChange={(e) => setScanTarget(e.target.value)}
            placeholder="Enter target (IP, domain, contract address...)"
            className="flex-1 px-3 py-2 border rounded-md"
          />
          <button
            onClick={handleScan}
            disabled={loading || !scanTarget}
            className="px-4 py-2 bg-blue-500 text-white rounded-md disabled:opacity-50"
          >
            {loading ? 'Scanning...' : 'Start Scan'}
          </button>
        </div>
        
        {scanResults && (
          <div className="mt-4 p-4 bg-gray-50 rounded-md">
            <h3 className="font-medium">Scan Results</h3>
            <pre className="text-sm mt-2">{JSON.stringify(scanResults, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
};
```

## 🔐 Quantum Operations Component

```tsx
// src/components/QuantumOperations.tsx
import React, { useState } from 'react';
import { api } from '../lib/api';

export const QuantumOperations: React.FC = () => {
  const [message, setMessage] = useState('');
  const [encryptResult, setEncryptResult] = useState<any>(null);
  const [keyGenResult, setKeyGenResult] = useState<any>(null);

  const handleEncrypt = async () => {
    if (!message) return;
    try {
      const response = await api.quantumEncrypt(message);
      setEncryptResult(response.data);
    } catch (error) {
      console.error('Encryption failed:', error);
    }
  };

  const handleGenerateKeys = async () => {
    try {
      const response = await api.generateKeys();
      setKeyGenResult(response.data);
    } catch (error) {
      console.error('Key generation failed:', error);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Encryption */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Quantum Encryption</h2>
        <div className="space-y-4">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Enter message to encrypt..."
            className="w-full px-3 py-2 border rounded-md"
            rows={3}
          />
          <button
            onClick={handleEncrypt}
            className="px-4 py-2 bg-green-500 text-white rounded-md"
          >
            Encrypt Message
          </button>
          
          {encryptResult && (
            <div className="p-4 bg-gray-50 rounded-md">
              <h3 className="font-medium">Encryption Result</h3>
              <p className="text-sm mt-2 break-all">{encryptResult.encrypted_data}</p>
            </div>
          )}
        </div>
      </div>

      {/* Key Generation */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Key Generation</h2>
        <button
          onClick={handleGenerateKeys}
          className="px-4 py-2 bg-purple-500 text-white rounded-md"
        >
          Generate New Key Pair
        </button>
        
        {keyGenResult && (
          <div className="mt-4 p-4 bg-gray-50 rounded-md">
            <h3 className="font-medium">Generated Key</h3>
            <p className="text-sm mt-2"><strong>Key ID:</strong> {keyGenResult.key_id}</p>
            <p className="text-sm"><strong>Algorithm:</strong> {keyGenResult.algorithm}</p>
            <p className="text-sm"><strong>Created:</strong> {keyGenResult.created_at}</p>
          </div>
        )}
      </div>
    </div>
  );
};
```

## 🧪 Testing the Integration

1. **Start the FastAPI backend:**
   ```bash
   python -m scorpius.api.main
   ```

2. **Test the API endpoints:**
   ```bash
   python test_api_integration.py
   ```

3. **Start your React development server:**
   ```bash
   npm run dev
   ```

## 📡 WebSocket Events

The backend sends these real-time events:

- `connection_established` - Connection confirmed
- `subscription_confirmed` - Event subscription confirmed  
- `quantum_operation` - Quantum crypto operations
- `security_scan` - Security scan updates
- `threat_notification` - New threats detected
- `metrics_update` - System metrics (every 5 seconds)
- `pong` - Heartbeat response

## 🔒 Authentication

The demo uses a simple bearer token (`demo-token`). For production:

1. Implement proper JWT authentication
2. Add user management
3. Role-based access control
4. Token refresh mechanism

## 📈 Performance Tips

1. **Debounce API calls** when user types in search/filter inputs
2. **Use React.memo** for expensive components
3. **Implement virtual scrolling** for large data lists
4. **Cache API responses** using React Query or SWR
5. **Lazy load components** for better initial load time

## 🚀 Production Deployment

1. **Backend:** Use Docker with the provided `docker-compose.enterprise.yml`
2. **Frontend:** Build with `npm run build` and serve with nginx
3. **Environment:** Set proper CORS origins and API URLs
4. **SSL:** Enable HTTPS for both frontend and backend
5. **Monitoring:** Use the built-in metrics and health endpoints

---

🎉 **You're ready to build your Scorpius quantum security dashboard!**

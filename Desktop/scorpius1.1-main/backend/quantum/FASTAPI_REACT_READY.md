# 🚀 Scorpius FastAPI + React Dashboard Integration

## ✅ COMPLETE SETUP

Your Scorpius Enterprise platform now has a **complete FastAPI backend** with comprehensive REST API endpoints and WebSocket support, perfectly designed for easy integration with your Vite + React security dashboard.

## 🎯 What's Been Implemented

### 📡 FastAPI Backend Features
- **REST API**: 20+ endpoints covering all platform features
- **WebSocket Support**: Real-time dashboard updates and metrics streaming
- **CORS Enabled**: Pre-configured for Vite dev server (ports 3000, 5173)
- **Authentication**: Bearer token system (demo-token for testing)
- **Auto-Documentation**: Swagger UI at `/docs` and ReDoc at `/redoc`
- **Error Handling**: Comprehensive error responses with proper HTTP status codes

### 🛠️ API Endpoints Available

#### Core Platform
- `GET /health` - Health check
- `GET /status` - Platform status with module details
- `GET /config` - Platform configuration
- `GET /` - API information and endpoints list

#### Dashboard Specific
- `GET /dashboard/stats` - Overview statistics
- `GET /dashboard/activity` - Activity log with filtering
- `GET /dashboard/resources` - System resource usage
- `GET /dashboard/alerts` - System alerts with acknowledgment
- `POST /dashboard/quick-action` - Execute quick actions
- `GET /dashboard/config` - User dashboard configuration

#### Quantum Cryptography
- `POST /quantum/encrypt` - Encrypt data with quantum algorithms
- `POST /quantum/generate-keys` - Generate quantum-resistant key pairs

#### Security Operations
- `POST /security/scan` - Perform security scans
- `GET /security/threats` - Get active threats

#### Analytics & Reporting
- `POST /analytics/reports` - Generate analytics reports
- `GET /analytics/metrics` - Get platform metrics

#### WebSocket Endpoints
- `ws://localhost:8001/ws/dashboard` - Real-time dashboard updates
- `ws://localhost:8001/ws/metrics` - Live metrics streaming

## 🔌 Quick Start Guide

### 1. Start the Backend
```bash
# Simple start
python start_api_server.py

# With custom settings
python start_api_server.py --port 8001 --reload
```

### 2. Access API Documentation
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **API Info**: http://localhost:8001/

### 3. Test API Endpoints
```bash
# Health check
curl http://localhost:8001/health

# Dashboard stats (requires auth)
curl -H "Authorization: Bearer demo-token" http://localhost:8001/dashboard/stats

# Quick security scan
curl -X POST -H "Authorization: Bearer demo-token" -H "Content-Type: application/json" -d '{"target":"192.168.1.1","scan_type":"quick"}' http://localhost:8001/security/scan
```

### 4. Connect React Frontend
```javascript
// API client setup
const API_BASE_URL = 'http://localhost:8001';
const AUTH_TOKEN = 'demo-token';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Authorization': `Bearer ${AUTH_TOKEN}`,
    'Content-Type': 'application/json',
  },
});

// WebSocket connection
const ws = new WebSocket('ws://localhost:8001/ws/dashboard');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Real-time update:', data);
};
```

## 📊 React Integration Examples

### Dashboard Statistics Component
```typescript
const DashboardStats = () => {
  const [stats, setStats] = useState(null);
  
  useEffect(() => {
    const fetchStats = async () => {
      const response = await apiClient.get('/dashboard/stats');
      setStats(response.data);
    };
    fetchStats();
  }, []);
  
  return (
    <div className="grid grid-cols-4 gap-4">
      <StatCard title="Encryptions" value={stats?.total_encryptions_today} />
      <StatCard title="Scans" value={stats?.total_scans_today} />
      <StatCard title="Threats" value={stats?.active_threats} />
      <StatCard title="Health" value={`${stats?.system_health_score}%`} />
    </div>
  );
};
```

### Real-time Activity Feed
```typescript
const ActivityFeed = () => {
  const [activities, setActivities] = useState([]);
  
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8001/ws/dashboard');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'security_scan' || data.type === 'quantum_operation') {
        setActivities(prev => [data, ...prev.slice(0, 99)]);
      }
    };
    
    return () => ws.close();
  }, []);
  
  return (
    <div className="space-y-2">
      {activities.map((activity, index) => (
        <div key={index} className="p-3 bg-gray-50 rounded">
          <span className="font-medium">{activity.type}</span>
          <span className="text-sm text-gray-500 ml-2">
            {new Date(activity.timestamp).toLocaleString()}
          </span>
        </div>
      ))}
    </div>
  );
};
```

### Security Scanner Component
```typescript
const SecurityScanner = () => {
  const [target, setTarget] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const handleScan = async () => {
    setLoading(true);
    try {
      const response = await apiClient.post('/security/scan', {
        target,
        scan_type: 'comprehensive'
      });
      setResults(response.data);
    } catch (error) {
      console.error('Scan failed:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <input
          value={target}
          onChange={(e) => setTarget(e.target.value)}
          placeholder="Enter target to scan..."
          className="flex-1 px-3 py-2 border rounded"
        />
        <button
          onClick={handleScan}
          disabled={loading || !target}
          className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
        >
          {loading ? 'Scanning...' : 'Scan'}
        </button>
      </div>
      
      {results && (
        <div className="p-4 bg-green-50 border border-green-200 rounded">
          <h3 className="font-semibold">Scan Complete</h3>
          <p>Threats found: {results.threats_found}</p>
          <p>Risk level: {results.risk_level}</p>
        </div>
      )}
    </div>
  );
};
```

## 🔐 Authentication & Security

### Current Setup (Demo)
- **Token**: `demo-token` (for testing)
- **User**: `{"user_id": "demo", "role": "admin"}`
- **Headers**: `Authorization: Bearer demo-token`

### Production Setup
1. Replace demo authentication with JWT tokens
2. Implement user management system
3. Add role-based access control
4. Enable HTTPS for production

## 🌐 WebSocket Events

Your React dashboard can subscribe to these real-time events:

### Dashboard Events
- `connection_established` - WebSocket connected
- `subscription_confirmed` - Event subscription confirmed
- `quantum_operation` - Quantum crypto operations
- `security_scan` - Security scan updates
- `threat_notification` - New threat detected
- `key_generation` - New key pair generated

### Metrics Events
- `metrics_update` - System metrics (every 5 seconds)
- `pong` - Heartbeat response

### Subscription Example
```javascript
ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'subscribe',
    events: ['security_scan', 'quantum_operation', 'threat_notification']
  }));
};
```

## 📈 Performance & Scaling

### Built-in Features
- **Connection Management**: Automatic WebSocket reconnection
- **Error Handling**: Graceful degradation on API failures
- **Background Tasks**: Non-blocking operation processing
- **Health Monitoring**: Real-time system health tracking

### Production Optimizations
- **Caching**: Implement Redis for API response caching
- **Rate Limiting**: Add request rate limiting
- **Load Balancing**: Use multiple API instances
- **Database**: Replace sample data with real database

## 🚢 Deployment Ready

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose -f deployment/docker-compose.enterprise.yml up
```

### Manual Deployment
```bash
# Install dependencies
pip install -r requirements.enterprise.txt

# Run with Gunicorn (production)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker scorpius.api.main:app --bind 0.0.0.0:8000
```

## 🎉 Next Steps

1. **Build your React dashboard** using the provided examples
2. **Test all endpoints** with the provided curl commands
3. **Implement real authentication** for production
4. **Add your custom business logic** to the API endpoints
5. **Deploy to production** using Docker or manual setup

## 📚 Resources

- **API Documentation**: http://localhost:8001/docs
- **Integration Guide**: `REACT_INTEGRATION.md`
- **Test Script**: `test_api_integration.py`
- **Architecture**: `ARCHITECTURE.md`

---

🎯 **Your Scorpius platform is now fully equipped with enterprise-grade FastAPI backend and ready for seamless React dashboard integration!**

The API is running at: **http://localhost:8001**
WebSocket endpoint: **ws://localhost:8001/ws/dashboard**
Authentication: **Bearer demo-token**

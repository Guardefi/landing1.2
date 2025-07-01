# Scorpius X - Backend Integration Guide

This guide explains how to integrate the Scorpius X frontend with your FastAPI backend for real-time data and interactive functionality.

## 🚀 Quick Start

### 1. Environment Setup

Copy `.env.example` to `.env` and configure your backend URLs:

```bash
cp .env.example .env
```

```env
# Your FastAPI backend URLs
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_BASE_URL=ws://localhost:8000/ws
```

### 2. Install Dependencies

The frontend already includes all necessary dependencies:

- `@tanstack/react-query` - For REST API state management
- Native WebSocket - For real-time data
- `sonner` - For notifications

## 📡 WebSocket Integration

### FastAPI WebSocket Endpoint

Your FastAPI backend should implement these WebSocket endpoints:

```python
from fastapi import FastAPI, WebSocket
import json
import asyncio

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    await websocket.accept()

    # Authenticate user with token if provided
    user = authenticate_websocket_token(token)

    try:
        while True:
            # Send real-time data based on subscriptions
            await send_real_time_data(websocket, user)
            await asyncio.sleep(1)  # Send updates every second
    except:
        await websocket.close()

async def send_real_time_data(websocket: WebSocket, user):
    """Send different types of real-time data"""

    # System Metrics
    await websocket.send_text(json.dumps({
        "event": "system_metrics",
        "data": {
            "cpu_usage": get_cpu_usage(),
            "memory_usage": get_memory_usage(),
            "disk_usage": get_disk_usage(),
            "network_io": get_network_io(),
            "active_connections": get_active_connections(),
            "response_time": get_response_time()
        },
        "timestamp": datetime.utcnow().isoformat()
    }))

    # Trading Data
    await websocket.send_text(json.dumps({
        "event": "trading_stats",
        "data": get_trading_stats(),
        "timestamp": datetime.utcnow().isoformat()
    }))

    # More events...
```

### WebSocket Events

The frontend expects these WebSocket events:

| Event                  | Description                     | Data Type              |
| ---------------------- | ------------------------------- | ---------------------- |
| `system_metrics`       | Real-time system performance    | `SystemMetrics`        |
| `system_alerts`        | System alerts and notifications | `SystemAlert[]`        |
| `trading_stats`        | Trading performance stats       | `TradingStats`         |
| `trading_bots`         | Bot status updates              | `TradingBot[]`         |
| `trading_transactions` | Live transaction feed           | `TradingTransaction[]` |
| `bridge_metrics`       | Bridge network metrics          | `BridgeMetrics`        |
| `bridge_transfers`     | Active transfers                | `BridgeTransfer[]`     |
| `cluster_metrics`      | Computing cluster stats         | `ClusterMetrics`       |
| `scan_results`         | Security scan results           | `ScanResult[]`         |

## 🔌 REST API Endpoints

### Authentication Endpoints

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

auth_router = APIRouter(prefix="/auth")

class LoginRequest(BaseModel):
    email: str
    password: str
    remember_me: bool = False

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserProfile
    expires_in: int

@auth_router.post("/login", response_model=APIResponse[LoginResponse])
async def login(request: LoginRequest):
    # Authenticate user
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return APIResponse(
        success=True,
        data=LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user,
            expires_in=3600
        )
    )

@auth_router.post("/license/verify")
async def verify_license(request: LicenseVerificationRequest):
    # Verify license key or file
    license_info = verify_license_key(request.license_key)
    return APIResponse(success=True, data=license_info)
```

### System Endpoints

```python
system_router = APIRouter(prefix="/system")

@system_router.get("/status", response_model=APIResponse[SystemStatus])
async def get_system_status():
    return APIResponse(
        success=True,
        data=SystemStatus(
            status="healthy",
            uptime=get_system_uptime(),
            version="1.0.0",
            environment="production"
        )
    )

@system_router.get("/metrics", response_model=APIResponse[SystemMetrics])
async def get_system_metrics():
    return APIResponse(
        success=True,
        data=SystemMetrics(
            cpu_usage=get_cpu_usage(),
            memory_usage=get_memory_usage(),
            # ... other metrics
        )
    )
```

### Trading Endpoints

```python
trading_router = APIRouter(prefix="/trading")

@trading_router.get("/stats", response_model=APIResponse[TradingStats])
async def get_trading_stats():
    return APIResponse(
        success=True,
        data=TradingStats(
            total_profit=get_total_profit(),
            total_trades=get_total_trades(),
            success_rate=get_success_rate(),
            # ... other stats
        )
    )

@trading_router.post("/strategies/toggle")
async def toggle_strategy(request: ToggleStrategyRequest):
    # Toggle strategy on/off
    strategy = update_strategy_status(request.strategy_id, request.enabled)
    return APIResponse(success=True, data=strategy)

@trading_router.get("/bots", response_model=APIResponse[List[TradingBot]])
async def get_trading_bots():
    bots = get_all_trading_bots()
    return APIResponse(success=True, data=bots)
```

## 🎛️ Frontend Integration Examples

### Using WebSocket Data

```typescript
// In any React component
import { useWebSocket } from "@/lib/api";

function SystemMetricsWidget() {
  const { data: metrics, connected } = useWebSocket<SystemMetrics>("system_metrics");

  if (!connected) {
    return <div>Connecting to real-time data...</div>;
  }

  return (
    <div>
      <h3>CPU Usage: {metrics?.cpu_usage}%</h3>
      <h3>Memory: {metrics?.memory_usage}%</h3>
    </div>
  );
}
```

### Using REST API with React Query

```typescript
// Using the pre-built hooks
import { useTradingStats, useToggleStrategy } from "@/lib/api/hooks";

function TradingDashboard() {
  const { data: stats, isLoading, error } = useTradingStats();
  const toggleStrategy = useToggleStrategy();

  const handleToggle = (strategyId: string, enabled: boolean) => {
    toggleStrategy.mutate({ strategy_id: strategyId, enabled });
  };

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h2>Total Profit: {stats?.total_profit} ETH</h2>
      {/* Strategy controls */}
    </div>
  );
}
```

### Making Direct API Calls

```typescript
import { apiService } from "@/lib/api";

// In event handlers or effects
async function handleStartScan() {
  try {
    const response = await apiService.startScan({
      target: "192.168.1.1",
      scan_type: "full",
      depth: 5,
    });

    if (response.success) {
      console.log("Scan started:", response.data);
    }
  } catch (error) {
    console.error("Scan failed:", error);
  }
}
```

## 📋 Required Backend Models

### Core Response Model

```python
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional
from datetime import datetime

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = datetime.utcnow()
```

### Authentication Models

```python
class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    role: str  # "admin" | "operator" | "viewer"
    organization: Optional[str] = None
    last_login: datetime
    permissions: List[str]

class LicenseInfo(BaseModel):
    id: str
    type: str  # "enterprise" | "professional" | "standard"
    status: str  # "active" | "expired" | "pending" | "invalid"
    holder: str
    organization: str
    issued_date: str
    expiry_date: str
    features: List[str]
    max_users: int
    current_users: int
    api_limits: dict
```

### System Models

```python
class SystemMetrics(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: float
    active_connections: int
    response_time: float

class SystemAlert(BaseModel):
    id: str
    severity: str  # "critical" | "warning" | "info"
    title: str
    description: str
    timestamp: datetime
    acknowledged: bool
    assignee: Optional[str] = None
    service: str
```

### Trading Models

```python
class TradingBot(BaseModel):
    id: str
    name: str
    strategy: str
    status: str  # "active" | "idle" | "processing" | "error"
    position: dict  # {"x": float, "y": float}
    profit: float
    trades: int
    gas_used: float
    color: str
    last_updated: datetime

class TradingStats(BaseModel):
    total_profit: float
    total_trades: int
    success_rate: float
    gas_efficiency: float
    protection_level: float
    attacks_prevented: int
    value_saved: float
```

## 🔧 Implementation Checklist

### Backend Requirements

- [ ] FastAPI server with CORS enabled
- [ ] WebSocket endpoint at `/ws`
- [ ] JWT authentication system
- [ ] All REST endpoints implemented
- [ ] Proper error handling and status codes
- [ ] Rate limiting (optional)
- [ ] Logging and monitoring

### Frontend Setup

- [ ] Environment variables configured
- [ ] API base URLs set correctly
- [ ] WebSocket connection working
- [ ] Authentication flow tested
- [ ] Error handling implemented
- [ ] Loading states configured

### Testing

- [ ] Login/logout functionality
- [ ] Real-time data updates
- [ ] Button/toggle interactions
- [ ] Error scenarios
- [ ] WebSocket reconnection
- [ ] API rate limiting response

## 🚨 Error Handling

The frontend includes comprehensive error handling:

- **Network errors**: Automatic retry with exponential backoff
- **Authentication errors**: Automatic token refresh
- **WebSocket disconnection**: Automatic reconnection
- **API errors**: User-friendly error messages via toast notifications

## 📊 Monitoring Integration

The frontend automatically sends usage analytics and error reports. Configure these endpoints in your backend:

```python
@app.post("/analytics/events")
async def track_event(event: AnalyticsEvent):
    # Track user interactions, errors, etc.
    pass

@app.post("/errors/report")
async def report_error(error: ErrorReport):
    # Handle frontend error reports
    pass
```

## 🔐 Security Considerations

- **JWT tokens**: Store securely, automatic refresh
- **CORS**: Configure properly for your domains
- **Rate limiting**: Implement on sensitive endpoints
- **Input validation**: Validate all inputs server-side
- **WebSocket authentication**: Verify tokens on connection

## 📝 Development Tips

1. **Mock Data**: Remove all mock data from components
2. **Error States**: Test error scenarios thoroughly
3. **Loading States**: Ensure good UX during API calls
4. **Real-time Data**: Test WebSocket reconnection
5. **Authentication**: Test token expiration handling

---

This integration provides a production-ready foundation for connecting your sophisticated Scorpius X frontend with any FastAPI backend. All buttons, toggles, and interactive elements are ready for real backend integration!

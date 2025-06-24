# 🚀 Live Data Integration Setup Guide

## Overview

This guide will help you connect your React frontend to your Python backend for real live data instead of mock simulations.

## ✅ What's Already Fixed

- ✅ LiveCounter auto-increment simulation removed
- ✅ Duplicate systemMetrics declarations resolved
- ✅ Null safety added for .toFixed() calls
- ✅ Navigation errors fixed (useNavigate imports)
- ✅ State management issues resolved
- ✅ useLiveStats hook providing realistic defaults
- ✅ WebSocket enabled in frontend configuration

## 🔧 Steps to Complete Live Data Integration

### Step 1: Start Your Python Backend

```bash
# Option A: Manual startup
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Option B: Use the startup script
./start_backend.sh
```

**Expected Result:** Backend running at http://localhost:8000

### Step 2: Verify Backend Endpoints

Your backend should expose these endpoints:

- `/api/scanner/stats` - Smart contract scanner metrics
- `/api/mev/stats` - MEV bot performance data
- `/api/bounties/stats` - Bug bounty program metrics
- `/api/training/stats` - Training system progress
- `/api/reports/stats` - Report generation statistics
- `/api/scheduler/stats` - Job scheduler metrics
- `/api/monitoring/stats` - System monitoring data
- `/api/dashboard/stats` - Overall dashboard metrics

### Step 3: WebSocket Server Setup

Ensure your Python backend includes WebSocket support for real-time updates:

- `ws://localhost:8000/ws/scanner` - Scanner events
- `ws://localhost:8000/ws/mev` - MEV transaction events
- `ws://localhost:8000/ws/monitoring` - System health events

### Step 4: Remaining Mock Data to Fix

**Critical Pages Still Using Simulation:**

1. **TrapGrid.tsx** (Lines 152-166, 279-289)

   - Generates fake threat events with Math.random()
   - Needs integration with honeypot detection backend

2. **SmartContractScanner.tsx** (Lines 212, 295)

   - Has progress simulation with Math.random()
   - Needs real scan progress from vulnerability scanner

3. **Visual Effects** (Multiple pages)
   - Background particle animations using Math.random() for positioning
   - These are cosmetic and can remain

## 🎯 Priority Fix List

### High Priority (Data Generation)

1. **TrapGrid.tsx** - Replace threat event simulation
2. **SmartContractScanner.tsx** - Remove progress simulation

### Medium Priority (Visual Polish)

3. **Charts/Graphs** - Ensure all use real data points
4. **Performance Metrics** - Remove any remaining Math.random() calculations

### Low Priority (Cosmetic)

5. **Animation Effects** - Particle positions, timing delays (can keep Math.random)

## 🔧 Quick Fixes Needed

### Fix TrapGrid Threat Events

```typescript
// Replace in TrapGrid.tsx
const fetchThreatEvents = useCallback(async () => {
  if (!backendAvailable) return;

  try {
    const response = await fetch('/api/trapgrid/events');
    const data = await response.json();
    setThreatEvents(data.events);
  } catch (error) {
    console.log('Threat events unavailable');
  }
}, [backendAvailable]);
```

### Fix Scanner Progress

```typescript
// Replace in SmartContractScanner.tsx
const fetchScanProgress = useCallback(async () => {
  if (!backendAvailable) return;

  try {
    const response = await fetch('/api/scanner/progress');
    const data = await response.json();
    setScanProgress(data.progress);
  } catch (error) {
    console.log('Scan progress unavailable');
  }
}, [backendAvailable]);
```

## 🧪 Testing Live Data Integration

### 1. Start Backend

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Check API Endpoints

```bash
curl http://localhost:8000/api/dashboard/stats
curl http://localhost:8000/api/scanner/stats
curl http://localhost:8000/api/mev/stats
```

### 3. Verify Frontend Connection

- Open browser dev tools
- Check Network tab for API calls
- Look for WebSocket connections in Console
- Verify data updates in real-time

## 🚨 Backend Requirements

Your Python backend must provide these data structures:

### Scanner Stats

```json
{
  "totalScans": 1247,
  "vulnerabilitiesFound": 89,
  "successRate": 95.0,
  "avgScanTime": 12.0
}
```

### MEV Stats

```json
{
  "activeBots": 23,
  "opportunitiesFound": 156,
  "totalProfit": 45.67,
  "successRate": 78.5
}
```

### Monitoring Stats

```json
{
  "uptime": 99.9,
  "responseTime": 156.0,
  "errorRate": 0.01,
  "servicesOnline": 6
}
```

## ✅ Success Indicators

When fully integrated, you should see:

- ✅ Real numbers from your Python modules
- ✅ Data that changes based on actual backend activity
- ✅ WebSocket connections in browser dev tools
- ✅ No more incrementing fake counters
- ✅ Consistent data across page refreshes
- ✅ Backend logs showing API requests

## 🆘 Troubleshooting

### Backend Not Starting

- Check Python dependencies: `pip install fastapi uvicorn`
- Verify port 8000 is available: `lsof -i :8000`
- Check backend logs for import errors

### Frontend Not Connecting

- Verify VITE_WEBSOCKET_ENABLED=true in .env.development
- Check browser console for CORS errors
- Ensure API_BASE_URL matches backend address

### Data Not Updating

- Check if useLiveStats hooks are using correct endpoints
- Verify backend is returning expected JSON structure
- Check WebSocket connections in browser dev tools

## 🎉 Final Result

Once completed, your dashboard will display **real live data** from your Python security modules instead of simulated mock data, providing an authentic cybersecurity monitoring experience!

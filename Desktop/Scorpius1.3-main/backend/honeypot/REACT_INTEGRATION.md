# Honeypot Detector API - React Dashboard Integration Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB (or Docker)
- Redis (or Docker)
- Node.js (for your React dashboard)

### 1. Setup API Server

#### Option A: Using Python Virtual Environment
```powershell
# Run setup script
.\setup_api.ps1

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start the API
python start_api.py
```

#### Option B: Using Docker
```powershell
# Start all services with Docker
docker-compose up -d

# Check logs
docker-compose logs -f api
```

### 2. API will be available at:
- **Main API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📡 API Endpoints for React Integration

### Authentication
All requests require the `X-API-Key` header:
```javascript
const headers = {
  'X-API-Key': 'honeypot-detector-api-key-12345',
  'Content-Type': 'application/json'
}
```

### Core Endpoints

#### 1. Health Check
```javascript
// GET /health
const response = await fetch('http://localhost:8000/health', { headers });
```

#### 2. Analyze Contract
```javascript
// POST /api/v1/analyze
const analyzeContract = async (address, chainId = 1, deepAnalysis = false) => {
  const response = await fetch('http://localhost:8000/api/v1/analyze', {
    method: 'POST',
    headers,
    body: JSON.stringify({
      address,
      chain_id: chainId,
      deep_analysis: deepAnalysis
    })
  });
  return await response.json();
};
```

#### 3. Dashboard Statistics
```javascript
// GET /api/v1/dashboard/stats?days=30
const getDashboardStats = async (days = 30) => {
  const response = await fetch(
    `http://localhost:8000/api/v1/dashboard/stats?days=${days}`, 
    { headers }
  );
  return await response.json();
};
```

#### 4. Trend Data for Charts
```javascript
// GET /api/v1/dashboard/trends?days=30
const getTrendData = async (days = 30) => {
  const response = await fetch(
    `http://localhost:8000/api/v1/dashboard/trends?days=${days}`, 
    { headers }
  );
  return await response.json();
};
```

#### 5. Search Contracts
```javascript
// GET /api/v1/dashboard/search
const searchContracts = async (query, filters = {}) => {
  const params = new URLSearchParams({
    query: query || '',
    limit: filters.limit || 20,
    offset: filters.offset || 0,
    ...(filters.risk_level && { risk_level: filters.risk_level }),
    ...(filters.is_honeypot !== undefined && { is_honeypot: filters.is_honeypot })
  });
  
  const response = await fetch(
    `http://localhost:8000/api/v1/dashboard/search?${params}`, 
    { headers }
  );
  return await response.json();
};
```

#### 6. Contract Details
```javascript
// GET /api/v1/dashboard/contract/{address}/details
const getContractDetails = async (address) => {
  const response = await fetch(
    `http://localhost:8000/api/v1/dashboard/contract/${address}/details`, 
    { headers }
  );
  return await response.json();
};
```

#### 7. Analysis History
```javascript
// GET /api/v1/history/{address}?limit=10
const getAnalysisHistory = async (address, limit = 10) => {
  const response = await fetch(
    `http://localhost:8000/api/v1/history/${address}?limit=${limit}`, 
    { headers }
  );
  return await response.json();
};
```

## 🎨 React Integration Examples

### 1. API Service Hook
```javascript
// hooks/useHoneypotAPI.js
import { useState, useCallback } from 'react';

const API_BASE = 'http://localhost:8000';
const API_KEY = 'honeypot-detector-api-key-12345';

const useHoneypotAPI = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const request = useCallback(async (endpoint, options = {}) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        headers: {
          'X-API-Key': API_KEY,
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      });
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { request, loading, error };
};

export default useHoneypotAPI;
```

### 2. Dashboard Component Example
```javascript
// components/Dashboard.jsx
import React, { useState, useEffect } from 'react';
import useHoneypotAPI from '../hooks/useHoneypotAPI';

const Dashboard = () => {
  const { request, loading, error } = useHoneypotAPI();
  const [stats, setStats] = useState(null);
  const [trends, setTrends] = useState(null);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const [statsData, trendsData] = await Promise.all([
          request('/api/v1/dashboard/stats?days=30'),
          request('/api/v1/dashboard/trends?days=30')
        ]);
        
        setStats(statsData);
        setTrends(trendsData);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      }
    };

    loadDashboardData();
  }, [request]);

  if (loading) return <div>Loading dashboard...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="dashboard">
      <div className="stats-grid">
        {stats && (
          <>
            <div className="stat-card">
              <h3>Total Analyses</h3>
              <p>{stats.total_analyses}</p>
            </div>
            <div className="stat-card">
              <h3>Honeypots Detected</h3>
              <p>{stats.honeypots_detected}</p>
            </div>
            <div className="stat-card">
              <h3>Detection Rate</h3>
              <p>{stats.detection_rate}%</p>
            </div>
          </>
        )}
      </div>
      
      {/* Add your charts and other components here */}
    </div>
  );
};

export default Dashboard;
```

### 3. Contract Analysis Component
```javascript
// components/ContractAnalyzer.jsx
import React, { useState } from 'react';
import useHoneypotAPI from '../hooks/useHoneypotAPI';

const ContractAnalyzer = () => {
  const { request, loading, error } = useHoneypotAPI();
  const [address, setAddress] = useState('');
  const [result, setResult] = useState(null);

  const analyzeContract = async (e) => {
    e.preventDefault();
    
    try {
      const data = await request('/api/v1/analyze', {
        method: 'POST',
        body: JSON.stringify({
          address,
          chain_id: 1,
          deep_analysis: false
        })
      });
      
      setResult(data);
    } catch (err) {
      console.error('Analysis failed:', err);
    }
  };

  return (
    <div className="contract-analyzer">
      <form onSubmit={analyzeContract}>
        <input
          type="text"
          value={address}
          onChange={(e) => setAddress(e.target.value)}
          placeholder="Enter contract address (0x...)"
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Analyzing...' : 'Analyze Contract'}
        </button>
      </form>

      {error && <div className="error">Error: {error}</div>}
      
      {result && (
        <div className="analysis-result">
          <h3>Analysis Result</h3>
          <div className={`result ${result.is_honeypot ? 'honeypot' : 'safe'}`}>
            <p><strong>Address:</strong> {result.address}</p>
            <p><strong>Is Honeypot:</strong> {result.is_honeypot ? 'Yes' : 'No'}</p>
            <p><strong>Confidence:</strong> {(result.confidence * 100).toFixed(1)}%</p>
            <p><strong>Risk Level:</strong> {result.risk_level}</p>
            {result.detected_techniques.length > 0 && (
              <div>
                <strong>Detected Techniques:</strong>
                <ul>
                  {result.detected_techniques.map((technique, index) => (
                    <li key={index}>{technique}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ContractAnalyzer;
```

## 🔧 Configuration

### Environment Variables
Update your `.env` file:
```env
API_KEY=your-secure-api-key-here
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173","*"]
DEBUG=true
```

### CORS Configuration
The API is already configured to accept requests from:
- http://localhost:3000 (Create React App default)
- http://localhost:5173 (Vite default)
- Any other origin (for development)

## 🔍 Testing the API

### Using curl:
```bash
# Health check
curl -H "X-API-Key: honeypot-detector-api-key-12345" http://localhost:8000/health

# Analyze a contract
curl -X POST -H "X-API-Key: honeypot-detector-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"address":"0x1234567890abcdef1234567890abcdef12345678","chain_id":1}' \
  http://localhost:8000/api/v1/analyze
```

### Using JavaScript (browser console):
```javascript
// Test the API from your browser console
const testAPI = async () => {
  const response = await fetch('http://localhost:8000/health', {
    headers: { 'X-API-Key': 'honeypot-detector-api-key-12345' }
  });
  console.log(await response.json());
};
testAPI();
```

## 📊 Data Models

### Analysis Response:
```typescript
interface AnalysisResponse {
  address: string;
  is_honeypot: boolean;
  confidence: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  detected_techniques: string[];
  analysis_timestamp: string;
  engine_results?: Record<string, any>;
  transaction_history?: Record<string, any>;
}
```

### Dashboard Stats:
```typescript
interface DashboardStats {
  total_analyses: number;
  honeypots_detected: number;
  false_positives: number;
  detection_rate: number;
  recent_analyses: Array<{
    address: string;
    is_honeypot: boolean;
    confidence: number;
    risk_level: string;
    timestamp: string;
    techniques: string[];
  }>;
  risk_distribution: Record<string, number>;
  technique_distribution: Record<string, number>;
}
```

## 🚀 Next Steps

1. **Start the API**: Run `python start_api.py` or `docker-compose up`
2. **Test endpoints**: Visit http://localhost:8000/docs for interactive API docs
3. **Integrate with React**: Use the provided examples and hooks
4. **Customize**: Modify the API endpoints to match your dashboard needs
5. **Deploy**: When ready, deploy using Docker or your preferred platform

The API is now ready for integration with your Vite React dashboard! 🎉

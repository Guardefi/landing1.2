# Honeypot Detector API - Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Python 3.8+ installed
- PowerShell (Windows)
- Optional: MongoDB and Redis (can use Docker)

### Step 1: Setup Environment
```powershell
# Run the setup script
.\setup_api.ps1
```

### Step 2: Start Dependencies (Optional)
```powershell
# Using Docker (recommended)
docker run -d -p 27017:27017 --name mongodb mongo:latest
docker run -d -p 6379:6379 --name redis redis:latest

# OR start your local MongoDB and Redis services
```

### Step 3: Start the API
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start the API server
python start_api.py
```

The API will start at `http://localhost:8000`

### Step 4: Test the API
```powershell
# Run comprehensive tests
python run_tests.py

# Run only React integration tests
python test_react_integration.py

# Run performance benchmarks
python test_performance.py
```

## 🔗 API Endpoints for React Integration

### Authentication
All requests require the `X-API-Key` header:
```
X-API-Key: honeypot-detector-api-key-12345
```

### Core Endpoints

#### Health Check
```http
GET /health
```

#### Analyze Contract
```http
POST /api/v1/analyze
Content-Type: application/json

{
  "address": "0xa0b86a33e6c3ca4fdd100269d7e5e50b637cab5d",
  "chain_id": 1,
  "deep_analysis": false
}
```

#### Dashboard Statistics
```http
GET /api/v1/dashboard/stats?days=30
```

#### Trend Data for Charts
```http
GET /api/v1/dashboard/trends?days=7
```

#### Search Contracts
```http
GET /api/v1/dashboard/search?query=0x123&limit=20
```

#### Contract Details
```http
GET /api/v1/dashboard/contract/{address}/details
```

#### Analysis History
```http
GET /api/v1/history/{address}?limit=10
```

## ⚛️ React Integration Example

### Setup Axios (or your HTTP client)
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'X-API-Key': 'honeypot-detector-api-key-12345',
    'Content-Type': 'application/json'
  }
});
```

### Analyze a Contract
```javascript
const analyzeContract = async (address) => {
  try {
    const response = await api.post('/api/v1/analyze', {
      address: address,
      chain_id: 1,
      deep_analysis: false
    });
    return response.data;
  } catch (error) {
    console.error('Analysis failed:', error);
    throw error;
  }
};
```

### Get Dashboard Stats
```javascript
const getDashboardStats = async () => {
  try {
    const response = await api.get('/api/v1/dashboard/stats');
    return response.data;
  } catch (error) {
    console.error('Failed to get stats:', error);
    throw error;
  }
};
```

### Get Trend Data for Charts
```javascript
const getTrendData = async (days = 7) => {
  try {
    const response = await api.get(`/api/v1/dashboard/trends?days=${days}`);
    return response.data;
  } catch (error) {
    console.error('Failed to get trends:', error);
    throw error;
  }
};
```

## 📊 Expected Data Structures

### Analysis Response
```json
{
  "address": "0xa0b86a33e6c3ca4fdd100269d7e5e50b637cab5d",
  "is_honeypot": true,
  "confidence": 0.92,
  "risk_level": "high",
  "detected_techniques": ["Hidden State Update", "Straw Man Contract"],
  "analysis_timestamp": "2025-06-24T10:30:00Z",
  "engine_results": {
    "static_engine": {"confidence": 0.85},
    "ml_engine": {"confidence": 0.98}
  }
}
```

### Dashboard Stats Response
```json
{
  "total_analyses": 1250,
  "honeypots_detected": 89,
  "false_positives": 1161,
  "detection_rate": 7.12,
  "recent_analyses": [...],
  "risk_distribution": {
    "low": 800,
    "medium": 361,
    "high": 78,
    "critical": 11
  },
  "technique_distribution": {
    "Hidden State Update": 45,
    "Balance Disorder": 23
  }
}
```

### Trend Data Response
```json
{
  "dates": ["2025-06-17", "2025-06-18", "2025-06-19"],
  "honeypot_counts": [12, 8, 15],
  "analysis_counts": [145, 132, 189],
  "detection_rates": [8.3, 6.1, 7.9]
}
```

## 🔧 Configuration

### Environment Variables (.env)
```env
# API Configuration
API_KEY=honeypot-detector-api-key-12345
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:5173", "*"]
DEBUG=true

# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=honeypot_detector

# Cache
REDIS_URL=redis://localhost:6379/0
```

## 📝 Testing

### Run All Tests
```powershell
python run_tests.py
```

### Test Specific Areas
```powershell
# API functionality
python test_comprehensive.py

# React integration
python test_react_integration.py

# Performance
python test_performance.py
```

## 🚨 Troubleshooting

### Common Issues

1. **API Key Error (401)**
   - Ensure you're sending the `X-API-Key` header
   - Check the key matches the one in `.env`

2. **CORS Errors**
   - Verify your React app origin is in `ALLOWED_ORIGINS`
   - Check the API is running on the correct port

3. **Database Errors (500)**
   - Ensure MongoDB is running
   - Check connection string in `.env`

4. **Slow Response Times**
   - Check if Redis is running for caching
   - Monitor system resources

### Health Check
```http
GET /health/status
```
Returns detailed system status including database connections.

## 🎯 Next Steps

1. **Production Deployment**
   - Use environment-specific configuration
   - Set up SSL/HTTPS
   - Configure proper API keys
   - Set up monitoring

2. **React Dashboard Features**
   - Real-time updates with WebSockets
   - Interactive charts with the trend data
   - Contract comparison features
   - Export functionality

3. **Advanced Features**
   - Batch analysis
   - Webhook notifications
   - Custom risk scoring
   - Machine learning model updates

## 📚 API Documentation

Once the server is running, visit:
- Interactive docs: `http://localhost:8000/docs`
- ReDoc docs: `http://localhost:8000/redoc`

## 🤝 Support

For issues or questions:
1. Check the test output for specific error messages
2. Review the logs in the `logs/` directory
3. Ensure all dependencies are properly installed
4. Verify MongoDB and Redis connectivity

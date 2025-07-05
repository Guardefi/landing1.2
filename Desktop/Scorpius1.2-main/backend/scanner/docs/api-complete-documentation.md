# Scorpius Enterprise API Documentation

## Overview

Scorpius Enterprise provides a comprehensive REST API ecosystem for vulnerability scanning, plugin management, and security analysis. The platform consists of multiple API services that work together to provide enterprise-grade security testing capabilities.

## API Services

### 1. Main Scorpius API (Port 8080)

The central API that orchestrates all scanning operations, manages plugins, and provides unified access to all features.

**Base URL:** `http://localhost:8080`

**Documentation:** `http://localhost:8080/docs`

#### Core Endpoints

- `GET /api/v1/scan` - Start a new vulnerability scan
- `GET /api/v1/scan/{scan_id}/status` - Get scan status
- `GET /api/v1/scan/{scan_id}/results` - Get scan results
- `POST /api/v1/simulation` - Start exploit simulation
- `GET /api/v1/plugins` - List available plugins
- `GET /api/v1/metrics` - Get system metrics

### 2. Plugin APIs

Each security analysis plugin runs as a separate microservice with its own REST API.

#### Slither API (Port 8081)

Static analysis for Solidity smart contracts.

**Base URL:** `http://localhost:8081`

**Capabilities:**
- Static code analysis
- Vulnerability detection (reentrancy, arithmetic, etc.)
- SARIF and JSON output formats

**Key Endpoints:**
- `GET /health` - Health check
- `GET /capabilities` - Get plugin capabilities
- `POST /scan` - Start Slither scan
- `POST /scan/upload` - Upload and scan file
- `GET /scan/{scan_id}/status` - Get scan status
- `GET /scan/{scan_id}/results` - Get scan results
- `DELETE /scan/{scan_id}` - Delete scan
- `GET /scans` - List all scans

**Example Usage:**
```bash
# Health check
curl http://localhost:8081/health

# Upload and scan a Solidity file
curl -X POST -F "file=@contract.sol" -F "options={}" http://localhost:8081/scan/upload

# Get scan results
curl http://localhost:8081/scan/{scan_id}/results
```

#### Mythril API (Port 8082)

Symbolic execution analysis for Ethereum smart contracts.

**Base URL:** `http://localhost:8082`

**Capabilities:**
- Symbolic execution
- Deep vulnerability analysis
- Bytecode analysis support

**Endpoints:** Same structure as Slither API

**Example Usage:**
```bash
# Start scan with custom options
curl -X POST -H "Content-Type: application/json" \
  -d '{"target_path":"/path/to/contract.sol","options":{"max_depth":10}}' \
  http://localhost:8082/scan
```

#### Manticore API (Port 8083)

Dynamic symbolic execution engine.

**Base URL:** `http://localhost:8083`

**Capabilities:**
- Dynamic symbolic execution
- Binary and smart contract analysis
- Concolic testing

**Endpoints:** Same structure as other plugin APIs

#### MythX API (Port 8084)

Cloud-based professional security analysis.

**Base URL:** `http://localhost:8084`

**Capabilities:**
- Cloud-based analysis
- Professional-grade vulnerability detection
- Requires API key authentication

**Additional Requirements:**
- MythX API key (set via environment variable `MYTHX_API_KEY`)

**Example Usage:**
```bash
# Scan with API key
curl -X POST -H "Content-Type: application/json" \
  -d '{"target_path":"/path/to/contract.sol","options":{"api_key":"your_mythx_key"}}' \
  http://localhost:8084/scan
```

### 3. Results API

Comprehensive results management and analytics.

**Base URL:** `http://localhost:8080/api/v1`

#### Results Endpoints

- `GET /results` - List scan results with filtering
- `GET /results/{scan_id}` - Get detailed scan result
- `DELETE /results/{scan_id}` - Delete scan result
- `POST /reports` - Generate scan report
- `GET /analytics/summary` - Get analytics summary

#### Simulation Endpoints

- `POST /simulations` - Start vulnerability simulation
- `GET /simulations` - List simulations
- `GET /simulations/{simulation_id}` - Get simulation result
- `DELETE /simulations/{simulation_id}` - Delete simulation

**Example Usage:**
```bash
# List recent scan results
curl "http://localhost:8080/api/v1/results?limit=10&status=completed"

# Start simulation for a vulnerability
curl -X POST -H "Content-Type: application/json" \
  -d '{"vulnerability_id":"vuln-123","target_identifier":"0x...","simulation_type":"proof_of_concept"}' \
  http://localhost:8080/api/v1/simulations

# Generate HTML report
curl -X POST -H "Content-Type: application/json" \
  -d '{"scan_id":"scan-123","format":"html","include_details":true}' \
  http://localhost:8080/api/v1/reports
```

### 4. Plugin Marketplace API

Advanced plugin marketplace for discovering and managing security tools.

**Base URL:** `http://localhost:8080/api/v1/marketplace`

#### Marketplace Endpoints

- `GET /plugins` - Search and filter plugins
- `GET /plugins/{plugin_id}` - Get plugin details
- `POST /plugins` - Upload new plugin
- `POST /plugins/{plugin_id}/install` - Install plugin
- `DELETE /plugins/{plugin_id}/install` - Uninstall plugin
- `GET /installed` - List installed plugins
- `POST /plugins/{plugin_id}/reviews` - Add review
- `GET /categories` - Get plugin categories
- `GET /stats` - Get marketplace statistics

#### Admin Endpoints

- `POST /admin/plugins/{plugin_id}/approve` - Approve plugin
- `POST /admin/plugins/{plugin_id}/verify` - Verify plugin

**Example Usage:**
```bash
# Search for static analysis plugins
curl "http://localhost:8080/api/v1/marketplace/plugins?category=static-analysis&verified_only=true"

# Get plugin details
curl http://localhost:8080/api/v1/marketplace/plugins/slither-official

# Install a plugin
curl -X POST -H "Content-Type: application/json" \
  -d '{"plugin_id":"slither-official","version":"latest"}' \
  http://localhost:8080/api/v1/marketplace/plugins/slither-official/install

# Add a review
curl -X POST -H "Content-Type: application/json" \
  -d '{"rating":5,"title":"Excellent tool","content":"Very comprehensive static analysis"}' \
  http://localhost:8080/api/v1/marketplace/plugins/slither-official/reviews
```

## Authentication

Most endpoints require authentication via Bearer token. Include the token in the Authorization header:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8080/api/v1/plugins
```

## Error Handling

All APIs return consistent error responses:

```json
{
  "detail": "Error description",
  "status_code": 400
}
```

Common HTTP status codes:
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

The APIs implement rate limiting to ensure fair usage:
- General endpoints: 100 requests/minute
- Upload endpoints: 10 requests/minute
- Scan endpoints: 5 requests/minute

## WebSocket Support

Real-time updates are available via WebSocket connections:

```javascript
const ws = new WebSocket('ws://localhost:8080/ws/scans');
ws.onmessage = function(event) {
    const update = JSON.parse(event.data);
    console.log('Scan update:', update);
};
```

## SDK and Client Libraries

### Python SDK Example

```python
import requests

class ScorpiusClient:
    def __init__(self, base_url="http://localhost:8080", token=None):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    def start_scan(self, target, scan_type="full"):
        response = requests.post(
            f"{self.base_url}/api/v1/scan",
            json={"target": target, "scan_type": scan_type},
            headers=self.headers
        )
        return response.json()
    
    def get_scan_results(self, scan_id):
        response = requests.get(
            f"{self.base_url}/api/v1/scan/{scan_id}/results",
            headers=self.headers
        )
        return response.json()

# Usage
client = ScorpiusClient(token="your_token")
scan = client.start_scan({"type": "source_code", "identifier": "contract.sol"})
results = client.get_scan_results(scan["scan_id"])
```

### JavaScript SDK Example

```javascript
class ScorpiusClient {
    constructor(baseUrl = 'http://localhost:8080', token = null) {
        this.baseUrl = baseUrl;
        this.headers = token ? { 'Authorization': `Bearer ${token}` } : {};
    }
    
    async startScan(target, scanType = 'full') {
        const response = await fetch(`${this.baseUrl}/api/v1/scan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...this.headers },
            body: JSON.stringify({ target, scan_type: scanType })
        });
        return response.json();
    }
    
    async getScanResults(scanId) {
        const response = await fetch(`${this.baseUrl}/api/v1/scan/${scanId}/results`, {
            headers: this.headers
        });
        return response.json();
    }
}

// Usage
const client = new ScorpiusClient('http://localhost:8080', 'your_token');
const scan = await client.startScan({type: 'source_code', identifier: 'contract.sol'});
const results = await client.getScanResults(scan.scan_id);
```

## Frontend Integration

### React Component Example

```jsx
import React, { useState, useEffect } from 'react';

const ScanResults = ({ scanId }) => {
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        const fetchResults = async () => {
            try {
                const response = await fetch(`/api/v1/scan/${scanId}/results`);
                const data = await response.json();
                setResults(data);
            } catch (error) {
                console.error('Failed to fetch results:', error);
            } finally {
                setLoading(false);
            }
        };
        
        fetchResults();
    }, [scanId]);
    
    if (loading) return <div>Loading...</div>;
    
    return (
        <div>
            <h2>Scan Results</h2>
            <p>Status: {results.status}</p>
            <p>Findings: {results.findings.length}</p>
            {results.findings.map(finding => (
                <div key={finding.id}>
                    <h3>{finding.title}</h3>
                    <p>Severity: {finding.severity}</p>
                    <p>{finding.description}</p>
                </div>
            ))}
        </div>
    );
};
```

## Monitoring and Logging

### Health Checks

All services provide health check endpoints:
```bash
curl http://localhost:8080/health      # Main API
curl http://localhost:8081/health      # Slither
curl http://localhost:8082/health      # Mythril
curl http://localhost:8083/health      # Manticore
curl http://localhost:8084/health      # MythX
```

### Metrics Endpoint

System metrics are available at:
```bash
curl http://localhost:8080/api/v1/metrics
```

### Log Aggregation

Logs are centralized using the ELK stack (when monitoring profile is enabled):
- Elasticsearch: http://localhost:9200
- Kibana: http://localhost:5601

## Deployment

### Docker Compose

```bash
# Start all services
docker-compose --profile plugins up -d

# Start with monitoring
docker-compose --profile plugins --profile monitoring up -d

# View logs
docker-compose logs -f
```

### Environment Variables

Key environment variables:
- `MYTHX_API_KEY` - MythX API key
- `SCORPIUS_ENV` - Environment (development/production)
- `POSTGRES_PASSWORD` - Database password
- `REDIS_PASSWORD` - Redis password

## Best Practices

1. **Authentication**: Always use authentication tokens in production
2. **Rate Limiting**: Respect rate limits to avoid service degradation
3. **Error Handling**: Implement proper error handling in client applications
4. **Caching**: Cache results when appropriate to reduce API calls
5. **Monitoring**: Monitor API health and performance metrics
6. **Security**: Use HTTPS in production environments

## Support and Resources

- API Documentation: http://localhost:8080/docs
- GitHub Repository: https://github.com/your-org/scorpius
- Issue Tracker: https://github.com/your-org/scorpius/issues
- Community: https://discord.gg/scorpius

For enterprise support and custom integrations, contact: enterprise@scorpius.security

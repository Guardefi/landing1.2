# Scorpius Simulation Service

Enterprise blockchain vulnerability scanner with advanced simulation capabilities.

## Features

- Advanced exploit simulation
- Real-time vulnerability detection
- Comprehensive reporting
- AI-powered analysis
- Sandboxed execution environment

## Setup

1. Install dependencies: `pip install -e .`
2. Start the service: `uvicorn scorpius_scanner.api.server:app --host 0.0.0.0 --port 8006`

## API Endpoints

- `POST /scan/comprehensive` - Start comprehensive scan
- `GET /scan/{scan_id}/status` - Get scan status
- `GET /scan/{scan_id}/results` - Get scan results
- `GET /health` - Health check
- `GET /capabilities` - Get service capabilities

## Docker

```bash
docker build -t scorpius-simulation-service .
docker run -p 8006:8006 scorpius-simulation-service
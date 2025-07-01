# Scorpius Reporting Service

Enterprise-grade signed PDF and SARIF reporting microservice with cryptographic integrity and immutable audit trails.

## Features

- **Signed PDF Reports**: Generate professional PDF reports with cryptographic signatures
- **SARIF Reports**: Static Analysis Results Interchange Format 2.1.0 compliant reports
- **Cryptographic Integrity**: RSA/ECDSA digital signatures with X.509 certificates
- **Immutable Audit Trails**: Amazon QLDB integration for tamper-evident document storage
- **Enterprise Authentication**: API key-based authentication with role-based access control
- **Real-time Monitoring**: Prometheus metrics and health checks
- **Scalable Architecture**: Async FastAPI with background task processing
- **Comprehensive Logging**: Structured audit logs with security event detection

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend/     │───▶│   Reporting     │───▶│   Background    │
│   API Client    │    │   Service       │    │   Processors    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                         │
                              ▼                         ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Signature     │    │   PDF/SARIF     │
                       │   Service       │    │   Generators    │
                       └─────────────────┘    └─────────────────┘
                              │                         │
                              ▼                         ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   QLDB Ledger   │    │   Audit Trail   │
                       │   (Immutable)   │    │   Database      │
                       └─────────────────┘    └─────────────────┘
```

## Quick Start

### Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/scorpius/enterprise-platform.git
cd enterprise-platform/packages/backend/reporting

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Start all services
docker-compose up -d

# Check service health
curl http://localhost:8007/health
```

### Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r config/config/requirements-dev.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Start the service
uvicorn app:app --reload --port 8007
```

## API Documentation

### Authentication

All endpoints require API key authentication via the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8007/v1/reports/pdf
```

### Generate PDF Report

```bash
POST /v1/reports/pdf
Content-Type: application/json
X-API-Key: your-api-key

{
  "title": "Security Analysis Report",
  "data": {
    "executive_summary": {
      "total_issues": 15,
      "critical": 2,
      "high": 5,
      "medium": 6,
      "low": 2
    },
    "findings": [
      {
        "id": "SEC-001",
        "severity": "critical",
        "title": "SQL Injection Vulnerability",
        "description": "Potential SQL injection in user input validation"
      }
    ]
  },
  "template": "security_report",
  "metadata": {
    "client": "Acme Corp",
    "analyst": "Jane Smith"
  }
}
```

### Generate SARIF Report

```bash
POST /v1/reports/sarif
Content-Type: application/json
X-API-Key: your-api-key

{
  "title": "Static Analysis Results",
  "scan_results": [
    {
      "rule_id": "CWE-79",
      "level": "error",
      "message": "Potential XSS vulnerability detected",
      "locations": [
        {
          "file_path": "src/main.js",
          "line": 42,
          "column": 15
        }
      ]
    }
  ],
  "tool_info": {
    "name": "Scorpius Scanner",
    "version": "1.0.0",
    "organization": "Scorpius Security"
  }
}
```

### Check Report Status

```bash
GET /v1/reports/{report_id}/status
X-API-Key: your-api-key
```

### Download Report

```bash
GET /v1/reports/{report_id}/download
X-API-Key: your-api-key
```

### Get Signature Information

```bash
GET /v1/reports/{report_id}/signature
X-API-Key: your-api-key
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | - | Application secret key (required) |
| `DATABASE_URL` | - | PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `AWS_REGION` | `us-east-1` | AWS region for QLDB |
| `QLDB_LEDGER_NAME` | `scorpius-audit` | QLDB ledger name |
| `SIGNATURE_CERT_PATH` | `./certs/signing.crt` | X.509 certificate path |
| `SIGNATURE_KEY_PATH` | `./certs/signing.key` | Private key path |
| `LOG_LEVEL` | `INFO` | Logging level |

### Certificates

Generate self-signed certificates for development:

```bash
# Create certificates directory
mkdir -p certs

# Generate private key
openssl genrsa -out certs/signing.key 2048

# Generate certificate
openssl req -new -x509 -key certs/signing.key -out certs/signing.crt -days 365 \
  -subj "/C=US/ST=CA/L=San Francisco/O=Scorpius/CN=Scorpius Reporting Service"
```

For production, use certificates from a trusted CA.

## Security

### Digital Signatures

Reports are signed using RSA-PSS with SHA-256:

1. **Document Hash**: SHA-256 hash of the document content
2. **Signature Metadata**: Timestamp, signer ID, and additional context
3. **Digital Signature**: RSA-PSS signature of the metadata
4. **Certificate Chain**: X.509 certificate for verification

### Audit Trail

All operations are logged to:

1. **Database**: PostgreSQL with structured audit events
2. **QLDB**: Immutable ledger for document hashes
3. **File System**: Daily audit log files
4. **Redis**: Recent events cache for real-time monitoring

### Access Control

- **API Key Authentication**: Required for all endpoints
- **Role-Based Access**: Admin, user, and reporter roles
- **Rate Limiting**: Configurable request limits
- **IP Allowlisting**: Optional IP-based restrictions

## Monitoring

### Health Checks

```bash
# Service health
curl http://localhost:8007/health

# Prometheus metrics
curl http://localhost:8007/metrics
```

### Metrics

- `reports_generated_total`: Total reports generated
- `signatures_created_total`: Total signatures created
- `audit_entries_total`: Total audit entries
- `service_uptime_seconds`: Service uptime

### Grafana Dashboards

Access Grafana at http://localhost:3000 (admin/admin) for:

- Report generation metrics
- Signature verification rates
- Audit trail visualization
- Service performance metrics

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_pdf_generator.py

# Run integration tests
pytest tests/integration/
```

## Deployment

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scorpius-reporting
spec:
  replicas: 3
  selector:
    matchLabels:
      app: scorpius-reporting
  template:
    metadata:
      labels:
        app: scorpius-reporting
    spec:
      containers:
      - name: reporting
        image: scorpius/reporting:1.0.0
        ports:
        - containerPort: 8007
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: reporting-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: reporting-secrets
              key: secret-key
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
```

### Production Checklist

- [ ] Configure production database
- [ ] Set up QLDB ledger
- [ ] Generate production certificates
- [ ] Configure AWS credentials
- [ ] Set up monitoring and alerting
- [ ] Configure log aggregation
- [ ] Set up backup strategy
- [ ] Review security settings
- [ ] Test disaster recovery

## Troubleshooting

### Common Issues

**Service won't start**
- Check environment variables in `.env`
- Verify database connectivity
- Check certificate paths

**PDF generation fails**
- Install ReportLab dependencies
- Check font permissions
- Verify template paths

**SARIF validation errors**
- Check SARIF schema version
- Validate input data structure
- Review scan results format

**Signature verification fails**
- Verify certificate validity
- Check private key permissions
- Confirm algorithm compatibility

### Debug Mode

Enable debug logging:

```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
uvicorn app:app --reload --log-level debug
```

### Support

For technical support:

- Check the [documentation](docs/)
- Review [troubleshooting guide](docs/troubleshooting.md)
- Open an [issue](https://github.com/scorpius/enterprise-platform/issues)
- Contact support: support@scorpius.io

## License

Enterprise License - See LICENSE file for details.

## Version History

- **1.0.0** - Initial release with PDF and SARIF generation
- **1.1.0** - Added QLDB integration and enhanced security
- **1.2.0** - Performance improvements and monitoring enhancements

---

© 2024 Scorpius Enterprise Platform. All rights reserved.

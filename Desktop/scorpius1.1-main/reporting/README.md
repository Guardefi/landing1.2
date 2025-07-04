# Scorpius Enterprise Reporting System

A production-ready, modular reporting engine for smart contract vulnerability scanners. Generate comprehensive security audit reports in multiple formats (PDF, HTML, JSON, CSV, SARIF) with digital signatures, diffing capabilities, and enterprise-grade features.

## 🚀 Features

### Multi-Format Report Generation
- **PDF Reports**: Professional reports with digital signatures and watermarks
- **HTML Reports**: Interactive web-based reports with charts and visualizations
- **JSON/CSV**: Machine-readable formats for integration and data analysis
- **SARIF v2.1.0**: Industry-standard format for security tools integration
- **Markdown**: Documentation-friendly format

### Enterprise Features
- **Digital Signatures**: PDF signing with X.509 certificates for authenticity
- **Watermarking**: Configurable watermarks for confidential reports
- **Diff Engine**: Compare scan results and highlight changes between runs
- **Audit Bundle**: Complete audit packages with all reports and artifacts
- **Template System**: Customizable Jinja2 templates for branded reports
- **Theme Support**: Multiple built-in themes with custom theme support

### API & Integration
- **FastAPI**: Modern async API with automatic OpenAPI documentation
- **Webhook Notifications**: Real-time notifications for scan completion and critical findings
- **Database Integration**: PostgreSQL with async SQLAlchemy for enterprise scale
- **Caching**: Redis integration for performance optimization
- **Authentication**: JWT-based API authentication

### Visualization & Analytics
- **Interactive Charts**: Chart.js-powered visualizations (severity distribution, trends, etc.)
- **Widget System**: Extensible widget framework for custom visualizations
- **Risk Metrics**: CVSS scoring, risk timelines, and trend analysis
- **Executive Summaries**: High-level overviews for management reporting

## 📦 Installation

### Using pip (Recommended)

```bash
pip install scorpius-reporting
```

### From Source

```bash
git clone https://github.com/scorpius-security/scorpius-reporting.git
cd scorpius-reporting
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/scorpius-security/scorpius-reporting.git
cd scorpius-reporting
pip install -e ".[dev,test]"
```

## 🏃‍♂️ Quick Start

### CLI Usage

Generate a sample report:

```bash
# Generate sample data and create reports
scorpius-report generate-sample --output-dir ./reports

# Generate specific format
scorpius-report generate --scan-id SCAN123 --format pdf --output report.pdf

# Create diff report
scorpius-report diff --scan1 SCAN123 --scan2 SCAN456 --output diff.html

# List available themes
scorpius-report themes list
```

### API Server

Start the reporting server:

```bash
# Using the CLI
scorpius-server

# Or using uvicorn directly
uvicorn reporting.app:app --host 0.0.0.0 --port 8000
```

### Python API

```python
from reporting.generator import ReportGenerator
from reporting.models import ScanResult, VulnerabilityFinding

# Create a scan result
scan_result = ScanResult(
    scan_id="SCAN_123",
    target_info={"address": "0x1234...", "name": "MyContract"},
    findings=[
        VulnerabilityFinding(
            id="VULN_001",
            title="Reentrancy Vulnerability",
            severity="HIGH",
            type="REENTRANCY",
            description="Potential reentrancy attack vector found..."
        )
    ],
    # ... other fields
)

# Generate reports
generator = ReportGenerator()

# Generate PDF report
pdf_path = await generator.generate_pdf_report(
    scan_result=scan_result,
    output_path="audit_report.pdf",
    theme="dark_pro",
    include_signature=True
)

# Generate interactive HTML report
html_path = await generator.generate_html_report(
    scan_result=scan_result,
    output_path="audit_report.html",
    theme="light_corporate"
)

# Generate audit bundle (all formats)
bundle_path = await generator.generate_audit_bundle(
    scan_result=scan_result,
    output_path="audit_bundle.zip"
)
```

## 🔧 Configuration

### Environment Variables

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=scorpius_reporting
DB_USER=reporting_user
DB_PASSWORD=your_password

# Security
SECRET_KEY=your-super-secret-key-here
PDF_SIGNING_ENABLED=true
PDF_CERT_PATH=/path/to/certificate.p12
PDF_CERT_PASSWORD=cert_password

# API
API_HOST=0.0.0.0
API_PORT=8000

# Webhooks
WEBHOOK_ENABLED=true
WEBHOOK_URLS=https://your-webhook-endpoint.com/notify

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Configuration File

Create a `config.yaml` file:

```yaml
database:
  host: localhost
  port: 5432
  database: scorpius_reporting
  username: reporting_user
  password: your_password

security:
  secret_key: your-super-secret-key-here
  pdf_signing_enabled: true
  pdf_cert_path: /path/to/certificate.p12

reporting:
  default_theme: dark_pro
  watermark_enabled: true
  watermark_text: "CONFIDENTIAL"
  supported_formats: ["pdf", "html", "json", "csv", "sarif"]

api:
  host: 0.0.0.0
  port: 8000
  cors_origins: ["*"]

webhook:
  enabled: true
  urls:
    - https://your-webhook-endpoint.com/notify
  timeout: 30
  max_retries: 3
```

## 📊 Report Formats

### PDF Reports
- Professional layout with cover page
- Digital signatures for authenticity
- Watermarks for confidentiality
- Print-optimized styling
- Embedded fonts and assets

### HTML Reports
- Interactive web interface
- Chart.js visualizations
- Responsive design
- Search and filter capabilities
- Print-friendly CSS

### SARIF v2.1.0
- Industry-standard security format
- Compatible with GitHub Security tab
- Integration with security tools
- Machine-readable vulnerability data

### JSON/CSV
- Structured data export
- API integration ready
- Spreadsheet compatible (CSV)
- Custom field selection

## 🎨 Themes and Customization

### Built-in Themes
- **Dark Pro**: Professional dark theme for security reports
- **Light Corporate**: Clean corporate styling
- **Custom Themes**: Create your own with JSON configuration

### Custom Theme Example

```json
{
  "name": "custom_theme",
  "display_name": "Custom Security Theme",
  "colors": {
    "primary": "#1a365d",
    "secondary": "#2d3748",
    "accent": "#3182ce",
    "success": "#38a169",
    "warning": "#d69e2e",
    "danger": "#e53e3e"
  },
  "typography": {
    "font_family": "Inter, sans-serif",
    "base_size": "14px"
  },
  "custom_css": "/* Additional custom styles */"
}
```

## 🔌 API Endpoints

### Core Endpoints

```http
POST /api/v1/scans                    # Submit scan results
GET  /api/v1/scans/{scan_id}          # Get scan details
POST /api/v1/reports/generate         # Generate report
GET  /api/v1/reports/{report_id}      # Get report details
GET  /api/v1/reports/{report_id}/download # Download report file
POST /api/v1/reports/diff             # Generate diff report
GET  /api/v1/themes                   # List available themes
POST /api/v1/audit-bundle             # Generate audit bundle
GET  /api/v1/health                   # Health check
```

### Example API Usage

```bash
# Submit scan results
curl -X POST http://localhost:8000/api/v1/scans \
  -H "Content-Type: application/json" \
  -d @scan_result.json

# Generate PDF report
curl -X POST http://localhost:8000/api/v1/reports/generate \
  -H "Content-Type: application/json" \
  -d '{
    "scan_id": "SCAN_123",
    "format": "pdf",
    "theme": "dark_pro",
    "include_signature": true
  }'

# Download report
curl -X GET http://localhost:8000/api/v1/reports/REPORT_456/download \
  -o audit_report.pdf
```

## 🔒 Security Features

### Digital Signatures
- X.509 certificate-based PDF signing
- Timestamp authority support
- Certificate validation
- Tamper detection

### Authentication
- JWT-based API authentication
- Role-based access control
- API key management
- OAuth2 integration ready

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- File upload restrictions

## 📈 Monitoring and Observability

### Logging
- Structured JSON logging
- Audit trail for all operations
- Performance metrics
- Error tracking

### Health Checks
- Database connectivity
- Service dependencies
- Resource utilization
- API endpoint monitoring

### Metrics
- Report generation times
- API response metrics
- Error rates
- Resource usage

## 🧪 Testing

Run the test suite:

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# All tests with coverage
pytest --cov=reporting --cov-report=html

# Performance tests
pytest tests/performance/ -m slow
```

## 🚀 Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install scorpius-reporting

EXPOSE 8000
CMD ["uvicorn", "reporting.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  reporting:
    image: scorpius-reporting:latest
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=postgres
      - REDIS_HOST=redis
    depends_on:
      - postgres
      - redis
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: scorpius_reporting
      POSTGRES_USER: reporting_user
      POSTGRES_PASSWORD: your_password
  
  redis:
    image: redis:7-alpine
```

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
        image: scorpius-reporting:latest
        ports:
        - containerPort: 8000
        env:
        - name: DB_HOST
          value: "postgres-service"
        - name: REDIS_HOST
          value: "redis-service"
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/scorpius-security/scorpius-reporting.git
cd scorpius-reporting
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev,test]"
pre-commit install
```

### Code Style

We use:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

```bash
# Format code
black .
isort .

# Lint code
flake8 .
mypy .

# Run all checks
pre-commit run --all-files
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [https://docs.scorpius.dev/reporting](https://docs.scorpius.dev/reporting)
- **Issues**: [GitHub Issues](https://github.com/scorpius-security/scorpius-reporting/issues)
- **Discussions**: [GitHub Discussions](https://github.com/scorpius-security/scorpius-reporting/discussions)
- **Email**: support@scorpius.dev

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   Report         │    │   Output        │
│   Web Server    │───▶│   Generator      │───▶│   Writers       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Database      │    │   Template       │    │   File System   │
│   (PostgreSQL)  │    │   Engine         │    │   Storage       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       
         ▼                       ▼                       
┌─────────────────┐    ┌──────────────────┐              
│   Cache         │    │   Theme          │              
│   (Redis)       │    │   Manager        │              
└─────────────────┘    └──────────────────┘              
```

## 🔮 Roadmap

- [ ] **v1.1**: Enhanced visualization widgets
- [ ] **v1.2**: Machine learning-based risk scoring
- [ ] **v1.3**: Multi-language report support
- [ ] **v1.4**: Real-time collaborative reporting
- [ ] **v2.0**: Microservices architecture

---

**Built with ❤️ by the Scorpius Security Team**

# Scorpius Enterprise Platform - API Documentation

## 🚀 API Overview

The Scorpius Enterprise Platform provides comprehensive RESTful APIs for blockchain security, wallet protection, compliance reporting, and enterprise management. All APIs use industry-standard authentication, provide detailed error handling, and include comprehensive audit trails.

---

## 🔐 Authentication

### **API Key Authentication**

All API requests require authentication using API keys in the `X-API-Key` header:

```bash
curl -X GET https://api.scorpius.com/v1/wallets \\
  -H "X-API-Key: sk_live_1234567890abcdef..." \\
  -H "Content-Type: application/json"
```

### **API Key Types**

| Type | Prefix | Use Case | Rate Limits |
|------|--------|----------|-------------|
| **Live** | `sk_live_` | Production environments | 10,000 req/hour |
| **Test** | `sk_test_` | Development and testing | 1,000 req/hour |
| **Restricted** | `sk_rest_` | Limited scope access | 100 req/hour |

### **Generating API Keys**

```bash
# Create API Key
POST /v1/auth/api-keys
{
  "name": "Production Integration",
  "permissions": [
    "wallets:read",
    "wallets:write", 
    "reports:generate",
    "audit:read"
  ],
  "rate_limit": 5000,
  "expires_at": "2026-06-27T00:00:00Z"
}

# Response
{
  "api_key": "sk_live_1234567890abcdef...",
  "key_id": "key_abc123",
  "name": "Production Integration",
  "permissions": ["wallets:read", "wallets:write", "reports:generate", "audit:read"],
  "rate_limit": 5000,
  "created_at": "2025-06-27T10:30:00Z",
  "expires_at": "2026-06-27T00:00:00Z"
}
```

---

## 🛡️ Wallet Guard API

### **Protect Wallet**

Add a wallet to real-time protection monitoring.

```bash
POST /v1/wallets/protect
```

**Request Body:**
```json
{
  "address": "0x742d35Cc6635C0532925a3b8D40Ec8C5e2fD",
  "chain": "ethereum",
  "name": "Corporate Treasury Wallet",
  "risk_threshold": 75,
  "alert_webhook": "https://company.com/webhooks/wallet-alerts",
  "monitoring_level": "high"
}
```

**Response:**
```json
{
  "wallet_id": "wlt_abc123",
  "address": "0x742d35Cc6635C0532925a3b8D40Ec8C5e2fD",
  "chain": "ethereum",
  "status": "protected",
  "risk_score": 12,
  "created_at": "2025-06-27T10:30:00Z",
  "last_transaction": "2025-06-27T09:45:00Z"
}
```

### **Get Wallet Status**

Retrieve current wallet protection status and risk assessment.

```bash
GET /v1/wallets/{wallet_id}
```

**Response:**
```json
{
  "wallet_id": "wlt_abc123",
  "address": "0x742d35Cc6635C0532925a3b8D40Ec8C5e2fD",
  "chain": "ethereum",
  "name": "Corporate Treasury Wallet",
  "status": "protected",
  "risk_score": 12,
  "risk_factors": [
    {
      "type": "unusual_volume",
      "severity": "low",
      "description": "Transaction volume 15% above normal"
    }
  ],
  "transaction_count_24h": 45,
  "balance": {
    "eth": "150.75",
    "usd_value": "245,820.50"
  },
  "last_updated": "2025-06-27T10:30:00Z"
}
```

### **List Protected Wallets**

Get all wallets under protection.

```bash
GET /v1/wallets?limit=50&offset=0&chain=ethereum
```

**Response:**
```json
{
  "wallets": [
    {
      "wallet_id": "wlt_abc123",
      "address": "0x742d35Cc6635C0532925a3b8D40Ec8C5e2fD",
      "chain": "ethereum",
      "name": "Corporate Treasury Wallet",
      "status": "protected",
      "risk_score": 12
    }
  ],
  "pagination": {
    "limit": 50,
    "offset": 0,
    "total": 127,
    "has_more": true
  }
}
```

### **Transaction Analysis**

Analyze specific transactions for risk factors.

```bash
POST /v1/wallets/{wallet_id}/analyze-transaction
```

**Request Body:**
```json
{
  "transaction_hash": "0x1234567890abcdef...",
  "include_predictions": true,
  "detail_level": "comprehensive"
}
```

**Response:**
```json
{
  "transaction_hash": "0x1234567890abcdef...",
  "risk_score": 85,
  "risk_level": "high",
  "risk_factors": [
    {
      "type": "suspicious_recipient",
      "severity": "high",
      "confidence": 0.92,
      "description": "Recipient address associated with known scam operations"
    },
    {
      "type": "unusual_gas_price",
      "severity": "medium", 
      "confidence": 0.78,
      "description": "Gas price 300% above network average"
    }
  ],
  "recommendations": [
    "Block this transaction immediately",
    "Review recipient address against threat intelligence",
    "Implement additional approval workflow for similar transactions"
  ],
  "analyzed_at": "2025-06-27T10:30:00Z"
}
```

---

## 📊 Usage Metering API

### **Get Usage Metrics**

Retrieve comprehensive usage statistics for billing and monitoring.

```bash
GET /v1/usage/metrics?period=current_month&granularity=daily
```

**Response:**
```json
{
  "period": {
    "start": "2025-06-01T00:00:00Z",
    "end": "2025-06-27T23:59:59Z"
  },
  "metrics": {
    "api_requests": {
      "total": 125430,
      "by_endpoint": {
        "/v1/wallets": 45230,
        "/v1/reports": 12450,
        "/v1/audit": 8930
      }
    },
    "wallets_protected": 245,
    "transactions_analyzed": 89760,
    "reports_generated": 156,
    "data_storage_gb": 12.5
  },
  "daily_breakdown": [
    {
      "date": "2025-06-27",
      "api_requests": 4567,
      "transactions_analyzed": 3201,
      "reports_generated": 8
    }
  ],
  "projected_monthly": {
    "api_requests": 145000,
    "estimated_cost": "$1,250.00"
  }
}
```

### **Set Usage Alerts**

Configure alerts for usage thresholds.

```bash
POST /v1/usage/alerts
```

**Request Body:**
```json
{
  "name": "Monthly API Limit Alert",
  "metric": "api_requests",
  "threshold": 100000,
  "period": "monthly",
  "notification_channels": [
    {
      "type": "email",
      "target": "admin@company.com"
    },
    {
      "type": "slack",
      "target": "https://hooks.slack.com/services/..."
    }
  ]
}
```

---

## 📋 Audit Trail API

### **Query Audit Events**

Search and retrieve audit trail events with advanced filtering.

```bash
GET /v1/audit/events?start_time=2025-06-01T00:00:00Z&end_time=2025-06-27T23:59:59Z&event_type=wallet_protection&limit=100
```

**Response:**
```json
{
  "events": [
    {
      "event_id": "evt_abc123",
      "timestamp": "2025-06-27T10:30:00Z",
      "event_type": "wallet_protection_enabled",
      "user_id": "usr_xyz789",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "details": {
        "wallet_address": "0x742d35Cc6635C0532925a3b8D40Ec8C5e2fD",
        "chain": "ethereum",
        "risk_threshold": 75
      },
      "hash": "sha256:abcdef1234567890...",
      "signature": "ecdsa:signature_here...",
      "previous_hash": "sha256:previous_event_hash..."
    }
  ],
  "pagination": {
    "limit": 100,
    "offset": 0,
    "total": 15672,
    "has_more": true
  },
  "integrity": {
    "chain_valid": true,
    "last_verified": "2025-06-27T10:25:00Z"
  }
}
```

### **Verify Audit Chain**

Verify the integrity of the audit trail chain.

```bash
POST /v1/audit/verify
```

**Request Body:**
```json
{
  "start_event_id": "evt_abc123",
  "end_event_id": "evt_xyz789",
  "include_details": true
}
```

**Response:**
```json
{
  "verification_id": "ver_def456",
  "chain_valid": true,
  "events_verified": 1543,
  "verification_details": {
    "hash_verification": "passed",
    "signature_verification": "passed", 
    "sequence_verification": "passed",
    "timestamp_verification": "passed"
  },
  "verified_at": "2025-06-27T10:30:00Z",
  "verification_signature": "ecdsa:verification_signature..."
}
```

---

## 📑 Reporting API

### **Generate PDF Report**

Create cryptographically signed PDF reports.

```bash
POST /v1/reports/pdf
```

**Request Body:**
```json
{
  "title": "Monthly Security Audit Report",
  "template": "security_audit",
  "data": {
    "period": {
      "start": "2025-06-01",
      "end": "2025-06-30"
    },
    "wallets_monitored": 245,
    "threats_detected": 12,
    "false_positives": 3,
    "response_time_avg": "00:02:45"
  },
  "metadata": {
    "author": "Security Team",
    "department": "Information Security",
    "classification": "Internal Use",
    "watermark": "CONFIDENTIAL"
  },
  "signature_required": true,
  "delivery": {
    "webhook": "https://company.com/webhooks/reports",
    "email": ["ciso@company.com", "security-team@company.com"]
  }
}
```

**Response:**
```json
{
  "report_id": "rpt_abc123",
  "status": "generating",
  "estimated_completion": "2025-06-27T10:35:00Z",
  "download_url": null,
  "created_at": "2025-06-27T10:30:00Z"
}
```

### **Generate SARIF Report**

Create SARIF 2.1.0 compliant security reports.

```bash
POST /v1/reports/sarif
```

**Request Body:**
```json
{
  "tool_info": {
    "name": "Scorpius Wallet Guard",
    "version": "1.0.0",
    "uri": "https://scorpius.com"
  },
  "scan_results": [
    {
      "rule_id": "suspicious_transaction",
      "message": "High-risk transaction detected",
      "level": "error",
      "locations": [
        {
          "wallet_address": "0x742d35Cc6635C0532925a3b8D40Ec8C5e2fD",
          "transaction_hash": "0x1234567890abcdef..."
        }
      ],
      "properties": {
        "risk_score": 85,
        "confidence": 0.92
      }
    }
  ],
  "metadata": {
    "scan_date": "2025-06-27T10:30:00Z",
    "organization": "Company Inc",
    "analyst": "Security Team"
  },
  "signature_required": true
}
```

### **Get Report Status**

Check the status of report generation.

```bash
GET /v1/reports/{report_id}
```

**Response:**
```json
{
  "report_id": "rpt_abc123",
  "status": "completed",
  "type": "pdf",
  "title": "Monthly Security Audit Report",
  "file_size": 2458643,
  "download_url": "https://api.scorpius.com/v1/reports/rpt_abc123/download",
  "signature_info": {
    "algorithm": "RSA-2048",
    "certificate_fingerprint": "SHA256:abcdef1234567890...",
    "signed_at": "2025-06-27T10:33:22Z"
  },
  "created_at": "2025-06-27T10:30:00Z",
  "completed_at": "2025-06-27T10:33:22Z",
  "expires_at": "2025-07-27T10:33:22Z"
}
```

### **Download Report**

Download completed reports.

```bash
GET /v1/reports/{report_id}/download
```

**Response:**
Binary file download with appropriate content headers:
- `Content-Type: application/pdf` or `application/json`
- `Content-Disposition: attachment; filename="report.pdf"`
- `X-Signature-Algorithm: RSA-2048`
- `X-Signature-Certificate: SHA256:abcdef...`

---

## 🔍 Search & Analytics API

### **Advanced Threat Search**

Search for threats and security events across all monitored assets.

```bash
POST /v1/search/threats
```

**Request Body:**
```json
{
  "query": {
    "time_range": {
      "start": "2025-06-20T00:00:00Z",
      "end": "2025-06-27T23:59:59Z"
    },
    "filters": {
      "risk_score": {"gte": 70},
      "chains": ["ethereum", "bitcoin"],
      "threat_types": ["suspicious_transaction", "unusual_volume"]
    },
    "aggregations": {
      "by_chain": true,
      "by_threat_type": true,
      "by_day": true
    }
  },
  "limit": 100,
  "include_details": true
}
```

**Response:**
```json
{
  "results": [
    {
      "threat_id": "thr_abc123",
      "timestamp": "2025-06-27T09:15:00Z",
      "threat_type": "suspicious_transaction",
      "risk_score": 85,
      "wallet_address": "0x742d35Cc6635C0532925a3b8D40Ec8C5e2fD",
      "chain": "ethereum",
      "details": {
        "transaction_hash": "0x1234567890abcdef...",
        "amount": "50.0 ETH",
        "recipient": "0x987654321fedcba..."
      }
    }
  ],
  "aggregations": {
    "by_chain": {
      "ethereum": 45,
      "bitcoin": 12
    },
    "by_threat_type": {
      "suspicious_transaction": 32,
      "unusual_volume": 25
    },
    "total_threats": 57
  },
  "query_time_ms": 245
}
```

---

## 🔧 Configuration API

### **Update Security Policies**

Configure security policies and thresholds.

```bash
PUT /v1/config/security-policies
```

**Request Body:**
```json
{
  "global_risk_threshold": 75,
  "auto_block_threshold": 90,
  "notification_settings": {
    "email_alerts": true,
    "webhook_alerts": true,
    "sms_alerts": false
  },
  "transaction_limits": {
    "daily_volume_threshold": "1000000.00",
    "transaction_count_threshold": 100,
    "suspicious_recipient_action": "alert"
  },
  "retention_policies": {
    "audit_logs": "7 years",
    "transaction_data": "5 years",
    "reports": "3 years"
  }
}
```

### **Manage Webhooks**

Configure webhook endpoints for real-time notifications.

```bash
POST /v1/config/webhooks
```

**Request Body:**
```json
{
  "url": "https://company.com/webhooks/scorpius",
  "events": [
    "wallet.threat_detected",
    "report.completed",
    "usage.threshold_exceeded"
  ],
  "secret": "whsec_1234567890abcdef...",
  "active": true,
  "retry_config": {
    "max_retries": 3,
    "retry_delay": 5000,
    "exponential_backoff": true
  }
}
```

---

## 📊 Error Handling

### **Standard Error Response**

All APIs return consistent error responses:

```json
{
  "error": {
    "code": "WALLET_NOT_FOUND",
    "message": "The specified wallet could not be found",
    "details": {
      "wallet_id": "wlt_invalid123",
      "suggestion": "Verify the wallet_id and ensure the wallet is registered"
    },
    "request_id": "req_abc123",
    "timestamp": "2025-06-27T10:30:00Z"
  }
}
```

### **Error Codes**

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_API_KEY` | 401 | API key is missing or invalid |
| `INSUFFICIENT_PERMISSIONS` | 403 | API key lacks required permissions |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests in time window |
| `WALLET_NOT_FOUND` | 404 | Specified wallet doesn't exist |
| `INVALID_ADDRESS` | 400 | Blockchain address format is invalid |
| `UNSUPPORTED_CHAIN` | 400 | Blockchain network not supported |
| `REPORT_GENERATION_FAILED` | 500 | Internal error during report creation |
| `AUDIT_INTEGRITY_VIOLATION` | 500 | Audit trail integrity check failed |

---

## 🔗 SDKs & Integration

### **Python SDK**

```bash
pip install scorpius-enterprise
```

```python
import scorpius

# Initialize client
client = scorpius.Client(api_key="sk_live_...")

# Protect a wallet
wallet = client.wallets.protect(
    address="0x742d35Cc6635C0532925a3b8D40Ec8C5e2fD",
    chain="ethereum",
    name="Corporate Treasury"
)

# Generate a report
report = client.reports.create_pdf(
    title="Security Audit",
    template="security_audit",
    data={"period": "monthly"},
    signature_required=True
)

# Wait for completion and download
report.wait_for_completion()
with open("security_audit.pdf", "wb") as f:
    f.write(report.download())
```

### **Node.js SDK**

```bash
npm install @scorpius/enterprise
```

```javascript
const Scorpius = require('@scorpius/enterprise');

const client = new Scorpius({
  apiKey: 'sk_live_...'
});

// Protect wallet
const wallet = await client.wallets.protect({
  address: '0x742d35Cc6635C0532925a3b8D40Ec8C5e2fD',
  chain: 'ethereum',
  name: 'Corporate Treasury'
});

// Generate SARIF report
const report = await client.reports.createSarif({
  toolInfo: {
    name: 'Security Scanner',
    version: '1.0.0'
  },
  scanResults: results,
  signatureRequired: true
});
```

---

## 📋 Rate Limits

### **Default Limits**

| Tier | Requests/Hour | Burst Limit | Description |
|------|---------------|-------------|-------------|
| **Free** | 1,000 | 100/min | Development and testing |
| **Professional** | 10,000 | 500/min | Production use |
| **Enterprise** | 100,000 | 2000/min | High-volume enterprise |
| **Custom** | Negotiated | Custom | Large-scale deployments |

### **Rate Limit Headers**

All responses include rate limit information:

```
X-RateLimit-Limit: 10000
X-RateLimit-Remaining: 9545
X-RateLimit-Reset: 1640995200
X-RateLimit-Burst: 500
X-RateLimit-Burst-Remaining: 245
```

---

## 🔍 Testing & Development

### **Sandbox Environment**

Use the sandbox environment for testing:

- **Base URL**: `https://sandbox-api.scorpius.com`
- **API Keys**: Use `sk_test_` prefixed keys
- **Rate Limits**: Reduced limits for testing
- **Data**: Non-production test data only

### **Postman Collection**

Download our comprehensive Postman collection:

```bash
curl -O https://api.scorpius.com/postman/scorpius-enterprise.json
```

### **OpenAPI Specification**

Access the complete OpenAPI 3.0 specification:

```bash
curl https://api.scorpius.com/openapi.json
```

---

## 📞 API Support

### **Developer Resources**

- **Documentation**: [https://docs.scorpius.com](https://docs.scorpius.com)
- **API Status**: [https://status.scorpius.com](https://status.scorpius.com)
- **Developer Forum**: [https://community.scorpius.com](https://community.scorpius.com)
- **GitHub**: [https://github.com/scorpius-enterprise](https://github.com/scorpius-enterprise)

### **Support Channels**

- **Developer Support**: [dev-support@scorpius.com](mailto:dev-support@scorpius.com)
- **API Issues**: [api-support@scorpius.com](mailto:api-support@scorpius.com)
- **Enterprise Support**: [enterprise@scorpius.com](mailto:enterprise@scorpius.com)
- **24/7 Support**: Available for Enterprise customers

---

*This API documentation is version-controlled and updated with each release. For the latest information, always refer to the online documentation at docs.scorpius.com.*

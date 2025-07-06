# Usage Metering & Billing Service

## Overview

The Usage Metering & Billing Service is a critical component of the Scorpius Enterprise Platform that tracks feature usage by organization, enforces limits, and integrates with Stripe for billing. It provides real-time usage tracking, overage handling, and comprehensive metrics for business intelligence.

## Features

- **Real-time Usage Tracking**: Track usage events with sub-second latency using Redis
- **Multi-tenant Support**: Isolated usage tracking per organization
- **Flexible Billing Plans**: Free, Professional, and Enterprise tiers with customizable limits
- **Stripe Integration**: Automated billing, webhooks, and subscription management
- **Usage Limits & Overages**: Enforce limits with overage detection and billing
- **Prometheus Metrics**: Comprehensive metrics for monitoring and alerting
- **Monthly Reset Cycles**: Automatic usage reset based on billing cycles
- **Audit Trail**: Complete billing event history for compliance

## API Endpoints

### Usage Tracking

#### POST `/usage/track`
Track a usage event for an organization.

**Request Body:**
```json
{
  "org_id": "org-123",
  "feature": "scans",
  "quantity": 5,
  "metadata": {
    "contract": "0x123",
    "chain": "ethereum"
  }
}
```

**Response:**
```json
{
  "org_id": "org-123",
  "feature": "scans",
  "current_usage": 15,
  "limit": 1000,
  "remaining": 985,
  "reset_date": "2024-02-01T00:00:00Z"
}
```

#### GET `/usage/{org_id}`
Get current usage for an organization.

**Response:**
```json
{
  "org_id": "org-123",
  "plan": "professional",
  "features": {
    "scans": {
      "current": 15,
      "limit": 1000,
      "reset_date": "2024-02-01T00:00:00Z",
      "last_updated": "2024-01-15T10:30:00Z"
    }
  },
  "stripe_customer_id": "cus_123",
  "payment_overdue": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Billing Management

#### POST `/billing/update`
Update organization billing plan and limits.

**Request Body:**
```json
{
  "org_id": "org-123",
  "plan": "professional",
  "limits": {
    "scans": 1000,
    "wallet_checks": 10000,
    "api_requests": 50000
  },
  "stripe_customer_id": "cus_123"
}
```

#### POST `/webhooks/stripe`
Handle Stripe webhook events for subscription changes.

### Monitoring

#### GET `/metrics/usage`
Prometheus metrics endpoint for usage data.

#### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "redis": "healthy",
    "stripe": "healthy"
  }
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379` |
| `REDIS_DB` | Redis database number | `2` |
| `STRIPE_SECRET_KEY` | Stripe API secret key | Required |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret | Required |
| `JWT_SECRET` | JWT signing secret | `changeme-in-production` |
| `DEBUG` | Enable debug mode | `false` |

### Plan Configuration

The service supports three built-in plans:

#### Free Plan
- Scans: 10/month
- Wallet Checks: 100/month
- API Requests: 1,000/month

#### Professional Plan
- Scans: 1,000/month
- Wallet Checks: 10,000/month
- API Requests: 50,000/month

#### Enterprise Plan
- Unlimited usage across all features

## Usage Patterns

### Basic Usage Tracking

```python
import httpx

# Track a scan usage event
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://usage-metering:8005/usage/track",
        json={
            "org_id": "my-org",
            "feature": "scans",
            "quantity": 1,
            "metadata": {"contract": "0x123"}
        },
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    usage = response.json()
    print(f"Remaining: {usage['remaining']}")
```

### Check Current Usage

```python
# Get current usage for organization
response = await client.get(
    f"http://usage-metering:8005/usage/{org_id}",
    headers={"Authorization": f"Bearer {jwt_token}"}
)
usage = response.json()
```

### Upgrade Organization Plan

```python
# Upgrade to professional plan
response = await client.post(
    "http://usage-metering:8005/billing/update",
    json={
        "org_id": "my-org",
        "plan": "professional",
        "limits": {
            "scans": 1000,
            "wallet_checks": 10000
        },
        "stripe_customer_id": "cus_123"
    },
    headers={"Authorization": f"Bearer {jwt_token}"}
)
```

## Monitoring & Metrics

### Prometheus Metrics

The service exposes the following metrics:

- `scorpius_usage_total`: Total usage events by org, feature, and plan
- `scorpius_billing_events_total`: Total billing events by type
- `scorpius_usage_api_duration_seconds`: API request duration histogram
- `scorpius_total_organizations`: Current number of organizations
- `scorpius_feature_usage_total`: Usage by feature and plan
- `scorpius_plan_distribution`: Organization distribution by plan
- `scorpius_org_usage_total`: Top organizations by usage

### Grafana Dashboard

A pre-configured Grafana dashboard is available at `grafana/usage-dashboard.json` with:

- Organization count and growth
- Usage patterns by feature and plan
- Billing event tracking
- API performance metrics
- Top organizations by usage

### Alerting

Set up alerts for:

- High API error rates
- Usage overage events
- Payment failures
- Service health issues

## Billing Integration

### Stripe Setup

1. Create Stripe products and prices for each plan
2. Configure webhook endpoints for subscription events
3. Set up usage-based billing for overage charges

### Supported Events

- `customer.subscription.updated`: Plan changes
- `customer.subscription.deleted`: Cancellations
- `invoice.payment_failed`: Payment failures

### Overage Handling

When usage exceeds limits:

1. Usage is still tracked and allowed
2. Overage billing event is created
3. Stripe usage record is generated for metered billing
4. Organization is flagged for overage charges

## Development

### Running Locally

```bash
# Install dependencies
pip install -r config/config/requirements-dev.txt
pip install -r test-config/config/requirements-dev.txt

# Start Redis
docker run -d -p 6379:6379 redis:7-alpine

# Set environment variables
export REDIS_URL=redis://localhost:6379/2
export STRIPE_SECRET_KEY=sk_test_...
export JWT_SECRET=your-secret-key

# Run the service
uvicorn app:app --host 0.0.0.0 --port 8005 --reload
```

### Testing

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests (requires Redis)
make test-integration

# Run with coverage
make test-cov
```

### Docker

```bash
# Build image
make docker-build

# Run container
make docker-run
```

## Security Considerations

- All API endpoints require JWT authentication
- Organization isolation enforced at the Redis key level
- Stripe webhook signatures are verified
- Rate limiting can be configured per organization
- Sensitive data (customer IDs, payment info) encrypted at rest

## Performance

- **Latency**: p95 < 100ms for usage tracking
- **Throughput**: 1000+ requests/second per instance
- **Scalability**: Horizontally scalable (stateless design)
- **Storage**: Redis for hot data, with configurable retention

## Troubleshooting

### Common Issues

1. **High Memory Usage**: Adjust Redis memory limits and retention
2. **Slow Responses**: Check Redis connection and network latency
3. **Missing Usage Data**: Verify JWT tokens and organization IDs
4. **Stripe Errors**: Check API keys and webhook configuration

### Debug Mode

Enable debug logging:
```bash
export DEBUG=true
export LOG_LEVEL=debug
```

### Health Checks

- Service: `GET /health`
- Redis: Check connection and response time
- Stripe: Verify API connectivity

## Compliance

- **SOC 2**: Audit trails for all billing events
- **PCI DSS**: No credit card data stored (handled by Stripe)
- **GDPR**: Organization data can be deleted on request
- **Data Retention**: Configurable retention periods for usage data

# Security Best Practices

## 1. Authentication & Authorization

### 1.1 JWT Authentication

```python
from fastapi import Depends
from app.auth import get_current_user

@app.post("/secure-endpoint")
async def secure_endpoint(
    user: User = Depends(get_current_user)
):
    # Implementation
    pass
```

### 1.2 Multi-Factor Authentication

```python
from app.auth import require_mfa

@app.post("/admin-action")
async def admin_action(
    user: User = Depends(require_mfa)
):
    # Implementation
    pass
```

### 1.3 Role-Based Access Control

```python
from app.auth import require_role

@app.post("/admin/endpoint")
async def admin_endpoint(
    user: User = Depends(require_role("admin"))
):
    # Implementation
    pass
```

## 2. Data Protection

### 2.1 Encryption

```python
from app.crypto import encrypt_data, decrypt_data

async def save_sensitive_data(data: dict):
    encrypted = encrypt_data(data)
    return await db.save(encrypted)

async def get_sensitive_data(id: str):
    encrypted = await db.get(id)
    return decrypt_data(encrypted)
```

### 2.2 Data Masking

```python
from app.security import mask_pii

async def handle_user_data(user_data: dict):
    masked_data = mask_pii(user_data)
    return masked_data
```

## 3. Input Validation

### 3.1 Pydantic Models

```python
from pydantic import BaseModel, validator

class ScanRequest(BaseModel):
    contract_address: str
    scan_type: str = "quick"
    
    @validator('contract_address')
    def validate_address(cls, v):
        if not re.match(r'^0x[a-fA-F0-9]{40}$', v):
            raise ValueError('Invalid Ethereum address')
        return v.lower()
```

### 3.2 Rate Limiting

```python
from app.limiter import rate_limit

@app.post("/api/endpoint")
@rate_limit(limit=100, window=60)
async def rate_limited_endpoint():
    # Implementation
    pass
```

## 4. API Security

### 4.1 Circuit Breaker

```python
from backend.decorators.rpc import resilient_rpc

@resilient_rpc(
    max_attempts=3,
    initial_wait=1.0,
    max_wait=30.0,
    failure_threshold=3,
    reset_timeout=60
)
async def external_call():
    # Implementation
    pass
```

### 4.2 API Key Validation

```python
from app.auth import validate_api_key

@app.post("/api/endpoint")
async def api_endpoint(api_key: str = Header(...)):
    validate_api_key(api_key)
    # Implementation
    pass
```

## 5. Database Security

### 5.1 Query Validation

```python
from app.db import validate_query

async def execute_query(query: str):
    if not validate_query(query):
        raise ValueError("Invalid query")
    return await db.execute(query)
```

### 5.2 Connection Pooling

```python
from app.db import get_pool

async def handle_db_operation():
    async with get_pool() as conn:
        result = await conn.execute("SELECT * FROM table")
        return result
```

## 6. File Security

### 6.1 File Validation

```python
from app.file import validate_file

async def handle_file_upload(file: UploadFile):
    if not validate_file(file):
        raise ValueError("Invalid file")
    return await save_file(file)
```

### 6.2 Size Limits

```python
from app.file import MAX_FILE_SIZE

async def validate_size(file: UploadFile):
    if file.size > MAX_FILE_SIZE:
        raise ValueError(f"File too large, max size: {MAX_FILE_SIZE}")
```

## 7. Network Security

### 7.1 IP Whitelisting

```python
from app.network import validate_ip

@app.post("/api/endpoint")
async def ip_restricted_endpoint(
    request: Request,
    client_ip: str = Header(...)
):
    validate_ip(client_ip)
    # Implementation
    pass
```

### 7.2 TLS Enforcement

```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()
app.add_middleware(HTTPSRedirectMiddleware)
```

## 8. Security Headers

```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["your-domain.com"],
)
```

## 9. Security Testing

### 9.1 Unit Tests

```python
import pytest
from fastapi.testclient import TestClient

client = TestClient(app)

@pytest.mark.asyncio
async def test_security_validation():
    response = await client.post("/secure-endpoint", headers={"Authorization": "Bearer token"})
    assert response.status_code == 200
```

### 9.2 Integration Tests

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_full_security_workflow():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test authentication
        login_response = await client.post("/auth/login", json={...})
        token = login_response.json()["access_token"]
        
        # Test authorization
        auth_response = await client.get("/secure-endpoint", headers={"Authorization": f"Bearer {token}"})
        assert auth_response.status_code == 200
```

## 10. Security Monitoring

### 10.1 Security Metrics

```python
from opentelemetry import metrics

meter = metrics.get_meter(__name__)
security_events = meter.create_counter(
    "security_events",
    description="Number of security events"
)
```

### 10.2 Audit Logging

```python
from app.logging import audit_log

async def handle_sensitive_operation():
    audit_log(
        user_id=current_user.id,
        action="sensitive_operation",
        details={"resource": "important_data"}
    )
    # Implementation
    pass
```

## 11. Security Commands

```bash
# Security scan
make security-scan

# Security validation
make security-validate

# Security audit
make security-audit

# Security test
make security-test

# Security monitor
make security-monitor

# Security compliance
make security-compliance

# Security incident response
make security-response
```

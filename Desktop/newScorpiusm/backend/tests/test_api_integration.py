"""
FastAPI integration tests using httpx.AsyncClient and in-memory SQLite.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi import FastAPI, HTTPException, Depends
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from datetime import datetime
import tempfile
import os

# Mock FastAPI app and models for testing
# In real implementation, these would be imported from your actual modules

Base = declarative_base()


class ScanResult(Base):
    """Mock scan result model."""
    __tablename__ = "scan_results"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_address = Column(String, index=True)
    risk_score = Column(Float)
    vulnerability_count = Column(Integer)
    scan_timestamp = Column(DateTime, default=datetime.utcnow)


class User(Base):
    """Mock user model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    api_key = Column(String, unique=True, index=True)


# Mock database dependency
def get_test_db():
    """Get test database session."""
    return test_db_session


# Mock FastAPI app
def create_test_app() -> FastAPI:
    """Create a test FastAPI application."""
    app = FastAPI(title="Scorpius Test API", version="1.0.0")
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    
    @app.post("/api/v1/scan")
    async def scan_contract(
        contract_data: dict,
        db: Session = Depends(get_test_db)
    ):
        """Mock contract scanning endpoint."""
        contract_address = contract_data.get("address")
        
        if not contract_address:
            raise HTTPException(status_code=400, detail="Contract address required")
        
        if not contract_address.startswith("0x") or len(contract_address) != 42:
            raise HTTPException(status_code=400, detail="Invalid Ethereum address")
        
        # Mock vulnerability analysis
        mock_vulnerabilities = [
            {"type": "reentrancy", "severity": "HIGH"},
            {"type": "integer_overflow", "severity": "MEDIUM"},
        ]
        
        risk_score = 7.5
        
        # Save to database
        scan_result = ScanResult(
            contract_address=contract_address,
            risk_score=risk_score,
            vulnerability_count=len(mock_vulnerabilities)
        )
        db.add(scan_result)
        db.commit()
        db.refresh(scan_result)
        
        return {
            "scan_id": scan_result.id,
            "contract_address": contract_address,
            "risk_score": risk_score,
            "vulnerabilities": mock_vulnerabilities,
            "status": "completed"
        }
    
    @app.get("/api/v1/scan/{scan_id}")
    async def get_scan_result(scan_id: int, db: Session = Depends(get_test_db)):
        """Get scan result by ID."""
        scan_result = db.query(ScanResult).filter(ScanResult.id == scan_id).first()
        
        if not scan_result:
            raise HTTPException(status_code=404, detail="Scan result not found")
        
        return {
            "scan_id": scan_result.id,
            "contract_address": scan_result.contract_address,
            "risk_score": scan_result.risk_score,
            "vulnerability_count": scan_result.vulnerability_count,
            "scan_timestamp": scan_result.scan_timestamp.isoformat()
        }
    
    @app.get("/api/v1/mev/detect")
    async def detect_mev(transaction_hash: str):
        """Mock MEV detection endpoint."""
        if not transaction_hash.startswith("0x") or len(transaction_hash) != 66:
            raise HTTPException(status_code=400, detail="Invalid transaction hash")
        
        # Mock MEV analysis
        return {
            "transaction_hash": transaction_hash,
            "mev_detected": True,
            "mev_type": "sandwich_attack",
            "estimated_profit": "0.5",
            "confidence": 0.85
        }
    
    @app.post("/api/v1/auth/api-key")
    async def create_api_key(user_data: dict, db: Session = Depends(get_test_db)):
        """Create API key for user."""
        email = user_data.get("email")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email required")
        
        # Check if user exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(status_code=409, detail="User already exists")
        
        # Generate mock API key
        import secrets
        api_key = f"sk-scorpius-{secrets.token_urlsafe(32)}"
        
        # Create user
        user = User(email=email, api_key=api_key)
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return {
            "user_id": user.id,
            "email": email,
            "api_key": api_key
        }
    
    return app


# Global test variables
test_db_session = None
test_app = None


@pytest.fixture(scope="function")
def test_db():
    """Create test database for each test."""
    global test_db_session
    
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    
    # Create engine and session
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    test_db_session = TestingSessionLocal()
    
    yield test_db_session
    
    # Cleanup
    test_db_session.close()
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def test_client(test_db):
    """Create test client with database dependency override."""
    global test_app
    test_app = create_test_app()
    
    # Override database dependency
    test_app.dependency_overrides[get_test_db] = lambda: test_db
    
    with TestClient(test_app) as client:
        yield client


@pytest_asyncio.fixture
async def async_client(test_db):
    """Create async test client."""
    global test_app
    test_app = create_test_app()
    
    # Override database dependency
    test_app.dependency_overrides[get_test_db] = lambda: test_db
    
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_check_sync(self, test_client):
        """Test health check with sync client."""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    @pytest.mark.asyncio
    async def test_health_check_async(self, async_client):
        """Test health check with async client."""
        response = await async_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestContractScanningAPI:
    """Test contract scanning API endpoints."""
    
    def test_scan_contract_success(self, test_client):
        """Test successful contract scan."""
        contract_data = {
            "address": "0x1234567890123456789012345678901234567890",
            "code": "pragma solidity ^0.8.0; contract Test {}"
        }
        
        response = test_client.post("/api/v1/scan", json=contract_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["contract_address"] == contract_data["address"]
        assert data["risk_score"] == 7.5
        assert len(data["vulnerabilities"]) == 2
        assert data["status"] == "completed"
        assert "scan_id" in data
    
    def test_scan_contract_invalid_address(self, test_client):
        """Test contract scan with invalid address."""
        contract_data = {
            "address": "invalid_address",
            "code": "pragma solidity ^0.8.0; contract Test {}"
        }
        
        response = test_client.post("/api/v1/scan", json=contract_data)
        
        assert response.status_code == 400
        assert "Invalid Ethereum address" in response.json()["detail"]
    
    def test_scan_contract_missing_address(self, test_client):
        """Test contract scan without address."""
        contract_data = {
            "code": "pragma solidity ^0.8.0; contract Test {}"
        }
        
        response = test_client.post("/api/v1/scan", json=contract_data)
        
        assert response.status_code == 400
        assert "Contract address required" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_scan_contract_async(self, async_client):
        """Test contract scan with async client."""
        contract_data = {
            "address": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
            "code": "pragma solidity ^0.8.0; contract AsyncTest {}"
        }
        
        response = await async_client.post("/api/v1/scan", json=contract_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["contract_address"] == contract_data["address"]
        assert "scan_id" in data
    
    def test_get_scan_result_success(self, test_client):
        """Test retrieving scan result by ID."""
        # First, create a scan
        contract_data = {
            "address": "0x1111111111111111111111111111111111111111"
        }
        scan_response = test_client.post("/api/v1/scan", json=contract_data)
        scan_id = scan_response.json()["scan_id"]
        
        # Then, retrieve it
        response = test_client.get(f"/api/v1/scan/{scan_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["scan_id"] == scan_id
        assert data["contract_address"] == contract_data["address"]
        assert data["risk_score"] == 7.5
        assert data["vulnerability_count"] == 2
        assert "scan_timestamp" in data
    
    def test_get_scan_result_not_found(self, test_client):
        """Test retrieving non-existent scan result."""
        response = test_client.get("/api/v1/scan/99999")
        
        assert response.status_code == 404
        assert "Scan result not found" in response.json()["detail"]


class TestMEVDetectionAPI:
    """Test MEV detection API endpoints."""
    
    def test_mev_detection_success(self, test_client):
        """Test successful MEV detection."""
        tx_hash = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef12"
        
        response = test_client.get(f"/api/v1/mev/detect?transaction_hash={tx_hash}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["transaction_hash"] == tx_hash
        assert data["mev_detected"] is True
        assert data["mev_type"] == "sandwich_attack"
        assert data["estimated_profit"] == "0.5"
        assert data["confidence"] == 0.85
    
    def test_mev_detection_invalid_hash(self, test_client):
        """Test MEV detection with invalid transaction hash."""
        invalid_hash = "invalid_hash"
        
        response = test_client.get(f"/api/v1/mev/detect?transaction_hash={invalid_hash}")
        
        assert response.status_code == 400
        assert "Invalid transaction hash" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_mev_detection_async(self, async_client):
        """Test MEV detection with async client."""
        tx_hash = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdef"
        
        response = await async_client.get(f"/api/v1/mev/detect?transaction_hash={tx_hash}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["transaction_hash"] == tx_hash
        assert data["mev_detected"] is True


class TestAuthenticationAPI:
    """Test authentication API endpoints."""
    
    def test_create_api_key_success(self, test_client):
        """Test successful API key creation."""
        user_data = {
            "email": "test@example.com"
        }
        
        response = test_client.post("/api/v1/auth/api-key", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["api_key"].startswith("sk-scorpius-")
        assert "user_id" in data
    
    def test_create_api_key_duplicate_user(self, test_client):
        """Test API key creation for existing user."""
        user_data = {
            "email": "duplicate@example.com"
        }
        
        # Create user first time
        response1 = test_client.post("/api/v1/auth/api-key", json=user_data)
        assert response1.status_code == 200
        
        # Try to create again
        response2 = test_client.post("/api/v1/auth/api-key", json=user_data)
        assert response2.status_code == 409
        assert "User already exists" in response2.json()["detail"]
    
    def test_create_api_key_missing_email(self, test_client):
        """Test API key creation without email."""
        user_data = {}
        
        response = test_client.post("/api/v1/auth/api-key", json=user_data)
        
        assert response.status_code == 400
        assert "Email required" in response.json()["detail"]


class TestDatabaseIntegration:
    """Test database integration in API endpoints."""
    
    def test_scan_persistence(self, test_client, test_db):
        """Test that scan results are properly persisted."""
        contract_data = {
            "address": "0x2222222222222222222222222222222222222222"
        }
        
        # Create scan
        response = test_client.post("/api/v1/scan", json=contract_data)
        scan_id = response.json()["scan_id"]
        
        # Verify in database
        scan_result = test_db.query(ScanResult).filter(ScanResult.id == scan_id).first()
        assert scan_result is not None
        assert scan_result.contract_address == contract_data["address"]
        assert scan_result.risk_score == 7.5
        assert scan_result.vulnerability_count == 2
    
    def test_user_persistence(self, test_client, test_db):
        """Test that users are properly persisted."""
        user_data = {
            "email": "persistence@example.com"
        }
        
        # Create user
        response = test_client.post("/api/v1/auth/api-key", json=user_data)
        user_id = response.json()["user_id"]
        
        # Verify in database
        user = test_db.query(User).filter(User.id == user_id).first()
        assert user is not None
        assert user.email == user_data["email"]
        assert user.api_key.startswith("sk-scorpius-")
    
    def test_multiple_scans_same_address(self, test_client, test_db):
        """Test multiple scans for the same contract address."""
        contract_data = {
            "address": "0x3333333333333333333333333333333333333333"
        }
        
        # Create multiple scans
        response1 = test_client.post("/api/v1/scan", json=contract_data)
        response2 = test_client.post("/api/v1/scan", json=contract_data)
        
        scan_id1 = response1.json()["scan_id"]
        scan_id2 = response2.json()["scan_id"]
        
        # Verify both are saved
        assert scan_id1 != scan_id2
        
        scan_count = test_db.query(ScanResult).filter(
            ScanResult.contract_address == contract_data["address"]
        ).count()
        assert scan_count == 2


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_json_decode_error(self, test_client):
        """Test handling of malformed JSON."""
        response = test_client.post(
            "/api/v1/scan",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        # FastAPI should return 422 for malformed JSON
        assert response.status_code == 422
    
    def test_missing_content_type(self, test_client):
        """Test handling of missing content type."""
        response = test_client.post("/api/v1/scan", data="test")
        
        # Should handle gracefully
        assert response.status_code in [400, 422]
    
    @pytest.mark.asyncio
    async def test_database_error_handling(self, async_client):
        """Test handling of database errors."""
        # This would be more complex in a real implementation
        # Here we just test that the endpoint exists and handles basic cases
        response = await async_client.get("/api/v1/scan/1")
        
        # Should either return 404 or 200 depending on whether scan exists
        assert response.status_code in [200, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

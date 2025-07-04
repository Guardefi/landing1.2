import os
import pytest
import importlib.util
from pathlib import Path

os.environ.setdefault("JWT_SECRET", "test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

gateway_path = Path(__file__).resolve().parents[1] / "enhanced_gateway.py"
source_lines = []
with open(gateway_path) as f:
    for line in f:
        source_lines.append(line)
        if "SCANNER SERVICE ROUTES" in line:
            break
source = "".join(source_lines)
spec = importlib.util.spec_from_loader("gateway_partial", loader=None)
gateway = importlib.util.module_from_spec(spec)
exec(source, gateway.__dict__)
app = gateway.app

from fastapi.testclient import TestClient

client = TestClient(app)


def test_verify_license_valid():
    resp = client.post("/license/verify", json={"license_key": "SX-ENT-2024-7891"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["id"] == "SX-ENT-2024-7891"


def test_verify_license_invalid():
    resp = client.post("/license/verify", json={"license_key": "INVALID"})
    assert resp.status_code == 400
    data = resp.json()
    assert data["success"] is False

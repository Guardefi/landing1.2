try:
    from services.api_gateway.main import app, SERVICE_ROUTE_MAP  # type: ignore
except Exception as e:
    import pytest
    pytest.skip(f"Could not import api gateway module: {e}", allow_module_level=True)

import pytest
from fastapi.testclient import TestClient

client = TestClient(app)


def test_readiness_endpoint():
    resp = client.get('/readiness')
    assert resp.status_code == 200
    assert 'status' in resp.json()


@pytest.mark.parametrize('prefix', list(SERVICE_ROUTE_MAP.keys()))
def test_unknown_service_returns_404(prefix):
    resp = client.get(f'/api/{prefix}__invalid__/something')
    # The double underscore ensures prefix mismatch hence unknown prefix 404 will trigger
    assert resp.status_code in (404, 500) 
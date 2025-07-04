import pytest


def test_login_success(client):
    resp = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "password123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data


def test_login_invalid_password(client):
    resp = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "wrong"},
    )
    assert resp.status_code == 401

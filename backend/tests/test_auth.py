"""Tests for the auth module — login and token validation."""

import os
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///./test_auth.db"

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


class TestLogin:
    @patch("app.api.auth.wechat_code2session", new_callable=AsyncMock)
    def test_login_creates_new_user(self, mock_code2session):
        mock_code2session.return_value = {"openid": "test_openid_123", "session_key": "sk"}

        resp = client.post("/api/auth/login", json={"code": "fake_code"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_new"] is True
        assert data["token"]
        assert data["nickname"] == "Learner"

    @patch("app.api.auth.wechat_code2session", new_callable=AsyncMock)
    def test_login_returns_existing_user(self, mock_code2session):
        mock_code2session.return_value = {"openid": "existing_openid", "session_key": "sk"}

        resp1 = client.post("/api/auth/login", json={"code": "code1"})
        assert resp1.json()["is_new"] is True
        user_id = resp1.json()["user_id"]

        resp2 = client.post("/api/auth/login", json={"code": "code2"})
        assert resp2.json()["is_new"] is False
        assert resp2.json()["user_id"] == user_id

    @patch("app.api.auth.wechat_code2session", new_callable=AsyncMock)
    def test_login_refreshes_token(self, mock_code2session):
        mock_code2session.return_value = {"openid": "openid_refresh", "session_key": "sk"}

        resp1 = client.post("/api/auth/login", json={"code": "c1"})
        token1 = resp1.json()["token"]

        resp2 = client.post("/api/auth/login", json={"code": "c2"})
        token2 = resp2.json()["token"]

        assert token1 != token2


class TestGetCurrentUser:
    @patch("app.api.auth.wechat_code2session", new_callable=AsyncMock)
    def test_valid_token(self, mock_code2session):
        mock_code2session.return_value = {"openid": "openid_valid", "session_key": "sk"}
        resp = client.post("/api/auth/login", json={"code": "c"})
        token = resp.json()["token"]

        me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_resp.status_code == 200
        assert me_resp.json()["nickname"] == "Learner"

    def test_missing_token(self):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_invalid_token(self):
        resp = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid_token"})
        assert resp.status_code == 401

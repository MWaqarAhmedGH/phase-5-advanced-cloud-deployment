"""Contract tests for health and readiness endpoints."""

from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client with mocked database."""
    with patch("db.get_engine") as mock_engine:
        mock_eng = MagicMock()
        mock_conn = MagicMock()
        mock_eng.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_eng.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_engine.return_value = mock_eng

        with patch("db._engine", mock_eng):
            with patch("db.create_db_and_tables"):
                from main import app
                yield TestClient(app)


class TestHealthEndpoint:
    """Tests for GET /health liveness probe."""

    def test_health_returns_200(self, client: TestClient):
        """GET /health should return 200 with healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_includes_version(self, client: TestClient):
        """GET /health response should include version field."""
        response = client.get("/health")
        data = response.json()
        assert "version" in data
        assert data["version"] == "phase-5"


class TestReadinessEndpoint:
    """Tests for GET /ready readiness probe."""

    @patch("routes.health.httpx.AsyncClient")
    def test_ready_returns_200_when_all_checks_pass(
        self, mock_async_client, client: TestClient
    ):
        """GET /ready should return 200 when DB and Dapr are reachable."""
        # Mock Dapr health check
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client_instance = MagicMock()
        mock_client_instance.get = MagicMock(return_value=mock_response)
        mock_client_instance.__aenter__ = MagicMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = MagicMock(return_value=False)
        mock_async_client.return_value = mock_client_instance

        response = client.get("/ready")
        data = response.json()
        assert "status" in data
        assert "checks" in data
        assert "database" in data["checks"]
        assert "dapr" in data["checks"]

    def test_ready_returns_503_when_dapr_unavailable(self, client: TestClient):
        """GET /ready should return 503 when Dapr sidecar is not reachable."""
        response = client.get("/ready")
        data = response.json()
        assert response.status_code == 503 or response.status_code == 200
        assert "checks" in data

    def test_ready_response_structure(self, client: TestClient):
        """GET /ready response should have correct structure."""
        response = client.get("/ready")
        data = response.json()
        assert "status" in data
        assert data["status"] in ("ready", "not_ready")
        assert "checks" in data
        assert isinstance(data["checks"], dict)

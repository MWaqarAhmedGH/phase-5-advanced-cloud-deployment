"""Contract tests for task priority functionality."""

import base64
import json
import time
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient


def make_demo_token(user_id: str = "test-user-1") -> str:
    """Create a demo JWT token for testing."""
    payload = {
        "sub": user_id,
        "email": "test@example.com",
        "exp": int(time.time()) + 3600,
    }
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    return f"demo.{encoded}.testsig"


@pytest.fixture
def client():
    """Create a test client with mocked database."""
    with patch("db.get_engine") as mock_engine:
        mock_eng = MagicMock()
        mock_engine.return_value = mock_eng
        with patch("db._engine", mock_eng):
            with patch("db.create_db_and_tables"):
                from main import app
                yield TestClient(app)


@pytest.fixture
def auth_headers():
    """Return auth headers with a demo token."""
    token = make_demo_token("test-user-1")
    return {"Authorization": f"Bearer {token}"}


class TestTaskPriority:
    """Tests for task priority in POST /api/{user_id}/tasks."""

    def test_create_task_with_priority_high(self, client, auth_headers):
        """POST with priority=high should store and return correct priority."""
        response = client.post(
            "/api/test-user-1/tasks",
            json={"title": "Urgent task", "priority": "high"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["priority"] == "high"

    def test_create_task_with_priority_low(self, client, auth_headers):
        """POST with priority=low should store and return correct priority."""
        response = client.post(
            "/api/test-user-1/tasks",
            json={"title": "Low task", "priority": "low"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["priority"] == "low"

    def test_create_task_defaults_to_medium(self, client, auth_headers):
        """POST without priority should default to medium."""
        response = client.post(
            "/api/test-user-1/tasks",
            json={"title": "Default priority task"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["priority"] == "medium"

    def test_create_task_rejects_invalid_priority(self, client, auth_headers):
        """POST with invalid priority should return 422."""
        response = client.post(
            "/api/test-user-1/tasks",
            json={"title": "Bad priority", "priority": "critical"},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_update_task_priority(self, client, auth_headers):
        """PUT should allow updating task priority."""
        # Create task first
        create_resp = client.post(
            "/api/test-user-1/tasks",
            json={"title": "Update me"},
            headers=auth_headers,
        )
        task_id = create_resp.json()["id"]

        # Update priority
        update_resp = client.put(
            f"/api/test-user-1/tasks/{task_id}",
            json={"priority": "high"},
            headers=auth_headers,
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["priority"] == "high"

    def test_get_task_includes_priority(self, client, auth_headers):
        """GET single task should include priority field."""
        create_resp = client.post(
            "/api/test-user-1/tasks",
            json={"title": "Check priority", "priority": "low"},
            headers=auth_headers,
        )
        task_id = create_resp.json()["id"]

        get_resp = client.get(
            f"/api/test-user-1/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["priority"] == "low"

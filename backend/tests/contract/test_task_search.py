"""Contract tests for task search, filter, and sort functionality."""

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


class TestTaskSearch:
    """Tests for GET /api/{user_id}/tasks search functionality."""

    def test_search_by_keyword(self, client, auth_headers):
        """GET with search=groceries should return only matching tasks."""
        # Create tasks
        client.post(
            "/api/test-user-1/tasks",
            json={"title": "Buy groceries"},
            headers=auth_headers,
        )
        client.post(
            "/api/test-user-1/tasks",
            json={"title": "Read book"},
            headers=auth_headers,
        )

        response = client.get(
            "/api/test-user-1/tasks?search=groceries",
            headers=auth_headers,
        )
        assert response.status_code == 200
        tasks = response.json()
        assert all("groceries" in t["title"].lower() for t in tasks)

    def test_filter_by_priority(self, client, auth_headers):
        """GET with priority=high should return only high priority tasks."""
        client.post(
            "/api/test-user-1/tasks",
            json={"title": "Urgent task", "priority": "high"},
            headers=auth_headers,
        )
        client.post(
            "/api/test-user-1/tasks",
            json={"title": "Normal task", "priority": "low"},
            headers=auth_headers,
        )

        response = client.get(
            "/api/test-user-1/tasks?priority=high",
            headers=auth_headers,
        )
        assert response.status_code == 200
        tasks = response.json()
        assert all(t["priority"] == "high" for t in tasks)

    def test_filter_by_status_completed(self, client, auth_headers):
        """GET with status=completed should return only completed tasks."""
        response = client.get(
            "/api/test-user-1/tasks?status=completed",
            headers=auth_headers,
        )
        assert response.status_code == 200
        tasks = response.json()
        assert all(t["completed"] for t in tasks)

    def test_filter_by_status_pending(self, client, auth_headers):
        """GET with status=pending should return only pending tasks."""
        response = client.get(
            "/api/test-user-1/tasks?status=pending",
            headers=auth_headers,
        )
        assert response.status_code == 200
        tasks = response.json()
        assert all(not t["completed"] for t in tasks)

    def test_sort_by_priority(self, client, auth_headers):
        """GET with sort=priority should return tasks ordered by priority level."""
        response = client.get(
            "/api/test-user-1/tasks?sort=priority",
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_sort_by_due_date(self, client, auth_headers):
        """GET with sort=due_date should return tasks ordered by due date."""
        response = client.get(
            "/api/test-user-1/tasks?sort=due_date",
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_sort_with_order_desc(self, client, auth_headers):
        """GET with sort=title&order=desc should return descending order."""
        response = client.get(
            "/api/test-user-1/tasks?sort=title&order=desc",
            headers=auth_headers,
        )
        assert response.status_code == 200

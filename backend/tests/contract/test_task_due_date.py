"""Contract tests for task due date functionality."""

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


class TestTaskDueDate:
    """Tests for due date in task endpoints."""

    def test_create_task_with_due_date(self, client, auth_headers):
        """POST with due_date should store and return it."""
        response = client.post(
            "/api/test-user-1/tasks",
            json={
                "title": "Task with deadline",
                "due_date": "2026-02-15T14:00:00Z",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["due_date"] is not None

    def test_create_task_with_reminder(self, client, auth_headers):
        """POST with reminder_offset_minutes should store it."""
        response = client.post(
            "/api/test-user-1/tasks",
            json={
                "title": "Task with reminder",
                "due_date": "2026-02-15T14:00:00Z",
                "reminder_offset_minutes": 30,
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["reminder_offset_minutes"] == 30

    def test_create_task_without_due_date(self, client, auth_headers):
        """POST without due_date should return null."""
        response = client.post(
            "/api/test-user-1/tasks",
            json={"title": "No deadline"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["due_date"] is None

    def test_get_task_returns_due_date(self, client, auth_headers):
        """GET should return due_date field."""
        create_resp = client.post(
            "/api/test-user-1/tasks",
            json={
                "title": "Due date check",
                "due_date": "2026-03-01T09:00:00Z",
            },
            headers=auth_headers,
        )
        task_id = create_resp.json()["id"]

        get_resp = client.get(
            f"/api/test-user-1/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["due_date"] is not None

    def test_filter_tasks_by_due_date_range(self, client, auth_headers):
        """GET with due_from and due_to should filter tasks."""
        response = client.get(
            "/api/test-user-1/tasks?due_from=2026-02-01T00:00:00Z&due_to=2026-02-28T23:59:59Z",
            headers=auth_headers,
        )
        assert response.status_code == 200

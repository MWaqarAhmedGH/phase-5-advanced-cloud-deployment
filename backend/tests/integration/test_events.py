"""Integration tests for event publishing via Dapr Pub/Sub."""

import base64
import json
import time
from unittest.mock import patch, MagicMock, AsyncMock

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


class TestEventPublishing:
    """Tests that task CRUD operations publish events via Dapr."""

    @patch("routes.tasks.publish_event", new_callable=AsyncMock)
    def test_create_task_publishes_event(
        self, mock_publish, client, auth_headers
    ):
        """Creating a task should publish a task.created event."""
        mock_publish.return_value = True

        response = client.post(
            "/api/test-user-1/tasks",
            json={"title": "Test event publishing"},
            headers=auth_headers,
        )
        assert response.status_code == 201

        mock_publish.assert_called_once()
        call_kwargs = mock_publish.call_args
        assert call_kwargs.kwargs["topic"] == "task-events"
        assert call_kwargs.kwargs["event_type"] == "task.created"
        assert call_kwargs.kwargs["user_id"] == "test-user-1"

    @patch("routes.tasks.publish_event", new_callable=AsyncMock)
    def test_update_task_publishes_event(
        self, mock_publish, client, auth_headers
    ):
        """Updating a task should publish a task.updated event."""
        mock_publish.return_value = True

        # Create task
        create_resp = client.post(
            "/api/test-user-1/tasks",
            json={"title": "Original"},
            headers=auth_headers,
        )
        task_id = create_resp.json()["id"]
        mock_publish.reset_mock()

        # Update task
        client.put(
            f"/api/test-user-1/tasks/{task_id}",
            json={"title": "Updated"},
            headers=auth_headers,
        )

        mock_publish.assert_called_once()
        assert mock_publish.call_args.kwargs["event_type"] == "task.updated"

    @patch("routes.tasks.publish_event", new_callable=AsyncMock)
    def test_complete_task_publishes_event(
        self, mock_publish, client, auth_headers
    ):
        """Completing a task should publish a task.completed event."""
        mock_publish.return_value = True

        create_resp = client.post(
            "/api/test-user-1/tasks",
            json={"title": "Complete me"},
            headers=auth_headers,
        )
        task_id = create_resp.json()["id"]
        mock_publish.reset_mock()

        client.patch(
            f"/api/test-user-1/tasks/{task_id}/complete",
            headers=auth_headers,
        )

        mock_publish.assert_called_once()
        assert mock_publish.call_args.kwargs["event_type"] == "task.completed"

    @patch("routes.tasks.publish_event", new_callable=AsyncMock)
    def test_delete_task_publishes_event(
        self, mock_publish, client, auth_headers
    ):
        """Deleting a task should publish a task.deleted event."""
        mock_publish.return_value = True

        create_resp = client.post(
            "/api/test-user-1/tasks",
            json={"title": "Delete me"},
            headers=auth_headers,
        )
        task_id = create_resp.json()["id"]
        mock_publish.reset_mock()

        client.delete(
            f"/api/test-user-1/tasks/{task_id}",
            headers=auth_headers,
        )

        mock_publish.assert_called_once()
        assert mock_publish.call_args.kwargs["event_type"] == "task.deleted"

    def test_event_handler_accepts_task_event(self, client):
        """POST /api/events/task should accept and process events."""
        event = {
            "event_type": "task.created",
            "task_id": 1,
            "user_id": "test-user-1",
            "task_data": {"title": "Test task"},
            "timestamp": "2026-02-07T00:00:00Z",
        }
        response = client.post("/api/events/task", json=event)
        assert response.status_code == 200
        assert response.json()["status"] == "SUCCESS"

    def test_event_handler_accepts_reminder_event(self, client):
        """POST /api/events/reminder should accept and process events."""
        event = {
            "task_id": 1,
            "user_id": "test-user-1",
            "title": "Test reminder",
        }
        response = client.post("/api/events/reminder", json=event)
        assert response.status_code == 200
        assert response.json()["status"] == "SUCCESS"

    def test_dapr_subscribe_returns_subscriptions(self, client):
        """GET /dapr/subscribe should return topic subscriptions."""
        response = client.get("/dapr/subscribe")
        assert response.status_code == 200
        subs = response.json()
        topics = [s["topic"] for s in subs]
        assert "task-events" in topics
        assert "reminders" in topics

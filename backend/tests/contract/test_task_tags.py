"""Contract tests for task tag management."""

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


class TestTaskTags:
    """Tests for tag management endpoints."""

    def test_add_tags_to_task(self, client, auth_headers):
        """POST /api/{user_id}/tasks/{id}/tags should add tags."""
        # Create task
        create_resp = client.post(
            "/api/test-user-1/tasks",
            json={"title": "Tagged task"},
            headers=auth_headers,
        )
        task_id = create_resp.json()["id"]

        # Add tags
        tag_resp = client.post(
            f"/api/test-user-1/tasks/{task_id}/tags",
            json={"tags": ["work", "urgent"]},
            headers=auth_headers,
        )
        assert tag_resp.status_code == 200
        data = tag_resp.json()
        assert "tags" in data
        assert "work" in data["tags"]
        assert "urgent" in data["tags"]

    def test_remove_tag_from_task(self, client, auth_headers):
        """DELETE /api/{user_id}/tasks/{id}/tags/{tag} should remove the tag."""
        # Create task with tags
        create_resp = client.post(
            "/api/test-user-1/tasks",
            json={"title": "Tag removal test"},
            headers=auth_headers,
        )
        task_id = create_resp.json()["id"]

        # Add tags
        client.post(
            f"/api/test-user-1/tasks/{task_id}/tags",
            json={"tags": ["work", "personal"]},
            headers=auth_headers,
        )

        # Remove one tag
        del_resp = client.delete(
            f"/api/test-user-1/tasks/{task_id}/tags/work",
            headers=auth_headers,
        )
        assert del_resp.status_code == 200
        data = del_resp.json()
        assert "work" not in data["tags"]
        assert "personal" in data["tags"]

    def test_get_task_includes_tags(self, client, auth_headers):
        """GET task response should include tags array."""
        create_resp = client.post(
            "/api/test-user-1/tasks",
            json={"title": "With tags"},
            headers=auth_headers,
        )
        task_id = create_resp.json()["id"]

        # Add tags
        client.post(
            f"/api/test-user-1/tasks/{task_id}/tags",
            json={"tags": ["groceries"]},
            headers=auth_headers,
        )

        get_resp = client.get(
            f"/api/test-user-1/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_resp.status_code == 200
        data = get_resp.json()
        assert "tags" in data
        assert "groceries" in data["tags"]

    def test_list_tasks_includes_tags(self, client, auth_headers):
        """GET tasks list should include tags for each task."""
        create_resp = client.post(
            "/api/test-user-1/tasks",
            json={"title": "List tags test"},
            headers=auth_headers,
        )
        task_id = create_resp.json()["id"]

        client.post(
            f"/api/test-user-1/tasks/{task_id}/tags",
            json={"tags": ["work"]},
            headers=auth_headers,
        )

        list_resp = client.get(
            "/api/test-user-1/tasks",
            headers=auth_headers,
        )
        assert list_resp.status_code == 200
        tasks = list_resp.json()
        assert any("tags" in t for t in tasks)

"""Integration tests for Todo API routes using FastAPI TestClient."""
import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_repository():
    """Clear the shared in-memory store before and after each test."""
    from src.api.routes import _repository

    _repository._store.clear()
    yield
    _repository._store.clear()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def create_todo(client: TestClient, title: str = "Test Todo", **kwargs) -> dict:
    payload = {"title": title, **kwargs}
    resp = client.post("/api/v1/todos", json=payload)
    assert resp.status_code == 201
    return resp.json()


# ---------------------------------------------------------------------------
# GET /todos  — list
# ---------------------------------------------------------------------------

class TestListTodos:
    def test_empty_returns_200(self, client):
        resp = client.get("/api/v1/todos")
        assert resp.status_code == 200

    def test_empty_store_response_shape(self, client):
        data = client.get("/api/v1/todos").json()
        assert data["total"] == 0
        assert data["items"] == []
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert data["total_pages"] == 1

    def test_lists_created_todos(self, client):
        create_todo(client, "A")
        create_todo(client, "B")
        data = client.get("/api/v1/todos").json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    def test_pagination_page_parameter(self, client):
        for i in range(5):
            create_todo(client, f"Todo {i}")
        data = client.get("/api/v1/todos?page=2&page_size=2").json()
        assert data["page"] == 2
        assert len(data["items"]) == 2

    def test_pagination_total_pages(self, client):
        for i in range(5):
            create_todo(client, f"Todo {i}")
        data = client.get("/api/v1/todos?page_size=2").json()
        assert data["total_pages"] == 3

    def test_invalid_page_zero_returns_422(self, client):
        assert client.get("/api/v1/todos?page=0").status_code == 422

    def test_page_size_exceeding_max_returns_422(self, client):
        assert client.get("/api/v1/todos?page_size=101").status_code == 422


# ---------------------------------------------------------------------------
# GET /todos/{id}  — get one
# ---------------------------------------------------------------------------

class TestGetTodo:
    def test_get_existing_todo(self, client):
        todo = create_todo(client, "Find me")
        resp = client.get(f"/api/v1/todos/{todo['id']}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Find me"

    def test_get_returns_all_fields(self, client):
        todo = create_todo(client, "Full", description="desc", priority="high")
        data = client.get(f"/api/v1/todos/{todo['id']}").json()
        assert data["id"] == todo["id"]
        assert data["title"] == "Full"
        assert data["description"] == "desc"
        assert data["priority"] == "high"
        assert data["status"] == "pending"
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_nonexistent_returns_404(self, client):
        resp = client.get("/api/v1/todos/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404

    def test_get_invalid_uuid_returns_422(self, client):
        assert client.get("/api/v1/todos/not-a-uuid").status_code == 422


# ---------------------------------------------------------------------------
# POST /todos  — create
# ---------------------------------------------------------------------------

class TestCreateTodo:
    def test_returns_201(self, client):
        assert client.post("/api/v1/todos", json={"title": "New"}).status_code == 201

    def test_response_contains_id(self, client):
        data = client.post("/api/v1/todos", json={"title": "Task"}).json()
        assert "id" in data

    def test_default_status_is_pending(self, client):
        data = client.post("/api/v1/todos", json={"title": "Task"}).json()
        assert data["status"] == "pending"

    def test_default_priority_is_medium(self, client):
        data = client.post("/api/v1/todos", json={"title": "Task"}).json()
        assert data["priority"] == "medium"

    def test_custom_priority_is_saved(self, client):
        data = client.post("/api/v1/todos", json={"title": "T", "priority": "high"}).json()
        assert data["priority"] == "high"

    def test_description_is_saved(self, client):
        data = client.post("/api/v1/todos", json={"title": "T", "description": "Some desc"}).json()
        assert data["description"] == "Some desc"

    def test_empty_title_returns_422(self, client):
        assert client.post("/api/v1/todos", json={"title": ""}).status_code == 422

    def test_missing_title_returns_422(self, client):
        assert client.post("/api/v1/todos", json={}).status_code == 422

    def test_invalid_priority_returns_422(self, client):
        assert client.post("/api/v1/todos", json={"title": "T", "priority": "urgent"}).status_code == 422

    def test_title_too_long_returns_422(self, client):
        assert client.post("/api/v1/todos", json={"title": "x" * 201}).status_code == 422


# ---------------------------------------------------------------------------
# PATCH /todos/{id}  — update
# ---------------------------------------------------------------------------

class TestUpdateTodo:
    def test_update_title(self, client):
        todo = create_todo(client, "Old")
        resp = client.patch(f"/api/v1/todos/{todo['id']}", json={"title": "New"})
        assert resp.status_code == 200
        assert resp.json()["title"] == "New"

    def test_update_status_to_in_progress(self, client):
        todo = create_todo(client, "Task")
        resp = client.patch(f"/api/v1/todos/{todo['id']}", json={"status": "in_progress"})
        assert resp.json()["status"] == "in_progress"

    def test_update_status_to_done(self, client):
        todo = create_todo(client, "Task")
        resp = client.patch(f"/api/v1/todos/{todo['id']}", json={"status": "done"})
        assert resp.json()["status"] == "done"

    def test_update_priority(self, client):
        todo = create_todo(client, "Task")
        resp = client.patch(f"/api/v1/todos/{todo['id']}", json={"priority": "low"})
        assert resp.json()["priority"] == "low"

    def test_partial_update_keeps_other_fields(self, client):
        todo = create_todo(client, "Keep", description="stay", priority="high")
        resp = client.patch(f"/api/v1/todos/{todo['id']}", json={"status": "in_progress"})
        data = resp.json()
        assert data["title"] == "Keep"
        assert data["description"] == "stay"
        assert data["priority"] == "high"
        assert data["status"] == "in_progress"

    def test_update_nonexistent_returns_404(self, client):
        resp = client.patch("/api/v1/todos/00000000-0000-0000-0000-000000000000", json={"title": "x"})
        assert resp.status_code == 404

    def test_update_invalid_status_returns_422(self, client):
        todo = create_todo(client, "T")
        resp = client.patch(f"/api/v1/todos/{todo['id']}", json={"status": "invalid"})
        assert resp.status_code == 422

    def test_update_empty_title_returns_422(self, client):
        todo = create_todo(client, "T")
        resp = client.patch(f"/api/v1/todos/{todo['id']}", json={"title": ""})
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# DELETE /todos/{id}  — delete
# ---------------------------------------------------------------------------

class TestDeleteTodo:
    def test_returns_204(self, client):
        todo = create_todo(client, "Delete me")
        resp = client.delete(f"/api/v1/todos/{todo['id']}")
        assert resp.status_code == 204

    def test_deleted_todo_returns_404_on_get(self, client):
        todo = create_todo(client, "Gone")
        client.delete(f"/api/v1/todos/{todo['id']}")
        assert client.get(f"/api/v1/todos/{todo['id']}").status_code == 404

    def test_deleted_todo_not_in_list(self, client):
        create_todo(client, "Keep")
        gone = create_todo(client, "Gone")
        client.delete(f"/api/v1/todos/{gone['id']}")
        data = client.get("/api/v1/todos").json()
        ids = [item["id"] for item in data["items"]]
        assert gone["id"] not in ids

    def test_delete_nonexistent_returns_404(self, client):
        resp = client.delete("/api/v1/todos/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404

    def test_delete_reduces_total(self, client):
        t1 = create_todo(client, "A")
        create_todo(client, "B")
        client.delete(f"/api/v1/todos/{t1['id']}")
        assert client.get("/api/v1/todos").json()["total"] == 1


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

class TestHealthCheck:
    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

"""Unit tests for TodoService — repository is always mocked."""
import pytest
from unittest.mock import MagicMock
from uuid import uuid4

from src.exceptions import TodoNotFoundError
from src.models.todo import (
    Todo,
    TodoCreateRequest,
    TodoPriority,
    TodoStatus,
    TodoUpdateRequest,
)
from src.services.todo_service import TodoService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_repo() -> MagicMock:
    return MagicMock()


def make_todo(title: str = "Test", **kwargs) -> Todo:
    defaults = {"title": title, "description": "", "priority": TodoPriority.MEDIUM}
    defaults.update(kwargs)
    return Todo(**defaults)


def build_service(repo=None) -> tuple[TodoService, MagicMock]:
    repo = repo or make_repo()
    return TodoService(repository=repo), repo


# ---------------------------------------------------------------------------
# list_todos
# ---------------------------------------------------------------------------

class TestListTodos:
    def test_returns_paginated_response(self):
        service, repo = build_service()
        todos = [make_todo(f"T{i}") for i in range(3)]
        repo.get_all.return_value = (todos, 3)

        result = service.list_todos(page=1, page_size=10)

        assert result.total == 3
        assert result.page == 1
        assert len(result.items) == 3

    def test_calculates_total_pages_correctly(self):
        service, repo = build_service()
        repo.get_all.return_value = ([make_todo()], 25)

        result = service.list_todos(page=1, page_size=5)

        assert result.total_pages == 5

    def test_total_pages_rounds_up(self):
        service, repo = build_service()
        repo.get_all.return_value = ([], 11)

        result = service.list_todos(page=1, page_size=5)

        assert result.total_pages == 3

    def test_empty_list_returns_one_total_page(self):
        service, repo = build_service()
        repo.get_all.return_value = ([], 0)

        result = service.list_todos()

        assert result.total_pages == 1
        assert result.total == 0
        assert result.items == []

    def test_passes_correct_skip_to_repository(self):
        service, repo = build_service()
        repo.get_all.return_value = ([], 0)

        service.list_todos(page=3, page_size=10)

        repo.get_all.assert_called_once_with(skip=20, limit=10)

    def test_page_size_capped_at_max(self):
        service, repo = build_service()
        repo.get_all.return_value = ([], 0)

        result = service.list_todos(page=1, page_size=999)

        # page_size should be clamped to MAX_PAGE_SIZE (100)
        assert result.page_size <= 100


# ---------------------------------------------------------------------------
# get_todo
# ---------------------------------------------------------------------------

class TestGetTodo:
    def test_returns_todo_response(self):
        service, repo = build_service()
        todo = make_todo("My Todo")
        repo.get_by_id.return_value = todo

        result = service.get_todo(todo.id)

        assert result.id == todo.id
        assert result.title == "My Todo"

    def test_raises_when_not_found(self):
        service, repo = build_service()
        repo.get_by_id.return_value = None

        with pytest.raises(TodoNotFoundError) as exc_info:
            service.get_todo(uuid4())

        assert "not found" in str(exc_info.value).lower()

    def test_calls_repo_with_correct_id(self):
        service, repo = build_service()
        todo = make_todo()
        repo.get_by_id.return_value = todo

        service.get_todo(todo.id)

        repo.get_by_id.assert_called_once_with(todo.id)


# ---------------------------------------------------------------------------
# create_todo
# ---------------------------------------------------------------------------

class TestCreateTodo:
    def test_creates_and_returns_todo(self):
        service, repo = build_service()
        repo.create.side_effect = lambda t: t

        payload = TodoCreateRequest(title="Buy milk", description="2%", priority=TodoPriority.LOW)
        result = service.create_todo(payload)

        assert result.title == "Buy milk"
        assert result.description == "2%"
        assert result.priority == TodoPriority.LOW

    def test_default_priority_is_medium(self):
        service, repo = build_service()
        repo.create.side_effect = lambda t: t

        result = service.create_todo(TodoCreateRequest(title="Default"))

        assert result.priority == TodoPriority.MEDIUM

    def test_default_status_is_pending(self):
        service, repo = build_service()
        repo.create.side_effect = lambda t: t

        result = service.create_todo(TodoCreateRequest(title="New"))

        assert result.status == TodoStatus.PENDING

    def test_persists_todo_via_repository(self):
        service, repo = build_service()
        repo.create.side_effect = lambda t: t

        service.create_todo(TodoCreateRequest(title="Persist me"))

        repo.create.assert_called_once()

    def test_generated_id_is_unique(self):
        service, repo = build_service()
        repo.create.side_effect = lambda t: t

        r1 = service.create_todo(TodoCreateRequest(title="A"))
        r2 = service.create_todo(TodoCreateRequest(title="B"))

        assert r1.id != r2.id


# ---------------------------------------------------------------------------
# update_todo
# ---------------------------------------------------------------------------

class TestUpdateTodo:
    def test_updates_title(self):
        service, repo = build_service()
        todo = make_todo("Old title")
        repo.get_by_id.return_value = todo
        repo.update.side_effect = lambda t: t

        result = service.update_todo(todo.id, TodoUpdateRequest(title="New title"))

        assert result.title == "New title"

    def test_updates_status(self):
        service, repo = build_service()
        todo = make_todo()
        repo.get_by_id.return_value = todo
        repo.update.side_effect = lambda t: t

        result = service.update_todo(todo.id, TodoUpdateRequest(status=TodoStatus.DONE))

        assert result.status == TodoStatus.DONE

    def test_updates_priority(self):
        service, repo = build_service()
        todo = make_todo()
        repo.get_by_id.return_value = todo
        repo.update.side_effect = lambda t: t

        result = service.update_todo(todo.id, TodoUpdateRequest(priority=TodoPriority.HIGH))

        assert result.priority == TodoPriority.HIGH

    def test_partial_update_keeps_unchanged_fields(self):
        service, repo = build_service()
        todo = make_todo("Keep title", description="Keep desc")
        repo.get_by_id.return_value = todo
        repo.update.side_effect = lambda t: t

        result = service.update_todo(todo.id, TodoUpdateRequest(status=TodoStatus.IN_PROGRESS))

        assert result.title == "Keep title"
        assert result.description == "Keep desc"
        assert result.status == TodoStatus.IN_PROGRESS

    def test_raises_when_todo_not_found(self):
        service, repo = build_service()
        repo.get_by_id.return_value = None

        with pytest.raises(TodoNotFoundError):
            service.update_todo(uuid4(), TodoUpdateRequest(title="x"))

    def test_updated_at_is_refreshed(self):
        import time
        from datetime import datetime, timezone

        service, repo = build_service()
        todo = make_todo()
        original_updated_at = todo.updated_at
        time.sleep(0.01)

        repo.get_by_id.return_value = todo
        repo.update.side_effect = lambda t: t

        result = service.update_todo(todo.id, TodoUpdateRequest(title="Changed"))

        assert result.updated_at >= original_updated_at


# ---------------------------------------------------------------------------
# delete_todo
# ---------------------------------------------------------------------------

class TestDeleteTodo:
    def test_deletes_via_repository(self):
        service, repo = build_service()
        todo = make_todo()
        repo.get_by_id.return_value = todo

        service.delete_todo(todo.id)

        repo.delete.assert_called_once_with(todo.id)

    def test_raises_when_todo_not_found(self):
        service, repo = build_service()
        repo.get_by_id.return_value = None

        with pytest.raises(TodoNotFoundError):
            service.delete_todo(uuid4())

    def test_does_not_call_delete_when_not_found(self):
        service, repo = build_service()
        repo.get_by_id.return_value = None

        with pytest.raises(TodoNotFoundError):
            service.delete_todo(uuid4())

        repo.delete.assert_not_called()

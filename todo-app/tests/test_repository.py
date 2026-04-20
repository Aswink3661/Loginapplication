"""Unit tests for InMemoryTodoRepository."""
import pytest
from uuid import uuid4

from src.models.todo import Todo, TodoPriority, TodoStatus
from src.repositories.todo_repository import InMemoryTodoRepository


def make_todo(title: str = "Test Todo", **kwargs) -> Todo:
    return Todo(title=title, **kwargs)


class TestInMemoryTodoRepositoryCreate:
    def setup_method(self):
        self.repo = InMemoryTodoRepository()

    def test_create_returns_todo(self):
        todo = make_todo("Buy milk")
        saved = self.repo.create(todo)
        assert saved.id == todo.id
        assert saved.title == "Buy milk"

    def test_create_preserves_all_fields(self):
        todo = Todo(
            title="Rich",
            description="desc here",
            status=TodoStatus.IN_PROGRESS,
            priority=TodoPriority.HIGH,
        )
        saved = self.repo.create(todo)
        assert saved.description == "desc here"
        assert saved.status == TodoStatus.IN_PROGRESS
        assert saved.priority == TodoPriority.HIGH

    def test_create_multiple_todos_are_independent(self):
        t1 = self.repo.create(make_todo("A"))
        t2 = self.repo.create(make_todo("B"))
        assert t1.id != t2.id


class TestInMemoryTodoRepositoryGetById:
    def setup_method(self):
        self.repo = InMemoryTodoRepository()

    def test_get_existing_todo(self):
        todo = self.repo.create(make_todo("Find me"))
        found = self.repo.get_by_id(todo.id)
        assert found is not None
        assert found.id == todo.id
        assert found.title == "Find me"

    def test_get_nonexistent_returns_none(self):
        result = self.repo.get_by_id(uuid4())
        assert result is None

    def test_get_after_delete_returns_none(self):
        todo = self.repo.create(make_todo())
        self.repo.delete(todo.id)
        assert self.repo.get_by_id(todo.id) is None


class TestInMemoryTodoRepositoryGetAll:
    def setup_method(self):
        self.repo = InMemoryTodoRepository()

    def test_get_all_empty_store(self):
        items, total = self.repo.get_all()
        assert items == []
        assert total == 0

    def test_get_all_returns_all_items(self):
        for i in range(3):
            self.repo.create(make_todo(f"Todo {i}"))
        items, total = self.repo.get_all()
        assert total == 3
        assert len(items) == 3

    def test_get_all_skip(self):
        for i in range(5):
            self.repo.create(make_todo(f"Todo {i}"))
        items, total = self.repo.get_all(skip=3, limit=10)
        assert total == 5
        assert len(items) == 2

    def test_get_all_limit(self):
        for i in range(10):
            self.repo.create(make_todo(f"Todo {i}"))
        items, total = self.repo.get_all(skip=0, limit=4)
        assert total == 10
        assert len(items) == 4

    def test_get_all_skip_and_limit(self):
        for i in range(10):
            self.repo.create(make_todo(f"Todo {i}"))
        items, total = self.repo.get_all(skip=5, limit=3)
        assert total == 10
        assert len(items) == 3

    def test_get_all_skip_beyond_total_returns_empty(self):
        self.repo.create(make_todo())
        items, total = self.repo.get_all(skip=100, limit=10)
        assert total == 1
        assert items == []


class TestInMemoryTodoRepositoryUpdate:
    def setup_method(self):
        self.repo = InMemoryTodoRepository()

    def test_update_changes_title(self):
        todo = self.repo.create(make_todo("Old title"))
        updated = todo.model_copy(update={"title": "New title"})
        result = self.repo.update(updated)
        assert result.title == "New title"

    def test_update_is_persisted(self):
        todo = self.repo.create(make_todo())
        updated = todo.model_copy(update={"title": "Persisted"})
        self.repo.update(updated)
        found = self.repo.get_by_id(todo.id)
        assert found.title == "Persisted"

    def test_update_status(self):
        todo = self.repo.create(make_todo())
        updated = todo.model_copy(update={"status": TodoStatus.DONE})
        result = self.repo.update(updated)
        assert result.status == TodoStatus.DONE


class TestInMemoryTodoRepositoryDelete:
    def setup_method(self):
        self.repo = InMemoryTodoRepository()

    def test_delete_removes_todo(self):
        todo = self.repo.create(make_todo())
        self.repo.delete(todo.id)
        assert self.repo.get_by_id(todo.id) is None

    def test_delete_reduces_count(self):
        t1 = self.repo.create(make_todo("A"))
        self.repo.create(make_todo("B"))
        self.repo.delete(t1.id)
        _, total = self.repo.get_all()
        assert total == 1

    def test_delete_nonexistent_does_not_raise(self):
        # Should silently ignore missing IDs
        self.repo.delete(uuid4())

    def test_delete_only_removes_target(self):
        t1 = self.repo.create(make_todo("Keep"))
        t2 = self.repo.create(make_todo("Delete"))
        self.repo.delete(t2.id)
        assert self.repo.get_by_id(t1.id) is not None
        assert self.repo.get_by_id(t2.id) is None

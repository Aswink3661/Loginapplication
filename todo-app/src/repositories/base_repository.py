from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from uuid import UUID

from src.models.todo import Todo


class AbstractTodoRepository(ABC):
    """Interface that every concrete storage backend must implement."""

    @abstractmethod
    def get_all(self, *, skip: int = 0, limit: int = 20) -> Tuple[List[Todo], int]:
        """Return a page of todos and the total count."""

    @abstractmethod
    def get_by_id(self, todo_id: UUID) -> Optional[Todo]:
        """Return a single todo by primary key, or None if not found."""

    @abstractmethod
    def create(self, todo: Todo) -> Todo:
        """Persist a new todo and return it."""

    @abstractmethod
    def update(self, todo: Todo) -> Todo:
        """Persist changes to an existing todo and return it."""

    @abstractmethod
    def delete(self, todo_id: UUID) -> None:
        """Remove a todo by primary key."""

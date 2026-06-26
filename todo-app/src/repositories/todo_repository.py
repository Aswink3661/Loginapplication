from typing import Dict, List, Optional, Tuple
from uuid import UUID

from src.models.todo import Todo
from src.repositories.base_repository import AbstractTodoRepository
from src.utils.logger import get_logger
from src.utils.telemetry import emit_event, start_span

logger = get_logger(__name__)


class InMemoryTodoRepository(AbstractTodoRepository):
    """Thread-unsafe in-memory store — suitable for development/testing.

    Replace with a SQLAlchemy/PostgreSQL repository for production by
    swapping the dependency in the service layer.
    """

    def __init__(self) -> None:
        self._store: Dict[UUID, Todo] = {}
        logger.debug("InMemoryTodoRepository initialised.")

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_all(self, *, skip: int = 0, limit: int = 20) -> Tuple[List[Todo], int]:
        with start_span(
            "todo.repository.get_all",
            {"db.system": "in_memory", "todo.skip": skip, "todo.limit": limit},
        ) as span:
            all_items = list(self._store.values())
            total = len(all_items)
            page = all_items[skip : skip + limit]
            span.set_attribute("todo.total", total)
            span.set_attribute("todo.returned", len(page))
            logger.debug("get_all | skip=%d limit=%d returned=%d total=%d", skip, limit, len(page), total)
            return page, total

    def get_by_id(self, todo_id: UUID) -> Optional[Todo]:
        with start_span(
            "todo.repository.get_by_id",
            {"db.system": "in_memory", "todo.id": str(todo_id)},
        ) as span:
            todo = self._store.get(todo_id)
            span.set_attribute("todo.found", todo is not None)
            if todo:
                logger.debug("get_by_id | found id=%s", todo_id)
            else:
                logger.debug("get_by_id | not found id=%s", todo_id)
            return todo

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def create(self, todo: Todo) -> Todo:
        with start_span(
            "todo.repository.create",
            {"db.system": "in_memory", "todo.id": str(todo.id)},
        ):
            self._store[todo.id] = todo
            emit_event("todo.repository.created", {"todo.id": str(todo.id)})
            logger.info("create | persisted todo id=%s title=%r", todo.id, todo.title)
            return todo

    def update(self, todo: Todo) -> Todo:
        with start_span(
            "todo.repository.update",
            {"db.system": "in_memory", "todo.id": str(todo.id)},
        ):
            self._store[todo.id] = todo
            emit_event("todo.repository.updated", {"todo.id": str(todo.id)})
            logger.info("update | persisted todo id=%s", todo.id)
            return todo

    def delete(self, todo_id: UUID) -> None:
        with start_span(
            "todo.repository.delete",
            {"db.system": "in_memory", "todo.id": str(todo_id)},
        ):
            self._store.pop(todo_id, None)
            emit_event("todo.repository.deleted", {"todo.id": str(todo_id)})
            logger.info("delete | removed todo id=%s", todo_id)

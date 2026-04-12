from typing import Dict, List, Optional, Tuple
from uuid import UUID

from src.models.todo import Todo
from src.repositories.base_repository import AbstractTodoRepository
from src.utils.logger import get_logger

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
        all_items = list(self._store.values())
        total = len(all_items)
        page = all_items[skip : skip + limit]
        logger.debug("get_all | skip=%d limit=%d returned=%d total=%d", skip, limit, len(page), total)
        return page, total

    def get_by_id(self, todo_id: UUID) -> Optional[Todo]:
        todo = self._store.get(todo_id)
        if todo:
            logger.debug("get_by_id | found id=%s", todo_id)
        else:
            logger.debug("get_by_id | not found id=%s", todo_id)
        return todo

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def create(self, todo: Todo) -> Todo:
        self._store[todo.id] = todo
        logger.info("create | persisted todo id=%s title=%r", todo.id, todo.title)
        return todo

    def update(self, todo: Todo) -> Todo:
        self._store[todo.id] = todo
        logger.info("update | persisted todo id=%s", todo.id)
        return todo

    def delete(self, todo_id: UUID) -> None:
        self._store.pop(todo_id, None)
        logger.info("delete | removed todo id=%s", todo_id)

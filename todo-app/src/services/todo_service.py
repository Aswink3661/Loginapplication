import math
from datetime import datetime, timezone
from uuid import UUID

from src.config.settings import get_settings
from src.exceptions import TodoNotFoundError
from src.models.todo import (
    PaginatedTodoResponse,
    Todo,
    TodoCreateRequest,
    TodoResponse,
    TodoUpdateRequest,
)
from src.repositories.base_repository import AbstractTodoRepository
from typing import Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class TodoService:
    """Encapsulates all business logic for the Todo domain."""

    def __init__(self, repository: AbstractTodoRepository) -> None:
        self._repo = repository

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def list_todos(self, page: int = 1, page_size: Optional[int] = None) -> PaginatedTodoResponse:
        page_size = min(page_size or settings.DEFAULT_PAGE_SIZE, settings.MAX_PAGE_SIZE)
        skip = (page - 1) * page_size

        logger.info("list_todos | page=%d page_size=%d", page, page_size)
        items, total = self._repo.get_all(skip=skip, limit=page_size)
        total_pages = math.ceil(total / page_size) if total else 1

        return PaginatedTodoResponse(
            items=[TodoResponse.model_validate(t) for t in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def get_todo(self, todo_id: UUID) -> TodoResponse:
        logger.info("get_todo | id=%s", todo_id)
        todo = self._repo.get_by_id(todo_id)
        if not todo:
            logger.warning("get_todo | not found id=%s", todo_id)
            raise TodoNotFoundError(str(todo_id))
        return TodoResponse.model_validate(todo)

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    def create_todo(self, payload: TodoCreateRequest) -> TodoResponse:
        logger.info("create_todo | title=%r priority=%s", payload.title, payload.priority)
        todo = Todo(
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
        )
        saved = self._repo.create(todo)
        logger.info("create_todo | created id=%s", saved.id)
        return TodoResponse.model_validate(saved)

    def update_todo(self, todo_id: UUID, payload: TodoUpdateRequest) -> TodoResponse:
        logger.info("update_todo | id=%s payload=%s", todo_id, payload.model_dump(exclude_none=True))
        todo = self._repo.get_by_id(todo_id)
        if not todo:
            logger.warning("update_todo | not found id=%s", todo_id)
            raise TodoNotFoundError(str(todo_id))

        updated_data = todo.model_dump()
        for field, value in payload.model_dump(exclude_none=True).items():
            updated_data[field] = value
        updated_data["updated_at"] = datetime.now(timezone.utc)

        updated_todo = Todo(**updated_data)
        saved = self._repo.update(updated_todo)
        logger.info("update_todo | updated id=%s", saved.id)
        return TodoResponse.model_validate(saved)

    def delete_todo(self, todo_id: UUID) -> None:
        logger.info("delete_todo | id=%s", todo_id)
        todo = self._repo.get_by_id(todo_id)
        if not todo:
            logger.warning("delete_todo | not found id=%s", todo_id)
            raise TodoNotFoundError(str(todo_id))
        self._repo.delete(todo_id)
        logger.info("delete_todo | deleted id=%s", todo_id)

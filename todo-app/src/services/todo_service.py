import math
from datetime import datetime, timezone
from typing import Optional
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

from src.utils.logger import get_logger
from src.utils.telemetry import emit_event, record_todo_operation, start_span

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

        with start_span(
            "todo.list",
            {"todo.page": page, "todo.page_size": page_size, "todo.skip": skip},
        ) as span:
            logger.info("list_todos | page=%d page_size=%d", page, page_size)
            items, total = self._repo.get_all(skip=skip, limit=page_size)
            total_pages = math.ceil(total / page_size) if total else 1
            span.set_attribute("todo.total", total)
            emit_event("todo.listed", {"todo.total": total, "todo.returned": len(items)})
            record_todo_operation("list", "success", {"todo.total": total})

            return PaginatedTodoResponse(
                items=[TodoResponse.model_validate(t) for t in items],
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
            )

    def get_todo(self, todo_id: UUID) -> TodoResponse:
        with start_span("todo.get", {"todo.id": str(todo_id)}) as span:
            logger.info("get_todo | id=%s", todo_id)
            todo = self._repo.get_by_id(todo_id)
            if not todo:
                logger.warning("get_todo | not found id=%s", todo_id)
                emit_event("todo.not_found", {"todo.id": str(todo_id), "todo.operation": "get"})
                record_todo_operation("get", "not_found")
                raise TodoNotFoundError(str(todo_id))

            span.set_attribute("todo.status", todo.status.value)
            emit_event("todo.found", {"todo.id": str(todo_id), "todo.status": todo.status.value})
            record_todo_operation("get", "success")
            return TodoResponse.model_validate(todo)

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    def create_todo(self, payload: TodoCreateRequest) -> TodoResponse:
        with start_span("todo.create", {"todo.priority": payload.priority.value}) as span:
            logger.info("create_todo | title=%r priority=%s", payload.title, payload.priority)
            todo = Todo(
                title=payload.title,
                description=payload.description,
                priority=payload.priority,
            )
            saved = self._repo.create(todo)
            span.set_attribute("todo.id", str(saved.id))
            span.set_attribute("todo.status", saved.status.value)
            emit_event(
                "todo.created",
                {"todo.id": str(saved.id), "todo.priority": saved.priority.value},
            )
            record_todo_operation("create", "success", {"todo.priority": saved.priority.value})
            logger.info("create_todo | created id=%s", saved.id)
            return TodoResponse.model_validate(saved)

    def update_todo(self, todo_id: UUID, payload: TodoUpdateRequest) -> TodoResponse:
        patch = payload.model_dump(exclude_none=True)
        with start_span(
            "todo.update",
            {"todo.id": str(todo_id), "todo.changed_fields": list(patch.keys())},
        ) as span:
            logger.info("update_todo | id=%s payload=%s", todo_id, patch)
            todo = self._repo.get_by_id(todo_id)
            if not todo:
                logger.warning("update_todo | not found id=%s", todo_id)
                emit_event("todo.not_found", {"todo.id": str(todo_id), "todo.operation": "update"})
                record_todo_operation("update", "not_found")
                raise TodoNotFoundError(str(todo_id))

            updated_data = todo.model_dump()
            for field, value in patch.items():
                updated_data[field] = value
            updated_data["updated_at"] = datetime.now(timezone.utc)

            updated_todo = Todo(**updated_data)
            saved = self._repo.update(updated_todo)
            span.set_attribute("todo.status", saved.status.value)
            emit_event(
                "todo.updated",
                {"todo.id": str(saved.id), "todo.changed_field_count": len(patch)},
            )
            record_todo_operation("update", "success", {"todo.changed_field_count": len(patch)})
            logger.info("update_todo | updated id=%s", saved.id)
            return TodoResponse.model_validate(saved)

    def delete_todo(self, todo_id: UUID) -> None:
        with start_span("todo.delete", {"todo.id": str(todo_id)}):
            logger.info("delete_todo | id=%s", todo_id)
            todo = self._repo.get_by_id(todo_id)
            if not todo:
                logger.warning("delete_todo | not found id=%s", todo_id)
                emit_event("todo.not_found", {"todo.id": str(todo_id), "todo.operation": "delete"})
                record_todo_operation("delete", "not_found")
                raise TodoNotFoundError(str(todo_id))
            self._repo.delete(todo_id)
            emit_event("todo.deleted", {"todo.id": str(todo_id)})
            record_todo_operation("delete", "success")
            logger.info("delete_todo | deleted id=%s", todo_id)

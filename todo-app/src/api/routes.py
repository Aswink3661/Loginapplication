from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.config.settings import Settings, get_settings
from src.exceptions import TodoNotFoundError
from src.models.todo import (
    PaginatedTodoResponse,
    TodoCreateRequest,
    TodoResponse,
    TodoUpdateRequest,
)
from src.repositories.todo_repository import InMemoryTodoRepository
from src.services.todo_service import TodoService
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/todos", tags=["Todos"])


# ---------------------------------------------------------------------------
# Dependency injection
# ---------------------------------------------------------------------------

_repository = InMemoryTodoRepository()


def get_todo_service(settings: Settings = Depends(get_settings)) -> TodoService:
    return TodoService(repository=_repository)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("", response_model=PaginatedTodoResponse, summary="List all todos")
def list_todos(
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    service: TodoService = Depends(get_todo_service),
) -> PaginatedTodoResponse:
    logger.debug("GET /todos page=%d page_size=%d", page, page_size)
    return service.list_todos(page=page, page_size=page_size)


@router.get("/{todo_id}", response_model=TodoResponse, summary="Get a todo by ID")
def get_todo(
    todo_id: UUID,
    service: TodoService = Depends(get_todo_service),
) -> TodoResponse:
    logger.debug("GET /todos/%s", todo_id)
    try:
        return service.get_todo(todo_id)
    except TodoNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED, summary="Create a todo")
def create_todo(
    payload: TodoCreateRequest,
    service: TodoService = Depends(get_todo_service),
) -> TodoResponse:
    logger.debug("POST /todos title=%r", payload.title)
    return service.create_todo(payload)


@router.patch("/{todo_id}", response_model=TodoResponse, summary="Partially update a todo")
def update_todo(
    todo_id: UUID,
    payload: TodoUpdateRequest,
    service: TodoService = Depends(get_todo_service),
) -> TodoResponse:
    logger.debug("PATCH /todos/%s", todo_id)
    try:
        return service.update_todo(todo_id, payload)
    except TodoNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a todo")
def delete_todo(
    todo_id: UUID,
    service: TodoService = Depends(get_todo_service),
) -> None:
    logger.debug("DELETE /todos/%s", todo_id)
    try:
        service.delete_todo(todo_id)
    except TodoNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from typing import List, Optional

from pydantic import BaseModel, Field


class TodoStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TodoPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# ---------------------------------------------------------------------------
# Persistence / domain model
# ---------------------------------------------------------------------------

class Todo(BaseModel):
    """Internal domain model — stored in the repository."""

    id: UUID = Field(default_factory=uuid4)
    title: str
    description: str = ""
    status: TodoStatus = TodoStatus.PENDING
    priority: TodoPriority = TodoPriority.MEDIUM
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# API request / response schemas
# ---------------------------------------------------------------------------

class TodoCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, examples=["Buy groceries"])
    description: str = Field(default="", max_length=1000)
    priority: TodoPriority = TodoPriority.MEDIUM


class TodoUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[TodoStatus] = None
    priority: Optional[TodoPriority] = None


class TodoResponse(BaseModel):
    id: UUID
    title: str
    description: str
    status: TodoStatus
    priority: TodoPriority
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedTodoResponse(BaseModel):
    items: List[TodoResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

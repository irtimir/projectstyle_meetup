from __future__ import annotations

from datetime import datetime

from app.api.schemas import BaseSchema
from app.core.tasks.models import TaskPriority, TaskStatus


class CreateTaskValidator(BaseSchema):
    title: str
    description: str | None = None
    project_id: int
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee_id: int | None = None


class UpdateTaskValidator(BaseSchema):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None


class AssignTaskValidator(BaseSchema):
    assignee_id: int | None


class TagShortSerializer(BaseSchema):
    id: int
    name: str
    color: str


class TaskSerializer(BaseSchema):
    id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    project_id: int
    assignee_id: int | None
    created_at: datetime
    completed_at: datetime | None
    tags: list[TagShortSerializer]


class TaskListSerializer(BaseSchema):
    id: int
    title: str
    status: TaskStatus
    priority: TaskPriority
    project_id: int
    assignee_id: int | None
    tags: list[TagShortSerializer]

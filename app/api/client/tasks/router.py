from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.client.tasks import schemas
from app.api.dependencies import CurrentUserRequired, DbSession, PaginationDep
from app.api.exceptions import BadRequestError, NotFoundError
from app.api.schemas import PaginatedResponse
from app.core.tasks.exceptions import TaskAlreadyCompletedError, TaskNotFoundError
from app.core.tasks.models import TaskPriority, TaskSort, TaskStatus
from app.core.tasks.services import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=PaginatedResponse[schemas.TaskListSerializer])
async def list_tasks_view(
    session: DbSession,
    pagination: PaginationDep,
    project_id: Annotated[int | None, Query()] = None,
    assignee_id: Annotated[int | None, Query()] = None,
    status_filter: Annotated[TaskStatus | None, Query(alias="status")] = None,
    priority: Annotated[TaskPriority | None, Query()] = None,
    search: Annotated[str | None, Query()] = None,
    sort: Annotated[list[TaskSort] | None, Query()] = None,
) -> PaginatedResponse[schemas.TaskListSerializer]:
    offset, limit = pagination
    service = TaskService(session)
    page = await service.get_list(
        offset=offset,
        limit=limit,
        project_id=project_id,
        assignee_id=assignee_id,
        status=status_filter,
        priority=priority,
        search=search,
        sort=sort,
    )
    return PaginatedResponse.from_page(page, schemas.TaskListSerializer)


@router.get("/{task_id}", response_model=schemas.TaskSerializer)
async def get_task_view(
    session: DbSession,
    task_id: int,
) -> schemas.TaskSerializer:
    service = TaskService(session)
    try:
        task = await service.get_by_id(task_id)
    except TaskNotFoundError as e:
        raise NotFoundError(code=e.code, message=e.message) from e
    return schemas.TaskSerializer.model_validate(task)


@router.post("", response_model=schemas.TaskSerializer, status_code=status.HTTP_201_CREATED)
async def create_task_view(
    session: DbSession,
    _user: CurrentUserRequired,
    data: schemas.CreateTaskValidator,
) -> schemas.TaskSerializer:
    service = TaskService(session)
    task = await service.create(
        title=data.title,
        project_id=data.project_id,
        description=data.description,
        priority=data.priority,
        assignee_id=data.assignee_id,
    )
    task = await service.get_by_id(task.id)
    return schemas.TaskSerializer.model_validate(task)


@router.patch("/{task_id}", response_model=schemas.TaskSerializer)
async def update_task_view(
    session: DbSession,
    _user: CurrentUserRequired,
    task_id: int,
    data: schemas.UpdateTaskValidator,
) -> schemas.TaskSerializer:
    service = TaskService(session)
    try:
        task = await service.update(
            task_id=task_id,
            title=data.title,
            description=data.description,
            status=data.status,
            priority=data.priority,
        )
    except TaskNotFoundError as e:
        raise NotFoundError(code=e.code, message=e.message) from e
    return schemas.TaskSerializer.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_view(
    session: DbSession,
    _user: CurrentUserRequired,
    task_id: int,
) -> None:
    service = TaskService(session)
    try:
        await service.delete(task_id)
    except TaskNotFoundError as e:
        raise NotFoundError(code=e.code, message=e.message) from e


@router.post("/{task_id}/assign", response_model=schemas.TaskSerializer)
async def assign_task_view(
    session: DbSession,
    _user: CurrentUserRequired,
    task_id: int,
    data: schemas.AssignTaskValidator,
) -> schemas.TaskSerializer:
    service = TaskService(session)
    try:
        task = await service.assign(task_id, data.assignee_id)
    except TaskNotFoundError as e:
        raise NotFoundError(code=e.code, message=e.message) from e
    return schemas.TaskSerializer.model_validate(task)


@router.post("/{task_id}/complete", response_model=schemas.TaskSerializer)
async def complete_task_view(
    session: DbSession,
    _user: CurrentUserRequired,
    task_id: int,
) -> schemas.TaskSerializer:
    service = TaskService(session)
    try:
        task = await service.complete(task_id)
    except TaskNotFoundError as e:
        raise NotFoundError(code=e.code, message=e.message) from e
    except TaskAlreadyCompletedError as e:
        raise BadRequestError(code=e.code, message=e.message) from e
    return schemas.TaskSerializer.model_validate(task)

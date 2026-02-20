from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.client.projects import schemas
from app.api.client.tasks import schemas as task_schemas
from app.api.dependencies import CurrentUser, DbSession, GetAccessContext, LimitOffetPagination
from app.api.exceptions import ForbiddenError, NotFoundError
from app.api.schemas import PaginatedResponse
from app.common.rules import is_owner
from app.core.projects.exceptions import ProjectNotFoundError
from app.core.projects.services import ProjectService
from app.core.tasks.services import TaskService
from app.extensions import guard

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=PaginatedResponse[schemas.ProjectListSerializer])
async def list_projects_view(
    session: DbSession,
    pagination: LimitOffetPagination,
    owner_id: Annotated[int | None, Query()] = None,
) -> PaginatedResponse[schemas.ProjectListSerializer]:
    offset, limit = pagination
    service = ProjectService(session)
    page = await service.get_list(offset=offset, limit=limit, owner_id=owner_id)
    return PaginatedResponse.from_page(page, schemas.ProjectListSerializer)


@router.get("/{project_id}", response_model=schemas.ProjectSerializer)
async def get_project_view(
    session: DbSession,
    project_id: int,
) -> schemas.ProjectSerializer:
    service = ProjectService(session)
    try:
        project = await service.get_by_id(project_id)
    except ProjectNotFoundError as e:
        raise NotFoundError(code=e.code, message=e.message) from e
    return schemas.ProjectSerializer.model_validate(project)


@router.get("/{project_id}/tasks", response_model=PaginatedResponse[task_schemas.TaskListSerializer])
async def get_project_tasks_view(
    session: DbSession,
    project_id: int,
    pagination: LimitOffetPagination,
) -> PaginatedResponse[task_schemas.TaskListSerializer]:
    project_service = ProjectService(session)
    try:
        await project_service.get_by_id(project_id)
    except ProjectNotFoundError as e:
        raise NotFoundError(code=e.code, message=e.message) from e

    offset, limit = pagination
    task_service = TaskService(session)
    page = await task_service.get_by_project(project_id, offset=offset, limit=limit)
    return PaginatedResponse.from_page(page, task_schemas.TaskListSerializer)


@router.post("", response_model=schemas.ProjectSerializer, status_code=status.HTTP_201_CREATED)
async def create_project_view(
    session: DbSession,
    user: CurrentUser,
    data: schemas.CreateProjectValidator,
) -> schemas.ProjectSerializer:
    service = ProjectService(session)
    project = await service.create(
        name=data.name,
        owner_id=user.id,
        description=data.description,
    )
    return schemas.ProjectSerializer.model_validate(project)


@router.patch("/{project_id}", response_model=schemas.ProjectSerializer)
async def update_project_view(
    session: DbSession,
    ctx: GetAccessContext,
    project_id: int,
    data: schemas.UpdateProjectValidator,
) -> schemas.ProjectSerializer:
    service = ProjectService(session)
    try:
        project = await service.get_by_id(project_id)
    except ProjectNotFoundError as e:
        raise NotFoundError(code=e.code, message=e.message) from e

    if not await guard.check(ctx, is_owner, project):
        raise ForbiddenError()

    project = await service.update(
        project_id=project_id,
        name=data.name,
        description=data.description,
    )
    return schemas.ProjectSerializer.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_view(
    session: DbSession,
    ctx: GetAccessContext,
    project_id: int,
) -> None:
    service = ProjectService(session)
    try:
        project = await service.get_by_id(project_id)
    except ProjectNotFoundError as e:
        raise NotFoundError(code=e.code, message=e.message) from e

    if not await guard.check(ctx, is_owner, project):
        raise ForbiddenError()

    await service.delete(project_id)

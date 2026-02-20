from __future__ import annotations

from fastapi import APIRouter, status

from app.api.client.comments import schemas
from app.api.dependencies import CurrentUser, DbSession, GetAccessContext, LimitOffetPagination
from app.api.exceptions import ForbiddenError, NotFoundError
from app.api.schemas import PaginatedResponse
from app.common.rules import is_owner
from app.core.comments.services import CommentNotFoundError, CommentService
from app.core.tasks.exceptions import TaskNotFoundError
from app.core.tasks.services import TaskService
from app.extensions import guard

router = APIRouter(tags=["comments"])


@router.get("/tasks/{task_id}/comments", response_model=PaginatedResponse[schemas.CommentListSerializer])
async def list_task_comments_view(
    session: DbSession,
    task_id: int,
    pagination: LimitOffetPagination,
) -> PaginatedResponse[schemas.CommentListSerializer]:
    task_service = TaskService(session)
    try:
        await task_service.get_by_id(task_id)
    except TaskNotFoundError as e:
        raise NotFoundError(code=e.code, message=e.message) from e

    offset, limit = pagination
    comment_service = CommentService(session)
    page = await comment_service.get_by_task(task_id, offset=offset, limit=limit)
    return PaginatedResponse.from_page(page, schemas.CommentListSerializer)


@router.post("/tasks/{task_id}/comments", response_model=schemas.CommentSerializer, status_code=status.HTTP_201_CREATED)
async def create_comment_view(
    session: DbSession,
    user: CurrentUser,
    task_id: int,
    data: schemas.CreateCommentValidator,
) -> schemas.CommentSerializer:
    task_service = TaskService(session)
    try:
        await task_service.get_by_id(task_id)
    except TaskNotFoundError as e:
        raise NotFoundError(code=e.code, message=e.message) from e

    comment_service = CommentService(session)
    comment = await comment_service.create(
        task_id=task_id,
        author_id=user.id,
        content=data.content,
    )
    return schemas.CommentSerializer.model_validate(comment)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment_view(
    session: DbSession,
    ctx: GetAccessContext,
    comment_id: int,
) -> None:
    comment_service = CommentService(session)
    try:
        comment = await comment_service.get_by_id(comment_id)
    except CommentNotFoundError as e:
        raise NotFoundError(code=e.code, message=e.message) from e

    if not await guard.check(ctx, is_owner, comment):
        raise ForbiddenError()

    await comment_service.delete(comment_id)

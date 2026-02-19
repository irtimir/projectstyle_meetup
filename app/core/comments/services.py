from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.exceptions import TaskManagerError
from app.common.pagination import Page, Paginator
from app.core.comments.models import Comment
from app.error_codes import ErrorCodes


class CommentNotFoundError(TaskManagerError):
    code = ErrorCodes.COMMENT_NOT_FOUND
    message = "Comment not found"


class CommentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_task(
        self,
        task_id: int,
        offset: int = 0,
        limit: int = 50,
    ) -> Page[Comment]:
        query = (
            select(Comment)
            .where(Comment.task_id == task_id)
            .options(selectinload(Comment.author))
            .order_by(Comment.created_at.desc())
        )
        return await Paginator(self.session, query).get_page(offset, limit)

    async def get_by_id(self, comment_id: int) -> Comment:
        result = await self.session.execute(
            select(Comment).where(Comment.id == comment_id).options(selectinload(Comment.author))
        )
        comment = result.scalar_one_or_none()
        if not comment:
            raise CommentNotFoundError()
        return comment

    async def create(self, task_id: int, author_id: int, content: str) -> Comment:
        comment = Comment(task_id=task_id, author_id=author_id, content=content)
        self.session.add(comment)
        await self.session.flush()
        return await self.get_by_id(comment.id)

    async def delete(self, comment_id: int) -> None:
        comment = await self.get_by_id(comment_id)
        await self.session.delete(comment)
        await self.session.flush()

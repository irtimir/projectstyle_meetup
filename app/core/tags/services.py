from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import TaskManagerError
from app.common.pagination import Page, Paginator
from app.core.tags.models import Tag
from app.error_codes import ErrorCodes


class TagNotFoundError(TaskManagerError):
    error = ErrorCodes.TAG_NOT_FOUND


class TagNameExistsError(TaskManagerError):
    error = ErrorCodes.TAG_NAME_EXISTS


class TagService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_list(
        self,
        offset: int = 0,
        limit: int = 50,
    ) -> Page[Tag]:
        query = select(Tag).order_by(Tag.name)
        return await Paginator(self.session, query).get_page(offset, limit)

    async def get_by_id(self, tag_id: int) -> Tag:
        tag = await self.session.get(Tag, tag_id)
        if not tag:
            raise TagNotFoundError()
        return tag

    async def create(self, name: str, color: str = "#6366f1") -> Tag:
        tag = Tag(name=name, color=color)
        self.session.add(tag)
        try:
            await self.session.flush()
        except IntegrityError as e:
            await self.session.rollback()
            if "name" in str(e).lower():
                raise TagNameExistsError() from e
            raise
        return tag

    async def delete(self, tag_id: int) -> None:
        tag = await self.get_by_id(tag_id)
        await self.session.delete(tag)
        await self.session.flush()

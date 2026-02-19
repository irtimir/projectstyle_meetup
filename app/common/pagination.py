from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlalchemy import Select, func, select

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class Page[T]:
    items: list[T]
    total: int
    offset: int
    limit: int

    @property
    def has_next(self) -> bool:
        return self.offset + self.limit < self.total

    @property
    def has_prev(self) -> bool:
        return self.offset > 0


class Paginator[T]:
    def __init__(self, session: AsyncSession, query: Select[tuple[T]]) -> None:
        self.session = session
        self.query = query

    async def get_page(self, offset: int = 0, limit: int = 20) -> Page[T]:
        count_query = select(func.count()).select_from(self.query.subquery())
        total = await self.session.scalar(count_query) or 0

        paginated_query = self.query.offset(offset).limit(limit)
        result = await self.session.execute(paginated_query)
        items = list(result.scalars().all())

        return Page(items=items, total=total, offset=offset, limit=limit)

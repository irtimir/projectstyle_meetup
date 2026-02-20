from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.exceptions import UnauthorizedError
from app.common.guard import AccessContext
from app.core.users.models import User
from app.extensions import db


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with db.session() as session:
        yield session


DbSession = Annotated[AsyncSession, Depends(get_db_session)]


async def maybe_get_current_user(
    session: DbSession,
    x_user_id: Annotated[int | None, Header()] = None,
) -> User | None:
    if x_user_id is None:
        return None
    user = await session.get(User, x_user_id)
    return user


MaybeCurrentUser = Annotated[User | None, Depends(maybe_get_current_user)]


async def get_current_user(user: MaybeCurrentUser) -> User:
    if user is None:
        raise UnauthorizedError()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_access_context(user: MaybeCurrentUser) -> AccessContext:
    return AccessContext(user=user)  # type: ignore[arg-type]


GetAccessContext = Annotated[AccessContext, Depends(get_access_context)]


def limit_offset_pagination_params(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> tuple[int, int]:
    return offset, limit


LimitOffetPagination = Annotated[tuple[int, int], Depends(limit_offset_pagination_params)]

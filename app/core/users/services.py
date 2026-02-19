from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination import Page, Paginator
from app.core.users.exceptions import UserEmailExistsError, UserNotFoundError
from app.core.users.models import User


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_list(
        self,
        offset: int = 0,
        limit: int = 20,
        search: str | None = None,
    ) -> Page[User]:
        query = select(User).order_by(User.id)

        if search:
            query = query.where(User.name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%"))

        return await Paginator(self.session, query).get_page(offset, limit)

    async def get_by_id(self, user_id: int) -> User:
        user = await self.session.get(User, user_id)
        if not user:
            raise UserNotFoundError()
        return user

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, email: str, name: str) -> User:
        user = User(email=email, name=name)
        self.session.add(user)
        try:
            await self.session.flush()
        except IntegrityError as e:
            await self.session.rollback()
            if "email" in str(e):
                raise UserEmailExistsError() from e
            raise
        return user

    async def update(self, user_id: int, email: str | None = None, name: str | None = None) -> User:
        user = await self.get_by_id(user_id)
        if email is not None:
            user.email = email
        if name is not None:
            user.name = name
        try:
            await self.session.flush()
        except IntegrityError as e:
            await self.session.rollback()
            if "email" in str(e):
                raise UserEmailExistsError() from e
            raise
        return user

    async def delete(self, user_id: int) -> None:
        user = await self.get_by_id(user_id)
        await self.session.delete(user)
        await self.session.flush()

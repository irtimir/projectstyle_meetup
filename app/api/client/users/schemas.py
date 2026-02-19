from __future__ import annotations

from datetime import datetime

from pydantic import EmailStr

from app.api.schemas import BaseSchema


class CreateUserValidator(BaseSchema):
    email: EmailStr
    name: str


class UpdateUserValidator(BaseSchema):
    email: EmailStr | None = None
    name: str | None = None


class UserSerializer(BaseSchema):
    id: int
    email: str
    name: str
    created_at: datetime


class UserListSerializer(BaseSchema):
    id: int
    email: str
    name: str

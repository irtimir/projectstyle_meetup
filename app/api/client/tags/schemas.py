from __future__ import annotations

from app.api.schemas import BaseSchema


class CreateTagValidator(BaseSchema):
    name: str
    color: str = "#6366f1"


class TagSerializer(BaseSchema):
    id: int
    name: str
    color: str


class TagListSerializer(BaseSchema):
    id: int
    name: str
    color: str

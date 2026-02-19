from __future__ import annotations

from datetime import datetime

from app.api.schemas import BaseSchema


class CreateProjectValidator(BaseSchema):
    name: str
    description: str | None = None


class UpdateProjectValidator(BaseSchema):
    name: str | None = None
    description: str | None = None


class ProjectSerializer(BaseSchema):
    id: int
    name: str
    description: str | None
    owner_id: int
    created_at: datetime


class ProjectListSerializer(BaseSchema):
    id: int
    name: str
    description: str | None
    owner_id: int

from __future__ import annotations

from datetime import datetime

from app.api.schemas import BaseSchema


class CreateCommentValidator(BaseSchema):
    content: str


class CommentAuthorSerializer(BaseSchema):
    id: int
    name: str


class CommentSerializer(BaseSchema):
    id: int
    content: str
    task_id: int
    author_id: int
    author: CommentAuthorSerializer
    created_at: datetime


class CommentListSerializer(BaseSchema):
    id: int
    content: str
    author_id: int
    author: CommentAuthorSerializer
    created_at: datetime

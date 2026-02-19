from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.database import Base

if TYPE_CHECKING:
    from app.core.comments.models import Comment
    from app.core.projects.models import Project
    from app.core.tags.models import Tag
    from app.core.users.models import User


class TaskStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskSort(StrEnum):
    TITLE = "title"
    TITLE_DESC = "-title"
    STATUS = "status"
    STATUS_DESC = "-status"
    PRIORITY = "priority"
    PRIORITY_DESC = "-priority"
    CREATED_AT = "created_at"
    CREATED_AT_DESC = "-created_at"
    COMPLETED_AT = "completed_at"
    COMPLETED_AT_DESC = "-completed_at"


task_tags = Base.metadata.tables.get("task_tags")
if task_tags is None:
    task_tags = Table(
        "task_tags",
        Base.metadata,
        Column("task_id", Integer, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
        Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(String(50), default=TaskStatus.PENDING)
    priority: Mapped[TaskPriority] = mapped_column(String(50), default=TaskPriority.MEDIUM)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    project: Mapped[Project] = relationship(back_populates="tasks")
    assignee: Mapped[User | None] = relationship(
        back_populates="assigned_tasks",
        foreign_keys=[assignee_id],
    )
    comments: Mapped[list[Comment]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
    )
    tags: Mapped[list[Tag]] = relationship(
        secondary=task_tags,
        back_populates="tasks",
    )

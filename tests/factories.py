from __future__ import annotations

from typing import TYPE_CHECKING

from factory.base import Factory
from factory.declarations import LazyAttribute, Sequence

from app.core.comments.models import Comment
from app.core.projects.models import Project
from app.core.tags.models import Tag
from app.core.tasks.models import Task, TaskPriority, TaskStatus
from app.core.users.models import User

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class AsyncFactory[T](Factory):
    @classmethod
    async def create_async(cls, session: AsyncSession, **kwargs) -> T:
        obj = cls.build(**kwargs)
        session.add(obj)
        await session.flush()
        await session.refresh(obj)
        return obj


class UserFactory(AsyncFactory[User]):
    class Meta:  # type: ignore[override]
        model = User

    email = Sequence(lambda n: f"user{n}@example.com")
    name = Sequence(lambda n: f"User {n}")


class ProjectFactory(AsyncFactory[Project]):
    class Meta:  # type: ignore[override]
        model = Project

    name = Sequence(lambda n: f"Project {n}")
    description = LazyAttribute(lambda o: f"Description for {o.name}")
    owner_id = None

    @classmethod
    async def create_async(cls, session: AsyncSession, owner: User | None = None, **kwargs) -> Project:
        if owner:
            kwargs["owner_id"] = owner.id
        return await super().create_async(session, **kwargs)


class TaskFactory(AsyncFactory[Task]):
    class Meta:  # type: ignore[override]
        model = Task

    title = Sequence(lambda n: f"Task {n}")
    description = None
    status = TaskStatus.PENDING
    priority = TaskPriority.MEDIUM
    project_id = None
    assignee_id = None

    @classmethod
    async def create_async(
        cls,
        session: AsyncSession,
        project: Project | None = None,
        assignee: User | None = None,
        **kwargs,
    ) -> Task:
        if project:
            kwargs["project_id"] = project.id
        if assignee:
            kwargs["assignee_id"] = assignee.id
        return await super().create_async(session, **kwargs)


class TagFactory(AsyncFactory[Tag]):
    class Meta:  # type: ignore[override]
        model = Tag

    name = Sequence(lambda n: f"tag-{n}")
    color = "#6366f1"


class CommentFactory(AsyncFactory[Comment]):
    class Meta:  # type: ignore[override]
        model = Comment

    content = Sequence(lambda n: f"Comment {n}")
    task_id = None
    author_id = None

    @classmethod
    async def create_async(
        cls,
        session: AsyncSession,
        task: Task | None = None,
        author: User | None = None,
        **kwargs,
    ) -> Comment:
        if task:
            kwargs["task_id"] = task.id
        if author:
            kwargs["author_id"] = author.id
        return await super().create_async(session, **kwargs)

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.pagination import Page, Paginator
from app.core.tasks.exceptions import TaskAlreadyCompletedError, TaskNotFoundError
from app.core.tasks.models import Task, TaskPriority, TaskSort, TaskStatus


class TaskService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_list(
        self,
        offset: int = 0,
        limit: int = 20,
        project_id: int | None = None,
        assignee_id: int | None = None,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        search: str | None = None,
        sort: list[TaskSort] | None = None,
    ) -> Page[Task]:
        query = select(Task).options(selectinload(Task.tags))

        if project_id is not None:
            query = query.where(Task.project_id == project_id)
        if assignee_id is not None:
            query = query.where(Task.assignee_id == assignee_id)
        if status is not None:
            query = query.where(Task.status == status)
        if priority is not None:
            query = query.where(Task.priority == priority)
        if search:
            query = query.where(Task.title.ilike(f"%{search}%"))

        sort_mapping = {
            TaskSort.TITLE: Task.title.asc(),
            TaskSort.TITLE_DESC: Task.title.desc(),
            TaskSort.STATUS: Task.status.asc(),
            TaskSort.STATUS_DESC: Task.status.desc(),
            TaskSort.PRIORITY: Task.priority.asc(),
            TaskSort.PRIORITY_DESC: Task.priority.desc(),
            TaskSort.CREATED_AT: Task.created_at.asc(),
            TaskSort.CREATED_AT_DESC: Task.created_at.desc(),
            TaskSort.COMPLETED_AT: Task.completed_at.asc(),
            TaskSort.COMPLETED_AT_DESC: Task.completed_at.desc(),
        }
        for field in sort or [TaskSort.CREATED_AT_DESC]:
            query = query.order_by(sort_mapping[field])

        return await Paginator(self.session, query).get_page(offset, limit)

    async def get_by_id(self, task_id: int) -> Task:
        result = await self.session.execute(select(Task).where(Task.id == task_id).options(selectinload(Task.tags)))
        task = result.scalar_one_or_none()
        if not task:
            raise TaskNotFoundError()
        return task

    async def create(
        self,
        title: str,
        project_id: int,
        description: str | None = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        assignee_id: int | None = None,
    ) -> Task:
        task = Task(
            title=title,
            project_id=project_id,
            description=description,
            priority=priority,
            assignee_id=assignee_id,
        )
        self.session.add(task)
        await self.session.flush()
        return task

    async def update(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
    ) -> Task:
        task = await self.get_by_id(task_id)
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if status is not None:
            task.status = status
        if priority is not None:
            task.priority = priority
        await self.session.flush()
        return task

    async def delete(self, task_id: int) -> None:
        task = await self.get_by_id(task_id)
        await self.session.delete(task)
        await self.session.flush()

    async def assign(self, task_id: int, assignee_id: int | None) -> Task:
        task = await self.get_by_id(task_id)
        task.assignee_id = assignee_id
        if task.status == TaskStatus.PENDING and assignee_id is not None:
            task.status = TaskStatus.IN_PROGRESS
        await self.session.flush()
        return task

    async def complete(self, task_id: int) -> Task:
        task = await self.get_by_id(task_id)
        if task.status == TaskStatus.COMPLETED:
            raise TaskAlreadyCompletedError()
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now(UTC)
        await self.session.flush()
        return task

    async def get_by_project(
        self,
        project_id: int,
        offset: int = 0,
        limit: int = 20,
    ) -> Page[Task]:
        return await self.get_list(offset=offset, limit=limit, project_id=project_id)

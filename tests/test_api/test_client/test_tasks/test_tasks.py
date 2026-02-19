from httpx import AsyncClient

from app.core.tasks.models import TaskPriority, TaskStatus
from app.error_codes import ErrorCodes
from tests.factories import ProjectFactory, TaskFactory, UserFactory


class TestListTasks:
    async def test_list_tasks_empty(self, client: AsyncClient):
        response = await client.get("/api/tasks")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["data"] == []

    async def test_list_tasks_with_data(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        project = await ProjectFactory.create_async(session, owner=user)
        await TaskFactory.create_async(session, project=project)
        await TaskFactory.create_async(session, project=project)
        await session.commit()

        response = await client.get("/api/tasks")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    async def test_list_tasks_filter_by_status(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        project = await ProjectFactory.create_async(session, owner=user)
        await TaskFactory.create_async(session, project=project, status=TaskStatus.PENDING)
        await TaskFactory.create_async(session, project=project, status=TaskStatus.COMPLETED)
        await session.commit()

        response = await client.get("/api/tasks", params={"status": "pending"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["data"][0]["status"] == "pending"

    async def test_list_tasks_filter_by_priority(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        project = await ProjectFactory.create_async(session, owner=user)
        await TaskFactory.create_async(session, project=project, priority=TaskPriority.HIGH)
        await TaskFactory.create_async(session, project=project, priority=TaskPriority.LOW)
        await session.commit()

        response = await client.get("/api/tasks", params={"priority": "high"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["data"][0]["priority"] == "high"

    async def test_list_tasks_search(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        project = await ProjectFactory.create_async(session, owner=user)
        await TaskFactory.create_async(session, project=project, title="Fix bug")
        await TaskFactory.create_async(session, project=project, title="Add feature")
        await session.commit()

        response = await client.get("/api/tasks", params={"search": "bug"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert "bug" in data["data"][0]["title"].lower()

    async def test_list_tasks_sorting(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        project = await ProjectFactory.create_async(session, owner=user)
        await TaskFactory.create_async(session, project=project, title="B Task")
        await TaskFactory.create_async(session, project=project, title="A Task")
        await session.commit()

        response = await client.get("/api/tasks", params={"sort": "title"})
        assert response.status_code == 200
        data = response.json()
        assert data["data"][0]["title"] == "A Task"


class TestGetTask:
    async def test_get_task_success(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        project = await ProjectFactory.create_async(session, owner=user)
        task = await TaskFactory.create_async(session, project=project, title="My Task")
        await session.commit()

        response = await client.get(f"/api/tasks/{task.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task.id
        assert data["title"] == "My Task"

    async def test_get_task_not_found(self, client: AsyncClient):
        response = await client.get("/api/tasks/999")
        assert response.status_code == 404
        data = response.json()
        assert data["code"] == ErrorCodes.TASK_NOT_FOUND


class TestCreateTask:
    async def test_create_task_success(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        project = await ProjectFactory.create_async(session, owner=user)
        await session.commit()

        response = await client.post(
            "/api/tasks",
            json={
                "title": "New Task",
                "project_id": project.id,
                "priority": "high",
            },
            headers={"X-User-Id": str(user.id)},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Task"
        assert data["priority"] == "high"
        assert data["status"] == "pending"

    async def test_create_task_unauthorized(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        project = await ProjectFactory.create_async(session, owner=user)
        await session.commit()

        response = await client.post(
            "/api/tasks",
            json={"title": "Task", "project_id": project.id},
        )
        assert response.status_code == 401


class TestUpdateTask:
    async def test_update_task_success(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        project = await ProjectFactory.create_async(session, owner=user)
        task = await TaskFactory.create_async(session, project=project)
        await session.commit()

        response = await client.patch(
            f"/api/tasks/{task.id}",
            json={"title": "Updated Title", "status": "in_progress"},
            headers={"X-User-Id": str(user.id)},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["status"] == "in_progress"

    async def test_update_task_not_found(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        await session.commit()

        response = await client.patch(
            "/api/tasks/999",
            json={"title": "Title"},
            headers={"X-User-Id": str(user.id)},
        )
        assert response.status_code == 404


class TestDeleteTask:
    async def test_delete_task_success(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        project = await ProjectFactory.create_async(session, owner=user)
        task = await TaskFactory.create_async(session, project=project)
        await session.commit()

        response = await client.delete(
            f"/api/tasks/{task.id}",
            headers={"X-User-Id": str(user.id)},
        )
        assert response.status_code == 204


class TestAssignTask:
    async def test_assign_task_success(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        assignee = await UserFactory.create_async(session)
        project = await ProjectFactory.create_async(session, owner=user)
        task = await TaskFactory.create_async(session, project=project)
        await session.commit()

        response = await client.post(
            f"/api/tasks/{task.id}/assign",
            json={"assignee_id": assignee.id},
            headers={"X-User-Id": str(user.id)},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["assignee_id"] == assignee.id
        assert data["status"] == "in_progress"

    async def test_unassign_task(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        project = await ProjectFactory.create_async(session, owner=user)
        task = await TaskFactory.create_async(session, project=project, assignee=user)
        await session.commit()

        response = await client.post(
            f"/api/tasks/{task.id}/assign",
            json={"assignee_id": None},
            headers={"X-User-Id": str(user.id)},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["assignee_id"] is None


class TestCompleteTask:
    async def test_complete_task_success(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        project = await ProjectFactory.create_async(session, owner=user)
        task = await TaskFactory.create_async(session, project=project, status=TaskStatus.IN_PROGRESS)
        await session.commit()

        response = await client.post(
            f"/api/tasks/{task.id}/complete",
            headers={"X-User-Id": str(user.id)},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["completed_at"] is not None

    async def test_complete_task_already_completed(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        project = await ProjectFactory.create_async(session, owner=user)
        task = await TaskFactory.create_async(session, project=project, status=TaskStatus.COMPLETED)
        await session.commit()

        response = await client.post(
            f"/api/tasks/{task.id}/complete",
            headers={"X-User-Id": str(user.id)},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["code"] == ErrorCodes.TASK_ALREADY_COMPLETED

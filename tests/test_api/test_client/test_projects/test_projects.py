from httpx import AsyncClient

from app.error_codes import ErrorCodes
from tests.factories import ProjectFactory, TaskFactory, UserFactory


class TestListProjects:
    async def test_list_projects_empty(self, client: AsyncClient):
        response = await client.get("/api/projects")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["data"] == []

    async def test_list_projects_with_data(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        await ProjectFactory.create_async(session, owner=user)
        await ProjectFactory.create_async(session, owner=user)
        await session.commit()

        response = await client.get("/api/projects")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    async def test_list_projects_filter_by_owner(self, client: AsyncClient, session):
        user1 = await UserFactory.create_async(session)
        user2 = await UserFactory.create_async(session)
        await ProjectFactory.create_async(session, owner=user1)
        await ProjectFactory.create_async(session, owner=user2)
        await session.commit()

        response = await client.get("/api/projects", params={"owner_id": user1.id})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["data"][0]["owner_id"] == user1.id


class TestGetProject:
    async def test_get_project_success(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        project = await ProjectFactory.create_async(session, owner=user, name="My Project")
        await session.commit()

        response = await client.get(f"/api/projects/{project.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project.id
        assert data["name"] == "My Project"

    async def test_get_project_not_found(self, client: AsyncClient):
        response = await client.get("/api/projects/999")
        assert response.status_code == 404
        data = response.json()
        assert data["code"] == ErrorCodes.PROJECT_NOT_FOUND


class TestGetProjectTasks:
    async def test_get_project_tasks_success(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        project = await ProjectFactory.create_async(session, owner=user)
        await TaskFactory.create_async(session, project=project, title="Task 1")
        await TaskFactory.create_async(session, project=project, title="Task 2")
        await session.commit()

        response = await client.get(f"/api/projects/{project.id}/tasks")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    async def test_get_project_tasks_not_found(self, client: AsyncClient):
        response = await client.get("/api/projects/999/tasks")
        assert response.status_code == 404
        data = response.json()
        assert data["code"] == ErrorCodes.PROJECT_NOT_FOUND


class TestCreateProject:
    async def test_create_project_success(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        await session.commit()

        response = await client.post(
            "/api/projects",
            json={"name": "New Project", "description": "A test project"},
            headers={"X-User-Id": str(user.id)},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Project"
        assert data["owner_id"] == user.id

    async def test_create_project_unauthorized(self, client: AsyncClient):
        response = await client.post(
            "/api/projects",
            json={"name": "New Project"},
        )
        assert response.status_code == 401
        data = response.json()
        assert data["code"] == ErrorCodes.UNAUTHORIZED


class TestUpdateProject:
    async def test_update_project_success(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        project = await ProjectFactory.create_async(session, owner=user)
        await session.commit()

        response = await client.patch(
            f"/api/projects/{project.id}",
            json={"name": "Updated Name"},
            headers={"X-User-Id": str(user.id)},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    async def test_update_project_forbidden(self, client: AsyncClient, session):
        owner = await UserFactory.create_async(session)
        other_user = await UserFactory.create_async(session)
        project = await ProjectFactory.create_async(session, owner=owner)
        await session.commit()

        response = await client.patch(
            f"/api/projects/{project.id}",
            json={"name": "Hacked"},
            headers={"X-User-Id": str(other_user.id)},
        )
        assert response.status_code == 403
        data = response.json()
        assert data["code"] == ErrorCodes.FORBIDDEN

    async def test_update_project_not_found(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        await session.commit()

        response = await client.patch(
            "/api/projects/999",
            json={"name": "Name"},
            headers={"X-User-Id": str(user.id)},
        )
        assert response.status_code == 404


class TestDeleteProject:
    async def test_delete_project_success(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        project = await ProjectFactory.create_async(session, owner=user)
        await session.commit()

        response = await client.delete(
            f"/api/projects/{project.id}",
            headers={"X-User-Id": str(user.id)},
        )
        assert response.status_code == 204

    async def test_delete_project_forbidden(self, client: AsyncClient, session):
        owner = await UserFactory.create_async(session)
        other_user = await UserFactory.create_async(session)
        project = await ProjectFactory.create_async(session, owner=owner)
        await session.commit()

        response = await client.delete(
            f"/api/projects/{project.id}",
            headers={"X-User-Id": str(other_user.id)},
        )
        assert response.status_code == 403
        data = response.json()
        assert data["code"] == ErrorCodes.FORBIDDEN

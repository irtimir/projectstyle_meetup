from httpx import AsyncClient

from app.error_codes import ErrorCodes
from tests.factories import CommentFactory, ProjectFactory, TaskFactory, UserFactory


class TestListTaskComments:
    async def test_list_comments_empty(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        project = await ProjectFactory.create_async(session, owner=user)
        task = await TaskFactory.create_async(session, project=project)
        await session.commit()

        response = await client.get(f"/api/tasks/{task.id}/comments")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["data"] == []

    async def test_list_comments_with_data(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        project = await ProjectFactory.create_async(session, owner=user)
        task = await TaskFactory.create_async(session, project=project)
        await CommentFactory.create_async(session, task=task, author=user, content="First comment")
        await CommentFactory.create_async(session, task=task, author=user, content="Second comment")
        await session.commit()

        response = await client.get(f"/api/tasks/{task.id}/comments")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    async def test_list_comments_task_not_found(self, client: AsyncClient):
        response = await client.get("/api/tasks/999/comments")
        assert response.status_code == 404
        data = response.json()
        assert data["code"] == ErrorCodes.TASK_NOT_FOUND.code_id


class TestCreateComment:
    async def test_create_comment_success(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        project = await ProjectFactory.create_async(session, owner=user)
        task = await TaskFactory.create_async(session, project=project)
        await session.commit()

        response = await client.post(
            f"/api/tasks/{task.id}/comments",
            json={"content": "This is a comment"},
            headers={"X-User-Id": str(user.id)},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "This is a comment"
        assert data["author_id"] == user.id
        assert data["task_id"] == task.id
        assert "author" in data
        assert data["author"]["id"] == user.id

    async def test_create_comment_unauthorized(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        project = await ProjectFactory.create_async(session, owner=user)
        task = await TaskFactory.create_async(session, project=project)
        await session.commit()

        response = await client.post(
            f"/api/tasks/{task.id}/comments",
            json={"content": "Comment"},
        )
        assert response.status_code == 401

    async def test_create_comment_task_not_found(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        await session.commit()

        response = await client.post(
            "/api/tasks/999/comments",
            json={"content": "Comment"},
            headers={"X-User-Id": str(user.id)},
        )
        assert response.status_code == 404
        data = response.json()
        assert data["code"] == ErrorCodes.TASK_NOT_FOUND.code_id


class TestDeleteComment:
    async def test_delete_comment_success(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        project = await ProjectFactory.create_async(session, owner=user)
        task = await TaskFactory.create_async(session, project=project)
        comment = await CommentFactory.create_async(session, task=task, author=user)
        await session.commit()

        response = await client.delete(
            f"/api/comments/{comment.id}",
            headers={"X-User-Id": str(user.id)},
        )
        assert response.status_code == 204

    async def test_delete_comment_forbidden(self, client: AsyncClient, session):
        author = await UserFactory.create_async(session)
        other_user = await UserFactory.create_async(session)
        project = await ProjectFactory.create_async(session, owner=author)
        task = await TaskFactory.create_async(session, project=project)
        comment = await CommentFactory.create_async(session, task=task, author=author)
        await session.commit()

        response = await client.delete(
            f"/api/comments/{comment.id}",
            headers={"X-User-Id": str(other_user.id)},
        )
        assert response.status_code == 403
        data = response.json()
        assert data["code"] == ErrorCodes.FORBIDDEN.code_id

    async def test_delete_comment_not_found(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        await session.commit()

        response = await client.delete(
            "/api/comments/999",
            headers={"X-User-Id": str(user.id)},
        )
        assert response.status_code == 404
        data = response.json()
        assert data["code"] == ErrorCodes.COMMENT_NOT_FOUND.code_id

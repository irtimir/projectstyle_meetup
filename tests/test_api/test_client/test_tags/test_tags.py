from httpx import AsyncClient

from app.error_codes import ErrorCodes
from tests.factories import TagFactory, UserFactory


class TestListTags:
    async def test_list_tags_empty(self, client: AsyncClient):
        response = await client.get("/api/tags")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["data"] == []

    async def test_list_tags_with_data(self, client: AsyncClient, session):
        await TagFactory.create_async(session, name="bug")
        await TagFactory.create_async(session, name="feature")
        await session.commit()

        response = await client.get("/api/tags")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2


class TestCreateTag:
    async def test_create_tag_success(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        await session.commit()

        response = await client.post(
            "/api/tags",
            json={"name": "urgent", "color": "#ff0000"},
            headers={"X-User-Id": str(user.id)},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "urgent"
        assert data["color"] == "#ff0000"

    async def test_create_tag_default_color(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        await session.commit()

        response = await client.post(
            "/api/tags",
            json={"name": "simple"},
            headers={"X-User-Id": str(user.id)},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["color"] == "#6366f1"

    async def test_create_tag_duplicate_name(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        await TagFactory.create_async(session, name="existing")
        await session.commit()

        response = await client.post(
            "/api/tags",
            json={"name": "existing"},
            headers={"X-User-Id": str(user.id)},
        )
        assert response.status_code == 409
        data = response.json()
        assert data["code"] == ErrorCodes.TAG_NAME_EXISTS.code_id

    async def test_create_tag_unauthorized(self, client: AsyncClient):
        response = await client.post("/api/tags", json={"name": "tag"})
        assert response.status_code == 401


class TestDeleteTag:
    async def test_delete_tag_success(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        tag = await TagFactory.create_async(session)
        await session.commit()

        response = await client.delete(
            f"/api/tags/{tag.id}",
            headers={"X-User-Id": str(user.id)},
        )
        assert response.status_code == 204

    async def test_delete_tag_not_found(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        await session.commit()

        response = await client.delete(
            "/api/tags/999",
            headers={"X-User-Id": str(user.id)},
        )
        assert response.status_code == 404
        data = response.json()
        assert data["code"] == ErrorCodes.TAG_NOT_FOUND.code_id

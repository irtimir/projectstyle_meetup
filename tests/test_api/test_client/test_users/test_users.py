from httpx import AsyncClient

from app.error_codes import ErrorCodes
from tests.factories import UserFactory


class TestListUsers:
    async def test_list_users_empty(self, client: AsyncClient):
        response = await client.get("/api/users")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["data"] == []

    async def test_list_users_with_data(self, client: AsyncClient, session):
        await UserFactory.create_async(session, name="Alice")
        await UserFactory.create_async(session, name="Bob")
        await session.commit()

        response = await client.get("/api/users")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["data"]) == 2

    async def test_list_users_search(self, client: AsyncClient, session):
        await UserFactory.create_async(session, name="Alice")
        await UserFactory.create_async(session, name="Bob")
        await session.commit()

        response = await client.get("/api/users", params={"search": "Alice"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["data"][0]["name"] == "Alice"

    async def test_list_users_pagination(self, client: AsyncClient, session):
        for _ in range(5):
            await UserFactory.create_async(session)
        await session.commit()

        response = await client.get("/api/users", params={"offset": 2, "limit": 2})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["data"]) == 2


class TestGetUser:
    async def test_get_user_success(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session, name="Test User", email="test@example.com")
        await session.commit()

        response = await client.get(f"/api/users/{user.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user.id
        assert data["name"] == "Test User"
        assert data["email"] == "test@example.com"

    async def test_get_user_not_found(self, client: AsyncClient):
        response = await client.get("/api/users/999")
        assert response.status_code == 404
        data = response.json()
        assert data["code"] == ErrorCodes.USER_NOT_FOUND


class TestGetCurrentUser:
    async def test_get_current_user_success(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        await session.commit()

        response = await client.get("/api/users/me", headers={"X-User-Id": str(user.id)})
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user.id

    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        response = await client.get("/api/users/me")
        assert response.status_code == 401
        data = response.json()
        assert data["code"] == ErrorCodes.UNAUTHORIZED


class TestCreateUser:
    async def test_create_user_success(self, client: AsyncClient):
        response = await client.post(
            "/api/users",
            json={"email": "new@example.com", "name": "New User"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@example.com"
        assert data["name"] == "New User"
        assert "id" in data

    async def test_create_user_duplicate_email(self, client: AsyncClient, session):
        await UserFactory.create_async(session, email="existing@example.com")
        await session.commit()

        response = await client.post(
            "/api/users",
            json={"email": "existing@example.com", "name": "Another User"},
        )
        assert response.status_code == 409
        data = response.json()
        assert data["code"] == ErrorCodes.USER_EMAIL_EXISTS

    async def test_create_user_invalid_email(self, client: AsyncClient):
        response = await client.post(
            "/api/users",
            json={"email": "invalid-email", "name": "User"},
        )
        assert response.status_code == 422
        data = response.json()
        assert data["code"] == ErrorCodes.VALIDATION_ERROR


class TestUpdateUser:
    async def test_update_user_success(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        await session.commit()

        response = await client.patch(
            f"/api/users/{user.id}",
            json={"name": "Updated Name"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    async def test_update_user_not_found(self, client: AsyncClient):
        response = await client.patch("/api/users/999", json={"name": "Name"})
        assert response.status_code == 404
        data = response.json()
        assert data["code"] == ErrorCodes.USER_NOT_FOUND


class TestDeleteUser:
    async def test_delete_user_success(self, client: AsyncClient, session):
        user = await UserFactory.create_async(session)
        await session.commit()

        response = await client.delete(f"/api/users/{user.id}")
        assert response.status_code == 204

        response = await client.get(f"/api/users/{user.id}")
        assert response.status_code == 404

    async def test_delete_user_not_found(self, client: AsyncClient):
        response = await client.delete("/api/users/999")
        assert response.status_code == 404
        data = response.json()
        assert data["code"] == ErrorCodes.USER_NOT_FOUND

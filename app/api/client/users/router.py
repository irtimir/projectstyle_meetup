from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.client.users import schemas
from app.api.dependencies import CurrentUser, DbSession, LimitOffetPagination
from app.api.exceptions import ConflictError, NotFoundError
from app.api.schemas import PaginatedResponse
from app.core.users.exceptions import UserEmailExistsError, UserNotFoundError
from app.core.users.services import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=PaginatedResponse[schemas.UserListSerializer])
async def list_users_view(
    session: DbSession,
    pagination: LimitOffetPagination,
    search: Annotated[str | None, Query()] = None,
) -> PaginatedResponse[schemas.UserListSerializer]:
    offset, limit = pagination
    service = UserService(session)
    page = await service.get_list(offset=offset, limit=limit, search=search)
    return PaginatedResponse.from_page(page, schemas.UserListSerializer)


@router.get("/me", response_model=schemas.UserSerializer)
async def get_current_user_view(
    user: CurrentUser,
) -> schemas.UserSerializer:
    return schemas.UserSerializer.model_validate(user)


@router.get("/{user_id}", response_model=schemas.UserSerializer)
async def get_user_view(
    session: DbSession,
    user_id: int,
) -> schemas.UserSerializer:
    service = UserService(session)
    try:
        user = await service.get_by_id(user_id)
    except UserNotFoundError as e:
        raise NotFoundError(code=e.code, message=e.message) from e
    return schemas.UserSerializer.model_validate(user)


@router.post("", response_model=schemas.UserSerializer, status_code=status.HTTP_201_CREATED)
async def create_user_view(
    session: DbSession,
    data: schemas.CreateUserValidator,
) -> schemas.UserSerializer:
    service = UserService(session)
    try:
        user = await service.create(email=data.email, name=data.name)
    except UserEmailExistsError as e:
        raise ConflictError(code=e.code, message=e.message) from e
    return schemas.UserSerializer.model_validate(user)


@router.patch("/{user_id}", response_model=schemas.UserSerializer)
async def update_user_view(
    session: DbSession,
    user_id: int,
    data: schemas.UpdateUserValidator,
) -> schemas.UserSerializer:
    service = UserService(session)
    try:
        user = await service.update(
            user_id=user_id,
            email=data.email,
            name=data.name,
        )
    except UserNotFoundError as e:
        raise NotFoundError(code=e.code, message=e.message) from e
    except UserEmailExistsError as e:
        raise ConflictError(code=e.code, message=e.message) from e
    return schemas.UserSerializer.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_view(
    session: DbSession,
    user_id: int,
) -> None:
    service = UserService(session)
    try:
        await service.delete(user_id)
    except UserNotFoundError as e:
        raise NotFoundError(code=e.code, message=e.message) from e

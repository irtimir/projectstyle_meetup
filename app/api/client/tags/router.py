from __future__ import annotations

from fastapi import APIRouter, status

from app.api.client.tags import schemas
from app.api.dependencies import CurrentUserRequired, DbSession, PaginationDep
from app.api.exceptions import ConflictError, NotFoundError
from app.api.schemas import PaginatedResponse
from app.core.tags.services import TagNameExistsError, TagNotFoundError, TagService

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=PaginatedResponse[schemas.TagListSerializer])
async def list_tags_view(
    session: DbSession,
    pagination: PaginationDep,
) -> PaginatedResponse[schemas.TagListSerializer]:
    offset, limit = pagination
    service = TagService(session)
    page = await service.get_list(offset=offset, limit=limit)
    return PaginatedResponse.from_page(page, schemas.TagListSerializer)


@router.post("", response_model=schemas.TagSerializer, status_code=status.HTTP_201_CREATED)
async def create_tag_view(
    session: DbSession,
    _user: CurrentUserRequired,
    data: schemas.CreateTagValidator,
) -> schemas.TagSerializer:
    service = TagService(session)
    try:
        tag = await service.create(name=data.name, color=data.color)
    except TagNameExistsError as e:
        raise ConflictError(code=e.code, message=e.message) from e
    return schemas.TagSerializer.model_validate(tag)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag_view(
    session: DbSession,
    _user: CurrentUserRequired,
    tag_id: int,
) -> None:
    service = TagService(session)
    try:
        await service.delete(tag_id)
    except TagNotFoundError as e:
        raise NotFoundError(code=e.code, message=e.message) from e

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from app.common.pagination import Page


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse[T: BaseModel](BaseModel):
    total: int
    data: list[T]

    @classmethod
    def from_page[M](cls, page: Page[M], schema: type[T]) -> PaginatedResponse[T]:
        return cls(
            total=page.total,
            data=[schema.model_validate(item) for item in page.items],
        )


class ErrorDetail(BaseModel):
    field: str
    message: str


class ErrorResponse(BaseModel):
    code: str
    message: str
    errors: list[ErrorDetail] | None = None


class PaginationParams(BaseModel):
    offset: int = 0
    limit: int = 20

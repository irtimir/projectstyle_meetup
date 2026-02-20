from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.exceptions import APIException
from app.common.exceptions import TaskManagerError
from app.error_codes import ErrorCodes


async def api_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, APIException)

    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )


async def task_manager_error_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, TaskManagerError)

    status_map: dict[str, int] = {
        ErrorCodes.NOT_FOUND.code_id: status.HTTP_404_NOT_FOUND,
        ErrorCodes.USER_NOT_FOUND.code_id: status.HTTP_404_NOT_FOUND,
        ErrorCodes.PROJECT_NOT_FOUND.code_id: status.HTTP_404_NOT_FOUND,
        ErrorCodes.TASK_NOT_FOUND.code_id: status.HTTP_404_NOT_FOUND,
        ErrorCodes.TAG_NOT_FOUND.code_id: status.HTTP_404_NOT_FOUND,
        ErrorCodes.COMMENT_NOT_FOUND.code_id: status.HTTP_404_NOT_FOUND,
        ErrorCodes.ALREADY_EXISTS.code_id: status.HTTP_409_CONFLICT,
        ErrorCodes.USER_EMAIL_EXISTS.code_id: status.HTTP_409_CONFLICT,
        ErrorCodes.TAG_NAME_EXISTS.code_id: status.HTTP_409_CONFLICT,
        ErrorCodes.FORBIDDEN.code_id: status.HTTP_403_FORBIDDEN,
        ErrorCodes.UNAUTHORIZED.code_id: status.HTTP_401_UNAUTHORIZED,
    }
    http_status = status_map.get(exc.code, status.HTTP_400_BAD_REQUEST)
    return JSONResponse(
        status_code=http_status,
        content=exc.to_dict(),
    )


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)

    errors: list[dict[str, Any]] = []
    for error in exc.errors():
        loc = error.get("loc", [])
        field = ".".join(str(x) for x in loc[1:]) if len(loc) > 1 else str(loc[0]) if loc else "unknown"
        errors.append(
            {
                "field": field,
                "message": error.get("msg", "Validation error"),
            }
        )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "code": ErrorCodes.VALIDATION_ERROR.code_id,
            "message": ErrorCodes.VALIDATION_ERROR.message,
            "errors": errors,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(APIException, api_exception_handler)
    app.add_exception_handler(TaskManagerError, task_manager_error_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

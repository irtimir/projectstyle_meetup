from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.client.comments.router import router as comments_router
from app.api.client.projects.router import router as projects_router
from app.api.client.tags.router import router as tags_router
from app.api.client.tasks.router import router as tasks_router
from app.api.client.users.router import router as users_router
from app.api.exceptions import APIException
from app.common.exceptions import OctoError
from app.error_codes import ErrorCodes

app = FastAPI(
    title="Task Manager API",
    description="Demo Task Manager API",
    version="0.1.0",
)


@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )


@app.exception_handler(OctoError)
async def octo_error_handler(request: Request, exc: OctoError) -> JSONResponse:
    status_map: dict[str, int] = {
        ErrorCodes.NOT_FOUND: status.HTTP_404_NOT_FOUND,
        ErrorCodes.USER_NOT_FOUND: status.HTTP_404_NOT_FOUND,
        ErrorCodes.PROJECT_NOT_FOUND: status.HTTP_404_NOT_FOUND,
        ErrorCodes.TASK_NOT_FOUND: status.HTTP_404_NOT_FOUND,
        ErrorCodes.TAG_NOT_FOUND: status.HTTP_404_NOT_FOUND,
        ErrorCodes.COMMENT_NOT_FOUND: status.HTTP_404_NOT_FOUND,
        ErrorCodes.ALREADY_EXISTS: status.HTTP_409_CONFLICT,
        ErrorCodes.USER_EMAIL_EXISTS: status.HTTP_409_CONFLICT,
        ErrorCodes.TAG_NAME_EXISTS: status.HTTP_409_CONFLICT,
        ErrorCodes.FORBIDDEN: status.HTTP_403_FORBIDDEN,
        ErrorCodes.UNAUTHORIZED: status.HTTP_401_UNAUTHORIZED,
    }
    http_status = status_map.get(exc.code, status.HTTP_400_BAD_REQUEST)
    return JSONResponse(
        status_code=http_status,
        content=exc.to_dict(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
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
            "code": ErrorCodes.VALIDATION_ERROR,
            "message": "Validation error",
            "errors": errors,
        },
    )


app.include_router(users_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")
app.include_router(tags_router, prefix="/api")
app.include_router(comments_router, prefix="/api")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

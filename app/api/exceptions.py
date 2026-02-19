from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status

from app.error_codes import ErrorCodes


class APIException(HTTPException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    code: str = ErrorCodes.VALIDATION_ERROR
    message: str = "Bad request"

    def __init__(
        self,
        message: str | None = None,
        code: str | None = None,
        errors: dict[str, Any] | None = None,
    ) -> None:
        self.code = code or self.code
        self.message = message or self.message
        self.errors = errors
        detail: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
        }
        if errors:
            detail["errors"] = errors
        super().__init__(status_code=self.status_code, detail=detail)


class BadRequestError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = ErrorCodes.VALIDATION_ERROR
    message = "Bad request"


class UnauthorizedError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = ErrorCodes.UNAUTHORIZED
    message = "Authentication required"


class ForbiddenError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    code = ErrorCodes.FORBIDDEN
    message = "Permission denied"


class NotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    code = ErrorCodes.NOT_FOUND
    message = "Resource not found"


class ConflictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    code = ErrorCodes.ALREADY_EXISTS
    message = "Resource already exists"

from __future__ import annotations

from typing import Any, ClassVar

from fastapi import HTTPException, status

from app.error_codes import ErrorCode, ErrorCodes


class APIException(HTTPException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    error: ClassVar[ErrorCode] = ErrorCodes.VALIDATION_ERROR

    def __init__(
        self,
        message: str | None = None,
        code: str | None = None,
        errors: dict[str, Any] | None = None,
    ) -> None:
        self.code = code or self.error.code_id
        self.message = message or self.error.message
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
    error = ErrorCodes.VALIDATION_ERROR


class UnauthorizedError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    error = ErrorCodes.UNAUTHORIZED


class ForbiddenError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    error = ErrorCodes.FORBIDDEN


class NotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    error = ErrorCodes.NOT_FOUND


class ConflictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    error = ErrorCodes.ALREADY_EXISTS

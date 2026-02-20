from __future__ import annotations

from typing import Any, ClassVar

from app.error_codes import ErrorCode, ErrorCodes


class TaskManagerError(Exception):
    error: ClassVar[ErrorCode] = ErrorCodes.VALIDATION_ERROR

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message or self.error.message
        self.code = self.error.code_id
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
        }
        if self.details:
            result["errors"] = self.details
        return result


class PermissionDeniedError(TaskManagerError):
    error = ErrorCodes.FORBIDDEN

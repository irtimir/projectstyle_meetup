from __future__ import annotations

from typing import Any


class TaskManagerError(Exception):
    code: str = "error"
    message: str = "An error occurred"

    def __init__(
        self,
        message: str | None = None,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message or self.message
        self.code = code or self.code
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
    code = "forbidden"
    message = "Permission denied"

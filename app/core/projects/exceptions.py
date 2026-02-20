from __future__ import annotations

from app.common.exceptions import TaskManagerError
from app.error_codes import ErrorCodes


class ProjectNotFoundError(TaskManagerError):
    error = ErrorCodes.PROJECT_NOT_FOUND

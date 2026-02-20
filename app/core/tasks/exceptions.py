from __future__ import annotations

from app.common.exceptions import TaskManagerError
from app.error_codes import ErrorCodes


class TaskNotFoundError(TaskManagerError):
    error = ErrorCodes.TASK_NOT_FOUND


class TaskAlreadyCompletedError(TaskManagerError):
    error = ErrorCodes.TASK_ALREADY_COMPLETED


class TaskInvalidStatusError(TaskManagerError):
    error = ErrorCodes.TASK_INVALID_STATUS

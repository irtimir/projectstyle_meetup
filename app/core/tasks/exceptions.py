from __future__ import annotations

from app.common.exceptions import TaskManagerError
from app.error_codes import ErrorCodes


class TaskNotFoundError(TaskManagerError):
    code = ErrorCodes.TASK_NOT_FOUND
    message = "Task not found"


class TaskAlreadyCompletedError(TaskManagerError):
    code = ErrorCodes.TASK_ALREADY_COMPLETED
    message = "Task is already completed"


class TaskInvalidStatusError(TaskManagerError):
    code = ErrorCodes.TASK_INVALID_STATUS
    message = "Invalid task status transition"

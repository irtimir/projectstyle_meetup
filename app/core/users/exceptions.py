from __future__ import annotations

from app.common.exceptions import TaskManagerError
from app.error_codes import ErrorCodes


class UserNotFoundError(TaskManagerError):
    error = ErrorCodes.USER_NOT_FOUND


class UserEmailExistsError(TaskManagerError):
    error = ErrorCodes.USER_EMAIL_EXISTS

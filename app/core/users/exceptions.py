from __future__ import annotations

from app.common.exceptions import TaskManagerError
from app.error_codes import ErrorCodes


class UserNotFoundError(TaskManagerError):
    code = ErrorCodes.USER_NOT_FOUND
    message = "User not found"


class UserEmailExistsError(TaskManagerError):
    code = ErrorCodes.USER_EMAIL_EXISTS
    message = "User with this email already exists"

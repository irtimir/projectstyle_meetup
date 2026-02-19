from __future__ import annotations

from app.common.exceptions import OctoError
from app.error_codes import ErrorCodes


class UserNotFoundError(OctoError):
    code = ErrorCodes.USER_NOT_FOUND
    message = "User not found"


class UserEmailExistsError(OctoError):
    code = ErrorCodes.USER_EMAIL_EXISTS
    message = "User with this email already exists"

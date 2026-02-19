from __future__ import annotations

from enum import StrEnum


class ErrorCodes(StrEnum):
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"
    ALREADY_EXISTS = "already_exists"
    FORBIDDEN = "forbidden"
    UNAUTHORIZED = "unauthorized"

    USER_NOT_FOUND = "user_not_found"
    USER_EMAIL_EXISTS = "user_email_exists"

    PROJECT_NOT_FOUND = "project_not_found"
    PROJECT_NAME_EXISTS = "project_name_exists"

    TASK_NOT_FOUND = "task_not_found"
    TASK_ALREADY_COMPLETED = "task_already_completed"
    TASK_INVALID_STATUS = "task_invalid_status"

    TAG_NOT_FOUND = "tag_not_found"
    TAG_NAME_EXISTS = "tag_name_exists"

    COMMENT_NOT_FOUND = "comment_not_found"

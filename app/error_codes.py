from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True)
class ErrorCode:
    code_id: str
    message: str = ""


class ErrorCodes:
    VALIDATION_ERROR = ErrorCode("validation_error", "Validation error")
    NOT_FOUND = ErrorCode("not_found", "Resource not found")
    ALREADY_EXISTS = ErrorCode("already_exists", "Resource already exists")
    FORBIDDEN = ErrorCode("forbidden", "Permission denied")
    UNAUTHORIZED = ErrorCode("unauthorized", "Authentication required")

    USER_NOT_FOUND = ErrorCode("user_not_found", "User not found")
    USER_EMAIL_EXISTS = ErrorCode("user_email_exists", "User with this email already exists")

    PROJECT_NOT_FOUND = ErrorCode("project_not_found", "Project not found")
    PROJECT_NAME_EXISTS = ErrorCode("project_name_exists", "Project with this name already exists")

    TASK_NOT_FOUND = ErrorCode("task_not_found", "Task not found")
    TASK_ALREADY_COMPLETED = ErrorCode("task_already_completed", "Task is already completed")
    TASK_INVALID_STATUS = ErrorCode("task_invalid_status", "Invalid task status")

    TAG_NOT_FOUND = ErrorCode("tag_not_found", "Tag not found")
    TAG_NAME_EXISTS = ErrorCode("tag_name_exists", "Tag with this name already exists")

    COMMENT_NOT_FOUND = ErrorCode("comment_not_found", "Comment not found")

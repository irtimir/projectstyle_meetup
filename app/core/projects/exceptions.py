from __future__ import annotations

from app.common.exceptions import OctoError
from app.error_codes import ErrorCodes


class ProjectNotFoundError(OctoError):
    code = ErrorCodes.PROJECT_NOT_FOUND
    message = "Project not found"

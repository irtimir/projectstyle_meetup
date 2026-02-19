from __future__ import annotations

from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any

from app.api.exceptions import ForbiddenError
from app.common.guard import AccessContext
from app.common.rules import Rule


def permission_required[**P, R](
    rule: Rule, obj_param: str | None = None
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            ctx: AccessContext | None = None
            for _key, value in kwargs.items():
                if isinstance(value, AccessContext):
                    ctx = value
                    break

            if ctx is None:
                raise RuntimeError("permission_required requires AccessContext in kwargs")

            obj: Any = None
            if obj_param is not None:
                obj = kwargs.get(obj_param)

            if not await rule(ctx, obj):
                raise ForbiddenError()

            return await func(*args, **kwargs)

        return wrapper

    return decorator

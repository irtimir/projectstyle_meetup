from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from app.common.guard import AccessContext

type Rule = Callable[[AccessContext, object], Awaitable[bool]]


@runtime_checkable
class Owned(Protocol):
    @property
    def owner_id(self) -> int: ...


def all_of(*rules: Rule) -> Rule:
    async def check(ctx: AccessContext, obj: object = None) -> bool:
        for rule in rules:
            if not await rule(ctx, obj):
                return False
        return True

    return check


def any_of(*rules: Rule) -> Rule:
    async def check(ctx: AccessContext, obj: object = None) -> bool:
        for rule in rules:
            if await rule(ctx, obj):
                return True
        return False

    return check


def none_of(*rules: Rule) -> Rule:
    async def check(ctx: AccessContext, obj: object = None) -> bool:
        for rule in rules:
            if await rule(ctx, obj):
                return False
        return True

    return check


async def is_authenticated(ctx: AccessContext, _obj: object = None) -> bool:
    return ctx.user is not None


async def is_owner(ctx: AccessContext, obj: object) -> bool:
    if ctx.user is None:
        return False
    if not isinstance(obj, Owned):
        return False
    return obj.owner_id == ctx.user.id

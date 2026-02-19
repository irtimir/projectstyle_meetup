from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from app.common.exceptions import PermissionDeniedError
from app.common.rules import Rule


class HasId(Protocol):
    @property
    def id(self) -> int: ...


@dataclass
class AccessContext:
    user: HasId | None = None
    request_id: str | None = None


class Guard:
    async def check(self, ctx: AccessContext, rule: Rule, obj: Any = None) -> bool:
        return await rule(ctx, obj)

    async def ensure(self, ctx: AccessContext, rule: Rule, obj: Any = None) -> None:
        if not await self.check(ctx, rule, obj):
            raise PermissionDeniedError()

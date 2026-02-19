from __future__ import annotations

from app.common.database import Database
from app.common.guard import Guard
from app.config import settings

db = Database(settings.database_url)
guard = Guard()

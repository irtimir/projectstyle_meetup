#!/bin/bash
set -e

export DATABASE_URL="sqlite+aiosqlite:///./test.db"

rm -f test.db
uv run alembic upgrade head
uv run pytest "$@"
rm -f test.db

# Task Manager API

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Installation

```bash
uv sync --all-extras
```

## Running

```bash
# Apply migrations
uv run alembic upgrade head

# Start server
uv run uvicorn app.main:app --reload
```

API available at http://localhost:8000

Documentation: http://localhost:8000/docs

## Tests

```bash
./scripts/test.sh
```

## Pre-commit

```bash
pre-commit install
pre-commit run --all-files
```

from __future__ import annotations

from fastapi import FastAPI

from app.api.client.comments.router import router as comments_router
from app.api.client.projects.router import router as projects_router
from app.api.client.tags.router import router as tags_router
from app.api.client.tasks.router import router as tasks_router
from app.api.client.users.router import router as users_router
from app.api.exception_handlers import register_exception_handlers

app = FastAPI(
    title="Task Manager API",
    description="Demo Task Manager API",
    version="0.1.0",
)

register_exception_handlers(app)

app.include_router(users_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")
app.include_router(tags_router, prefix="/api")
app.include_router(comments_router, prefix="/api")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

"""Learning OS — FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Learning OS", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api import auth, project, task, progress, user, phase2  # noqa: E402
from app.database import init_db  # noqa: E402

app.include_router(auth.router)
app.include_router(project.router)
app.include_router(task.router)
app.include_router(progress.router)
app.include_router(user.router)
app.include_router(phase2.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {"name": "Learning OS", "version": "0.1.0"}

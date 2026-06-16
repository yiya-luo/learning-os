"""Project API — create, list, detail, and import from Markdown DSL."""

import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Project, Stage, Task
from app.models.schemas import (
    CreateProjectRequest,
    ImportRequest,
    ImportResponse,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectResponse,
    StageSummary,
)
from app.services.parser import normalize_markdown, parse_markdown, validate_dsl

router = APIRouter(prefix="/api", tags=["Projects"])


def _project_to_response(p: Project) -> ProjectResponse:
    return ProjectResponse(
        id=p.id,
        title=p.title,
        description=p.description or "",
        reward=p.reward,
        reward_price=p.reward_price,
        deadline=str(p.deadline) if p.deadline else None,
        progress=p.progress,
        created_at=p.created_at,
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─── POST /api/projects ────────────────────────────────────────────────────────


@router.post("/projects", status_code=201, response_model=ProjectResponse)
def create_project(body: CreateProjectRequest, db: Session = Depends(get_db)):
    project = Project(
        id=uuid.uuid4().hex[:16],
        title=body.title,
        description=body.description or "",
        reward=body.reward,
        reward_price=body.reward_price or 0,
        deadline=body.deadline,
        progress=0.0,
        created_at=_now(),
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return _project_to_response(project)


# ─── GET /api/projects ─────────────────────────────────────────────────────────


@router.get("/projects", response_model=ProjectListResponse)
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    return {"projects": [_project_to_response(p) for p in projects]}


# ─── GET /api/projects/{pid} ───────────────────────────────────────────────────


@router.get("/projects/{pid}", response_model=ProjectDetailResponse)
def get_project(pid: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == pid).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    stages = db.query(Stage).filter(Stage.project_id == pid).order_by(Stage.sort_order).all()
    stage_summaries = []
    for s in stages:
        total = db.query(Task).filter(Task.stage_id == s.id).count()
        done = db.query(Task).filter(Task.stage_id == s.id, Task.status == "done").count()
        stage_summaries.append(
            StageSummary(
                id=s.id,
                title=s.title,
                sort_order=s.sort_order,
                progress=s.progress,
                task_count=total,
                done_count=done,
            )
        )

    return ProjectDetailResponse(
        id=project.id,
        title=project.title,
        description=project.description or "",
        reward=project.reward,
        reward_price=project.reward_price,
        deadline=str(project.deadline) if project.deadline else None,
        progress=project.progress,
        created_at=project.created_at,
        stages=stage_summaries,
    )


# ─── POST /api/projects/parse ─────────────────────────────────────────────────


@router.post("/projects/parse")
def parse_project(body: ImportRequest):
    markdown = body.markdown

    if not markdown or not markdown.strip():
        raise HTTPException(status_code=422, detail="Markdown content is empty")

    normalized = normalize_markdown(markdown)
    parsed = parse_markdown(normalized)

    if "error" in parsed:
        raise HTTPException(status_code=422, detail=parsed["message"])

    errors = validate_dsl(parsed)
    if errors:
        raise HTTPException(status_code=422, detail=errors[0].message)

    pdata = parsed["project"]
    stages_data = parsed.get("stages", [])
    task_count = sum(len(s.get("tasks", [])) for s in stages_data)

    return {
        "title": pdata.get("title", ""),
        "description": pdata.get("description", ""),
        "stage_count": len(stages_data),
        "task_count": task_count,
        "stages": [
            {"title": s.get("title", f"Stage {i+1}"), "task_count": len(s.get("tasks", []))}
            for i, s in enumerate(stages_data)
        ],
    }


# ─── POST /api/projects/import ─────────────────────────────────────────────────


@router.post("/projects/import", status_code=201, response_model=ImportResponse)
def import_project(body: ImportRequest, db: Session = Depends(get_db)):
    markdown = body.markdown

    if not markdown or not markdown.strip():
        raise HTTPException(
            status_code=422,
            detail={
                "error": "PARSE_ERROR",
                "line": 1,
                "message": "Markdown content is empty",
            },
        )

    normalized = normalize_markdown(markdown)
    parsed = parse_markdown(normalized)

    if "error" in parsed:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "PARSE_ERROR",
                "line": parsed.get("line", 1),
                "message": parsed["message"],
            },
        )

    errors = validate_dsl(parsed)
    if errors:
        err = errors[0]
        raise HTTPException(
            status_code=422,
            detail={
                "error": "VALIDATION_ERROR",
                "line": err.line,
                "message": err.message,
            },
        )

    pdata = parsed["project"]
    stages_data = parsed.get("stages", [])

    project = Project(
        id=uuid.uuid4().hex[:16],
        title=pdata["title"],
        description=pdata.get("description", "") or "",
        reward=pdata.get("reward"),
        reward_price=pdata.get("reward_price") or 0,
        deadline=pdata.get("deadline") or 0,
        progress=0.0,
        created_at=_now(),
    )
    db.add(project)
    db.flush()

    task_count = 0
    dsl_to_uuid: dict[str, str] = {}

    for si, sdata in enumerate(stages_data):
        stage = Stage(
            id=uuid.uuid4().hex[:16],
            project_id=project.id,
            title=sdata.get("title", f"Stage {si + 1}"),
            sort_order=si,
            progress=0.0,
        )
        db.add(stage)
        db.flush()

        for ti, tdata in enumerate(sdata.get("tasks", [])):
            dsl_id = tdata.get("id", "")
            depends_raw = tdata.get("depends") or []
            depends_json = json.dumps(depends_raw) if depends_raw else "[]"

            task = Task(
                id=uuid.uuid4().hex[:16],
                dsl_id=dsl_id,
                stage_id=stage.id,
                project_id=project.id,
                title=tdata.get("title", ""),
                type=tdata.get("type", "theory"),
                xp=tdata.get("xp", 10),
                estimate=tdata.get("estimate") or 30,
                status="pending",
                depends=depends_json,
                check=tdata.get("check") or "",
                resource=tdata.get("resource") or "",
                sort_order=ti,
                created_at=_now(),
            )
            db.add(task)
            if dsl_id:
                dsl_to_uuid[dsl_id] = task.id
            task_count += 1

    db.commit()
    db.refresh(project)

    return ImportResponse(
        project_id=project.id,
        title=project.title,
        stage_count=len(stages_data),
        task_count=task_count,
    )

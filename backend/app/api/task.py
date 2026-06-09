"""Task API — list, detail, start, checkin. Integrates engine + reward services."""

import json
import uuid
from datetime import date, datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Checkin, Project, Stage, Task, User
from app.models.schemas import (
    CheckinResponse,
    EncouragementResponse,
    TaskDetail,
    TaskListResponse,
    TaskStatusResponse,
    TodayTask,
    TodayTaskListResponse,
)
from app.services.encouragement import get_encouragement
from app.services.engine import (
    TaskStateError,
    TaskStatus,
    checkin,
    get_today_tasks as engine_get_today_tasks,
    transition,
)
from app.services.reward import (
    get_level_info,
    process_task_completed,
)

router = APIRouter(prefix="/api", tags=["Tasks"])


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _task_to_dict(t: Task) -> dict:
    return {
        "id": t.id,
        "dsl_id": t.dsl_id,
        "stage_id": t.stage_id,
        "project_id": t.project_id,
        "title": t.title,
        "type": t.type,
        "xp": t.xp,
        "estimate": t.estimate,
        "status": t.status,
        "depends": json.loads(t.depends) if t.depends else [],
        "check": t.check or None,
        "resource": t.resource or None,
        "sort_order": t.sort_order,
        "created_at": t.created_at,
        "completed_at": t.completed_at,
        "stage_order": 0,
    }


# ─── GET /api/projects/{pid}/tasks ─────────────────────────────────────────────


@router.get("/projects/{pid}/tasks", response_model=TaskListResponse)
def list_tasks(
    pid: str,
    status: Optional[str] = Query(None, enum=["pending", "doing", "done"]),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == pid).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    q = db.query(Task).filter(Task.project_id == pid)
    if status:
        q = q.filter(Task.status == status)
    tasks = q.order_by(Task.sort_order).all()

    return {
        "tasks": [
            TaskDetail.model_validate(_task_to_dict(t)) for t in tasks
        ]
    }


# ─── GET /api/projects/{pid}/tasks/today ───────────────────────────────────────


def _task_to_engine_dict(t: Task) -> dict:
    d = _task_to_dict(t)
    stage = t.stage
    if stage:
        d["stage_order"] = stage.sort_order
    return d


@router.get("/projects/{pid}/tasks/today", response_model=TodayTaskListResponse)
def list_today_tasks(pid: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == pid).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    all_tasks = db.query(Task).filter(Task.project_id == pid).all()
    task_dicts = [_task_to_engine_dict(t) for t in all_tasks]
    available = engine_get_today_tasks(pid, task_dicts)

    done_ids = {t.id for t in all_tasks if t.status == "done"}
    today_date = date.today().isoformat()
    today_tasks: list[TodayTask] = []

    for td in available:
        depends = td.get("depends", [])
        if isinstance(depends, str):
            depends = json.loads(depends) if depends else []
        blocked_by = [d for d in depends if d not in done_ids]

        stage = db.query(Stage).filter(Stage.id == td["stage_id"]).first()
        stage_title = stage.title if stage else ""

        today_tasks.append(
            TodayTask(
                id=td["id"],
                stage_id=td.get("stage_id", ""),
                stage_title=stage_title,
                title=td.get("title", ""),
                type=td.get("type", "theory"),
                xp=td.get("xp", 0),
                status=td.get("status", "pending"),
                depends=depends,
                blocked=len(blocked_by) > 0,
                check=td.get("check"),
                sort_order=td.get("sort_order", 0),
            )
        )

    return {"date": today_date, "tasks": today_tasks}


# ─── GET /api/tasks/{tid} ──────────────────────────────────────────────────────


@router.get("/tasks/{tid}", response_model=TaskDetail)
def get_task(tid: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == tid).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    stage = db.query(Stage).filter(Stage.id == task.stage_id).first()
    stage_title = stage.title if stage else ""

    return TaskDetail(
        id=task.id,
        stage_id=task.stage_id,
        stage_title=stage_title,
        project_id=task.project_id,
        title=task.title,
        type=task.type,
        xp=task.xp,
        estimate=task.estimate,
        status=task.status,
        depends=json.loads(task.depends) if task.depends else [],
        check=task.check or None,
        resource=task.resource or None,
        sort_order=task.sort_order,
        created_at=task.created_at,
        completed_at=task.completed_at,
    )


# ─── PATCH /api/tasks/{tid}/start ──────────────────────────────────────────────


@router.patch("/tasks/{tid}/start", response_model=TaskStatusResponse)
def start_task(tid: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == tid).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    current = TaskStatus(task.status)
    if current != TaskStatus.PENDING:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "INVALID_TRANSITION",
                "message": f"Task is already in '{current.value}' status",
                "current_status": current.value,
                "required_status": "pending",
            },
        )

    depends = json.loads(task.depends) if task.depends else []
    if depends:
        done_dsl_ids = set()
        all_tasks = db.query(Task).filter(Task.project_id == task.project_id).all()
        for t in all_tasks:
            if t.status == "done" and t.dsl_id:
                done_dsl_ids.add(t.dsl_id)

        blocked_by = [d for d in depends if d not in done_dsl_ids]
        if blocked_by:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "DEPENDENCY_BLOCKED",
                    "message": "Cannot start task — dependencies not met",
                    "blocked_by": blocked_by,
                },
            )

    previous_status = task.status
    try:
        new_status = transition(current, TaskStatus.DOING)
    except TaskStateError as e:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "INVALID_TRANSITION",
                "message": str(e),
                "current_status": current.value,
                "required_status": "pending",
            },
        )

    task.status = new_status.value
    db.commit()

    return TaskStatusResponse(
        id=tid,
        status=task.status,
        previous_status=previous_status,
        started_at=_now(),
    )


# ─── POST /api/tasks/{tid}/checkin ─────────────────────────────────────────────


@router.post("/tasks/{tid}/checkin", response_model=CheckinResponse)
def checkin_task(tid: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == tid).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    current = TaskStatus(task.status)
    if current != TaskStatus.DOING:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "INVALID_TRANSITION",
                "message": "Can only check in tasks that are in 'doing' status",
                "current_status": current.value,
                "required_status": "doing",
            },
        )

    task_dict = _task_to_dict(task)

    try:
        result = checkin(task_dict, user_id=1)
    except TaskStateError as e:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "INVALID_TRANSITION",
                "message": str(e),
                "current_status": current.value,
                "required_status": "doing",
            },
        )

    user = db.query(User).filter(User.id == "u1").first()
    project = db.query(Project).filter(Project.id == task.project_id).first()

    # Gather context for achievement detection (before current task is marked done)
    current_checkin_count = db.query(Checkin).filter(Checkin.user_id == user.id).count()

    completed_tasks = (
        db.query(Task)
        .filter(Task.status == "done")
        .all()
    )
    # The current task is not yet "done" in DB, so add it to counts
    theory_completed = sum(1 for t in completed_tasks if t.type == "theory")
    practice_completed = sum(1 for t in completed_tasks if t.type == "practice")
    output_completed = sum(1 for t in completed_tasks if t.type == "output")
    total_completed = len(completed_tasks)

    # Include current task in type counts
    if task_dict.get("type") == "theory":
        theory_completed += 1
    elif task_dict.get("type") == "practice":
        practice_completed += 1
    elif task_dict.get("type") == "output":
        output_completed += 1
    total_completed += 1

    reward_result = process_task_completed(
        user={
            "id": user.id,
            "xp": user.xp,
            "streak": user.streak,
            "last_checkin_date": user.last_checkin_date,
            "longest_streak": user.longest_streak,
        },
        task=task_dict,
        reward_price=project.reward_price if project else 0,
        db_session=db,
        current_checkin_count=current_checkin_count,
        theory_completed=theory_completed,
        practice_completed=practice_completed,
        output_completed=output_completed,
        total_completed=total_completed,
    )

    task.status = "done"
    task.completed_at = result.timestamp.isoformat()

    checkin_record = Checkin(
        id=uuid.uuid4().hex[:16],
        task_id=task.id,
        user_id=user.id,
        xp_earned=reward_result["xp_earned"],
        dream_value_earned=int(reward_result["dream_value"]),
        checked_at=result.timestamp.isoformat(),
    )
    db.add(checkin_record)

    user.xp = user.xp + reward_result["xp_earned"]
    user.level = reward_result["level"]
    user.streak = reward_result["streak"]
    user.longest_streak = max(user.longest_streak, reward_result["streak"])
    user.last_checkin_date = date.today().isoformat()
    user.updated_at = _now()

    _recalc_project_progress(db, task.project_id)

    db.commit()
    db.refresh(task)

    level_info = get_level_info(user.xp)

    # Phase 3: Get AI encouragement
    encouragement = get_encouragement(
        project_id=task.project_id,
        trigger_event="checkin",
        db_session=db,
        task_id=tid,
    )

    return CheckinResponse(
        id=tid,
        status="done",
        previous_status="doing",
        completed_at=task.completed_at,
        xp_earned=reward_result["xp_earned"],
        dream_value_earned=reward_result["dream_value"],
        new_total_xp=user.xp,
        new_level=reward_result["level"],
        xp_to_next_level=level_info.xp_to_next_level,
        streak=reward_result["streak"],
        easter_egg=reward_result.get("easter_egg"),
        achievement_unlocked=reward_result.get("achievement_unlocked"),
        encouragement=EncouragementResponse(**encouragement) if encouragement else None,
    )


def _recalc_project_progress(db: Session, project_id: str):
    total = db.query(Task).filter(Task.project_id == project_id).count()
    if total == 0:
        return
    done = (
        db.query(Task)
        .filter(Task.project_id == project_id, Task.status == "done")
        .count()
    )
    progress = done / total
    db.query(Project).filter(Project.id == project_id).update({"progress": progress})

    stages = db.query(Stage).filter(Stage.project_id == project_id).all()
    for stage in stages:
        st_total = db.query(Task).filter(Task.stage_id == stage.id).count()
        st_done = (
            db.query(Task)
            .filter(Task.stage_id == stage.id, Task.status == "done")
            .count()
        )
        stage.progress = st_done / st_total if st_total > 0 else 0.0

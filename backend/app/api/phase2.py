"""Phase 2 API — heatmap, DAG, stage detail, achievements, theme, reward image."""

import base64
import json
import random
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Achievement, Checkin, Project, Stage, Task, User
from app.models.schemas import (
    AchievementItem,
    AchievementsResponse,
    DagEdge,
    DagNode,
    DagResponse,
    DagStage,
    HeatmapCell,
    HeatmapResponse,
    HeatmapStats,
    RewardImageResponse,
    StageDetailResponse,
    StageTask,
    ThemeResponse,
    ThemeUpdate,
)

router = APIRouter(prefix="/api", tags=["Phase2"])

# ─── Achievement definitions ──────────────────────────────────────────────────

ALL_ACHIEVEMENTS = [
    AchievementItem(id="ACH_FIRST_CHECKIN", name="初出茅庐", description="完成第一次打卡", icon="star"),
    AchievementItem(id="ACH_STREAK_3", name="连续三日", description="连续打卡 3 天", icon="fire"),
    AchievementItem(id="ACH_STREAK_7", name="周不懈怠", description="连续打卡 7 天", icon="fire"),
    AchievementItem(id="ACH_STREAK_30", name="月度全勤", description="连续打卡 30 天", icon="trophy"),
    AchievementItem(id="ACH_LEVEL_5", name="小有所成", description="达到等级 5", icon="star"),
    AchievementItem(id="ACH_LEVEL_10", name="学富五车", description="达到等级 10", icon="trophy"),
    AchievementItem(id="ACH_TASKS_10", name="始知学海", description="完成 10 个任务", icon="book"),
    AchievementItem(id="ACH_TASKS_50", name="学而不厌", description="完成 50 个任务", icon="book"),
    AchievementItem(id="ACH_TASKS_100", name="水滴石穿", description="完成 100 个任务", icon="trophy"),
    AchievementItem(id="ACH_ALL_TYPES", name="全面发展", description="完成过 theory, practice, output 三种类型的任务", icon="check-circle"),
]

ACH_XP_BONUSES = {
    "ACH_FIRST_CHECKIN": 10,
    "ACH_STREAK_3": 15,
    "ACH_STREAK_7": 30,
    "ACH_STREAK_30": 100,
    "ACH_LEVEL_5": 25,
    "ACH_LEVEL_10": 50,
    "ACH_TASKS_10": 20,
    "ACH_TASKS_50": 50,
    "ACH_TASKS_100": 100,
    "ACH_ALL_TYPES": 25,
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ═══════════════════════════════════════════════════════════════════════════════
#  GET /api/users/me/heatmap
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/users/me/heatmap", response_model=HeatmapResponse)
def get_heatmap(days: int = 365, db: Session = Depends(get_db)):
    if days < 1 or days > 730:
        raise HTTPException(status_code=422, detail="days must be between 1 and 730")

    user = db.query(User).filter(User.id == "u1").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    today = date.today()
    start_date = today - timedelta(days=days - 1)

    checkins = (
        db.query(Checkin)
        .filter(
            Checkin.user_id == "u1",
            Checkin.checked_at >= start_date.isoformat(),
            Checkin.checked_at <= today.isoformat() + "T23:59:59",
        )
        .all()
    )

    date_map: dict[str, dict] = {}
    for c in checkins:
        try:
            d = c.checked_at[:10]
        except (TypeError, IndexError):
            continue
        if d not in date_map:
            date_map[d] = {"count": 0, "xp": 0}
        date_map[d]["count"] += 1
        date_map[d]["xp"] += c.xp_earned

    heatmap = []
    for i in range(days):
        d = start_date + timedelta(days=i)
        d_str = d.isoformat()
        info = date_map.get(d_str, {"count": 0, "xp": 0})
        heatmap.append(HeatmapCell(date=d_str, count=info["count"], xp=info["xp"]))

    heatmap.sort(key=lambda x: x.date, reverse=True)

    active_dates = [h for h in heatmap if h.count > 0]
    total_days_active = len(active_dates)
    total_checkins = sum(h.count for h in heatmap)
    total_xp = sum(h.xp for h in heatmap)
    avg_xp = round(total_xp / total_days_active, 1) if total_days_active > 0 else 0.0

    active_set = set(h.date for h in active_dates)
    longest = 0
    current_run = 0
    best_day = None
    best_xp = 0
    for h in heatmap:
        if h.xp > best_xp:
            best_xp = h.xp
            best_day = {"date": h.date, "xp": h.xp}
    for i in range(days):
        d = (start_date + timedelta(days=i)).isoformat()
        if d in active_set:
            current_run += 1
            longest = max(longest, current_run)
        else:
            if d >= today.isoformat():
                continue
            current_run = 0

    def _calc_current_streak():
        cur = 0
        for i in range(days):
            d = (today - timedelta(days=i)).isoformat()
            if d in active_set:
                cur += 1
            elif d == today.isoformat():
                continue
            else:
                return cur
        return cur

    current_streak = _calc_current_streak()

    stats = HeatmapStats(
        total_days_active=total_days_active,
        longest_streak=max(longest, user.longest_streak),
        current_streak=max(current_streak, 0),
        average_xp_per_day=avg_xp,
        total_checkins=total_checkins,
        best_day=best_day,
    )

    return HeatmapResponse(heatmap=heatmap, stats=stats)


# ═══════════════════════════════════════════════════════════════════════════════
#  GET /api/projects/{pid}/dag
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/projects/{pid}/dag", response_model=DagResponse)
def get_task_dag(pid: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == pid).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    stages = db.query(Stage).filter(Stage.project_id == pid).order_by(Stage.sort_order).all()
    tasks = db.query(Task).filter(Task.project_id == pid).order_by(Task.sort_order).all()

    stage_map = {s.id: s for s in stages}
    nodes: list[DagNode] = []
    edges: list[DagEdge] = []

    for t in tasks:
        stage = stage_map.get(t.stage_id)
        nodes.append(
            DagNode(
                id=t.id,
                title=t.title,
                type=t.type,
                status=t.status,
                xp=t.xp,
                stage_id=t.stage_id,
                stage_title=stage.title if stage else "",
                sort_order=t.sort_order,
            )
        )

        depends_raw = t.depends or "[]"
        try:
            depends = json.loads(depends_raw) if isinstance(depends_raw, str) else depends_raw
        except (json.JSONDecodeError, TypeError):
            depends = []

        for dep_dsl_id in depends:
            dsl_to_uuid = {tt.dsl_id: tt.id for tt in tasks if tt.dsl_id}
            dep_uuid = dsl_to_uuid.get(dep_dsl_id, dep_dsl_id)
            edges.append(DagEdge(source=dep_uuid.split("-")[0] if "-" in dep_uuid else dep_uuid[:8], target=t.id))

    edges = []
    for t in tasks:
        depends_raw = t.depends or "[]"
        try:
            depends = json.loads(depends_raw) if isinstance(depends_raw, str) else depends_raw
        except (json.JSONDecodeError, TypeError):
            depends = []
        dsl_to_uuid = {tt.dsl_id: tt.id for tt in tasks if tt.dsl_id}
        for dep_dsl_id in depends:
            dep_uuid = dsl_to_uuid.get(dep_dsl_id, dep_dsl_id)
            edges.append(DagEdge(source=dep_uuid, target=t.id))

    stage_summaries = []
    for s in stages:
        st_tasks = [t for t in tasks if t.stage_id == s.id]
        total = len(st_tasks)
        done = sum(1 for t in st_tasks if t.status == "done")
        stage_summaries.append(
            DagStage(
                title=s.title,
                progress=round(done / total, 2) if total > 0 else 0.0,
                task_count=total,
                done_count=done,
            )
        )

    return DagResponse(nodes=nodes, edges=edges, stages=stage_summaries)


# ═══════════════════════════════════════════════════════════════════════════════
#  GET /api/projects/{pid}/stages/{sid}
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/projects/{pid}/stages/{sid}", response_model=StageDetailResponse)
def get_stage_detail(pid: str, sid: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == pid).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    stage = db.query(Stage).filter(Stage.id == sid, Stage.project_id == pid).first()
    if not stage:
        raise HTTPException(status_code=404, detail="Stage not found")

    all_stages = (
        db.query(Stage)
        .filter(Stage.project_id == pid)
        .order_by(Stage.sort_order)
        .all()
    )

    tasks = (
        db.query(Task)
        .filter(Task.stage_id == sid)
        .order_by(Task.sort_order)
        .all()
    )

    done_ids = {
        t.id
        for s in all_stages
        for t in db.query(Task)
        .filter(Task.stage_id == s.id, Task.status == "done")
        .all()
    }

    stage_tasks: list[StageTask] = []
    for t in tasks:
        depends_raw = t.depends or "[]"
        try:
            depends = json.loads(depends_raw) if isinstance(depends_raw, str) else depends_raw
        except (json.JSONDecodeError, TypeError):
            depends = []

        dsl_to_uuid = {}
        all_project_tasks = db.query(Task).filter(Task.project_id == pid).all()
        for pt in all_project_tasks:
            if pt.dsl_id:
                dsl_to_uuid[pt.dsl_id] = pt.id

        blocked = False
        for dep_dsl_id in depends:
            dep_uuid = dsl_to_uuid.get(dep_dsl_id, dep_dsl_id)
            if dep_uuid not in done_ids:
                blocked = True
                break

        stage_tasks.append(
            StageTask(
                id=t.id,
                title=t.title,
                type=t.type,
                status=t.status,
                xp=t.xp,
                sort_order=t.sort_order,
                blocked=blocked,
            )
        )

    total = len(tasks)
    done = sum(1 for t in tasks if t.status == "done")

    current_idx = next((i for i, s in enumerate(all_stages) if s.id == sid), -1)

    prev_stage_id = None
    prev_stage_title = None
    if current_idx > 0:
        prev = all_stages[current_idx - 1]
        prev_stage_id = prev.id
        prev_stage_title = prev.title

    next_stage_id = None
    next_stage_title = None
    if current_idx < len(all_stages) - 1:
        nxt = all_stages[current_idx + 1]
        next_stage_id = nxt.id
        next_stage_title = nxt.title

    return StageDetailResponse(
        id=stage.id,
        title=stage.title,
        sort_order=stage.sort_order,
        progress=round(done / total, 2) if total > 0 else 0.0,
        task_count=total,
        done_count=done,
        tasks=stage_tasks,
        next_stage_id=next_stage_id,
        next_stage_title=next_stage_title,
        prev_stage_id=prev_stage_id,
        prev_stage_title=prev_stage_title,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  GET /api/users/me/achievements
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/users/me/achievements", response_model=AchievementsResponse)
def get_achievements(db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == "u1").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    earned_records = db.query(Achievement).filter(Achievement.user_id == "u1").all()
    earned_map = {r.achievement_key: r.unlocked_at for r in earned_records}

    result: list[AchievementItem] = []
    for ach in ALL_ACHIEVEMENTS:
        earned_at = earned_map.get(ach.id)
        xp_bonus = ACH_XP_BONUSES.get(ach.id) if earned_at else None
        result.append(
            AchievementItem(
                id=ach.id,
                name=ach.name,
                description=ach.description,
                icon=ach.icon,
                earned_at=earned_at,
                xp_bonus=xp_bonus,
            )
        )

    total_earned = sum(1 for a in result if a.earned_at is not None)

    return AchievementsResponse(
        achievements=result,
        total_earned=total_earned,
        total_available=len(ALL_ACHIEVEMENTS),
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  PATCH /api/users/me/theme
# ═══════════════════════════════════════════════════════════════════════════════


@router.patch("/users/me/theme", response_model=ThemeResponse)
def update_theme(theme: ThemeUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == "u1").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.theme = theme.theme
    user.updated_at = _now()
    db.commit()

    return ThemeResponse(theme=theme.theme)


# ═══════════════════════════════════════════════════════════════════════════════
#  PUT /api/projects/{pid}/reward-image
# ═══════════════════════════════════════════════════════════════════════════════

MAX_IMAGE_SIZE = 2 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg"}


@router.put("/projects/{pid}/reward-image", response_model=RewardImageResponse)
def upload_reward_image(pid: str, image: UploadFile = File(...), db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == pid).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image format. Only PNG and JPEG are accepted.",
        )

    contents = image.file.read()
    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="Image too large. Maximum size is 2 MB.")

    encoded = base64.b64encode(contents).decode("utf-8")
    mime = image.content_type or "image/png"
    data_uri = f"data:{mime};base64,{encoded}"

    project.reward_image = data_uri
    db.commit()

    return RewardImageResponse(image_url=data_uri)


# ─── Easter egg and achievement helpers ───────────────────────────────────────


def roll_easter_egg(streak: int, level: int) -> dict | None:
    base = 0.20
    streak_bonus = min(streak * 0.02, 0.30)
    probability = max(0.05, min(base + streak_bonus, 0.50))

    if random.random() > probability:
        return None

    roll = random.random()
    if roll < 0.70:
        bonus_xp = random.randint(10, 50)
        bonus_xp = min(bonus_xp, 10 + level * 10)
        return {
            "type": "bonus_xp",
            "message": f"运气不错！额外获得 {bonus_xp} XP！",
            "bonus_xp": bonus_xp,
        }
    elif roll < 0.95:
        return {
            "type": "double_xp",
            "message": "双倍经验！本次任务 XP 翻倍！",
            "bonus_xp": None,
        }
    else:
        return {
            "type": "streak_freeze",
            "message": "获得连击保护！下次断签不中断连击！",
            "bonus_xp": None,
        }


def evaluate_achievements(user: User, db: Session) -> dict | None:
    earned_keys = {
        r.achievement_key
        for r in db.query(Achievement).filter(Achievement.user_id == user.id).all()
    }

    total_checkins = db.query(Checkin).filter(Checkin.user_id == user.id).count()

    done_tasks = (
        db.query(Task)
        .filter(Task.status == "done")
        .all()
    )

    user_task_ids = {
        c.task_id
        for c in db.query(Checkin).filter(Checkin.user_id == user.id).all()
    }
    user_done_tasks = [t for t in done_tasks if t.id in user_task_ids]
    total_tasks_completed = len(user_done_tasks)

    types_completed = set()
    for t in user_done_tasks:
        types_completed.add(t.type)

    checks = [
        ("ACH_FIRST_CHECKIN", total_checkins >= 1),
        ("ACH_STREAK_3", user.streak >= 3),
        ("ACH_STREAK_7", user.streak >= 7),
        ("ACH_STREAK_30", user.streak >= 30),
        ("ACH_LEVEL_5", user.level >= 5),
        ("ACH_LEVEL_10", user.level >= 10),
        ("ACH_TASKS_10", total_tasks_completed >= 10),
        ("ACH_TASKS_50", total_tasks_completed >= 50),
        ("ACH_TASKS_100", total_tasks_completed >= 100),
        ("ACH_ALL_TYPES", len(types_completed) >= 3),
    ]

    for key, earned in checks:
        if earned and key not in earned_keys:
            ach_def = next((a for a in ALL_ACHIEVEMENTS if a.id == key), None)
            if ach_def:
                db.add(
                    Achievement(user_id=user.id, achievement_key=key, unlocked_at=_now())
                )
                xp_bonus = ACH_XP_BONUSES.get(key, 0)
                user.xp += xp_bonus
                db.flush()
                return {
                    "id": ach_def.id,
                    "name": ach_def.name,
                    "xp_bonus": xp_bonus,
                }

    return None

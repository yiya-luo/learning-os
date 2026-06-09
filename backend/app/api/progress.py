"""Progress API — XP, streak, and dream reward progress. Integrates reward service."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Achievement, Checkin, Project, Task, User
from app.models.schemas import (
    AchievementItem,
    AchievementsResponse,
    AnalyticsResponse,
    EncouragementRequest,
    EncouragementResponse,
    MilestonesResponse,
    RewardResponse,
    StreakResponse,
    TimelineResponse,
    XpResponse,
)
from app.services.reward import (
    ACHIEVEMENTS,
    calculate_dream_progress,
    get_level_info,
)

router = APIRouter(prefix="/api", tags=["Progress"])


@router.get("/users/me/xp", response_model=XpResponse)
def get_user_xp(db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == "u1").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    level_info = get_level_info(user.xp)
    total_completed = db.query(Checkin).filter(Checkin.user_id == user.id).count()
    total_dream = (
        db.query(Checkin)
        .filter(Checkin.user_id == user.id)
        .with_entities(Checkin.dream_value_earned)
        .all()
    )
    total_dream_value = sum(d[0] for d in total_dream)

    return XpResponse(
        total_xp=user.xp,
        level=level_info.level,
        xp_to_next_level=level_info.xp_to_next_level,
        total_tasks_completed=total_completed,
        total_dream_value=float(total_dream_value),
    )


@router.get("/users/me/streak", response_model=StreakResponse)
def get_user_streak(db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == "u1").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    today_str = date.today().isoformat()
    checked_in_today = user.last_checkin_date == today_str

    return StreakResponse(
        current_streak=user.streak,
        longest_streak=user.longest_streak,
        checked_in_today=checked_in_today,
        last_checkin_date=user.last_checkin_date,
    )


@router.get("/projects/{pid}/reward", response_model=RewardResponse)
def get_project_reward(pid: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == pid).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    user = db.query(User).filter(User.id == "u1").first()
    total_xp = user.xp if user else 0

    dream_progress = calculate_dream_progress(
        reward_price=project.reward_price,
        total_xp_earned=total_xp,
    )

    estimated_days = None
    if project.reward_price and project.reward_price > 0 and dream_progress.progress_percent > 0:
        done_tasks = (
            db.query(Task)
            .filter(Task.project_id == pid, Task.status == "done")
            .count()
        )
        total_tasks = db.query(Task).filter(Task.project_id == pid).count()
        if done_tasks > 0 and total_tasks > 0:
            remaining_percent = 1.0 - (dream_progress.progress_percent / 100.0)
            if remaining_percent > 0:
                days_per_percent = done_tasks / (dream_progress.progress_percent / 100.0)
                tasks_per_day = done_tasks / max(days_per_percent, 1)
                remaining_tasks = total_tasks - done_tasks
                if tasks_per_day > 0:
                    estimated_days = int(remaining_tasks / tasks_per_day)

    return RewardResponse(
        project_id=pid,
        reward_name=project.reward,
        reward_price=project.reward_price,
        dream_value_earned=float(dream_progress.accumulated_value),
        progress_percent=dream_progress.progress_percent,
        estimated_days_remaining=estimated_days,
    )


_ACH_ICONS = {
    "ACH001": "star",
    "ACH002": "book",
    "ACH003": "book",
    "ACH004": "book",
    "ACH005": "fire",
    "ACH006": "fire",
    "ACH007": "trophy",
    "ACH008": "check-circle",
    "ACH009": "trophy",
    "ACH010": "star",
}


@router.get("/users/me/achievements", response_model=AchievementsResponse)
def get_user_achievements(db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == "u1").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    earned = (
        db.query(Achievement)
        .filter(Achievement.user_id == user.id)
        .all()
    )
    earned_map = {ach.achievement_key: ach for ach in earned}

    items = []
    for key, ach_def in ACHIEVEMENTS.items():
        earned_record = earned_map.get(key)
        items.append(AchievementItem(
            id=key,
            name=ach_def["name"],
            description=ach_def["description"],
            icon=_ACH_ICONS.get(key, "star"),
            earned_at=earned_record.unlocked_at if earned_record else None,
            xp_bonus=ach_def["xp_bonus"] if earned_record else None,
        ))

    # Sort: earned first (by date desc), then unearned
    items.sort(key=lambda x: (x.earned_at is None, x.earned_at or ""), reverse=False)
    # Re-sort to put earned first but descending date
    earned_items = [i for i in items if i.earned_at is not None]
    unearned_items = [i for i in items if i.earned_at is None]
    earned_items.sort(key=lambda x: x.earned_at or "", reverse=True)
    items = earned_items + unearned_items

    return AchievementsResponse(
        achievements=items,
        total_earned=len(earned_items),
        total_available=len(ACHIEVEMENTS),
    )


@router.get("/users/me/analytics", response_model=AnalyticsResponse)
def get_user_analytics(period: str = "week", db: Session = Depends(get_db)):
    from app.services.analytics import get_analytics

    result = get_analytics(user_id="u1", period=period, db=db)
    return result


@router.get("/users/me/milestones", response_model=MilestonesResponse)
def get_user_milestones(db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == "u1").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    from app.services.milestones import evaluate_milestones

    milestones = evaluate_milestones(user, db)
    achieved_count = sum(1 for m in milestones if m["achieved"])

    return MilestonesResponse(
        milestones=milestones,
        achieved_count=achieved_count,
        total_count=len(milestones),
    )


@router.post("/encouragement/trigger", response_model=EncouragementResponse)
def trigger_encouragement(body: EncouragementRequest, db: Session = Depends(get_db)):
    from app.services.encouragement import get_encouragement

    project = db.query(Project).filter(Project.id == body.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Not found")

    return get_encouragement(
        project_id=body.project_id,
        trigger_event=body.trigger_event,
        db_session=db,
        task_id=body.task_id,
    )


@router.get("/users/me/timeline", response_model=TimelineResponse)
def get_user_timeline(
    page: int = 1,
    page_size: int = 20,
    filter: str = "all",
    db: Session = Depends(get_db),
):
    from app.services.timeline import get_timeline

    user = db.query(User).filter(User.id == "u1").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = get_timeline(
        user_id="u1",
        page=page,
        page_size=page_size,
        filter_type=filter,
        db_session=db,
    )
    return result

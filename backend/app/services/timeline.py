"""Timeline service — paginated event feed from checkins, milestones, achievements, stages."""



def get_timeline(
    user_id: str,
    page: int,
    page_size: int,
    filter_type: str,
    db_session,
) -> dict:
    """Get paginated timeline events in reverse chronological order.

    Args:
        user_id: User ID (always "u1" in current implementation)
        page: 1-based page number
        page_size: Number of events per page (1-100)
        filter_type: Event type filter — all, milestone, achievement, checkin, stage
        db_session: SQLAlchemy session

    Returns:
        {"events": list[dict], "pagination": {"page": int, "page_size": int, "total": int, "has_more": bool}}
    """
    from app.models.models import Achievement, Checkin, Stage, Task

    events: list[dict] = []

    # ─── Collect checkin events ────────────────────────────────────────────────
    checkins = (
        db_session.query(Checkin)
        .filter(Checkin.user_id == user_id)
        .order_by(Checkin.checked_at.desc())
        .all()
    )
    for ci in checkins:
        task = db_session.query(Task).filter(Task.id == ci.task_id).first()
        task_title = task.title if task else "Unknown task"
        task_type = task.type if task else "theory"

        events.append({
            "type": "checkin",
            "date": _extract_date(ci.checked_at),
            "title": f"完成: {task_title}",
            "checked_at": ci.checked_at,
            "xp_earned": ci.xp_earned,
            "task_type": task_type,
        })

    # ─── Collect achievement events ─────────────────────────────────────────────
    achievements = (
        db_session.query(Achievement)
        .filter(
            Achievement.user_id == user_id,
            ~Achievement.achievement_key.startswith("milestone_"),
        )
        .order_by(Achievement.unlocked_at.desc())
        .all()
    )

    ACH_DEFS = _get_achievement_defs()

    for a in achievements:
        key = a.achievement_key
        ach_def = ACH_DEFS.get(key, {})
        events.append({
            "type": "achievement",
            "date": _extract_date(a.unlocked_at),
            "title": ach_def.get("name", key),
            "checked_at": a.unlocked_at,
            "description": ach_def.get("description", ""),
            "icon": _ach_icon(key),
            "color": "#8B5CF6",
            "xp_bonus": ach_def.get("xp_bonus", 0),
        })

    # ─── Collect milestone events ───────────────────────────────────────────────
    milestones = (
        db_session.query(Achievement)
        .filter(
            Achievement.user_id == user_id,
            Achievement.achievement_key.startswith("milestone_"),
        )
        .order_by(Achievement.unlocked_at.desc())
        .all()
    )

    MS_DEFS = _get_milestone_defs()

    for m in milestones:
        ms_id = m.achievement_key.replace("milestone_", "")
        ms_def = MS_DEFS.get(ms_id, {})
        events.append({
            "type": "milestone",
            "date": _extract_date(m.unlocked_at),
            "title": ms_def.get("name", ms_id),
            "checked_at": m.unlocked_at,
            "description": ms_def.get("description", ""),
            "icon": ms_def.get("icon", "🏆"),
            "color": "#FFD700",
            "xp_bonus": ms_def.get("xp_bonus", 0),
        })

    # ─── Collect stage completion events ────────────────────────────────────────
    stages = db_session.query(Stage).all()
    for s in stages:
        s_total = db_session.query(Task).filter(Task.stage_id == s.id).count()
        s_done = (
            db_session.query(Task)
            .filter(Task.stage_id == s.id, Task.status == "done")
            .count()
        )
        if s_total > 0 and s_done == s_total:
            # Find the completion date from the last task completed in this stage
            last_done = (
                db_session.query(Task)
                .filter(Task.stage_id == s.id, Task.status == "done")
                .order_by(Task.completed_at.desc())
                .first()
            )
            completed_at = last_done.completed_at if last_done else None
            events.append({
                "type": "stage",
                "date": _extract_date(completed_at) if completed_at else "",
                "title": "完成阶段",
                "checked_at": completed_at or "",
                "description": s.title,
                "stage_progress": 100.0,
                "tasks_completed": s_done,
            })

    # ─── Filter ─────────────────────────────────────────────────────────────────
    if filter_type != "all":
        events = [e for e in events if e["type"] == filter_type]

    # ─── Sort and paginate ──────────────────────────────────────────────────────
    events.sort(key=lambda e: e.get("checked_at", ""), reverse=True)
    total = len(events)

    start = (page - 1) * page_size
    end = start + page_size
    paged_events = events[start:end]

    # Strip internal sort key
    for e in paged_events:
        e.pop("checked_at", None)

    has_more = end < total

    return {
        "events": paged_events,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "has_more": has_more,
        },
    }


def _extract_date(timestamp_str: str | None) -> str:
    """Extract YYYY-MM-DD from an ISO timestamp string."""
    if not timestamp_str:
        return ""
    if "T" in timestamp_str:
        return timestamp_str[:10]
    if len(timestamp_str) >= 10:
        return timestamp_str[:10]
    return timestamp_str


def _get_achievement_defs() -> dict:
    from app.services.reward import ACHIEVEMENTS
    return ACHIEVEMENTS


def _get_milestone_defs() -> dict:
    from app.services.milestones import MILESTONES
    return {m["id"]: m for m in MILESTONES}


def _ach_icon(key: str) -> str:
    icons = {
        "ACH001": "⭐",
        "ACH002": "📘",
        "ACH003": "🔧",
        "ACH004": "✏️",
        "ACH005": "🔥",
        "ACH006": "🔥",
        "ACH007": "🏆",
        "ACH008": "🎖️",
        "ACH009": "🏆",
        "ACH010": "⭐",
    }
    return icons.get(key, "⭐")

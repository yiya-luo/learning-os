"""Analytics aggregation service — period-over-period comparison, radar scores,
task type distribution, stage progress, and lifetime summary."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.models.models import Checkin, Project, Stage, Task


def _date_range_for_period(period: str, today: date) -> tuple[tuple[date, date], tuple[date, date]]:
    """Return (current_start, current_end), (previous_start, previous_end) for the given period."""
    if period == "week":
        current_start = today - timedelta(days=today.weekday())  # Monday
        current_end = current_start + timedelta(days=6)  # Sunday
        previous_start = current_start - timedelta(days=7)
        previous_end = current_start - timedelta(days=1)
        return (current_start, current_end), (previous_start, previous_end)

    elif period == "month":
        current_start = today.replace(day=1)
        if today.month == 12:
            current_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            current_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        # Previous month
        if today.month == 1:
            previous_start = today.replace(year=today.year - 1, month=12, day=1)
            previous_end = today.replace(day=1) - timedelta(days=1)
        else:
            previous_start = today.replace(month=today.month - 1, day=1)
            previous_end = today.replace(day=1) - timedelta(days=1)
        return (current_start, current_end), (previous_start, previous_end)

    elif period == "all":
        # For "all", previous = first half of total range, current = second half
        return (date.min, date.max), (date.min, date.max)  # Placeholder, computed later


_CN_WEEKDAYS = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]


def _get_checkins_for_range(
    user_id: str, start: date, end: date, db: Session
) -> list[dict]:
    """Return checkins within a date range as {checked_at, xp_earned} dicts."""
    start_str = start.isoformat()
    end_str = (end + timedelta(days=1)).isoformat()  # exclusive upper bound
    rows = (
        db.query(Checkin)
        .filter(
            Checkin.user_id == user_id,
            Checkin.checked_at >= start_str,
            Checkin.checked_at < end_str,
        )
        .all()
    )
    return [{"checked_at": r.checked_at, "xp_earned": r.xp_earned} for r in rows]


def _compute_period_data(
    checkins: list[dict],
    period_start: date,
    period_end: date,
    period: str,
) -> dict:
    """Compute AnalyticsPeriodData fields from a list of checkins."""
    tasks_completed = len(checkins)
    xp_earned = sum(c["xp_earned"] for c in checkins)
    total_days = (period_end - period_start).days + 1

    # Group by date
    by_date = defaultdict(lambda: {"tasks": 0, "xp": 0})
    for c in checkins:
        d = c["checked_at"][:10]
        by_date[d]["tasks"] += 1
        by_date[d]["xp"] += c["xp_earned"]

    streak_days = len(by_date)
    active_days = streak_days
    average_xp_per_day = round(xp_earned / active_days, 1) if active_days > 0 else 0.0
    completion_rate = round(streak_days / total_days, 4) if total_days > 0 else 0.0

    most_productive_day = None
    if period == "week":
        day_counts: dict[int, int] = defaultdict(int)
        for c in checkins:
            d = datetime.fromisoformat(c["checked_at"])
            day_counts[d.weekday()] += 1
        if day_counts:
            most_productive_day = _CN_WEEKDAYS[max(day_counts, key=lambda k: day_counts[k])]

    return {
        "tasks_completed": tasks_completed,
        "xp_earned": xp_earned,
        "average_xp_per_day": average_xp_per_day,
        "most_productive_day": most_productive_day,
        "streak_days": streak_days if period != "all" else None,
        "completion_rate": completion_rate,
    }


def _compute_changes(current: dict, previous: dict) -> dict:
    """Compute percentage deltas between current and previous period data."""
    prev_tasks = previous["tasks_completed"]
    prev_xp = previous["xp_earned"]

    return {
        "tasks_completed_pct": (
            round((current["tasks_completed"] - prev_tasks) / prev_tasks * 100, 1)
            if prev_tasks > 0 else None
        ),
        "xp_earned_pct": (
            round((current["xp_earned"] - prev_xp) / prev_xp * 100, 1)
            if prev_xp > 0 else None
        ),
        "completion_rate_pct": (
            round(current["completion_rate"] - previous["completion_rate"], 4)
        ),
    }


def _compute_trend(
    checkins: list[dict],
    period_start: date,
    period_end: date,
) -> list[dict]:
    """Compute daily trend array for current period."""
    by_date: dict[str, dict] = defaultdict(lambda: {"tasks": 0, "xp": 0})
    for c in checkins:
        d = c["checked_at"][:10]
        by_date[d]["tasks"] += 1
        by_date[d]["xp"] += c["xp_earned"]

    trend = []
    d = period_start
    while d <= period_end:
        ds = d.isoformat()
        if ds in by_date:
            trend.append({"date": ds, "tasks": by_date[ds]["tasks"], "xp": by_date[ds]["xp"]})
        else:
            trend.append({"date": ds, "tasks": 0, "xp": 0})
        d += timedelta(days=1)
    return trend


def _compute_task_type_distribution(user_id: str, checkins: list[dict], db: Session) -> dict:
    """Compute count/percent for theory/practice/output tasks in current period."""
    task_ids = [c.get("task_id") for c in checkins]
    if not task_ids:
        return {
            "theory": {"count": 0, "percent": 0.0},
            "practice": {"count": 0, "percent": 0.0},
            "output": {"count": 0, "percent": 0.0},
        }

    tasks = db.query(Task).filter(Task.id.in_(task_ids)).all()
    type_counts: dict[str, int] = defaultdict(int)
    for t in tasks:
        type_counts[t.type] += 1

    total = sum(type_counts.values())
    result = {}
    for tp in ("theory", "practice", "output"):
        count = type_counts.get(tp, 0)
        pct = round(count / total * 100, 1) if total > 0 else 0.0
        result[tp] = {"count": count, "percent": pct}
    return result


def _compute_stage_progress(db: Session) -> list[dict]:
    """Per-stage breakdown across all projects."""
    stages = db.query(Stage).order_by(Stage.project_id, Stage.sort_order).all()
    result = []
    for stage in stages:
        tasks = db.query(Task).filter(Task.stage_id == stage.id).all()
        total = len(tasks)
        done = sum(1 for t in tasks if t.status == "done")
        doing = sum(1 for t in tasks if t.status == "doing")
        pending = sum(1 for t in tasks if t.status == "pending")
        percent = round(done / total * 100, 1) if total > 0 else 0.0
        result.append({
            "stage_title": stage.title,
            "done": done,
            "doing": doing,
            "pending": pending,
            "total": total,
            "percent": percent,
        })
    return result


def _compute_radar(user_id: str, db: Session) -> dict:
    """Compute 5-axis radar scores (0-100 each)."""
    all_tasks = db.query(Task).all()
    total_tasks = len(all_tasks)
    done_tasks = sum(1 for t in all_tasks if t.status == "done")

    # Completion: done_tasks / total_tasks * 100
    completion = round(done_tasks / total_tasks * 100) if total_tasks > 0 else 0

    # Efficiency: min(actual_checkins / days_since_start * 100, 100)
    first_checkin = (
        db.query(Checkin.checked_at)
        .filter(Checkin.user_id == user_id)
        .order_by(Checkin.checked_at.asc())
        .first()
    )
    if first_checkin:
        first_date = date.fromisoformat(first_checkin[0][:10])
        days_since_start = (date.today() - first_date).days
    else:
        days_since_start = 0

    distinct_days = (
        db.query(Checkin.checked_at)
        .filter(Checkin.user_id == user_id)
        .all()
    )
    actual_checkins = len(set(r[0][:10] for r in distinct_days))

    if days_since_start > 0:
        efficiency = min(round(actual_checkins / days_since_start * 100), 100)
    else:
        efficiency = 0

    # Streak: current_streak / max(30, longest_streak) * 100
    from app.models.models import User
    user = db.query(User).filter(User.id == user_id).first()
    current_streak = user.streak if user else 0
    longest_streak = user.longest_streak if user else 0
    denominator = max(30, longest_streak)
    streak_score = round(current_streak / denominator * 100) if current_streak > 0 else 0

    # Quality: tasks_with_check / total_done * 100
    done_rows = db.query(Task).filter(Task.status == "done").all()
    total_done = len(done_rows)
    check_done = sum(1 for t in done_rows if t.check and t.check.strip())
    quality = round(check_done / total_done * 100) if total_done > 0 else 0

    # Speed: tasks_completed_before_estimate / total_done * 100
    # Task has no estimate -> counts as "on time"
    # We compare completed_at vs created_at (minutes) <= estimate
    on_time = 0
    for t in done_rows:
        if not t.estimate or t.estimate <= 0:
            on_time += 1
        elif t.completed_at and t.created_at:
            try:
                created_dt = datetime.fromisoformat(t.created_at)
                completed_dt = datetime.fromisoformat(t.completed_at)
                actual_minutes = (completed_dt - created_dt).total_seconds() / 60
                if actual_minutes <= t.estimate:
                    on_time += 1
            except (ValueError, OverflowError):
                on_time += 1
        else:
            on_time += 1

    speed = round(on_time / total_done * 100) if total_done > 0 else 0

    return {
        "completion": completion,
        "efficiency": efficiency,
        "streak": streak_score,
        "quality": quality,
        "speed": speed,
    }


def _compute_summary(user_id: str, db: Session) -> dict:
    """Lifetime summary (period-independent)."""
    from app.models.models import User
    user = db.query(User).filter(User.id == user_id).first()

    checkins = db.query(Checkin).filter(Checkin.user_id == user_id).all()
    total_tasks_completed = len(checkins)
    total_xp = sum(c.xp_earned for c in checkins)

    distinct_dates = set(c.checked_at[:10] for c in checkins)
    total_days_active = len(distinct_dates)

    longest_streak = user.longest_streak if user else 0
    current_streak = user.streak if user else 0

    # Favorite type from ALL completed tasks
    all_done_tasks = (
        db.query(Task)
        .filter(Task.status == "done")
        .all()
    )
    type_counts: dict[str, int] = defaultdict(int)
    for t in all_done_tasks:
        type_counts[t.type] += 1
    favorite_type = max(type_counts, key=lambda k: type_counts[k]) if type_counts else "theory"

    projects_completed = (
        db.query(Project)
        .filter(Project.progress >= 1.0)
        .count()
    )

    stages = db.query(Stage).all()
    stages_completed = 0
    for stage in stages:
        tasks = db.query(Task).filter(Task.stage_id == stage.id).all()
        if tasks and all(t.status == "done" for t in tasks):
            stages_completed += 1

    first_checkin = (
        db.query(Checkin.checked_at)
        .filter(Checkin.user_id == user_id)
        .order_by(Checkin.checked_at.asc())
        .first()
    )
    first_checkin_date = first_checkin[0][:10] if first_checkin else None

    return {
        "total_tasks_completed": total_tasks_completed,
        "total_xp": total_xp,
        "total_days_active": total_days_active,
        "longest_streak": longest_streak,
        "current_streak": current_streak,
        "favorite_type": favorite_type,
        "projects_completed": projects_completed,
        "stages_completed": stages_completed,
        "first_checkin_date": first_checkin_date,
    }


def get_analytics(user_id: str, period: str, db: Session) -> dict:
    """Compute full analytics response for the given user and period.

    Returns a dict matching the AnalyticsResponse schema.
    """
    today = date.today()

    if period == "all":
        # Determine total time range from all checkins
        all_checkins = (
            db.query(Checkin)
            .filter(Checkin.user_id == user_id)
            .order_by(Checkin.checked_at.asc())
            .all()
        )

        if not all_checkins:
            empty = {
                "tasks_completed": 0,
                "xp_earned": 0,
                "average_xp_per_day": 0.0,
                "most_productive_day": None,
                "streak_days": None,
                "completion_rate": 0.0,
            }
            return {
                "period": "all",
                "current": empty,
                "previous": empty,
                "changes": {
                    "tasks_completed_pct": None,
                    "xp_earned_pct": None,
                    "completion_rate_pct": 0.0,
                },
                "trend": [],
                "task_type_distribution": {
                    "theory": {"count": 0, "percent": 0.0},
                    "practice": {"count": 0, "percent": 0.0},
                    "output": {"count": 0, "percent": 0.0},
                },
                "stage_progress": _compute_stage_progress(db),
                "radar": _compute_radar(user_id, db),
                "summary": _compute_summary(user_id, db),
            }

        first_date_str = all_checkins[0].checked_at[:10]
        last_date_str = all_checkins[-1].checked_at[:10]
        first_date = date.fromisoformat(first_date_str)
        last_date = date.fromisoformat(last_date_str)
        total_days = (last_date - first_date).days + 1

        if total_days < 2:
            # Single day of data: current = that day, previous = empty
            current_start = first_date
            current_end = first_date
            previous_start = first_date
            previous_end = first_date
            prev_checkins = []
            curr_checkins = [{"checked_at": c.checked_at, "xp_earned": c.xp_earned, "task_id": c.task_id} for c in all_checkins]
        else:
            midpoint = first_date + timedelta(days=total_days // 2)
            # First half
            previous_start = first_date
            previous_end = midpoint - timedelta(days=1)
            # Second half
            current_start = midpoint
            current_end = last_date

            prev_checkins = [
                {"checked_at": c.checked_at, "xp_earned": c.xp_earned, "task_id": c.task_id}
                for c in all_checkins
                if c.checked_at[:10] < midpoint.isoformat()
            ]
            curr_checkins = [
                {"checked_at": c.checked_at, "xp_earned": c.xp_earned, "task_id": c.task_id}
                for c in all_checkins
                if c.checked_at[:10] >= midpoint.isoformat()
            ]

        current_data = _compute_period_data(curr_checkins, current_start, current_end, "all")
        current_data["most_productive_day"] = None
        previous_data = _compute_period_data(prev_checkins, previous_start, previous_end, "all")
        previous_data["most_productive_day"] = None

        # For "all", compute trend across entire time range
        trend = _compute_trend(curr_checkins, current_start, current_end)

        # Task type distribution across all checkins in current period
        task_type_dist = _compute_task_type_distribution(user_id, curr_checkins, db)

        return {
            "period": "all",
            "current": current_data,
            "previous": previous_data,
            "changes": _compute_changes(current_data, previous_data),
            "trend": trend,
            "task_type_distribution": task_type_dist,
            "stage_progress": _compute_stage_progress(db),
            "radar": _compute_radar(user_id, db),
            "summary": _compute_summary(user_id, db),
        }

    # Week / Month periods
    (current_start, current_end), (previous_start, previous_end) = _date_range_for_period(period, today)

    curr_checkins = _get_checkins_for_range(user_id, current_start, current_end, db)
    # Attach task_id for distribution computation
    curr_checkins_full = (
        db.query(Checkin)
        .filter(
            Checkin.user_id == user_id,
            Checkin.checked_at >= current_start.isoformat(),
            Checkin.checked_at < (current_end + timedelta(days=1)).isoformat(),
        )
        .all()
    )
    curr_list = [{"checked_at": c.checked_at, "xp_earned": c.xp_earned, "task_id": c.task_id} for c in curr_checkins_full]

    prev_checkins = _get_checkins_for_range(user_id, previous_start, previous_end, db)

    current_data = _compute_period_data(curr_list, current_start, current_end, period)
    previous_data = _compute_period_data(prev_checkins, previous_start, previous_end, period)

    trend = _compute_trend(curr_list, current_start, current_end)

    task_type_dist = _compute_task_type_distribution(user_id, curr_list, db)

    return {
        "period": period,
        "current": current_data,
        "previous": previous_data,
        "changes": _compute_changes(current_data, previous_data),
        "trend": trend,
        "task_type_distribution": task_type_dist,
        "stage_progress": _compute_stage_progress(db),
        "radar": _compute_radar(user_id, db),
        "summary": _compute_summary(user_id, db),
    }

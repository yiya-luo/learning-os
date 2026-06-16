"""Unit and integration tests for the analytics service and API endpoint."""

import os
from datetime import date, datetime, timedelta

import pytest

# Use in-memory SQLite for tests
os.environ["DATABASE_URL"] = "sqlite:///./test_analytics.db"

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models.models import Checkin, Project, Stage, Task, User  # noqa: E402
from app.services.analytics import (  # noqa: E402
    _compute_changes,
    _compute_period_data,
    _compute_radar,
    _compute_stage_progress,
    _compute_summary,
    _compute_trend,
    _date_range_for_period,
    get_analytics,
)
from fastapi.testclient import TestClient

from app.main import app  # noqa: E402

client = TestClient(app)


def _today() -> date:
    return date.today()


# ─── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def fresh_db():
    """Drop and recreate all tables before each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    if not db.query(User).filter(User.id == "u1").first():
        db.add(User(id="u1", nickname="Learner"))
        db.commit()
    db.close()

    yield

    db = SessionLocal()
    db.close()


@pytest.fixture
def db_session():
    db = SessionLocal()
    yield db
    db.rollback()
    db.close()


def _seed_user(db, **kwargs):
    user = db.query(User).filter(User.id == "u1").first()
    for k, v in kwargs.items():
        setattr(user, k, v)
    db.commit()


def _seed_task(db, task_id="t1", status="done", task_type="theory", xp=30,
               estimate=30, stage_id=None, project_id=None, check="", title="Test Task",
               created_at=None, completed_at=None):
    if project_id is not None:
        existing = db.query(Project).filter(Project.id == project_id).first()
        if existing is None:
            existing = Project(id=project_id, title="Test Project", progress=0.0)
            db.add(existing)
            db.flush()

    if stage_id is not None:
        existing_stage = db.query(Stage).filter(Stage.id == stage_id).first()
        if existing_stage is None:
            existing_stage = Stage(
                id=stage_id, project_id=project_id or "p1",
                title="Test Stage", sort_order=0, progress=0.0,
            )
            db.add(existing_stage)
            db.flush()

    if stage_id is None:
        # Auto-create with unique IDs
        import uuid as _uuid
        sid = _uuid.uuid4().hex[:12]
        pid = project_id or _uuid.uuid4().hex[:12]
        existing_proj = db.query(Project).filter(Project.id == pid).first()
        if existing_proj is None:
            existing_proj = Project(id=pid, title="Test Project", progress=0.0)
            db.add(existing_proj)
            db.flush()
        stage = Stage(id=sid, project_id=pid, title="Test Stage", sort_order=0, progress=0.0)
        db.add(stage)
        db.flush()
        stage_id = sid
        project_id = pid

    task = Task(
        id=task_id, stage_id=stage_id, project_id=project_id,
        title=title, type=task_type, xp=xp, estimate=estimate, status=status,
        check=check, sort_order=0,
        created_at=created_at or datetime.now().isoformat(),
        completed_at=completed_at,
    )
    db.add(task)
    db.flush()
    return task


def _seed_checkin(db, task_id="t1", user_id="u1", xp_earned=30, checked_at=None):
    checkin = Checkin(
        task_id=task_id, user_id=user_id, xp_earned=xp_earned,
        checked_at=checked_at or datetime.now().isoformat(),
    )
    db.add(checkin)
    db.flush()
    return checkin


# ─── Date Range Tests ─────────────────────────────────────────────────────────


class TestDateRangeForPeriod:
    def test_week_period(self):
        # Use a known Monday to test
        a_monday = date(2026, 6, 8)
        (curr_start, curr_end), (prev_start, prev_end) = _date_range_for_period("week", a_monday)
        assert curr_start == a_monday
        assert curr_end == a_monday + timedelta(days=6)
        assert prev_start == a_monday - timedelta(days=7)
        assert prev_end == a_monday - timedelta(days=1)

    def test_month_period(self):
        a_day = date(2026, 6, 8)
        (curr_start, curr_end), (prev_start, prev_end) = _date_range_for_period("month", a_day)
        assert curr_start == date(2026, 6, 1)
        assert curr_end == date(2026, 6, 30)
        assert prev_start == date(2026, 5, 1)
        assert prev_end == date(2026, 5, 31)

    def test_month_period_january(self):
        a_day = date(2026, 1, 15)
        (curr_start, curr_end), (prev_start, prev_end) = _date_range_for_period("month", a_day)
        assert curr_start == date(2026, 1, 1)
        assert prev_start == date(2025, 12, 1)


# ─── Period Data Tests ────────────────────────────────────────────────────────


class TestComputePeriodData:
    def test_empty_period(self):
        result = _compute_period_data([], date(2026, 6, 8), date(2026, 6, 14), "week")
        assert result["tasks_completed"] == 0
        assert result["xp_earned"] == 0
        assert result["average_xp_per_day"] == 0.0
        assert result["completion_rate"] == 0.0
        assert result["streak_days"] == 0

    def test_with_data(self):
        checkins = [
            {"checked_at": "2026-06-08T10:00:00", "xp_earned": 30},
            {"checked_at": "2026-06-08T15:00:00", "xp_earned": 20},
            {"checked_at": "2026-06-09T10:00:00", "xp_earned": 50},
        ]
        result = _compute_period_data(checkins, date(2026, 6, 8), date(2026, 6, 14), "week")
        assert result["tasks_completed"] == 3
        assert result["xp_earned"] == 100
        assert result["streak_days"] == 2
        # 7 days in week period
        assert result["completion_rate"] == round(2 / 7, 4)
        # 3 checkins, 2 active days => avg 50 per day
        assert result["average_xp_per_day"] == 50.0

    def test_most_productive_day_week(self):
        # Monday = 0, Wednesday = 2
        checkins = [
            {"checked_at": "2026-06-08T10:00:00", "xp_earned": 10},  # Monday
            {"checked_at": "2026-06-10T10:00:00", "xp_earned": 10},  # Wednesday
            {"checked_at": "2026-06-10T15:00:00", "xp_earned": 10},  # Wednesday
        ]
        result = _compute_period_data(checkins, date(2026, 6, 8), date(2026, 6, 14), "week")
        assert result["most_productive_day"] == "星期三"

    def test_no_most_productive_day_for_month(self):
        checkins = [
            {"checked_at": "2026-06-08T10:00:00", "xp_earned": 10},
        ]
        result = _compute_period_data(checkins, date(2026, 6, 1), date(2026, 6, 30), "month")
        assert result["most_productive_day"] is None

    def test_no_most_productive_day_for_all(self):
        checkins = [
            {"checked_at": "2026-06-08T10:00:00", "xp_earned": 10},
        ]
        result = _compute_period_data(checkins, date(2026, 6, 1), date(2026, 6, 30), "all")
        assert result["most_productive_day"] is None


# ─── Changes Tests ────────────────────────────────────────────────────────────


class TestComputeChanges:
    def test_both_have_data(self):
        current = {"tasks_completed": 12, "xp_earned": 285, "completion_rate": 0.85}
        previous = {"tasks_completed": 8, "xp_earned": 190, "completion_rate": 0.65}
        changes = _compute_changes(current, previous)
        assert changes["tasks_completed_pct"] == 50.0
        assert changes["xp_earned_pct"] == 50.0
        assert changes["completion_rate_pct"] == 0.2

    def test_previous_zero_tasks(self):
        current = {"tasks_completed": 5, "xp_earned": 100, "completion_rate": 0.5}
        previous = {"tasks_completed": 0, "xp_earned": 0, "completion_rate": 0.0}
        changes = _compute_changes(current, previous)
        assert changes["tasks_completed_pct"] is None
        assert changes["xp_earned_pct"] is None
        assert changes["completion_rate_pct"] == 0.5


# ─── Trend Tests ──────────────────────────────────────────────────────────────


class TestComputeTrend:
    def test_empty(self):
        start = date(2026, 6, 8)
        end = date(2026, 6, 14)
        trend = _compute_trend([], start, end)
        assert len(trend) == 7
        assert all(t["tasks"] == 0 for t in trend)
        assert all(t["xp"] == 0 for t in trend)

    def test_with_data(self):
        checkins = [
            {"checked_at": "2026-06-08T10:00:00", "xp_earned": 30},
            {"checked_at": "2026-06-08T15:00:00", "xp_earned": 20},
        ]
        start = date(2026, 6, 8)
        end = date(2026, 6, 14)
        trend = _compute_trend(checkins, start, end)
        assert trend[0]["date"] == "2026-06-08"
        assert trend[0]["tasks"] == 2
        assert trend[0]["xp"] == 50
        assert trend[1]["date"] == "2026-06-09"
        assert trend[1]["tasks"] == 0


# ─── Stage Progress Tests ─────────────────────────────────────────────────────


class TestComputeStageProgress:
    def test_empty(self, db_session):
        result = _compute_stage_progress(db_session)
        assert result == []

    def test_stages_across_projects(self, db_session):
        p1 = Project(id="p1", title="Project 1", progress=0.0)
        p2 = Project(id="p2", title="Project 2", progress=0.0)
        db_session.add_all([p1, p2])
        db_session.flush()

        s1 = Stage(id="s1", project_id="p1", title="Stage 1", sort_order=0, progress=0.0)
        s2 = Stage(id="s2", project_id="p1", title="Stage 2", sort_order=1, progress=0.0)
        db_session.add_all([s1, s2])
        db_session.flush()

        _seed_task(db_session, "t1", status="done", stage_id="s1", project_id="p1")
        _seed_task(db_session, "t2", status="doing", stage_id="s1", project_id="p1")
        _seed_task(db_session, "t3", status="pending", stage_id="s2", project_id="p1")

        result = _compute_stage_progress(db_session)
        assert len(result) == 2
        assert result[0]["stage_title"] == "Stage 1"
        assert result[0]["done"] == 1
        assert result[0]["doing"] == 1
        assert result[0]["pending"] == 0
        assert result[0]["total"] == 2
        assert result[0]["percent"] == 50.0


# ─── Radar Score Tests ────────────────────────────────────────────────────────


class TestRadarScores:
    def test_empty_db(self, db_session):
        radar = _compute_radar("u1", db_session)
        assert radar["completion"] == 0
        assert radar["efficiency"] == 0
        assert radar["streak"] == 0
        assert radar["quality"] == 0
        assert radar["speed"] == 0

    def test_full_completion(self, db_session):
        user = db_session.query(User).filter(User.id == "u1").first()
        user.streak = 7
        user.longest_streak = 30
        db_session.flush()

        _seed_task(db_session, "t1", status="done")
        _seed_task(db_session, "t2", status="done")

        radar = _compute_radar("u1", db_session)
        assert radar["completion"] == 100
        # streak: 7 / max(30, 30) * 100 = 23
        assert radar["streak"] == 23

    def test_quality_with_check_fields(self, db_session):
        _seed_task(db_session, "t1", status="done", check="Verify correctness")
        _seed_task(db_session, "t2", status="done", check="")

        radar = _compute_radar("u1", db_session)
        assert radar["quality"] == 50  # 1 of 2 has check

    def test_speed_on_time(self, db_session):
        now = datetime.now()
        early = (now - timedelta(minutes=10)).isoformat()
        late = (now - timedelta(hours=2)).isoformat()

        # Task with estimate=30, completed in 10 min => on time
        _seed_task(db_session, "t1", status="done", estimate=30,
                   created_at=early, completed_at=now.isoformat())
        # Task with estimate=30, took 2 hours => late
        _seed_task(db_session, "t2", status="done", estimate=30,
                   created_at=late, completed_at=now.isoformat())

        radar = _compute_radar("u1", db_session)
        assert radar["speed"] == 50  # 1 of 2 on time

    def test_speed_no_estimate_counts_as_on_time(self, db_session):
        _seed_task(db_session, "t1", status="done", estimate=0)

        radar = _compute_radar("u1", db_session)
        assert radar["speed"] == 100


# ─── Summary Tests ────────────────────────────────────────────────────────────


class TestComputeSummary:
    def test_empty_user(self, db_session):
        summary = _compute_summary("u1", db_session)
        assert summary["total_tasks_completed"] == 0
        assert summary["total_xp"] == 0
        assert summary["total_days_active"] == 0
        assert summary["first_checkin_date"] is None
        assert summary["projects_completed"] == 0
        assert summary["stages_completed"] == 0

    def test_with_data(self, db_session):
        _seed_task(db_session, "t1", status="done")
        _seed_checkin(db_session, "t1", xp_earned=30,
                      checked_at="2026-06-01T10:00:00")
        _seed_checkin(db_session, "t1", xp_earned=20,
                      checked_at="2026-06-01T15:00:00")
        _seed_checkin(db_session, "t1", xp_earned=10,
                      checked_at="2026-06-02T10:00:00")

        summary = _compute_summary("u1", db_session)
        assert summary["total_tasks_completed"] == 3
        assert summary["total_xp"] == 60
        assert summary["total_days_active"] == 2
        assert summary["first_checkin_date"] == "2026-06-01"

    def test_favorite_type(self, db_session):
        _seed_task(db_session, "t1", status="done", task_type="theory")
        _seed_task(db_session, "t2", status="done", task_type="practice")
        _seed_task(db_session, "t3", status="done", task_type="practice")

        summary = _compute_summary("u1", db_session)
        assert summary["favorite_type"] == "practice"

    def test_projects_completed(self, db_session):
        db_session.add(Project(id="p1", title="Done Project", progress=1.0))
        db_session.add(Project(id="p2", title="Ongoing", progress=0.5))
        db_session.flush()

        summary = _compute_summary("u1", db_session)
        assert summary["projects_completed"] == 1


# ─── Integration: get_analytics ───────────────────────────────────────────────


class TestGetAnalytics:
    def test_week_period_empty(self, db_session):
        result = get_analytics("u1", "week", db_session)
        assert result["period"] == "week"
        assert result["current"]["tasks_completed"] == 0
        assert result["previous"]["tasks_completed"] == 0
        assert result["changes"]["tasks_completed_pct"] is None
        assert len(result["trend"]) == 7
        assert result["summary"]["total_tasks_completed"] == 0

    def test_month_period_empty(self, db_session):
        result = get_analytics("u1", "month", db_session)
        assert result["period"] == "month"
        assert result["current"]["tasks_completed"] == 0

    def test_all_period_empty(self, db_session):
        result = get_analytics("u1", "all", db_session)
        assert result["period"] == "all"
        assert result["current"]["tasks_completed"] == 0
        assert result["current"]["most_productive_day"] is None

    def test_week_with_data(self, db_session):
        today = _today()
        monday = today - timedelta(days=today.weekday())

        _seed_task(db_session, "t1", status="done")
        _seed_task(db_session, "t2", status="done")
        _seed_checkin(db_session, "t1", xp_earned=30,
                      checked_at=monday.isoformat() + "T10:00:00")
        _seed_checkin(db_session, "t2", xp_earned=20,
                      checked_at=monday.isoformat() + "T12:00:00")

        result = get_analytics("u1", "week", db_session)
        assert result["current"]["tasks_completed"] == 2
        assert result["current"]["xp_earned"] == 50
        assert result["current"]["most_productive_day"] is not None
        assert result["task_type_distribution"]["theory"]["count"] == 2

    def test_radar_present(self, db_session):
        result = get_analytics("u1", "week", db_session)
        radar = result["radar"]
        assert "completion" in radar
        assert "efficiency" in radar
        assert "streak" in radar
        assert "quality" in radar
        assert "speed" in radar
        for k in ("completion", "efficiency", "streak", "quality", "speed"):
            assert 0 <= radar[k] <= 100

    def test_summary_present(self, db_session):
        result = get_analytics("u1", "week", db_session)
        summary = result["summary"]
        assert "total_tasks_completed" in summary
        assert "favorite_type" in summary
        assert "first_checkin_date" in summary

    def test_most_productive_day_null_for_month(self, db_session):
        result = get_analytics("u1", "month", db_session)
        assert result["current"]["most_productive_day"] is None


# ─── API Endpoint Tests ───────────────────────────────────────────────────────


class TestAnalyticsAPI:
    def test_get_analytics_default_period(self):
        resp = client.get("/api/users/me/analytics")
        assert resp.status_code == 200
        data = resp.json()
        assert data["period"] == "week"
        assert "current" in data
        assert "previous" in data
        assert "changes" in data
        assert "trend" in data
        assert "task_type_distribution" in data
        assert "stage_progress" in data
        assert "radar" in data
        assert "summary" in data

    def test_get_analytics_week(self):
        resp = client.get("/api/users/me/analytics?period=week")
        assert resp.status_code == 200
        assert resp.json()["period"] == "week"

    def test_get_analytics_month(self):
        resp = client.get("/api/users/me/analytics?period=month")
        assert resp.status_code == 200
        assert resp.json()["period"] == "month"

    def test_get_analytics_all(self):
        resp = client.get("/api/users/me/analytics?period=all")
        assert resp.status_code == 200
        assert resp.json()["period"] == "all"

    def test_empty_user_has_no_checkin_date(self):
        resp = client.get("/api/users/me/analytics?period=all")
        data = resp.json()
        assert data["summary"]["first_checkin_date"] is None

    def test_task_type_distribution_structure(self):
        resp = client.get("/api/users/me/analytics")
        dist = resp.json()["task_type_distribution"]
        for key in ("theory", "practice", "output"):
            assert key in dist
            assert "count" in dist[key]
            assert "percent" in dist[key]

    def test_radar_scores_range(self):
        resp = client.get("/api/users/me/analytics")
        radar = resp.json()["radar"]
        for k in ("completion", "efficiency", "streak", "quality", "speed"):
            assert 0 <= radar[k] <= 100

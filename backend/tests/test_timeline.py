"""Tests for the timeline service."""

import pytest
from unittest.mock import MagicMock
from app.services.timeline import (
    get_timeline,
    _extract_date,
)


class TestExtractDate:
    """Test date extraction from ISO timestamps."""

    def test_extract_from_iso(self):
        assert _extract_date("2026-06-08T12:30:00Z") == "2026-06-08"

    def test_extract_from_date_only(self):
        assert _extract_date("2026-06-08") == "2026-06-08"

    def test_extract_none(self):
        assert _extract_date(None) == ""

    def test_extract_empty(self):
        assert _extract_date("") == ""


class TestTimelineEmpty:
    """Test timeline with empty results."""

    def test_empty_timeline(self):
        from app.models.models import Achievement, Checkin, Stage

        db = MagicMock()

        checkin_mock = MagicMock()
        checkin_mock.filter.return_value.order_by.return_value.all.return_value = []
        ach_mock = MagicMock()
        ach_mock.filter.return_value.order_by.return_value.all.return_value = []
        stage_mock = MagicMock()
        stage_mock.all.return_value = []

        db.query.side_effect = lambda model: {
            Checkin: checkin_mock,
            Achievement: ach_mock,
            Stage: stage_mock,
        }.get(model, MagicMock())

        result = get_timeline("u1", page=1, page_size=20, filter_type="all", db_session=db)
        assert result["events"] == []
        assert result["pagination"]["page"] == 1
        assert result["pagination"]["page_size"] == 20
        assert result["pagination"]["total"] == 0
        assert result["pagination"]["has_more"] is False


class TestTimelinePagination:
    """Test timeline pagination logic."""

    def test_has_more_true(self):
        """When there are more events than page_size, has_more should be True."""
        from app.models.models import Achievement, Checkin, Stage

        db = MagicMock()

        # Create 5 mock checkins
        checkins = []
        for i in range(5):
            ci = MagicMock()
            ci.user_id = "u1"
            ci.task_id = f"t{i}"
            ci.xp_earned = 10
            ci.checked_at = f"2026-06-0{i+1}T12:00:00"
            checkins.append(ci)

        from app.models.models import Task
        task = MagicMock(spec=Task)
        task.title = f"Test Task"
        task.type = "theory"

        checkin_mock = MagicMock()
        checkin_mock.filter.return_value.order_by.return_value.all.return_value = checkins
        ach_mock = MagicMock()
        ach_mock.filter.return_value.order_by.return_value.all.return_value = []
        stage_mock = MagicMock()
        stage_mock.all.return_value = []
        task_mock = MagicMock()
        task_mock.filter.return_value.first.return_value = task

        db.query.side_effect = lambda model: {
            Checkin: checkin_mock,
            Achievement: ach_mock,
            Stage: stage_mock,
            Task: task_mock,
        }.get(model, MagicMock())

        result = get_timeline("u1", page=1, page_size=3, filter_type="all", db_session=db)
        assert len(result["events"]) == 3
        assert result["pagination"]["total"] == 5
        assert result["pagination"]["has_more"] is True

    def test_page_2(self):
        """Second page should return remaining items."""
        from app.models.models import Achievement, Checkin, Stage, Task

        db = MagicMock()

        checkins = []
        for i in range(5):
            ci = MagicMock()
            ci.user_id = "u1"
            ci.task_id = f"t{i}"
            ci.xp_earned = 10
            ci.checked_at = f"2026-06-0{i+1}T12:00:00"
            checkins.append(ci)

        task = MagicMock(spec=Task)
        task.title = "Test Task"
        task.type = "theory"

        checkin_mock = MagicMock()
        checkin_mock.filter.return_value.order_by.return_value.all.return_value = checkins
        ach_mock = MagicMock()
        ach_mock.filter.return_value.order_by.return_value.all.return_value = []
        stage_mock = MagicMock()
        stage_mock.all.return_value = []
        task_mock = MagicMock()
        task_mock.filter.return_value.first.return_value = task

        db.query.side_effect = lambda model: {
            Checkin: checkin_mock,
            Achievement: ach_mock,
            Stage: stage_mock,
            Task: task_mock,
        }.get(model, MagicMock())

        result = get_timeline("u1", page=2, page_size=3, filter_type="all", db_session=db)
        assert len(result["events"]) == 2
        assert result["pagination"]["has_more"] is False


class TestTimelineFilter:
    """Test filter by event type."""

    def test_filter_checkin_only(self):
        from app.models.models import Achievement, Checkin, Stage, Task

        db = MagicMock()

        checkins = []
        for i in range(3):
            ci = MagicMock()
            ci.user_id = "u1"
            ci.task_id = f"t{i}"
            ci.xp_earned = 10
            ci.checked_at = f"2026-06-0{i+1}T12:00:00"
            checkins.append(ci)

        task = MagicMock(spec=Task)
        task.title = "Test Task"
        task.type = "theory"

        ach1 = MagicMock()
        ach1.user_id = "u1"
        ach1.achievement_key = "ACH001"
        ach1.unlocked_at = "2026-06-04T12:00:00"

        checkin_mock = MagicMock()
        checkin_mock.filter.return_value.order_by.return_value.all.return_value = checkins
        ach_mock = MagicMock()
        ach_mock.filter.return_value.order_by.return_value.all.return_value = [ach1]
        stage_mock = MagicMock()
        stage_mock.all.return_value = []
        task_mock = MagicMock()
        task_mock.filter.return_value.first.return_value = task

        db.query.side_effect = lambda model: {
            Checkin: checkin_mock,
            Achievement: ach_mock,
            Stage: stage_mock,
            Task: task_mock,
        }.get(model, MagicMock())

        result = get_timeline("u1", page=1, page_size=20, filter_type="checkin", db_session=db)
        assert all(e["type"] == "checkin" for e in result["events"])

    def test_filter_all_includes_mixed_types(self):
        from app.models.models import Achievement, Checkin, Stage, Task

        db = MagicMock()

        ci = MagicMock()
        ci.user_id = "u1"
        ci.task_id = "t1"
        ci.xp_earned = 10
        ci.checked_at = "2026-06-08T12:00:00"

        task = MagicMock(spec=Task)
        task.title = "Test Task"
        task.type = "theory"

        ach1 = MagicMock()
        ach1.user_id = "u1"
        ach1.achievement_key = "ACH001"
        ach1.unlocked_at = "2026-06-07T12:00:00"

        checkin_mock = MagicMock()
        checkin_mock.filter.return_value.order_by.return_value.all.return_value = [ci]
        ach_mock = MagicMock()
        ach_mock.filter.return_value.order_by.return_value.all.return_value = [ach1]
        stage_mock = MagicMock()
        stage_mock.all.return_value = []
        task_mock = MagicMock()
        task_mock.filter.return_value.first.return_value = task

        db.query.side_effect = lambda model: {
            Checkin: checkin_mock,
            Achievement: ach_mock,
            Stage: stage_mock,
            Task: task_mock,
        }.get(model, MagicMock())

        result = get_timeline("u1", page=1, page_size=20, filter_type="all", db_session=db)
        # Should have both checkin and achievement events
        types = {e["type"] for e in result["events"]}
        assert "checkin" in types
        assert "achievement" in types


class TestTimelineEventStructure:
    """Test event objects have correct fields."""

    def test_checkin_event_fields(self):
        from app.models.models import Achievement, Checkin, Stage, Task

        db = MagicMock()

        ci = MagicMock()
        ci.user_id = "u1"
        ci.task_id = "t1"
        ci.xp_earned = 25
        ci.checked_at = "2026-06-08T12:30:00"

        task = MagicMock(spec=Task)
        task.title = "Download Data"
        task.type = "practice"

        checkin_mock = MagicMock()
        checkin_mock.filter.return_value.order_by.return_value.all.return_value = [ci]
        ach_mock = MagicMock()
        ach_mock.filter.return_value.order_by.return_value.all.return_value = []
        stage_mock = MagicMock()
        stage_mock.all.return_value = []
        task_mock = MagicMock()
        task_mock.filter.return_value.first.return_value = task

        db.query.side_effect = lambda model: {
            Checkin: checkin_mock,
            Achievement: ach_mock,
            Stage: stage_mock,
            Task: task_mock,
        }.get(model, MagicMock())

        result = get_timeline("u1", page=1, page_size=20, filter_type="all", db_session=db)
        event = result["events"][0]
        assert event["type"] == "checkin"
        assert "date" in event
        assert "title" in event
        assert event["xp_earned"] == 25
        assert event["task_type"] == "practice"


class TestTimelineSortOrder:
    """Test events are sorted newest first."""

    def test_newest_first(self):
        from app.models.models import Achievement, Checkin, Stage, Task

        db = MagicMock()

        checkins = []
        for i, date_str in enumerate(["2026-06-08", "2026-06-05", "2026-06-01"]):
            ci = MagicMock()
            ci.user_id = "u1"
            ci.task_id = f"t{i}"
            ci.xp_earned = 10
            ci.checked_at = f"{date_str}T12:00:00"
            checkins.append(ci)

        task = MagicMock(spec=Task)
        task.title = "Task"
        task.type = "theory"

        checkin_mock = MagicMock()
        checkin_mock.filter.return_value.order_by.return_value.all.return_value = checkins
        ach_mock = MagicMock()
        ach_mock.filter.return_value.order_by.return_value.all.return_value = []
        stage_mock = MagicMock()
        stage_mock.all.return_value = []
        task_mock = MagicMock()
        task_mock.filter.return_value.first.return_value = task

        db.query.side_effect = lambda model: {
            Checkin: checkin_mock,
            Achievement: ach_mock,
            Stage: stage_mock,
            Task: task_mock,
        }.get(model, MagicMock())

        result = get_timeline("u1", page=1, page_size=20, filter_type="all", db_session=db)
        events = result["events"]
        assert events[0]["date"] == "2026-06-08"
        assert events[1]["date"] == "2026-06-05"
        assert events[2]["date"] == "2026-06-01"

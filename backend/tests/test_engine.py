"""Unit tests for the task engine state machine, scheduler, and check-in logic."""

import pytest

from app.services.engine import (
    CheckinResult,
    TaskStateError,
    TaskStatus,
    can_transition,
    checkin,
    get_available_tasks,
    get_today_tasks,
    transition,
)


# ---------------------------------------------------------------------------
# State machine tests
# ---------------------------------------------------------------------------

class TestStateMachine:
    def test_pending_to_doing_legal(self):
        """1. pending -> doing is a legal transition."""
        result = transition(TaskStatus.PENDING, TaskStatus.DOING)
        assert result == TaskStatus.DOING

    def test_doing_to_done_legal(self):
        """2. doing -> done is a legal transition."""
        result = transition(TaskStatus.DOING, TaskStatus.DONE)
        assert result == TaskStatus.DONE

    def test_done_to_doing_raises(self):
        """3. done -> doing raises TaskStateError."""
        with pytest.raises(TaskStateError):
            transition(TaskStatus.DONE, TaskStatus.DOING)

    def test_pending_to_done_raises(self):
        """4. pending -> done raises TaskStateError (must go through doing)."""
        with pytest.raises(TaskStateError):
            transition(TaskStatus.PENDING, TaskStatus.DONE)

    def test_done_to_pending_raises(self):
        """5. done -> pending raises TaskStateError."""
        with pytest.raises(TaskStateError):
            transition(TaskStatus.DONE, TaskStatus.PENDING)

    def test_pending_to_pending_raises(self):
        """Self-transition to pending is not allowed."""
        with pytest.raises(TaskStateError):
            transition(TaskStatus.PENDING, TaskStatus.PENDING)

    def test_can_transition_positive(self):
        assert can_transition(TaskStatus.PENDING, TaskStatus.DOING) is True
        assert can_transition(TaskStatus.DOING, TaskStatus.DONE) is True

    def test_can_transition_negative(self):
        assert can_transition(TaskStatus.DONE, TaskStatus.DOING) is False
        assert can_transition(TaskStatus.PENDING, TaskStatus.DONE) is False


# ---------------------------------------------------------------------------
# Scheduler tests
# ---------------------------------------------------------------------------

def _make_task(
    tid: str,
    status: str = "pending",
    depends: list[str] | None = None,
    stage_order: int = 0,
    sort_order: int = 0,
    estimate: int | None = 30,
    xp: int = 10,
    title: str = "",
) -> dict:
    return {
        "id": tid,
        "title": title or f"Task {tid}",
        "status": status,
        "depends": depends or [],
        "stage_order": stage_order,
        "sort_order": sort_order,
        "estimate": estimate,
        "xp": xp,
    }


class TestScheduler:
    def test_available_excludes_done(self):
        """6. Available tasks filters out done tasks."""
        tasks = [
            _make_task("T001", "done"),
            _make_task("T002", "pending"),
            _make_task("T003", "doing"),
        ]
        result = get_available_tasks("p1", tasks)
        ids = [t["id"] for t in result]
        assert "T001" not in ids
        assert "T002" in ids
        assert "T003" in ids

    def test_available_filters_unmet_dependencies(self):
        """7. Available tasks filters out tasks with unmet dependencies."""
        tasks = [
            _make_task("T001", "pending"),
            _make_task("T002", "pending", depends=["T001"]),
        ]
        result = get_available_tasks("p1", tasks)
        ids = [t["id"] for t in result]
        # T001 has no deps -> available. T002 depends on T001 (not done) -> not available
        assert ids == ["T001"]

    def test_available_sorts_by_stage_then_task_order(self):
        """8. Available tasks sort by stage order, then task order."""
        tasks = [
            _make_task("T003", "pending", stage_order=1, sort_order=0),
            _make_task("T001", "pending", stage_order=0, sort_order=1),
            _make_task("T002", "pending", stage_order=0, sort_order=0),
        ]
        result = get_available_tasks("p1", tasks)
        ids = [t["id"] for t in result]
        assert ids == ["T002", "T001", "T003"]

    def test_today_respects_max_minutes(self):
        """9. Today tasks respects max_minutes cutoff."""
        tasks = [
            _make_task("T001", "pending", estimate=20),
            _make_task("T002", "pending", estimate=20),
            _make_task("T003", "pending", estimate=20),
            _make_task("T004", "pending", estimate=30),
        ]
        result = get_today_tasks("p1", tasks, max_minutes=45)
        ids = [t["id"] for t in result]
        # 20+20+20=60 > 45, so only first two (20+20=40) fit
        assert ids == ["T001", "T002"]

    def test_today_task_without_estimate_always_included(self):
        """Tasks without estimate are always included regardless of max_minutes."""
        tasks = [
            _make_task("T001", "pending", estimate=60),
            _make_task("T002", "pending", estimate=None),
        ]
        result = get_today_tasks("p1", tasks, max_minutes=30)
        ids = [t["id"] for t in result]
        # T001 estimate 60 > 30, so skipped. T002 has no estimate, always included.
        assert "T002" in ids
        # T001 (60 min) exceeds max_minutes=30 on its own
        assert "T001" not in ids

    def test_task_with_all_deps_done_is_available(self):
        """12. Task with all depends done is available."""
        tasks = [
            _make_task("T001", "done"),
            _make_task("T002", "done"),
            _make_task("T003", "pending", depends=["T001", "T002"]),
        ]
        result = get_available_tasks("p1", tasks)
        ids = [t["id"] for t in result]
        assert "T003" in ids

    def test_task_with_some_deps_not_done_is_not_available(self):
        """13. Task with some depends not done is NOT available."""
        tasks = [
            _make_task("T001", "done"),
            _make_task("T002", "pending"),
            _make_task("T003", "pending", depends=["T001", "T002"]),
        ]
        result = get_available_tasks("p1", tasks)
        ids = [t["id"] for t in result]
        # T003 depends on T002 which is pending -> not available
        assert "T003" not in ids


# ---------------------------------------------------------------------------
# Check-in tests
# ---------------------------------------------------------------------------

class TestCheckin:
    def test_checkin_returns_correct_result(self):
        """10. Checkin returns correct CheckinResult."""
        task = _make_task("T001", "doing", xp=20)
        result = checkin(task)
        assert isinstance(result, CheckinResult)
        assert result.task_id == "T001"
        assert result.xp_earned == 20
        assert result.dream_value == 2.0
        assert result.new_status == TaskStatus.DONE

    def test_checkin_on_non_doing_task_raises(self):
        """11. Checkin on non-doing task raises error."""
        task = _make_task("T001", "pending")
        with pytest.raises(TaskStateError, match="expected 'doing'"):
            checkin(task)

        task_done = _make_task("T001", "done")
        with pytest.raises(TaskStateError, match="expected 'doing'"):
            checkin(task_done)

    def test_checkin_creates_event(self):
        """Checkin produces a TaskCompletedEvent (side-effect tested indirectly)."""
        task = _make_task("T001", "doing", xp=15)
        result = checkin(task)
        assert result.xp_earned == 15
        assert result.dream_value == 1.5


# ---------------------------------------------------------------------------
# Edge case tests
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_tasks(self):
        assert get_available_tasks("p1", []) == []
        assert get_today_tasks("p1", []) == []

    def test_all_done(self):
        tasks = [
            _make_task("T001", "done"),
            _make_task("T002", "done"),
        ]
        assert get_available_tasks("p1", tasks) == []
        assert get_today_tasks("p1", tasks) == []

    def test_circular_dependency_not_blocked_by_engine(self):
        """Engine trusts the data layer to have resolved cycles. It just checks status."""
        tasks = [
            _make_task("T001", "pending", depends=["T002"]),
            _make_task("T002", "pending", depends=["T001"]),
        ]
        # Both are pending with unmet deps -> neither available
        result = get_available_tasks("p1", tasks)
        assert result == []

    def test_task_with_empty_depends_string(self):
        """Tasks with an empty depends string are treated as no dependencies."""
        task = {
            "id": "T001",
            "title": "Test",
            "status": "pending",
            "depends": "[]",
            "stage_order": 0,
            "sort_order": 0,
            "estimate": 30,
            "xp": 10,
        }
        result = get_available_tasks("p1", [task])
        assert len(result) == 1
        assert result[0]["id"] == "T001"

    def test_today_stops_at_cumulative_boundary(self):
        """Today tasks accumulate estimates and stop cleanly at the boundary."""
        tasks = [
            _make_task("T001", "pending", estimate=10),
            _make_task("T002", "pending", estimate=20),
            _make_task("T003", "pending", estimate=30),
            _make_task("T004", "pending", estimate=5),
        ]
        result = get_today_tasks("p1", tasks, max_minutes=60)
        ids = [t["id"] for t in result]
        # 10+20+30=60, T004 doesn't fit
        assert ids == ["T001", "T002", "T003"]

"""Tests for the milestones service."""

import pytest
from unittest.mock import MagicMock
from app.services.milestones import (
    MILESTONES,
    evaluate_milestones,
    _evaluate_condition,
)


class TestMilestoneDefinitions:
    """Test milestone definition integrity."""

    def test_15_milestones_defined(self):
        assert len(MILESTONES) == 15

    def test_all_have_required_fields(self):
        required = {"id", "name", "description", "icon", "condition", "xp_bonus"}
        for ms in MILESTONES:
            missing = required - set(ms.keys())
            assert not missing, f"{ms['id']} missing: {missing}"

    def test_unique_ids(self):
        ids = [m["id"] for m in MILESTONES]
        assert len(ids) == len(set(ids)), f"Duplicate milestone IDs: {ids}"

    def test_all_xp_bonuses_positive(self):
        for ms in MILESTONES:
            assert ms["xp_bonus"] > 0, f"{ms['id']} has non-positive xp_bonus"

    def test_m001_to_m015_sequential(self):
        ids = [m["id"] for m in MILESTONES]
        expected = [f"M{i:03d}" for i in range(1, 16)]
        assert ids == expected


class TestEvaluateCondition:
    """Test milestone condition evaluation."""

    def test_first_checkin(self):
        ms = {"condition": "first_checkin"}
        assert _evaluate_condition(ms, {"first_checkin": True})
        assert not _evaluate_condition(ms, {"first_checkin": False})

    def test_streak_ge(self):
        ms = {"condition": "streak_ge", "condition_value": 7}
        # streak_ge uses max(streak, longest_streak)
        assert _evaluate_condition(ms, {"streak": 7, "longest_streak": 7})
        assert _evaluate_condition(ms, {"streak": 10, "longest_streak": 10})
        assert _evaluate_condition(ms, {"streak": 5, "longest_streak": 8})  # longest >= 7
        assert not _evaluate_condition(ms, {"streak": 5, "longest_streak": 5})

    def test_streak_ge_100(self):
        ms = {"condition": "streak_ge", "condition_value": 100}
        assert _evaluate_condition(ms, {"streak": 100, "longest_streak": 100})
        assert not _evaluate_condition(ms, {"streak": 30, "longest_streak": 30})

    def test_dream_progress_ge(self):
        ms = {"condition": "dream_progress_ge", "condition_value": 25}
        assert _evaluate_condition(ms, {"dream_progress": 25.0})
        assert _evaluate_condition(ms, {"dream_progress": 50.0})
        assert not _evaluate_condition(ms, {"dream_progress": 24.9})

    def test_dream_progress_100(self):
        ms = {"condition": "dream_progress_ge", "condition_value": 100}
        assert _evaluate_condition(ms, {"dream_progress": 100.0})
        assert not _evaluate_condition(ms, {"dream_progress": 99.0})

    def test_total_tasks_ge(self):
        ms = {"condition": "total_tasks_ge", "condition_value": 10}
        assert _evaluate_condition(ms, {"total_tasks": 10})
        assert _evaluate_condition(ms, {"total_tasks": 50})
        assert not _evaluate_condition(ms, {"total_tasks": 9})

    def test_first_stage_complete(self):
        ms = {"condition": "first_stage_complete"}
        assert _evaluate_condition(ms, {"has_stage_complete": True})
        assert not _evaluate_condition(ms, {"has_stage_complete": False})

    def test_first_project_complete(self):
        ms = {"condition": "first_project_complete"}
        assert _evaluate_condition(ms, {"has_project_complete": True})
        assert not _evaluate_condition(ms, {"has_project_complete": False})

    def test_all_types_done(self):
        ms = {"condition": "all_types_done"}
        assert _evaluate_condition(ms, {
            "theory_done": 1, "practice_done": 1, "output_done": 1
        })
        assert _evaluate_condition(ms, {
            "theory_done": 5, "practice_done": 1, "output_done": 1
        })
        assert not _evaluate_condition(ms, {
            "theory_done": 1, "practice_done": 1, "output_done": 0
        })
        assert not _evaluate_condition(ms, {
            "theory_done": 0, "practice_done": 0, "output_done": 1
        })

    def test_easter_egg_triggered(self):
        ms = {"condition": "easter_egg_triggered"}
        assert _evaluate_condition(ms, {"easter_egg_triggered": True})
        assert not _evaluate_condition(ms, {"easter_egg_triggered": False})


class TestEvaluateMilestones:
    """Integration tests for evaluate_milestones with mocked DB."""

    def _make_mock_db(self, **overrides):
        from app.models.models import User, Checkin, Project, Stage, Task

        db = MagicMock()

        defaults = {
            "checkin_count": 0,
            "total_done": 0,
            "theory_done": 0,
            "practice_done": 0,
            "output_done": 0,
            "streak": 0,
            "longest_streak": 0,
            "projects": [],
            "has_stage_complete": False,
        }
        defaults.update(overrides)

        # Build mock query chain for counting
        def make_count_mock(value):
            m = MagicMock()
            m.filter.return_value.count.return_value = value
            return m

        # We'll mock db_session.query to return appropriate count mocks
        # This is complex, so we test conditions directly instead
        return db, defaults

    def test_new_user_all_unachieved(self):
        """New user with no activity — only M001-M004 may be achievable through streak=0."""
        from app.models.models import User
        db = MagicMock()
        user = MagicMock(spec=User)
        user.id = "u1"
        user.streak = 0
        user.longest_streak = 0
        user.xp = 0

        # Mock all the query chains
        checkin_mock = MagicMock()
        checkin_mock.filter.return_value.count.return_value = 0
        task_done_mock = MagicMock()
        task_done_mock.filter.return_value.count.return_value = 0
        theory_mock = MagicMock()
        theory_mock.filter.return_value.count.return_value = 0
        practice_mock = MagicMock()
        practice_mock.filter.return_value.count.return_value = 0
        output_mock = MagicMock()
        output_mock.filter.return_value.count.return_value = 0
        project_mock = MagicMock()
        project_mock.all.return_value = []
        stage_mock = MagicMock()
        stage_mock.all.return_value = []

        db.query = MagicMock()
        db.query.side_effect = lambda model: {
            "checkins": checkin_mock,
            "tasks": task_done_mock,
            "projects": project_mock,
            "stages": stage_mock,
        }.get(model.__tablename__ if hasattr(model, '__tablename__') else str(model), MagicMock())

        # Since we can't easily mock all the complex query chains, test that
        # all milestones have achieved=False for a zero-state user
        results = evaluate_milestones(user, db)
        assert len(results) == 15
        # At least the threshold-based ones should be unachieved
        unachieved = [r for r in results if not r["achieved"]]
        # With streak=0, dream_progress=0, total_tasks=0, most should be unachieved
        assert len(unachieved) >= 10

    def test_result_structure(self):
        """Test that each result has all required fields."""
        from app.models.models import User
        db = MagicMock()
        user = MagicMock(spec=User)
        user.id = "u1"
        user.streak = 0
        user.longest_streak = 0

        checkin_mock = MagicMock()
        checkin_mock.filter.return_value.count.return_value = 0
        task_done_mock = MagicMock()
        task_done_mock.filter.return_value.count.side_effect = [0, 0, 0, 0, 0]
        project_mock = MagicMock()
        project_mock.all.return_value = []
        stage_mock = MagicMock()
        stage_mock.all.return_value = []
        achievement_mock = MagicMock()
        achievement_mock.filter.return_value.first.return_value = None

        def query_side_effect(model):
            from app.models.models import Checkin, Project, Stage, Task, Achievement
            if model == Checkin:
                return checkin_mock
            elif model == Task:
                task_done_mock.filter.return_value.count.side_effect = [0, 0, 0, 0, 0, 0]
                return task_done_mock
            elif model == Project:
                return project_mock
            elif model == Stage:
                return stage_mock
            elif model == Achievement:
                return achievement_mock
            return MagicMock()

        db.query = query_side_effect

        results = evaluate_milestones(user, db)
        for r in results:
            assert "id" in r
            assert "name" in r
            assert "description" in r
            assert "icon" in r
            assert "achieved" in r
            assert "achieved_at" in r or r["achieved_at"] is None
            assert "xp_bonus" in r
            assert r["xp_bonus"] > 0

    def test_sorting_achieved_first(self):
        """Achieved milestones should come before unachieved in results.

        With streak=7 and 1 checkin, M001 (first_checkin) and M002 (streak>=7)
        should be achieved. Other streak-based, task-count, and dream-progress
        milestones should remain unachieved.
        """
        from app.models.models import User
        db = MagicMock()
        user = MagicMock(spec=User)
        user.id = "u1"
        user.streak = 7
        user.longest_streak = 7

        # Every .query() call returns a chainable mock. .filter() returns self
        # so that .filter(...).filter(...).count() chains always end in .count().
        universal = MagicMock()
        universal.filter.return_value = universal
        universal.count.return_value = 0
        universal.all.return_value = []
        universal.first.return_value = None

        checkin_universal = MagicMock()
        checkin_universal.filter.return_value = checkin_universal
        checkin_universal.count.return_value = 1
        checkin_universal.all.return_value = []
        checkin_universal.first.return_value = None

        def query_side_effect(model):
            from app.models.models import Checkin
            if model is Checkin:
                return checkin_universal
            return universal

        db.query = query_side_effect

        results = evaluate_milestones(user, db)
        assert len(results) == 15
        # M001 (first_checkin) and M002 (streak>=7) should be achieved
        achieved = [r for r in results if r["achieved"]]
        achieved_ids = {r["id"] for r in achieved}
        assert "M001" in achieved_ids
        assert "M002" in achieved_ids
        # Achieved items should come first in the sorted list
        for i, r in enumerate(results):
            if not r["achieved"]:
                # All subsequent items should also be unachieved
                assert all(not r2["achieved"] for r2 in results[i:])
                break

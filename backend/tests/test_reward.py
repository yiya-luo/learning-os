"""Unit tests for the reward service."""

import random
from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from app.services.reward import (
    ACHIEVEMENTS,
    DREAM_MULTIPLIER,
    EASTER_EGG_RESOURCES,
    LEVEL_THRESHOLDS,
    DreamProgress,
    LevelInfo,
    StreakInfo,
    calculate_dream_progress,
    calculate_xp,
    check_level_up,
    detect_achievements,
    get_level_info,
    process_task_completed,
    roll_easter_egg,
    streak_bonus_title,
    update_streak,
)


# ─── XP Calculation ──────────────────────────────────────────────────────────


class TestCalculateXp:
    def test_no_bonus(self):
        assert calculate_xp(20, 0) == 20
        assert calculate_xp(20, 1) == 20
        assert calculate_xp(20, 6) == 20

    def test_7_day_streak_10_percent(self):
        assert calculate_xp(20, 7) == 22
        assert calculate_xp(10, 7) == 11
        assert calculate_xp(100, 7) == 110

    def test_15_day_streak_20_percent(self):
        assert calculate_xp(20, 15) == 24
        assert calculate_xp(10, 20) == 12

    def test_30_day_streak_50_percent(self):
        assert calculate_xp(20, 30) == 30
        assert calculate_xp(10, 50) == 15

    def test_60_day_streak_75_percent(self):
        assert calculate_xp(10, 60) == 17  # 10 * 1.75 = 17.5 → 17
        assert calculate_xp(20, 75) == 35
        assert calculate_xp(7, 60) == 12  # 7 * 1.75 = 12.25 → 12

    def test_100_day_streak_100_percent(self):
        assert calculate_xp(10, 100) == 20
        assert calculate_xp(3, 100) == 6  # 3 * 2.0 = 6
        assert calculate_xp(1, 100) == 2  # 1 * 2.0 = 2

    def test_rounding_down(self):
        assert calculate_xp(3, 7) == 3  # 3.3 → 3
        assert calculate_xp(1, 15) == 1  # 1.2 → 1
        assert calculate_xp(7, 30) == 10  # 10.5 → 10

    def test_streak_bonus_title(self):
        assert streak_bonus_title(3) is None
        assert streak_bonus_title(7) == "一周坚持"
        assert streak_bonus_title(15) == "半个月"
        assert streak_bonus_title(30) == "一个月"
        assert streak_bonus_title(60) == "两个月"
        assert streak_bonus_title(100) == "百日英雄"


# ─── Level System ────────────────────────────────────────────────────────────


class TestGetLevelInfo:
    def test_level_1_fresh(self):
        info = get_level_info(0)
        assert info.level == 1
        assert info.title == "新手"
        assert info.current_xp == 0
        assert info.xp_to_next_level == 100

    def test_level_1_with_xp(self):
        info = get_level_info(50)
        assert info.level == 1
        assert info.title == "新手"
        assert info.current_xp == 50
        assert info.xp_to_next_level == 50
        assert info.total_xp_for_level == 100

    def test_level_2(self):
        info = get_level_info(150)
        assert info.level == 2
        assert info.title == "学习者"
        assert info.current_xp == 50
        assert info.xp_to_next_level == 150
        assert info.total_xp_for_level == 200

    def test_level_3(self):
        info = get_level_info(500)
        assert info.level == 3
        assert info.title == "工程师"
        assert info.current_xp == 200
        assert info.xp_to_next_level == 100
        assert info.total_xp_for_level == 300

    def test_level_4(self):
        info = get_level_info(700)
        assert info.level == 4
        assert info.title == "研究员"
        assert info.current_xp == 100
        assert info.xp_to_next_level == 300
        assert info.total_xp_for_level == 400

    def test_level_5(self):
        info = get_level_info(1200)
        assert info.level == 5
        assert info.title == "独立开发者"
        assert info.current_xp == 200
        assert info.xp_to_next_level == 800
        assert info.total_xp_for_level == 1000

    def test_level_6(self):
        info = get_level_info(2500)
        assert info.level == 6
        assert info.title == "长期主义者"
        assert info.current_xp == 500
        assert info.xp_to_next_level == 0
        assert info.total_xp_for_level == 0

    def test_exact_threshold(self):
        info = get_level_info(100)
        assert info.level == 2
        assert info.title == "学习者"
        assert info.current_xp == 0

    def test_threshold_minus_one(self):
        info = get_level_info(99)
        assert info.level == 1
        assert info.xp_to_next_level == 1


class TestCheckLevelUp:
    def test_no_level_up(self):
        assert check_level_up(50, 90) is None
        assert check_level_up(100, 200) is None

    def test_level_up_detected(self):
        assert check_level_up(90, 110) == 2
        assert check_level_up(50, 300) == 3
        assert check_level_up(250, 610) == 4

    def test_multiple_levels(self):
        assert check_level_up(0, 1000) == 5


# ─── Dream Value ─────────────────────────────────────────────────────────────


class TestDreamProgress:
    def test_basic_calculation(self):
        p = calculate_dream_progress(15000, 300, 5.0)
        assert p.reward_price == 15000
        assert p.accumulated_value == 1500.0
        assert p.progress_percent == 10.0
        assert p.remaining == 13500.0

    def test_capped_at_100_percent(self):
        p = calculate_dream_progress(100, 500, 5.0)
        assert p.progress_percent == 100.0
        assert p.remaining == 0.0

    def test_zero_reward_price(self):
        p = calculate_dream_progress(0, 100)
        assert p.progress_percent == 0.0

    def test_default_multiplier(self):
        p = calculate_dream_progress(100, 10)
        assert p.accumulated_value == 50.0

    def test_custom_multiplier(self):
        p = calculate_dream_progress(1000, 100, 10.0)
        assert p.accumulated_value == 1000.0
        assert p.progress_percent == 100.0


# ─── Streak System ───────────────────────────────────────────────────────────


class TestUpdateStreak:
    def test_first_checkin(self):
        result = update_streak(0, 0, None, date(2026, 6, 8))
        assert result.current_streak == 1
        assert result.longest_streak == 1
        assert result.last_checkin_date == date(2026, 6, 8)
        assert result.streak_bonus_percent == 0

    def test_consecutive_days_increment(self):
        result = update_streak(3, 3, date(2026, 6, 7), date(2026, 6, 8))
        assert result.current_streak == 4
        assert result.longest_streak == 4

    def test_gap_resets_to_one(self):
        result = update_streak(10, 12, date(2026, 6, 1), date(2026, 6, 8))
        assert result.current_streak == 1
        assert result.longest_streak == 12

    def test_same_day_no_change(self):
        result = update_streak(5, 5, date(2026, 6, 8), date(2026, 6, 8))
        assert result.current_streak == 5
        assert result.longest_streak == 5

    def test_longest_streak_preserved(self):
        result = update_streak(15, 20, date(2026, 6, 7), date(2026, 6, 8))
        assert result.current_streak == 16
        assert result.longest_streak == 20

    def test_longest_streak_updated(self):
        result = update_streak(5, 5, date(2026, 6, 7), date(2026, 6, 8))
        assert result.current_streak == 6
        assert result.longest_streak == 6

    def test_streak_bonus_percent(self):
        assert update_streak(6, 6, date(2026, 6, 7), date(2026, 6, 8)).streak_bonus_percent == 10
        assert update_streak(14, 14, date(2026, 6, 7), date(2026, 6, 8)).streak_bonus_percent == 20
        assert update_streak(29, 29, date(2026, 6, 7), date(2026, 6, 8)).streak_bonus_percent == 50
        assert update_streak(59, 59, date(2026, 6, 7), date(2026, 6, 8)).streak_bonus_percent == 75
        assert update_streak(99, 99, date(2026, 6, 7), date(2026, 6, 8)).streak_bonus_percent == 100


# ─── Integration ─────────────────────────────────────────────────────────────


class TestProcessTaskCompleted:
    def test_full_integration(self):
        user = {"id": "u1", "xp": 100, "level": 2, "streak": 6, "last_checkin_date": "2026-06-07"}
        task = {"id": "t1", "xp": 20}
        result = process_task_completed(user, task, 15000)

        assert result["xp_earned"] == 20  # streak 6, no bonus
        assert result["level"] == 2
        assert result["level_title"] == "学习者 · 坚持者"  # streak becomes 7 → suffix
        assert result["leveled_up"] is False
        assert result["new_level"] is None
        assert result["streak"] == 7
        assert result["streak_bonus"] == 10  # streak 7 qualifies for 10% bonus
        assert result["streak_bonus_title"] == "一周坚持"
        assert result["dream_value"] == 600.0  # 120 * 5
        assert result["dream_progress"] == 4.0
        assert result["easter_egg"] is None
        assert result["achievement_unlocked"] is None
        assert result["bonus_xp_total"] == 0

    def test_level_up_integration(self):
        user = {"id": "u1", "xp": 90, "level": 1, "streak": 7, "last_checkin_date": "2026-06-07"}
        task = {"id": "t1", "xp": 10}
        result = process_task_completed(user, task, 15000)

        assert result["xp_earned"] == 11  # +10% bonus
        assert result["level"] == 2
        assert result["level_title"] == "学习者 · 坚持者"
        assert result["leveled_up"] is True
        assert result["new_level"] == 2

    def test_zero_xp_task(self):
        user = {"id": "u1", "xp": 50, "level": 1, "streak": 3, "last_checkin_date": "2026-06-07"}
        task = {"id": "t1", "xp": 0}
        result = process_task_completed(user, task, 1000)

        assert result["xp_earned"] == 0
        assert result["level"] == 1
        assert result["leveled_up"] is False

    def test_streak_30_day_bonus(self):
        user = {"id": "u1", "xp": 100, "level": 2, "streak": 30, "last_checkin_date": "2026-06-07"}
        task = {"id": "t1", "xp": 20}
        result = process_task_completed(user, task, 10000)

        assert result["xp_earned"] == 30  # 50% bonus
        assert result["streak"] == 31
        assert result["streak_bonus"] == 50

    def test_same_day_no_streak_change(self):
        user = {"id": "u1", "xp": 50, "level": 1, "streak": 5, "last_checkin_date": date.today().isoformat()}
        task = {"id": "t1", "xp": 10}
        result = process_task_completed(user, task, 5000)

        assert result["streak"] == 5

    def test_none_last_checkin(self):
        user = {"id": "u1", "xp": 0, "level": 1, "streak": 0, "last_checkin_date": None}
        task = {"id": "t1", "xp": 10}
        result = process_task_completed(user, task, 5000)

        assert result["streak"] == 1
        assert result["xp_earned"] == 10


# ─── Easter Egg Tests ──────────────────────────────────────────────────────


class TestEasterEgg:
    def test_probability_distribution(self):
        random.seed(42)
        rolls = 1000
        triggered = sum(1 for _ in range(rolls) if roll_easter_egg(0) is not None)
        assert 30 <= triggered <= 100  # ~5% = 50, wide tolerance

    def test_easter_egg_never_exceeds_50_percent(self):
        random.seed(123)
        rolls = 500
        triggered = sum(1 for _ in range(rolls) if roll_easter_egg(10000) is not None)
        assert triggered <= 300  # max 50%

    def test_bonus_xp_returns_correct_range(self):
        random.seed(1)
        for _ in range(50):
            result = roll_easter_egg(0)
            if result is not None and result["type"] == "bonus_xp":
                assert result["bonus_xp"] in (5, 10, 15)

    def test_egg_type_distribution(self):
        random.seed(7)
        types = []
        for _ in range(5000):
            result = roll_easter_egg(0)
            if result is not None:
                types.append(result["type"])
        xp_count = sum(1 for t in types if t == "bonus_xp")
        res_count = sum(1 for t in types if t == "resource")
        ach_count = sum(1 for t in types if t == "achievement_check")
        total = len(types)
        # Roughly 40/40/20
        assert 0.28 <= xp_count / total <= 0.52
        assert 0.28 <= res_count / total <= 0.52
        assert 0.10 <= ach_count / total <= 0.30

    def test_resource_has_required_fields(self):
        random.seed(5)
        for _ in range(20):
            result = roll_easter_egg(0)
            if result is not None and result["type"] == "resource":
                r = result["resource"]
                assert "title" in r
                assert "url" in r
                assert "description" in r
                break

    def test_easter_egg_in_process_task_completed(self):
        random.seed(42)
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []

        user = {"id": "u1", "xp": 100, "level": 2, "streak": 0, "last_checkin_date": "2026-06-07", "longest_streak": 0}
        task = {"id": "t1", "xp": 20, "stage_id": "s1"}
        result = process_task_completed(user, task, 15000, db_session=mock_db,
                                        current_checkin_count=5,
                                        theory_completed=5, practice_completed=3,
                                        output_completed=2, total_completed=10)

        assert "easter_egg" in result
        assert "achievement_unlocked" in result
        assert "bonus_xp_total" in result


# ─── Achievement Tests ─────────────────────────────────────────────────────


class TestAchievements:
    def test_ach001_first_checkin(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []
        mock_db.query.return_value.filter.return_value.count.side_effect = lambda: 0

        context = {"is_first_checkin": True, "theory_completed": 0,
                   "practice_completed": 0, "output_completed": 0,
                   "total_completed": 0, "streak": 0}
        result = detect_achievements("u1", context, mock_db)
        keys = [a["key"] for a in result]
        assert "ACH001" in keys

    def test_ach005_streak_7(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []

        context = {"is_first_checkin": False, "theory_completed": 5,
                   "practice_completed": 5, "output_completed": 5,
                   "total_completed": 15, "streak": 7}
        result = detect_achievements("u1", context, mock_db)
        keys = [a["key"] for a in result]
        assert "ACH005" in keys

    def test_ach006_streak_30(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []

        context = {"is_first_checkin": False, "theory_completed": 10,
                   "practice_completed": 10, "output_completed": 10,
                   "total_completed": 30, "streak": 30}
        result = detect_achievements("u1", context, mock_db)
        keys = [a["key"] for a in result]
        assert "ACH006" in keys

    def test_ach008_total_50(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []

        context = {"is_first_checkin": False, "theory_completed": 20,
                   "practice_completed": 15, "output_completed": 15,
                   "total_completed": 50, "streak": 5}
        result = detect_achievements("u1", context, mock_db)
        keys = [a["key"] for a in result]
        assert "ACH008" in keys

    def test_ach002_theory_10(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []

        context = {"is_first_checkin": False, "theory_completed": 10,
                   "practice_completed": 5, "output_completed": 3,
                   "total_completed": 18, "streak": 3}
        result = detect_achievements("u1", context, mock_db)
        keys = [a["key"] for a in result]
        assert "ACH002" in keys

    def test_idempotency_already_earned(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = [("ACH001",)]

        context = {"is_first_checkin": True, "theory_completed": 0,
                   "practice_completed": 0, "output_completed": 0,
                   "total_completed": 0, "streak": 0}
        result = detect_achievements("u1", context, mock_db)
        keys = [a["key"] for a in result]
        assert "ACH001" not in keys  # already earned

    def test_threshold_ge_not_eq(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []

        context = {"is_first_checkin": False, "theory_completed": 11,  # 11 > 10
                   "practice_completed": 5, "output_completed": 3,
                   "total_completed": 19, "streak": 3}
        result = detect_achievements("u1", context, mock_db)
        keys = [a["key"] for a in result]
        assert "ACH002" in keys  # >= check should trigger


# ─── Level Display Title Tests ─────────────────────────────────────────────


class TestLevelDisplayTitle:
    def test_no_streak_suffix(self):
        info = get_level_info(150, 3)
        assert info.display_title == "学习者"

    def test_streak_7_suffix(self):
        info = get_level_info(150, 7)
        assert info.display_title == "学习者 · 坚持者"

    def test_streak_30_suffix(self):
        info = get_level_info(500, 35)
        assert info.display_title == "工程师 · 修行者"

    def test_streak_100_suffix(self):
        info = get_level_info(2500, 120)
        assert info.display_title == "长期主义者 · 传奇"

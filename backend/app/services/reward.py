"""Reward service — XP calculation, level system, dream value tracking, streak logic,
easter egg system, and achievements."""

import random
from dataclasses import dataclass, field
from datetime import date

DREAM_MULTIPLIER = 5.0

# ─── Level System ────────────────────────────────────────────────────────────

LEVEL_THRESHOLDS: list[tuple[int, str, int]] = [
    (1, "新手", 0),
    (2, "学习者", 100),
    (3, "工程师", 300),
    (4, "研究员", 600),
    (5, "独立开发者", 1000),
    (6, "长期主义者", 2000),
]


@dataclass
class LevelInfo:
    level: int
    title: str
    display_title: str
    current_xp: int
    xp_to_next_level: int
    total_xp_for_level: int


def _streak_title_suffix(streak: int) -> str | None:
    if streak >= 100:
        return "传奇"
    elif streak >= 30:
        return "修行者"
    elif streak >= 7:
        return "坚持者"
    return None


def get_level_info(total_xp: int, streak: int = 0) -> LevelInfo:
    level, title, level_base_xp = LEVEL_THRESHOLDS[0]
    for lv, lv_title, lv_base in reversed(LEVEL_THRESHOLDS):
        if total_xp >= lv_base:
            level, title, level_base_xp = lv, lv_title, lv_base
            break

    if level < len(LEVEL_THRESHOLDS):
        next_threshold = LEVEL_THRESHOLDS[level][2]
    else:
        next_threshold = level_base_xp

    if level == len(LEVEL_THRESHOLDS):
        xp_to_next = 0
    else:
        xp_to_next = next_threshold - total_xp

    suffix = _streak_title_suffix(streak)
    if suffix:
        display_title = f"{title} · {suffix}"
    else:
        display_title = title

    return LevelInfo(
        level=level,
        title=title,
        display_title=display_title,
        current_xp=total_xp - level_base_xp,
        xp_to_next_level=xp_to_next,
        total_xp_for_level=next_threshold - level_base_xp if level < len(LEVEL_THRESHOLDS) else 0,
    )


def check_level_up(old_xp: int, new_xp: int) -> int | None:
    old_info = get_level_info(old_xp)
    new_info = get_level_info(new_xp)
    if new_info.level > old_info.level:
        return new_info.level
    return None


# ─── XP Calculator ───────────────────────────────────────────────────────────


def calculate_xp(task_xp: int, current_streak: int = 0) -> int:
    if current_streak >= 100:
        bonus = 1.00
    elif current_streak >= 60:
        bonus = 0.75
    elif current_streak >= 30:
        bonus = 0.50
    elif current_streak >= 15:
        bonus = 0.20
    elif current_streak >= 7:
        bonus = 0.10
    else:
        bonus = 0.0
    return int(task_xp * (1 + bonus))


def streak_bonus_title(streak: int) -> str | None:
    if streak >= 100:
        return "百日英雄"
    elif streak >= 60:
        return "两个月"
    elif streak >= 30:
        return "一个月"
    elif streak >= 15:
        return "半个月"
    elif streak >= 7:
        return "一周坚持"
    return None


# ─── Dream Value System ──────────────────────────────────────────────────────


@dataclass
class DreamProgress:
    reward_title: str
    reward_price: int
    accumulated_value: float
    progress_percent: float
    remaining: float


def calculate_dream_progress(
    reward_price: int,
    total_xp_earned: int,
    multiplier: float = DREAM_MULTIPLIER,
) -> DreamProgress:
    if reward_price <= 0:
        return DreamProgress(
            reward_title="",
            reward_price=0,
            accumulated_value=0.0,
            progress_percent=0.0,
            remaining=0.0,
        )

    dream_value = total_xp_earned * multiplier
    progress = min(dream_value / reward_price * 100, 100.0)
    remaining_val = max(reward_price - dream_value, 0.0)

    return DreamProgress(
        reward_title="",
        reward_price=reward_price,
        accumulated_value=dream_value,
        progress_percent=round(progress, 1),
        remaining=remaining_val,
    )


# ─── Streak System ───────────────────────────────────────────────────────────


@dataclass
class StreakInfo:
    current_streak: int
    longest_streak: int
    last_checkin_date: date | None
    streak_bonus_percent: int


def _streak_bonus_percent(streak: int) -> int:
    if streak >= 100:
        return 100
    elif streak >= 60:
        return 75
    elif streak >= 30:
        return 50
    elif streak >= 15:
        return 20
    elif streak >= 7:
        return 10
    return 0


def update_streak(
    current_streak: int,
    longest_streak: int,
    last_checkin_date: date | None,
    today: date,
) -> StreakInfo:
    if last_checkin_date == today:
        new_streak = current_streak
    elif last_checkin_date is not None:
        delta = (today - last_checkin_date).days
        if delta == 1:
            new_streak = current_streak + 1
        else:
            new_streak = 1
    else:
        new_streak = 1

    new_longest = max(longest_streak, new_streak)
    return StreakInfo(
        current_streak=new_streak,
        longest_streak=new_longest,
        last_checkin_date=today,
        streak_bonus_percent=_streak_bonus_percent(new_streak),
    )


# ─── Easter Egg System ─────────────────────────────────────────────────────

EASTER_EGG_RESOURCES: list[dict] = [
    {
        "title": "量化交易入门",
        "url": "https://www.quantstart.com/",
        "description": "从零开始学习量化交易，覆盖回测、风险管理和策略开发",
        "tags": ["quant"],
    },
    {
        "title": "Python for Finance",
        "url": "https://github.com/yhilpisch/py4fi",
        "description": "Yves Hilpisch 的《Python金融编程》配套代码，覆盖金融数据分析与建模",
        "tags": ["python", "quant", "cfa"],
    },
    {
        "title": "Rust程序设计语言",
        "url": "https://doc.rust-lang.org/book/",
        "description": "Rust官方权威入门指南（The Book），覆盖所有权、生命周期等核心概念",
        "tags": ["rust"],
    },
    {
        "title": "MIT 6.006 算法导论",
        "url": "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/",
        "description": "MIT开放课程：算法与数据结构，含视频讲座和编程作业",
        "tags": ["python", "algorithm"],
    },
    {
        "title": "系统设计面试指南",
        "url": "https://github.com/donnemartin/system-design-primer",
        "description": "GitHub上最全面的系统设计学习资源，涵盖分布式系统核心概念",
        "tags": ["system-design"],
    },
    {
        "title": "CFA学习资源汇总",
        "url": "https://www.cfainstitute.org/en/programs/cfa",
        "description": "CFA官方课程大纲和学习资料入口",
        "tags": ["cfa"],
    },
    {
        "title": "深度学习专项课程（吴恩达）",
        "url": "https://www.deeplearning.ai/courses/deep-learning-specialization/",
        "description": "Andrew Ng的深度学习专项课程，5门课覆盖神经网络到序列模型",
        "tags": ["python", "ai"],
    },
    {
        "title": "The Missing Semester of Your CS Education",
        "url": "https://missing.csail.mit.edu/",
        "description": "MIT课程：补上大学计算机教育缺失的一环——Shell、Git、Vim等工具实战",
        "tags": ["tooling"],
    },
    {
        "title": "AlgoExpert — Coding Interview Prep",
        "url": "https://www.algoexpert.io/",
        "description": "系统化的编程面试刷题平台，覆盖数据结构与算法高频题",
        "tags": ["python", "algorithm"],
    },
    {
        "title": "机器学习实战（Hands-On ML）",
        "url": "https://github.com/ageron/handson-ml3",
        "description": "Aurélien Géron的《机器学习实战》第3版配套代码，基于Scikit-Learn和TensorFlow",
        "tags": ["python", "ai"],
    },
]


def roll_easter_egg(streak: int) -> dict | None:
    """
    5% base probability per checkin.
    If triggered, randomly pick:
    - 40%: bonus_xp (random +5, +10, or +15)
    - 40%: resource (pick from curated resource pool)
    - 20%: achievement_check (trigger ACH010 stage check)

    Returns None if no egg triggered.

    Streak bonus: each streak day adds 0.05% to probability, capped at 50% max.
    """
    streak_bonus = min(streak * 0.0005, 0.50)
    probability = min(0.05 + streak_bonus, 0.50)
    if random.random() > probability:
        return None

    roll = random.randint(0, 99)
    if roll < 40:
        return {"type": "bonus_xp", "bonus_xp": random.choice([5, 10, 15])}
    elif roll < 80:
        resource = random.choice(EASTER_EGG_RESOURCES)
        return {"type": "resource", "resource": resource}
    else:
        return {"type": "achievement_check"}


# ─── Achievements System ────────────────────────────────────────────────────

ACHIEVEMENTS: dict[str, dict] = {
    "ACH001": {"name": "初出茅庐", "description": "完成第一次打卡", "condition": "first_checkin", "xp_bonus": 10},
    "ACH002": {"name": "理论家", "description": "完成10个理论任务", "condition": "complete_n_theory", "condition_value": 10, "xp_bonus": 20},
    "ACH003": {"name": "实践者", "description": "完成10个实践任务", "condition": "complete_n_practice", "condition_value": 10, "xp_bonus": 20},
    "ACH004": {"name": "创作者", "description": "完成10个输出任务", "condition": "complete_n_output", "condition_value": 10, "xp_bonus": 20},
    "ACH005": {"name": "一周坚持", "description": "连续打卡7天", "condition": "streak_reach", "condition_value": 7, "xp_bonus": 15},
    "ACH006": {"name": "月度战士", "description": "连续打卡30天", "condition": "streak_reach", "condition_value": 30, "xp_bonus": 50},
    "ACH007": {"name": "百夫长", "description": "连续打卡100天", "condition": "streak_reach", "condition_value": 100, "xp_bonus": 200},
    "ACH008": {"name": "任务收割者", "description": "完成50个任务", "condition": "complete_n_total", "condition_value": 50, "xp_bonus": 30},
    "ACH009": {"name": "百战不殆", "description": "完成100个任务", "condition": "complete_n_total", "condition_value": 100, "xp_bonus": 100},
    "ACH010": {"name": "阶段完成者", "description": "完成一个阶段中的所有任务", "condition": "complete_stage", "xp_bonus": 40},
}


def _get_unlocked_keys(user_id: str, db_session) -> set[str]:
    """Return set of achievement keys already earned by user."""
    from app.models.models import Achievement
    rows = db_session.query(Achievement.achievement_key).filter(
        Achievement.user_id == user_id
    ).all()
    return {row[0] for row in rows}


def _evaluate_condition(ach: dict, context: dict, db_session) -> bool:
    cond = ach["condition"]
    val = ach.get("condition_value")

    if cond == "first_checkin":
        return context.get("is_first_checkin", False)

    elif cond == "complete_n_theory":
        return context.get("theory_completed", 0) >= val

    elif cond == "complete_n_practice":
        return context.get("practice_completed", 0) >= val

    elif cond == "complete_n_output":
        return context.get("output_completed", 0) >= val

    elif cond == "streak_reach":
        return context.get("streak", 0) >= val

    elif cond == "complete_n_total":
        return context.get("total_completed", 0) >= val

    elif cond == "complete_stage":
        stage_id = context.get("task_stage_id")
        return _is_stage_fully_complete(stage_id, db_session)

    return False


def _is_stage_fully_complete(stage_id: str, db_session) -> bool:
    """Check if all tasks in a stage are done."""
    if not stage_id:
        return False
    from app.models.models import Task
    total = db_session.query(Task).filter(Task.stage_id == stage_id).count()
    if total == 0:
        return False
    done = db_session.query(Task).filter(
        Task.stage_id == stage_id, Task.status == "done"
    ).count()
    return done == total


def detect_achievements(user_id: str, context: dict, db_session) -> list[dict]:
    """
    After checkin, detect any newly earned achievements.
    Only detects ACH001-ACH009 (ACH010 triggered by easter egg).
    Returns list of newly earned achievements with their bonus XP.
    """
    already_unlocked = _get_unlocked_keys(user_id, db_session)
    newly_unlocked = []

    for key, ach in ACHIEVEMENTS.items():
        if key in already_unlocked:
            continue
        # ACH010 is easter-egg-only
        if key == "ACH010":
            continue
        if _evaluate_condition(ach, context, db_session):
            newly_unlocked.append({
                "key": key,
                "name": ach["name"],
                "description": ach["description"],
                "xp_bonus": ach["xp_bonus"],
            })
            from app.models.models import Achievement
            db_session.add(Achievement(
                user_id=user_id,
                achievement_key=key,
            ))

    if newly_unlocked:
        db_session.flush()

    return newly_unlocked


# ─── Event Handler ───────────────────────────────────────────────────────────


def process_task_completed(
    user: dict,
    task: dict,
    reward_price: int,
    db_session=None,
    current_checkin_count: int = 0,
    theory_completed: int = 0,
    practice_completed: int = 0,
    output_completed: int = 0,
    total_completed: int = 0,
) -> dict:
    task_xp = task.get("xp", 0)
    current_streak = user.get("streak", 0)
    prev_streak = current_streak
    last_checkin_date = user.get("last_checkin_date")
    total_xp = user.get("xp", 0)
    longest_streak = user.get("longest_streak", current_streak)
    user_id = user.get("id", "u1")

    # 1. Calculate base XP with streak bonus
    xp_earned = calculate_xp(task_xp, current_streak)
    base_dream_xp = xp_earned  # dream value uses task XP only (with streak bonus)

    new_total_xp = total_xp + xp_earned

    # 2. Update streak
    today = date.today()
    if isinstance(last_checkin_date, str):
        last_checkin_date = date.fromisoformat(last_checkin_date)

    streak_info = update_streak(current_streak, longest_streak, last_checkin_date, today)

    # 3. Calculate dream progress (using task XP only)
    dream_progress = calculate_dream_progress(
        reward_price=reward_price,
        total_xp_earned=new_total_xp,
    )

    # 4. Level info
    leveled_up = check_level_up(total_xp, new_total_xp)
    new_level_info = get_level_info(new_total_xp, streak_info.current_streak)

    bonus_xp_total = 0
    easter_egg_result = None
    achievement_unlocked = None
    achievements_list = []

    if db_session is not None:
        # 5. Passive achievement detection (ACH001-ACH009)
        context = {
            "is_first_checkin": current_checkin_count == 0,
            "theory_completed": theory_completed,
            "practice_completed": practice_completed,
            "output_completed": output_completed,
            "total_completed": total_completed,
            "streak": streak_info.current_streak,
            "task_stage_id": task.get("stage_id"),
        }
        new_achievements = detect_achievements(user_id, context, db_session)
        for ach in new_achievements:
            bonus_xp_total += ach["xp_bonus"]
        achievements_list = new_achievements

        # 6. Easter egg roll
        easter_egg_result = roll_easter_egg(streak_info.current_streak)

        if easter_egg_result is not None:
            if easter_egg_result["type"] == "bonus_xp":
                bonus_xp_total += easter_egg_result["bonus_xp"]
                easter_egg_result["message"] = f"运气不错！额外获得 {easter_egg_result['bonus_xp']} XP！"
            elif easter_egg_result["type"] == "resource":
                r = easter_egg_result["resource"]
                easter_egg_result["message"] = f"发现稀有资源：《{r['title']}》——{r['description']}"
            elif easter_egg_result["type"] == "achievement_check":
                # Check ACH010
                ach010 = ACHIEVEMENTS["ACH010"]
                already = _get_unlocked_keys(user_id, db_session)
                if "ACH010" not in already:
                    ach_context = {"task_stage_id": task.get("stage_id")}
                    if _evaluate_condition(ach010, ach_context, db_session):
                        from app.models.models import Achievement as AchModel
                        db_session.add(AchModel(
                            user_id=user_id,
                            achievement_key="ACH010",
                        ))
                        db_session.flush()
                        bonus_xp_total += ach010["xp_bonus"]
                        achievements_list.append({
                            "key": "ACH010",
                            "name": ach010["name"],
                            "description": ach010["description"],
                            "xp_bonus": ach010["xp_bonus"],
                        })
                        easter_egg_result["message"] = f"隐藏成就解锁：{ach010['name']}！"
                    else:
                        easter_egg_result = None  # silent miss
                else:
                    easter_egg_result = None  # already unlocked, silent miss

        if easter_egg_result is not None:
            easter_egg_result["triggered"] = True

        # 7. Apply all bonus XP
        new_total_xp += bonus_xp_total

    # Re-check level after bonuses
    if bonus_xp_total > 0:
        leveled_up = check_level_up(total_xp, new_total_xp)
        new_level_info = get_level_info(new_total_xp, streak_info.current_streak)
        if leveled_up is not None:
            leveled_up = max(leveled_up, new_level_info.level)

    # Pick the first unlocked achievement for the response
    if achievements_list:
        ach = achievements_list[0]
        achievement_unlocked = {
            "id": ach["key"],
            "name": ach["name"],
            "xp_bonus": ach["xp_bonus"],
        }

    result = {
        "xp_earned": xp_earned + bonus_xp_total,
        "level": new_level_info.level,
        "level_title": new_level_info.display_title,
        "leveled_up": leveled_up is not None,
        "new_level": leveled_up,
        "streak": streak_info.current_streak,
        "streak_bonus": streak_info.streak_bonus_percent,
        "streak_bonus_title": streak_bonus_title(streak_info.current_streak),
        "dream_value": dream_progress.accumulated_value,
        "dream_progress": dream_progress.progress_percent,
        "dream_remaining": dream_progress.remaining,
        "easter_egg": easter_egg_result,
        "achievement_unlocked": achievement_unlocked,
        "bonus_xp_total": bonus_xp_total,
    }
    return result

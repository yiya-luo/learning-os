"""Encouragement engine — selects the most appropriate message based on user context.

5 encouragement types with priority selection algorithm.
Messages are pre-defined templates with variable substitution.
"""

import random

# ─── Type Configuration ────────────────────────────────────────────────────────

ENCOURAGEMENT_CONFIG = {
    "growth": {"icon": "🌱", "color": "#3B82F6"},
    "reward": {"icon": "🎁", "color": "#F59E0B"},
    "future": {"icon": "🔮", "color": "#8B5CF6"},
    "retrospective": {"icon": "📊", "color": "#10B981"},
    "easter_egg": {"icon": "✨", "color": "#EC4899"},
}

# ─── Message Templates ─────────────────────────────────────────────────────────

GROWTH_TEMPLATES = [
    "今天你又进步了一点。{streak}天前你还没开始这个项目。",
    "每一次打卡，都是向{reward_name}靠近的一步。",
    "学习的复利效应比你想象的更强大。坚持！",
    "你已经Level {level}了，继续加油！",
    "不积跬步，无以至千里。今天这步很稳。",
    "今天完成了{total_done}个任务，明天的你会感谢今天的自己。",
]

REWARD_TEMPLATES = [
    "你已经完成了梦想奖励的{progress}%! {reward_name}就在前方。",
    "{reward_name}越来越近了！梦想进度已达到{progress}%。",
    "看看进度条——{progress}%！每一次打卡都在靠近{reward_name}。",
    "想象一下拿到{reward_name}的感觉。还差{remaining}梦想值。",
    "进度{progress}%！{reward_name}正在向你招手。",
    "梦想奖励完成{progress}%！你已经赚了{dream_value}梦想值。",
]

FUTURE_TEMPLATES = [
    "你已经坚持了{streak}天。再过{remaining}天你就是百夫长了。",
    "阶段'{stage_name}'完成！下一个阶段更精彩。",
    "{streak}天连续打卡——你是真正的长期主义者。",
    "每一个30天都值得庆祝。你已经完成了{streak}天。",
    "完成了{stage_name}！看看接下来还有什么挑战。",
    "{streak}天，一个里程碑。下一个目标：{next_target}天。",
]

RETROSPECTIVE_TEMPLATES = [
    "项目已完成{progress}%。回头看看，你已经完成了{total_done}个任务。",
    "从零到{progress}%，你的成长轨迹令人惊叹。",
    "已完成{total_done}个任务，获得了{xp}经验值。",
    "这一路走来，{total_done}个任务见证了你的努力。",
    "回顾这{streak}天，你变得越来越强了。",
    "进度{progress}%！你正在打造一个更好的自己。",
]

EASTER_EGG_TEMPLATES = [
    "🌟 罕见的四叶草！你不仅完成了任务，还触发了隐藏奖励。",
    "🍀 幸运降临！额外获得{easter_xp}XP + 梦想值加成。",
    "✨ 隐藏彩蛋！你发现了这个项目的小秘密。",
    "🎉 惊喜时刻！系统奖励你{easter_xp}个额外经验。",
    "💫 今天运气真好！触发了一个隐藏buff。",
    "🌟 稀有奖励激活！这是属于你的幸运时刻。",
]

# ─── Main Function ─────────────────────────────────────────────────────────────


def get_encouragement(
    project_id: str,
    trigger_event: str,
    db_session,
    task_id: str | None = None,
) -> dict:
    """Select and generate an encouragement message based on user context.

    Returns:
        {"type": str, "icon": str, "color": str, "message": str, "bonus": dict | None}
    """
    from app.models.models import Project, Task, User

    user = db_session.query(User).filter(User.id == "u1").first()
    project = db_session.query(Project).filter(Project.id == project_id).first()
    if not user or not project:
        return _make_default_growth()

    streak = user.streak
    total_xp = user.xp
    total_done = (
        db_session.query(Task)
        .filter(Task.status == "done")
        .count()
    )

    # Build context for variable substitution
    ctx = {
        "streak": streak,
        "xp": total_xp,
        "dream_value": total_xp * 5.0,
        "reward_name": project.reward or "梦想奖励",
        "total_done": total_done,
        "stage_name": "",
        "project_title": project.title,
        "level": user.level,
        "remaining": max(project.reward_price - (total_xp * 5.0), 0) if project.reward_price else 100,
        "progress": int(project.progress * 100) if project else 0,
        "easter_xp": 0,
        "next_target": 0,
    }

    # Compute dream progress
    dream_progress = 0.0
    if project.reward_price and project.reward_price > 0:
        dream_progress = min((total_xp * 5.0) / project.reward_price * 100, 100.0)

    # 1. EASTER_EGG (2% flat chance) — checked FIRST
    if random.randint(0, 99) < 2:
        return _easter_egg_result(ctx)

    # 2. REWARD — dream progress thresholds
    reward_check = _check_reward_threshold(trigger_event, dream_progress, project)
    if reward_check:
        ctx["progress"] = int(reward_check)
        return _make_result("reward", ctx)

    # 3. FUTURE — streak milestones (checked AFTER streak update)
    if streak in (7, 15, 30):
        ctx["next_target"] = _next_streak_target(streak)
        return _make_result("future", ctx)

    # 4. FUTURE — stage completion
    if trigger_event == "stage_complete":
        if task_id:
            task = db_session.query(Task).filter(Task.id == task_id).first()
            if task and task.stage:
                ctx["stage_name"] = task.stage.title
        return _make_result("future", ctx)

    # 5. RETROSPECTIVE — project progress thresholds
    project_progress_pct = project.progress * 100 if project else 0
    if int(project_progress_pct) in (25, 50, 75):
        ctx["progress"] = int(project_progress_pct)
        return _make_result("retrospective", ctx)

    # 6. RETROSPECTIVE — streak divisible by 7
    if streak > 0 and streak % 7 == 0 and streak < 100:
        return _make_result("retrospective", ctx)

    # 7. GROWTH — default
    return _make_result("growth", ctx)


# ─── Helpers ───────────────────────────────────────────────────────────────────


def _make_result(enc_type: str, ctx: dict) -> dict:
    config = ENCOURAGEMENT_CONFIG[enc_type]
    message = _pick_message(enc_type, ctx)
    return {
        "type": enc_type,
        "icon": config["icon"],
        "color": config["color"],
        "message": message,
        "bonus": None,
    }


def _make_default_growth() -> dict:
    return {
        "type": "growth",
        "icon": "🌱",
        "color": "#3B82F6",
        "message": "不积跬步，无以至千里。今天这步很稳。",
        "bonus": None,
    }


def _pick_message(enc_type: str, ctx: dict) -> str:
    templates = {
        "growth": GROWTH_TEMPLATES,
        "reward": REWARD_TEMPLATES,
        "future": FUTURE_TEMPLATES,
        "retrospective": RETROSPECTIVE_TEMPLATES,
        "easter_egg": EASTER_EGG_TEMPLATES,
    }.get(enc_type, GROWTH_TEMPLATES)

    template = random.choice(templates)
    try:
        return template.format(
            streak=ctx.get("streak", 0),
            xp=ctx.get("xp", 0),
            dream_value=ctx.get("dream_value", 0),
            reward_name=ctx.get("reward_name", ""),
            total_done=ctx.get("total_done", 0),
            stage_name=ctx.get("stage_name", ""),
            project_title=ctx.get("project_title", ""),
            level=ctx.get("level", 1),
            remaining=ctx.get("remaining", 0),
            progress=ctx.get("progress", 0),
            easter_xp=ctx.get("easter_xp", 0),
            next_target=ctx.get("next_target", 0),
        )
    except (KeyError, ValueError):
        return template


def _easter_egg_result(ctx: dict) -> dict:
    xp_bonus = random.choice([5, 10, 15])
    dream_multiplier = random.choice([1.0, 1.1, 1.2])
    ctx["easter_xp"] = xp_bonus
    ctx["dream_value"] = ctx.get("dream_value", 0) * dream_multiplier

    config = ENCOURAGEMENT_CONFIG["easter_egg"]
    message = _pick_message("easter_egg", ctx)
    return {
        "type": "easter_egg",
        "icon": config["icon"],
        "color": config["color"],
        "message": message,
        "bonus": {
            "xp": xp_bonus,
            "dream_multiplier": dream_multiplier,
        },
    }


def _check_reward_threshold(trigger_event: str, dream_progress: float, project) -> int | None:
    """If dream progress just crossed a threshold, return the threshold value."""
    # For checkin events, we check if progress crossed a threshold boundary.
    # Since we don't have the "before" value here, we approximate:
    # If dream_progress is exactly at or just above a threshold, trigger reward.
    # The caller passes the current progress — this is called post-checkin.
    if trigger_event == "dream_milestone":
        if dream_progress >= 90:
            return 90
        elif dream_progress >= 75:
            return 75
        elif dream_progress >= 50:
            return 50
        elif dream_progress >= 25:
            return 25

    # For regular checkin, detect threshold crossing
    thresholds = [90, 75, 50, 25]
    for t in thresholds:
        # Simple heuristic: if progress is within 1% above the threshold
        if t <= dream_progress < t + 1:
            return t

    return None


def _next_streak_target(streak: int) -> int:
    if streak < 7:
        return 7
    elif streak < 15:
        return 15
    elif streak < 30:
        return 30
    elif streak < 100:
        return 100
    return streak + 100

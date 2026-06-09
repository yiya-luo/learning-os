# Phase 2 — Reward System Enhancement Spec v2.0

> **Status**: Ready for implementation
> **Depends on**: Phase 1 MVP (reward.py, streak system, XP/level system, dream value)
> **Target**: Backend `app/services/reward.py` + `app/models/models.py` (new tables)

---

## 1. Streak Bonus Table (Updated)

Replaces the existing 3-tier bonus in `calculate_xp()`. Expand to 6 tiers.

### 1.1 Bonus Table

| Streak Days | Bonus % | Title (Chinese) |
|-------------|---------|-----------------|
| 1–6         | 0%      | —               |
| 7–14        | 10%     | 一周坚持         |
| 15–29       | 20%     | 半个月           |
| 30–59       | 50%     | 一个月           |
| 60–99       | 75%     | 两个月           |
| 100+         | 100%    | 百日英雄         |

### 1.2 Formula

```
xp_earned = floor(task_xp * (1 + bonus_pct / 100))
```

Use integer floor — Python's `int()` cast is sufficient since `task_xp` and `bonus_pct` are non-negative integers. The multiplication result is positive, and `int()` truncates toward zero which is equivalent to floor for positive values.

### 1.3 Function Signature (Updated)

```python
def calculate_xp(task_xp: int, current_streak: int) -> int:
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
```

### 1.4 Helper: Streak Bonus Title

```python
def streak_bonus_title(streak: int) -> str | None:
    """Return bonus tier title, or None if no bonus active."""
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
```

---

## 2. Random Easter Egg System

### 2.1 Trigger Condition

- **Probability**: 5% on each successful `process_task_completed()` call.
- Implementation: `random.random() < 0.05`
- The Easter egg is rolled **after** XP is calculated and the task is marked complete, but before the response dict is assembled. It is independent of task XP or type.

### 2.2 Easter Egg Types

Three categories with distribution:

| Category | Weight | Probability |
|----------|--------|-------------|
| Extra XP  | 40     | 40%         |
| Resource   | 40     | 40%         |
| Achievement | 20    | 20%         |

Use weighted random selection. Total weight = 100. Generate a random int in [0, 99]; 0–39 → extra XP, 40–79 → resource, 80–99 → achievement unlock check.

### 2.3 Category A: Extra XP

Randomly grant +5, +10, or +15 XP with equal probability (1/3 each).

```python
def _easter_egg_xp() -> int:
    import random
    return random.choice([5, 10, 15])
```

The extra XP is added to `xp_earned` in the return dict. It does **not** count toward dream value (dream value is calculated from total_xp before the egg XP). It does count toward the user's total XP for level progression.

### 2.4 Category B: Rare Resource Recommendation

Return a curated resource from the pool defined in Section 5.

```python
def _easter_egg_resource(user_tags: list[str] | None = None) -> dict:
    """Select a resource. If user has tags, prefer matching resources."""
    import random
    from app.services.reward import EASTER_EGG_RESOURCES

    # If tags provided, filter matching resources first
    if user_tags:
        matching = [r for r in EASTER_EGG_RESOURCES
                    if any(t in r["tags"] for t in user_tags)]
        if matching:
            return random.choice(matching)

    return random.choice(EASTER_EGG_RESOURCES)
```

Return shape: `{"title": str, "url": str, "description": str}`

### 2.5 Category C: Hidden Achievement Unlock (Detection Only)

Roll for achievement unlock by calling `check_achievement_unlock()` (see Section 3). If an achievement unlocks, include it in the response. If no unlock conditions are met, the Easter egg is a "miss" — no visible effect to the user (they still see nothing special, which keeps the 5% trigger rate accurate but doesn't flood with "nothing" notifications).

---

## 3. Hidden Achievements

### 3.1 Data Model

New SQLAlchemy model:

```python
class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    achievement_key = Column(String, nullable=False)  # e.g. "ACH001"
    unlocked_at = Column(String, nullable=False, default=_now)

    # Composite unique: one user cannot unlock the same achievement twice
    __table_args__ = (
        UniqueConstraint("user_id", "achievement_key", name="uq_user_achievement"),
    )
```

A user-level `achievements` set (list of keys) can also be cached on the User model for fast lookups, but the `Achievement` table is the source of truth.

### 3.2 Achievement Definitions

```python
ACHIEVEMENTS: dict[str, dict] = {
    "ACH001": {
        "name": "初出茅庐",
        "description": "首次完成打卡",
        "condition": "first_checkin",
        "xp_bonus": 10,
    },
    "ACH002": {
        "name": "理论家",
        "description": "完成10个理论任务",
        "condition": "complete_n_theory",
        "condition_value": 10,
        "xp_bonus": 20,
    },
    "ACH003": {
        "name": "实践者",
        "description": "完成10个实践任务",
        "condition": "complete_n_practice",
        "condition_value": 10,
        "xp_bonus": 20,
    },
    "ACH004": {
        "name": "创作者",
        "description": "完成10个输出任务",
        "condition": "complete_n_output",
        "condition_value": 10,
        "xp_bonus": 20,
    },
    "ACH005": {
        "name": "一周坚持",
        "description": "连续打卡7天",
        "condition": "streak_reach",
        "condition_value": 7,
        "xp_bonus": 15,
    },
    "ACH006": {
        "name": "月度战士",
        "description": "连续打卡30天",
        "condition": "streak_reach",
        "condition_value": 30,
        "xp_bonus": 50,
    },
    "ACH007": {
        "name": "百夫长",
        "description": "连续打卡100天",
        "condition": "streak_reach",
        "condition_value": 100,
        "xp_bonus": 200,
    },
    "ACH008": {
        "name": "任务收割者",
        "description": "完成50个任务",
        "condition": "complete_n_total",
        "condition_value": 50,
        "xp_bonus": 30,
    },
    "ACH009": {
        "name": "百战不殆",
        "description": "完成100个任务",
        "condition": "complete_n_total",
        "condition_value": 100,
        "xp_bonus": 100,
    },
    "ACH010": {
        "name": "阶段完成者",
        "description": "完成一个阶段中的所有任务",
        "condition": "complete_stage",
        "xp_bonus": 40,
    },
}
```

### 3.3 Achievement Detection

Detection is split into two call sites:

#### 3.3.1 Passive detection (always runs on `process_task_completed()`)

These always check because the data is available from the current call context:

| Achievement | Trigger |
|-------------|---------|
| ACH001 | `total_checkins == 0` before this checkin |
| ACH002 | `theory_tasks_completed` reaches exactly `n` after this task |
| ACH003 | `practice_tasks_completed` reaches exactly `n` after this task |
| ACH004 | `output_tasks_completed` reaches exactly `n` after this task |
| ACH005–ACH007 | `streak` reaches exactly the threshold value |
| ACH008–ACH009 | `total_tasks_completed` reaches exactly `n` after this task |

Use `>=` not `==` to handle edge cases where a single action could skip over a threshold (e.g., batch operations in the future).

#### 3.3.2 Easter-egg-only detection (ACH010)

ACH010 requires checking whether all tasks in the current task's Stage are now complete. This is checked only during Easter egg processing (category C).

### 3.4 Detection Function

```python
def check_achievement_unlock(
    user_id: str,
    db_session,  # SQLAlchemy session
    context: dict,  # context from process_task_completed
) -> list[dict]:
    """
    Check all achievements for a user given the current context.
    Returns list of newly unlocked achievements (empty list if none).
    Each dict: {"key": "ACH001", "name": "初出茅庐", "xp_bonus": 10}
    """
    already_unlocked = _get_unlocked_keys(user_id, db_session)
    newly_unlocked = []

    for key, ach in ACHIEVEMENTS.items():
        if key in already_unlocked:
            continue
        if _evaluate_condition(ach, context, db_session):
            newly_unlocked.append({
                "key": key,
                "name": ach["name"],
                "description": ach["description"],
                "xp_bonus": ach["xp_bonus"],
            })
            # Record in DB
            db_session.add(Achievement(
                user_id=user_id,
                achievement_key=key,
                unlocked_at=_now(),
            ))

    if newly_unlocked:
        db_session.commit()

    return newly_unlocked
```

### 3.5 Condition Evaluators

```python
def _evaluate_condition(ach: dict, context: dict, db) -> bool:
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
        return _is_stage_fully_complete(stage_id, db)

    return False
```

---

## 4. Level Title Extensions

### 4.1 Display Title Format

```
"Lv.{level} {base_title} · {streak_suffix}"   if streak suffix applies
"Lv.{level} {base_title}"                      otherwise
```

### 4.2 Streak Suffix Rules

| Streak >= | Suffix    |
|-----------|-----------|
| 100       | 传奇       |
| 30        | 修行者     |
| 7         | 坚持者     |

Apply the highest-matching suffix only (not cumulative).

### 4.3 Example Displays

| XP | Streak | Display            |
|----|--------|--------------------|
| 500 | 3     | Lv.3 工程师          |
| 500 | 10    | Lv.3 工程师 · 坚持者 |
| 200 | 35    | Lv.2 学习者 · 修行者 |
| 3000 | 120  | Lv.6 长期主义者 · 传奇 |

### 4.4 Implementation

Extend `LevelInfo` dataclass with `display_title: str`:

```python
@dataclass
class LevelInfo:
    level: int
    title: str
    display_title: str      # NEW: the combined title
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
    # ... existing level logic ...
    suffix = _streak_title_suffix(streak)
    if suffix:
        display_title = f"{title} · {suffix}"
    else:
        display_title = title

    return LevelInfo(..., display_title=display_title)
```

---

## 5. Easter Egg Resource Pool

### 5.1 Data Definition

```python
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
```

### 5.2 Tag Matching Rules

- Resources are tagged with relevant domain tags: `quant`, `python`, `cfa`, `rust`, `algorithm`, `system-design`, `ai`, `tooling`.
- If a user's project/learning history has matching tags, prefer those resources (up-weight by filtering to match first, fallback to full pool).
- Tags for matching come from the project's task types and titles. For Phase 2, a simple approach: pass `user_tags` deduced from the current project's task `type` distribution (e.g., many `theory` tasks → `algorithm` tag) or from project `title` keyword match. Implementation detail — spec leaves exact tag derivation to the engineer.

---

## 6. Updated `process_task_completed()` Flow

The full flow, incorporating all Phase 2 additions:

```
process_task_completed(user, task, reward_price, db_session)
  1. Calculate base XP from task (via calculate_xp, includes streak bonus)
  2. Update streak (update_streak)
  3. Calculate dream progress (calculate_dream_progress)
  4. Check level (get_level_info, check_level_up)

  5. PASSIVE ACHIEVEMENT CHECK — always runs:
     a. Gather context: total_completed, theory_completed, practice_completed,
        output_completed, is_first_checkin, streak, task_stage_id
     b. check_achievement_unlock(user_id, db, context)
     c. Accumulate any achievement XP bonuses into xp_earned

  6. EASTER EGG ROLL — 5% probability:
     If triggered, weighted random selection:
       - Extra XP (40%):    add +5/+10/+15 to xp_earned
       - Resource (40%):    select resource from pool, include in response
       - Achievement (20%): run ACH010 check (complete_stage);
                            if unlocked, add to response + XP bonus

  7. Apply achievement XP bonuses to user's total XP
  8. Re-check level after all XP added (easter egg + achievement XP may change it)
  9. Persist user changes (XP, level, streak)
  10. Return enriched response dict
```

### 6.1 Return Dict Shape (Updated)

```python
{
    # Existing fields (unchanged)
    "xp_earned": int,           # base task XP + streak bonus + egg XP + achievement XP
    "level": int,
    "level_title": str,         # "Lv.3 工程师 · 坚持者" (with suffix)
    "leveled_up": bool,
    "new_level": int | None,
    "streak": int,
    "streak_bonus": int,
    "streak_bonus_title": str | None,   # NEW: "一周坚持", etc.
    "dream_value": float,
    "dream_progress": float,
    "dream_remaining": float,

    # Phase 2 additions
    "easter_egg": dict | None,   # { "type": "xp"|"resource"|"achievement", ... }
    "achievements": list[dict],  # newly unlocked achievements this call
}
```

---

## 7. Edge Cases and Constraints

### 7.1 Idempotency

- Each achievement must unlock at most once per user (`UniqueConstraint` on `(user_id, achievement_key)`).
- If `check_achievement_unlock()` is called and an achievement is already unlocked, skip it.
- For Easter egg achievement roll (category C): if the user has already earned ACH010 for this stage, the roll produces no result (silent miss).

### 7.2 XP Floor

- Extra XP from Easter eggs and achievements is floored to integer just like base XP.
- Total XP after all bonuses is stored as an integer.

### 7.3 Dream Value Isolation

- Dream value is calculated from the **task XP only** (base + streak bonus), not including Easter egg XP or achievement XP bonuses. This keeps dream value predictable and tied to planned tasks.

### 7.4 Rounding Verification

Test cases must confirm:
- `calculate_xp(3, 7)` → `3` (3.3 floored)
- `calculate_xp(1, 100)` → `2` (1.0 * 2.0 = 2.0, exact)
- `calculate_xp(7, 60)` → `12` (7 * 1.75 = 12.25, floored)

### 7.5 ACH010 Stage Completion

- A Stage is "fully complete" when ALL tasks in that Stage have status `done`.
- A Stage with zero tasks is trivially complete, but should NOT trigger ACH010.
- The ACH010 check fires only during Easter egg processing (not on every checkin) to limit DB cost.

### 7.6 Achievement on Streak

- ACH005–ACH007 fire when streak **reaches** the threshold value. Since streak increments by 1 each calendar day, the user will inevitably hit exactly 7, 30, 100 at some point (unless they miss a day just before, in which case they will hit it on the next run-up). Use `>=` to handle any edge case.

---

## Appendix A: Migration Notes

### A.1 New DB Table

```sql
CREATE TABLE achievements (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_key TEXT NOT NULL,
    unlocked_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(user_id, achievement_key)
);
```

### A.2 API Compatibility

- Existing API response fields remain unchanged.
- New fields (`easter_egg`, `achievements`, `streak_bonus_title`, `level_title`) are additive.
- Old clients ignoring unknown fields will continue to work (forward-compatible).

### A.3 Existing Code Changes Required

| File | Change |
|------|--------|
| `app/services/reward.py` | Expand `calculate_xp` bonus table; add `streak_bonus_title`; extend `LevelInfo`; add Easter egg logic; add achievement detection |
| `app/models/models.py` | Add `Achievement` model |
| `app/services/engine.py` | Pass `db_session` to `process_task_completed` |
| `tests/test_reward.py` | Add tests for new bonus tiers, Easter eggs, achievements |

---

## Appendix B: Test Specifications

### B.1 Streak Bonus Edge Cases

```
Input: task_xp=3, streak=100  → 3 * 2.0 = 6
Input: task_xp=1, streak=7    → 1 * 1.10 = 1 (floor)
Input: task_xp=100, streak=60 → 100 * 1.75 = 175
Input: task_xp=50, streak=0   → 50
Input: task_xp=10, streak=6   → 10
Input: task_xp=10, streak=14  → 11
Input: task_xp=10, streak=15  → 12
Input: task_xp=10, streak=29  → 12
Input: task_xp=10, streak=30  → 15
Input: task_xp=10, streak=59  → 15
Input: task_xp=10, streak=60  → 17 (floor: 17.5 → 17)
Input: task_xp=10, streak=99  → 17
Input: task_xp=10, streak=100 → 20
```

### B.2 Achievement Detection

```
ACH001: user with 0 prior checkins → unlocked
ACH002: user completes their 10th theory task → unlocked
ACH002: user completes their 11th theory task (unlocked late) → unlocked (>= check)
ACH002: already unlocked → not triggered again
ACH010: all tasks in stage "S1" done after this checkin → unlocked
ACH010: stage with zero tasks → NOT unlocked
```

### B.3 Easter Egg (Mock Random)

Seed `random.seed(42)` to verify:
- 5% trigger rate over large N (~10000 trials converging to ~500 triggers)
- Distribution of egg types (40/40/20)
- Equal distribution of +5/+10/+15 within extra XP category

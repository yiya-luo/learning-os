# Phase 3 — Advanced Features Spec v3.0

> **Status**: Ready for implementation
> **Depends on**: Phase 2 (reward system, achievements, easter eggs, heatmap)
> **Target**: `backend/app/services/encouragement.py` (new), `backend/app/api/progress.py` (extend), `backend/app/models/models.py` (extend)

---

## 1. AI Encouragement System

### 1.1 Overview

An intelligent encouragement engine that selects the most appropriate message based on user context. Messages are pre-defined templates with variable substitution — no actual AI/LLM is involved; "AI" refers to the smart selection logic.

### 1.2 Encouragement Types

| Type | Icon | Color | Trigger Context |
|------|------|-------|-----------------|
| `growth` | 🌱 | `#3B82F6` | Default daily checkin |
| `reward` | 🎁 | `#F59E0B` | Dream reward milestones |
| `future` | 🔮 | `#8B5CF6` | Streak or stage milestones |
| `retrospective` | 📊 | `#10B981` | Project progress or weekly reflection |
| `easter_egg` | ✨ | `#EC4899` | Random 2% chance, carries bonus |

### 1.3 Priority Selection Algorithm

Evaluated in order; FIRST match wins:

```
1. EASTER_EGG (2% flat chance):
   - Roll random 0-99; if result < 2, return type "easter_egg"
   - Bonus: randomly pick +5/+10/+15 XP and 1.0/1.1/1.2 dream_multiplier
   - This check runs BEFORE all others

2. REWARD (dream progress milestones):
   - Thresholds: 25%, 50%, 75%, 90%
   - Trigger when current progress just crossed a threshold

3. FUTURE — streak milestones:
   - Streak exactly hits 7, 15, or 30 days (after streak update)

4. FUTURE — stage completion:
   - trigger_event == "stage_complete"

5. RETROSPECTIVE — project progress:
   - Project crosses 25%, 50%, or 75% overall completion

6. RETROSPECTIVE — 7-day streak interval:
   - streak > 0 AND streak % 7 == 0 AND streak < 100

7. GROWTH (default):
   - Always falls through if no other condition matches
```

### 1.4 Message Templates

Each type has 6 pre-defined messages. Variables: `{streak}`, `{xp}`, `{dream_value}`, `{reward}`, `{total_done}`, `{stage_name}`, `{project_title}`, `{level}`, `{remaining}`, `{progress}`, `{easter_xp}`, `{next_target}`.

#### Growth (🌱 / blue)
```
1. "今天你又进步了一点。{streak}天前你还没开始这个项目。"
2. "每一次打卡，都是向{reward}靠近的一步。"
3. "学习的复利效应比你想象的更强大。坚持！"
4. "你已经Level {level}了，继续加油！"
5. "不积跬步，无以至千里。今天这步很稳。"
6. "今天完成了{total_done}个任务，明天的你会感谢今天的自己。"
```

#### Reward (🎁 / gold)
```
1. "你已经完成了梦想奖励的{progress}%! {reward}就在前方。"
2. "{reward}越来越近了！梦想进度已达到{progress}%。"
3. "看看进度条——{progress}%！每一次打卡都在靠近{reward}。"
4. "想象一下拿到{reward}的感觉。还差{remaining}梦想值。"
5. "进度{progress}%！{reward}正在向你招手。"
6. "梦想奖励完成{progress}%！你已经赚了{dream_value}梦想值。"
```

#### Future (🔮 / purple)
```
1. "你已经坚持了{streak}天。再过{remaining}天你就是百夫长了。"
2. "阶段'{stage_name}'完成！下一个阶段更精彩。"
3. "{streak}天连续打卡——你是真正的长期主义者。"
4. "每一个30天都值得庆祝。你已经完成了{streak}天。"
5. "完成了{stage_name}！看看接下来还有什么挑战。"
6. "{streak}天，一个里程碑。下一个目标：{next_target}天。"
```

#### Retrospective (📊 / green)
```
1. "项目已完成{progress}%。回头看看，你已经完成了{total_done}个任务。"
2. "从零到{progress}%，你的成长轨迹令人惊叹。"
3. "已完成{total_done}个任务，获得了{xp}经验值。"
4. "这一路走来，{total_done}个任务见证了你的努力。"
5. "回顾这{streak}天，你变得越来越强了。"
6. "进度{progress}%！你正在打造一个更好的自己。"
```

#### Easter Egg (✨ / pink)
```
1. "🌟 罕见的四叶草！你不仅完成了任务，还触发了隐藏奖励。"
2. "🍀 幸运降临！额外获得{easter_xp}XP + 梦想值加成。"
3. "✨ 隐藏彩蛋！你发现了这个项目的小秘密。"
4. "🎉 惊喜时刻！系统奖励你{easter_xp}个额外经验。"
5. "💫 今天运气真好！触发了一个隐藏buff。"
6. "🌟 稀有奖励激活！这是属于你的幸运时刻。"
```

### 1.5 API

**POST /api/encouragement/trigger**

Request:
```json
{
  "project_id": "a1b2c3d4",
  "trigger_event": "checkin",
  "task_id": "t1"
}
```

Response:
```json
{
  "type": "growth",
  "icon": "🌱",
  "color": "#3B82F6",
  "message": "不积跬步，无以至千里。今天这步很稳。",
  "bonus": null
}
```

`trigger_event` enum: `checkin`, `stage_complete`, `streak_milestone`, `dream_milestone`.

### 1.6 Integration Point

Called after `process_task_completed()` completes, before assembling API response. The encouragement result is included in the checkin response as an optional `encouragement` field.

---

## 2. Data Analytics

### 2.1 Overview

Provides period-over-period comparison, daily trend, task type distribution, stage progress, radar scores, and lifetime summary.

### 2.2 Periods

| Period | Current | Previous |
|--------|---------|----------|
| `week` | Mon–Sun | Previous Mon–Sun |
| `month` | 1st–end | Previous month |
| `all` | All time | First half vs second half |

### 2.3 Radar Scores (5-Axis, 0-100)

| Axis | Formula |
|------|---------|
| **completion** (完成率) | `done_tasks / total_tasks * 100` |
| **efficiency** (效率) | `min(actual_checkins / days_since_start * 100, 100)` |
| **streak** (连续) | `current_streak / max(30, longest_streak) * 100` |
| **quality** (质量) | `tasks_with_check_field / total_done * 100` |
| **speed** (速度) | `tasks_completed_before_estimate / total_done * 100` |

Edge cases: if denominator is 0, score is 0.

### 2.4 API

**GET /api/users/me/analytics?period={week|month|all}**

Returns: `period`, `current` (AnalyticsPeriodData), `previous` (AnalyticsPeriodData), `changes` (pct deltas), `trend` (daily array), `task_type_distribution` (theory/practice/output counts+percents), `stage_progress` (per-stage array), `radar` (5-axis scores), `summary` (lifetime stats).

---

## 3. Milestones

### 3.1 Overview

15 built-in milestones tracking long-term progress. Unlike achievements (which fire once and are detected), milestones are always computed — the API returns all 15 with `achieved` flags.

### 3.2 Milestone Definitions

| ID | Name | Condition | XP Bonus |
|----|------|-----------|----------|
| M001 | 首次启程 | First checkin ever | 25 |
| M002 | 周不懈怠 | Streak >= 7 | 30 |
| M003 | 月度坚守 | Streak >= 30 | 50 |
| M004 | 百日英雄 | Streak >= 100 | 200 |
| M005 | 梦想起航 | Dream progress >= 25% | 15 |
| M006 | 梦想半程 | Dream progress >= 50% | 25 |
| M007 | 梦想冲刺 | Dream progress >= 75% | 40 |
| M008 | 梦想完成 | Dream progress >= 100% | 100 |
| M009 | 初出茅庐 | Total tasks >= 10 | 20 |
| M010 | 学海无涯 | Total tasks >= 50 | 50 |
| M011 | 水滴石穿 | Total tasks >= 100 | 100 |
| M012 | 阶段推进 | First stage completed | 30 |
| M013 | 项目完成 | First project 100% | 150 |
| M014 | 全面发展 | Completed >=1 each of theory/practice/output | 25 |
| M015 | 天选之人 | Triggered >=1 easter egg | 50 |

### 3.3 API

**GET /api/users/me/milestones**

Returns sorted: achieved first (by achieved_at desc), then unachieved (by ID asc).

---

## 4. Event Timeline

### 4.1 Overview

Chronological feed of all user events: milestone unlocks, achievement earns, task checkins, stage completions.

### 4.2 Event Types

| Type | Fields |
|------|--------|
| `checkin` | task title, xp_earned, task_type |
| `milestone` | milestone name, description, icon, color, xp_bonus |
| `achievement` | achievement name, description, icon, color, xp_bonus |
| `stage` | stage title, stage_progress (100.0), tasks_completed |

### 4.3 API

**GET /api/users/me/timeline?page=1&page_size=20&filter=all**

Filter: `all` | `milestone` | `achievement` | `checkin` | `stage`.
Events sorted reverse-chronological.
Supports pagination (page, page_size, total, has_more).

---

## 5. Modified Checkin Flow (Phase 3)

```
process_task_completed(user, task, reward_price, db_session) -> enriched result
  [Phase 2 flow unchanged]
  v
After response built:
  1. POST /api/encouragement/trigger
     - Server gathers context from DB
     - Runs priority selection algorithm
     - Returns encouragement message
  2. If easter_egg type with bonus:
     - Apply bonus XP to user
     - Apply dream_multiplier bonus
  3. Attach encouragement to checkin response
```

---

## 6. Edge Cases

### 6.1 Encouragement
- Easter egg 2% chance checked FIRST — can override any other type
- Dream multiplier bonus is temporary (1.0-1.2), applied to current task only
- Stage completion check requires ALL tasks in stage done AND stage not already marked complete
- Streak milestones checked AFTER streak update in current checkin

### 6.2 Analytics
- `most_productive_day` only for `week` period
- Percentage changes: null if previous period had 0 tasks
- Radar scores: all 0 if no tasks ever done
- `favorite_type`: computed from lifetime data, not period-filtered

### 6.3 Milestones
- Always returns all 15, computed fresh each call
- `achieved_at` timestamp stored on first detection
- Milestone XP bonus is informational — actual XP awarded at detection time
- M015 (easter egg) detected from user's easter_egg trigger history

### 6.4 Timeline
- Events sorted reverse-chronological
- Pagination: default 20 per page, max 100
- Filtered at DB query level, not in-memory

---

## 7. Files to Create/Modify

### New Files
| File | Purpose |
|------|---------|
| `backend/app/services/encouragement.py` | Encouragement engine: type selection, message templates, priority algorithm |
| `backend/app/services/analytics.py` | Analytics aggregation: period comparison, radar scores, distribution |
| `backend/app/services/milestones.py` | Milestone definitions and evaluation |
| `backend/app/services/timeline.py` | Timeline event aggregation and pagination |
| `backend/tests/test_encouragement.py` | Encouragement engine tests |
| `backend/tests/test_analytics.py` | Analytics calculation tests |
| `backend/tests/test_milestones.py` | Milestone detection tests |
| `backend/tests/test_timeline.py` | Timeline pagination tests |
| `backend/tests/test_phase3_e2e.py` | Phase 3 integration tests |

### Modified Files
| File | Change |
|------|--------|
| `backend/app/api/task.py` | Attach encouragement to checkin response |
| `backend/app/api/progress.py` | Add analytics, milestones, timeline endpoints |
| `backend/app/models/models.py` | Add Milestone, TimelineEvent models if needed |

---

## 8. Test Specifications

### 8.1 Encouragement Engine
```
- Default trigger returns type "growth"
- 2% easter egg: seed random, verify type "easter_egg" with bonus
- Dream 25%/50%/75%/90% thresholds return type "reward"
- Streak 7/15/30 returns type "future"
- stage_complete event returns type "future"
- Project 25%/50%/75% returns type "retrospective"
- Streak divisible by 7 returns type "retrospective"
- Priority: easter_egg beats all others (verify with mock random)
- Easter egg bonus: verify +5/+10/+15 XP, 1.0/1.1/1.2 multiplier
```

### 8.2 Analytics
```
- weekly period returns Mon-Sun current vs previous
- monthly period returns current month vs previous month
- all-time: first half vs second half
- Period with 0 tasks -> percentage changes are null
- Radar: all zeros when no tasks
- Radar: completion = 100 when all tasks done
- Empty trend array when no data
```

### 8.3 Milestones
```
- New user: all milestones have achieved=false, achieved_count=0
- After first checkin: M001 achieved
- After 7-day streak: M002 achieved
- After 10 tasks: M009 achieved
- After completing one of each type: M014 achieved
```

### 8.4 Timeline
```
- Default page_size=20
- Filter=all returns all event types
- Filter=checkin returns only checkin events
- has_more=true when more pages exist
- Empty result when no events
- Events sorted newest first
```

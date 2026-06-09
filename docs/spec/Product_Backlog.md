# Product Backlog — Learning OS

Version: 1.0 | Date: 2026-06-08

---

## Phase 1: MVP (Core Learn-Execute Loop)

| ID | Title | Priority | Est. Effort | Dependencies | Description |
|----|-------|----------|-------------|--------------|-------------|
| P1-01 | DSL Parser — Project & Stage Parsing | P0 | 8h | None | Parse `# Project` fields and `## Stage` blocks from Markdown. Validate required fields, types, ranges. Return structured data or error list. |
| P1-02 | DSL Parser — Task Parsing & Dependency Graph | P0 | 12h | P1-01 | Parse `## Task` blocks. Validate ID format, type enum, XP range, dependency resolution (no cycles, no dangling refs). Build topological sorted task list. |
| P1-03 | DSL Import API (`POST /api/v1/plans/import`) | P0 | 6h | P1-02 | File upload endpoint. Accept multipart `.md` file, invoke parser, persist Plan+Stage+Task to SQLite, return created plan JSON. |
| P1-04 | Plan Model & SQLite Schema | P0 | 4h | None | Database tables: plans, stages, tasks, checkins. Indexes on task.depends resolution and today's-task query. Alembic/SQLAlchemy migrations. |
| P1-05 | Today's Tasks API (`GET /api/v1/tasks/today`) | P0 | 6h | P1-03, P1-04 | Query tasks where: (1) all dependencies are complete, (2) task itself not complete. Return ordered list with type/xp/check/resource. |
| P1-06 | Task Detail API (`GET /api/v1/tasks/{id}`) | P0 | 3h | P1-04 | Return single task with all fields. Include current completion status and dependency status. |
| P1-07 | Check-in API (`POST /api/v1/tasks/{id}/checkin`) | P0 | 8h | P1-04, P1-06 | Mark task complete. For `output` type, require `note` body (min 10 chars). Validate not already completed (409). Compute new total_xp. Return xp_earned, total_xp, dream_progress_pct. |
| P1-08 | Dream Reward API (`GET /api/v1/plans/{id}/reward`) | P0 | 5h | P1-07 | Return reward name, price, current XP, progress percentage, completed tasks list sorted by completion date. Handle missing reward gracefully. |
| P1-09 | UniApp Project Scaffold & Navigation | P0 | 6h | None | UniApp project init. Pages: home (today), task-detail, reward. Tab bar: Today, Reward. API client module. |
| P1-10 | Import Plan Page (Frontend) | P0 | 6h | P1-03, P1-09 | File picker for `.md` files. Upload + parse flow. Success/error toast. Navigate to today view on success. |
| P1-11 | Today's Tasks Page (Frontend) | P0 | 8h | P1-05, P1-09 | List today's ready tasks with type icon, title, XP badge. Pull-to-refresh. Tap to navigate to detail. Empty state. |
| P1-12 | Task Detail Page (Frontend) | P0 | 8h | P1-06, P1-07, P1-11 | Render task fields. Theory/practice: confirm button. Output: text input + submit. Check-in flow with XP animation. Resource link openable. |
| P1-13 | Dream Reward Page (Frontend) | P0 | 6h | P1-08, P1-09 | Reward name, price, progress bar with percentage, "remaining" text, completed tasks list. Empty state. Graceful no-reward handling. |

**Phase 1 Total Estimated Effort:** ~86 engineering hours

---

## Phase 2: XP System & Gamification

| ID | Title | Priority | Est. Effort | Dependencies | Description |
|----|-------|----------|-------------|--------------|-------------|
| P2-01 | XP Level System | P1 | 6h | P1-07 | Define XP→Level mapping (e.g. Lv1=0XP, Lv2=100XP, Lv3=250XP...). Add level field to user profile. Return level+XP on check-in. |
| P2-02 | Streak Tracking | P1 | 8h | P1-07 | Track consecutive days with at least 1 check-in. Streak bonus: +5 XP per day after 3-day streak. Display streak count and flame icon on today page. Streak reset on missed day. |
| P2-03 | Dream Reward Enhancement | P1 | 6h | P1-08, P2-01 | Visual reward unlocking animation at 100%. XP-to-CNY conversion display. Reward "locked/unlocked" state. |
| P2-04 | Learning Map Visualization | P1 | 16h | P1-11 | Interactive flowchart view of tasks and dependencies. Nodes colored by status (done/ready/blocked). Zoom/pinch support. Tap node → detail. |
| P2-05 | Weekly Summary | P1 | 8h | P1-07 | Auto-generated weekly report: XP earned, tasks completed, streak maintained, most productive day. Delivered as in-app notification every Monday. |
| P2-06 | Task Difficulty Tags | P2 | 4h | P1-02 | Optional `difficulty: easy|medium|hard` field in DSL. Affects XP multiplier (1x/1.5x/2x). Visual indicator on task cards. |
| P2-07 | Multiple Plan Support | P2 | 10h | P1-03 | User can import multiple plans. Plan switcher on home page. Tasks aggregated across active plans. Separate reward tracking per plan. |

**Phase 2 Total Estimated Effort:** ~58 engineering hours

---

## Phase 3: Intelligence & Insights

| ID | Title | Priority | Est. Effort | Dependencies | Description |
|----|-------|----------|-------------|--------------|-------------|
| P3-01 | AI Encouragement Messages | P2 | 10h | P2-01, P2-02 | LLM-generated motivational messages on check-in, streak milestones, and goal completion. Context-aware (references task type, XP progress, time remaining). Configurable tone. |
| P3-02 | Learning Analytics Dashboard | P2 | 16h | P2-05 | Charts: XP over time, tasks per day, completion rate by type, most productive time of day. Filterable by plan and date range. Export as image. |
| P3-03 | Growth Visualization | P2 | 12h | P3-02 | "Your Learning Journey" timeline. Skill radar chart based on completed task types. XP velocity trend line. Year-in-review style annual recap. |
| P3-04 | Smart Task Reordering | P2 | 8h | P1-05 | ML-based task priority suggestion based on: deadline proximity, dependency chain depth, estimated time remaining, user's historical pace. Optional opt-in. |
| P3-05 | Peer Comparison (Anonymous) | P3 | 12h | P3-02 | Opt-in anonymous leaderboard. Percentile ranking. Comparison by plan category. Privacy-first: no PII, minimum cohort size of 10. |
| P3-06 | Custom Check-in Templates | P2 | 6h | P1-07 | User can define custom check-in forms per task type. E.g., theory tasks could require note-taking template (key concepts, questions, summary). |
| P3-07 | Export & Backup | P2 | 8h | P1-03 | Export plan as DSL Markdown (round-trip). Export progress data as JSON/CSV. Automatic daily backup to local storage. |

**Phase 3 Total Estimated Effort:** ~72 engineering hours

---

## Summary

| Phase | Items | Est. Hours | Theme |
|-------|-------|-----------|-------|
| Phase 1 (MVP) | 13 | 86 | Core learn-execute loop: import → plan → do → check-in → reward |
| Phase 2 | 7 | 58 | XP system, streaks, learning map, multi-plan support |
| Phase 3 | 7 | 72 | AI encouragement, analytics, growth visualization, smart features |
| **Total** | **27** | **216** | |

---

## Priority Definitions

| Priority | Meaning |
|----------|---------|
| P0 | Must ship in Phase 1. Blocks all downstream features. |
| P1 | Ships in Phase 2. Important but not launch-blocking. |
| P2 | Ships in Phase 2 or 3. Nice to have, clear user value. |
| P3 | Phase 3 stretch goal. Requires user base for validation. |

## Estimation Notes

- Estimates assume one full-time full-stack engineer.
- Includes unit testing and basic error handling.
- Does NOT include: CI/CD setup, production deployment, security audit, performance optimization.
- Frontend estimates assume familiarity with UniApp/Vue 3.

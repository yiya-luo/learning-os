# Test Cases v1.0 — Learning OS Phase 1 MVP

Version: 1.0 | Date: 2026-06-08 | Author: QA

Total: 30 test cases. Distribution: Parser 8 | Engine 6 | Reward 5 | API 3 | Frontend 8.

---

## Module 1: Parser (TC-01 through TC-08, 8 cases)

---

### TC-01: Import valid complete DSL — parse success, return project tree

- **ID**: TC-01
- **Module**: Parser
- **Title**: Import valid complete DSL — parse success, return project tree
- **Priority**: P0
- **Preconditions**:
  - Parser module is loaded
  - `quant_trading.md` fixture (F-01) is available
- **Steps**:
  1. Read `quant_trading.md` contents as UTF-8 string
  2. Call `parse(markdown_text)`
  3. Inspect the returned `ParsedProject` object
- **Expected Result**:
  - Parse succeeds (no exception raised)
  - `project.title` == `"从0学习量化交易"`
  - `project.description` starts with `"系统学习量化交易"`
  - `project.reward` == `"Mac Studio"`, `project.reward_price` == `15000`
  - `project.deadline` == `180`
  - `len(project.stages)` == `4`
  - Stage 0 title == `"基础准备"`, contains 4 tasks (T001–T004)
  - Total task count == `17`
  - T001 type == `"practice"`, xp == `10`, estimate == `60`
  - T013 depends == `["T012", "T006"]`
- **Test Data**: F-01 (`quant_trading.md`)

---

### TC-02: Import empty file — error "DSL content is empty"

- **ID**: TC-02
- **Module**: Parser
- **Title**: Import empty file — error "DSL content is empty"
- **Priority**: P1
- **Preconditions**: Parser module is loaded
- **Steps**:
  1. Call `parse("")` with an empty string
  2. Catch the raised exception or inspect error list
- **Expected Result**:
  - Parse fails
  - Error with code `E010` (MISSING_PROJECT) or message containing "empty"
  - HTTP equivalent: 400 `{"error": "PARSE_ERROR", "message": "DSL content is empty"}`
- **Test Data**: N/A (empty string)

---

### TC-03: Import DSL missing project title — error with line number

- **ID**: TC-03
- **Module**: Parser
- **Title**: Import DSL missing project title — error with line number
- **Priority**: P1
- **Preconditions**: Parser module is loaded
- **Steps**:
  1. Construct DSL with `# Project` heading but no `title:` field:
     ```
     # Project
     description: A test plan
     deadline: 30
     ---
     ```
  2. Call `parse(markdown_text)`
- **Expected Result**:
  - Parse fails, error code == `E001` (MISSING_REQUIRED_FIELD)
  - References field `"title"`
  - Message: `"Missing required field 'title' in Project block"`
  - Line number is reported (line 1 or 2)
- **Test Data**: Inline DSL (constructed in test)

---

### TC-04: Import task missing id — error

- **ID**: TC-04
- **Module**: Parser
- **Title**: Import task missing id — error
- **Priority**: P1
- **Preconditions**: Parser module is loaded
- **Steps**:
  1. Construct DSL where a task block has no `id:` field:
     ```
     # Project
     title: Test
     description: Testing missing ID
     deadline: 30
     ---
     ## Stage
     title: Stage 1
     ## Task
     title: Task Without ID
     type: theory
     xp: 10
     ```
  2. Call `parse(markdown_text)`
- **Expected Result**:
  - Parse fails, error code == `E001`
  - References field `"id"` in task context
  - Line number corresponds to the `## Task` heading
- **Test Data**: Inline DSL (constructed in test)

---

### TC-05: Import task with invalid type ("reading") — error

- **ID**: TC-05
- **Module**: Parser
- **Title**: Import task with invalid type ("reading") — error
- **Priority**: P1
- **Preconditions**: Parser module is loaded
- **Steps**:
  1. Construct DSL with `type: reading` (invalid):
     ```
     # Project
     title: Test
     description: Invalid type test
     deadline: 30
     ---
     ## Task
     id: T001
     title: Read something
     type: reading
     xp: 10
     ```
  2. Call `parse(markdown_text)`
- **Expected Result**:
  - Parse fails, error code == `E011` (INVALID_ENUM_VALUE)
  - Message includes: `"Invalid value 'reading' for field 'type'. Expected one of: theory, practice, output"`
  - Line number corresponds to `type: reading`
- **Test Data**: Inline DSL (constructed in test)

---

### TC-06: Import DSL with circular dependency (T001→T002→T001) — error

- **ID**: TC-06
- **Module**: Parser
- **Title**: Import DSL with circular dependency (T001→T002→T001) — error
- **Priority**: P1
- **Preconditions**: Parser module is loaded
- **Steps**:
  1. Construct DSL with circular dependency:
     ```
     # Project
     title: Circular Dep Test
     description: Testing cycle detection
     deadline: 30
     ---
     ## Task
     id: T001
     title: First task
     type: theory
     xp: 10
     depends: T002
     ## Task
     id: T002
     title: Second task
     type: theory
     xp: 10
     depends: T001
     ```
  2. Call `parse(markdown_text)`
- **Expected Result**:
  - Parse fails, error code == `E006` (DEPENDENCY_CYCLE)
  - Message: `"Dependency cycle detected: T001 -> T002 -> T001"`
- **Test Data**: Inline DSL (constructed in test)

---

### TC-07: Import DSL with nested stages — correct hierarchy

- **ID**: TC-07
- **Module**: Parser
- **Title**: Import DSL with nested stages — correct hierarchy
- **Priority**: P1
- **Preconditions**: Parser module loaded; F-01 available
- **Steps**:
  1. Parse `quant_trading.md`
  2. Inspect stage and task hierarchy
- **Expected Result**:
  - Stage 0 "基础准备" index == 0, tasks: T001–T004 in order
  - Stage 1 "数据获取与处理" index == 1, tasks: T005–T008
  - Stage 2 "策略开发" index == 2, tasks: T009–T013
  - Stage 3 "风险管理与实盘" index == 3, tasks: T014–T017
  - No cross-stage task leakage
- **Test Data**: F-01 (`quant_trading.md`)

---

### TC-08: Import large DSL (500+ tasks) — parse time < 2 seconds

- **ID**: TC-08
- **Module**: Parser
- **Title**: Import large DSL (500+ tasks) — parse time < 2 seconds
- **Priority**: P2
- **Preconditions**: Parser module loaded
- **Steps**:
  1. Programmatically generate valid DSL: 500 tasks across 20 stages, each T001–T500
  2. Record `time.perf_counter()` before and after `parse()`
  3. Assert elapsed and structure
- **Expected Result**:
  - Parse succeeds, elapsed < 2.0s
  - Returned object has exactly 500 tasks across 20 stages
- **Test Data**: Programmatically generated 500-task DSL

---

## Module 2: Task Engine (TC-09 through TC-14, 6 cases)

---

### TC-09: pending → doing → done normal flow

- **ID**: TC-09
- **Module**: Engine
- **Title**: pending → doing → done normal flow
- **Priority**: P0
- **Preconditions**: Task Engine initialized with empty test DB; task with `status = "pending"`, no deps inserted
- **Steps**:
  1. `engine.start(task_id)` — pending → doing
  2. Assert status == `"doing"`, `started_at` is set
  3. `engine.checkin(task_id)` — doing → done
  4. Assert status == `"done"`, `completed_at` is set
- **Expected Result**:
  - Both transitions succeed
  - `started_at` and `completed_at` are UTC ISO 8601 timestamps
  - `previous_status` matches the prior state
- **Test Data**: F-03 (`rust_lang.md`), T001 (no deps)

---

### TC-10: done → doing illegal — TaskStateError

- **ID**: TC-10
- **Module**: Engine
- **Title**: done → doing illegal — TaskStateError
- **Priority**: P0
- **Preconditions**: Task Engine initialized; task in `"done"` status
- **Steps**:
  1. Set up task with `status = "done"`
  2. Attempt `engine.start(task_id)` on done task
- **Expected Result**:
  - Fails with `INVALID_TRANSITION` error
  - `current_status` == `"done"`, `required_status` == `"pending"`
  - HTTP: 409 Conflict
- **Test Data**: F-03, any task manually set to done

---

### TC-11: Task with unmet depends — cannot set to doing

- **ID**: TC-11
- **Module**: Engine
- **Title**: Task with unmet depends — cannot set to doing
- **Priority**: P0
- **Preconditions**: T001 pending (no deps); T004 pending, depends = `["T001"]`
- **Steps**:
  1. Attempt `engine.start(T004_id)` while T001 is still pending
- **Expected Result**:
  - Fails with `DEPENDENCY_BLOCKED`
  - `blocked_by` == `["T001"]`
  - HTTP: 409 Conflict
- **Test Data**: F-01 (`quant_trading.md`), T004 depends on T001

---

### TC-12: Task with all depends done — becomes available

- **ID**: TC-12
- **Module**: Engine
- **Title**: Task with all depends done — becomes available
- **Priority**: P0
- **Preconditions**: T001 pending; T004 depends = `["T001"]`
- **Steps**:
  1. Complete T001: `start(T001)` → `checkin(T001)`
  2. `engine.start(T004)` — deps now satisfied
- **Expected Result**:
  - T004 transitions to `"doing"` successfully
  - No `DEPENDENCY_BLOCKED`
- **Test Data**: F-01, chain T001 → T004

---

### TC-13: Today tasks only show available (not done, deps met)

- **ID**: TC-13
- **Module**: Engine
- **Title**: Today tasks only show available (not done, deps met)
- **Priority**: P0
- **Preconditions**: F-02 `cfa_prep.md` imported; all tasks `"pending"`
- **Steps**:
  1. Call `get_today_tasks(project_id)` — initial state
  2. Complete T001: `start(T001)` → `checkin(T001)`
  3. Call `get_today_tasks(project_id)` again
- **Expected Result**:
  - First call: T001, T002, T003, T004 returned (no unmet deps)
  - T005 (depends on T004) is blocked; T011 (depends on T010,T006,T001) is blocked
  - Second call: T001 NOT in list (done); tasks in DSL `sort_order`
- **Test Data**: F-02 (`cfa_prep.md`)

---

### TC-14: Today tasks ordered by sort_order, cumulative estimate displayed

- **ID**: TC-14
- **Module**: Engine
- **Title**: Today tasks ordered by sort_order, cumulative estimate displayed
- **Priority**: P2
- **Preconditions**: F-01 `quant_trading.md` imported; all tasks `"pending"`
- **Steps**:
  1. Call `get_today_tasks(project_id)`
  2. Verify ordering and estimate fields
- **Expected Result**:
  - Tasks ordered by `sort_order` (DSL appearance)
  - Each task includes `estimate` field when set
  - T001 (est 60), T002 (est 120), T003 (est 90) — all returned as available
- **Test Data**: F-01 (`quant_trading.md`)

---

## Module 3: Reward System (TC-15 through TC-19, 5 cases)

---

### TC-15: Complete 20XP task — earn 20XP

- **ID**: TC-15
- **Module**: Reward
- **Title**: Complete 20XP task — earn 20XP
- **Priority**: P0
- **Preconditions**: User total_xp = 0, level = 1, streak = 1; task with xp = 20 in `"doing"`
- **Steps**:
  1. `checkin(task_id)` on 20 XP task
  2. Inspect response
  3. `GET /api/users/me/xp` to verify persistence
- **Expected Result**:
  - `xp_earned` == `20`, `new_total_xp` == `20`
  - `dream_value_earned` == `100` (XP * 5.0 per spec)
  - Level remains 1 (XP < 100)
- **Test Data**: F-03 (`rust_lang.md`), T003 (xp: 20)

---

### TC-16: 7-day streak — XP bonus +10%

- **ID**: TC-16
- **Module**: Reward
- **Title**: 7-day streak — XP bonus +10%
- **Priority**: P1
- **Preconditions**: User current_streak == 6 (6 consecutive days of check-ins); task xp = 20 in `"doing"`
- **Steps**:
  1. Simulate 6 backdated check-in records
  2. Verify `current_streak` == `6`
  3. Perform today's check-in on 20 XP task
- **Expected Result**:
  - `xp_earned` == `22` (20 * 1.10)
  - `new_total_xp` reflects boosted amount
  - `streak` == `7`
- **Test Data**: F-03, backdated records + 1 today task

---

### TC-17: 30-day streak — XP bonus +50%

- **ID**: TC-17
- **Module**: Reward
- **Title**: 30-day streak — XP bonus +50%
- **Priority**: P1
- **Preconditions**: User current_streak == 29; task xp = 10 in `"doing"`
- **Steps**:
  1. Simulate 29 consecutive days of check-ins
  2. Perform today's check-in on 10 XP task
- **Expected Result**:
  - `xp_earned` == `15` (10 * 1.50)
  - `streak` == `30`
- **Test Data**: F-03, backdated records

---

### TC-18: Break streak (no checkin yesterday) — streak = 1

- **ID**: TC-18
- **Module**: Reward
- **Title**: Break streak (no checkin yesterday) — streak = 1
- **Priority**: P0
- **Preconditions**: User had streak of 4; no check-in yesterday
- **Steps**:
  1. Simulate check-ins on D-5, D-4, D-3, D-2
  2. Skip D-1 (yesterday)
  3. Perform check-in today (D)
- **Expected Result**:
  - `streak` == `1` (reset)
  - `longest_streak` stays at `4`
  - XP NOT multiplied (base only, no bonus)
- **Test Data**: F-03, backdated records with skip

---

### TC-19: XP reaches 100 — level up to Lv2

- **ID**: TC-19
- **Module**: Reward
- **Title**: XP reaches 100 — level up to Lv2
- **Priority**: P0
- **Preconditions**: User total_xp = 90, level = 1; task xp = 20 in `"doing"`
- **Steps**:
  1. Set user's total_xp to 90
  2. Complete 20 XP task
  3. Inspect `new_level` and `xp_to_next_level`
- **Expected Result**:
  - `new_total_xp` == `110`
  - `new_level` == `2`
  - Level formula: `level = floor(total_xp / 100) + 1`
  - `xp_to_next_level` (to Lv3) correctly calculated
- **Test Data**: F-03, any 20 XP task

---

## Module 4: API Integration (TC-20 through TC-22, 3 cases)

---

### TC-20: POST /api/projects/import — full flow success

- **ID**: TC-20
- **Module**: API
- **Title**: POST /api/projects/import — full flow success
- **Priority**: P0
- **Preconditions**: FastAPI server running; empty DB; F-01 loaded as string
- **Steps**:
  1. `POST /api/projects/import` with `{"markdown": "<quant_trading.md content>"}`
  2. Inspect 201 response
  3. `GET /api/projects/{pid}` to verify persistence
- **Expected Result**:
  - HTTP 201; `project_id` is valid UUID
  - `title` == `"从0学习量化交易"`, `stage_count` == `4`, `task_count` == `17`
  - All tasks and stages persisted in SQLite
- **Test Data**: F-01 (`quant_trading.md`)

---

### TC-21: POST /api/tasks/{tid}/checkin — full flow + schema conformance

- **ID**: TC-21
- **Module**: API
- **Title**: POST /api/tasks/{tid}/checkin — full flow + schema conformance
- **Priority**: P0
- **Preconditions**: F-03 imported; T001 started (`"doing"`); T001 xp = 5; user XP = 0, streak = 1
- **Steps**:
  1. `POST /api/tasks/{T001_id}/checkin`
  2. Inspect 200 response against `CheckinResponse` schema
  3. `GET /api/users/me/xp` for persistence
- **Expected Result**:
  - HTTP 200; `status` == `"done"`, `previous_status` == `"doing"`
  - `xp_earned` == `5`, `streak` >= 1
  - `completed_at` is valid UTC ISO 8601
  - `GET /api/users/me/xp`: `total_xp` == `5`, `total_tasks_completed` == `1`
  - Double check-in on same task → 409 Conflict
- **Test Data**: F-03 (`rust_lang.md`), T001

---

### TC-22: GET /api/projects/{pid}/tasks/today — correct task list + blocked flags

- **ID**: TC-22
- **Module**: API
- **Title**: GET /api/projects/{pid}/tasks/today — correct task list + blocked flags
- **Priority**: P0
- **Preconditions**: F-02 `cfa_prep.md` imported; all tasks `"pending"`; T004 completed
- **Steps**:
  1. `GET /api/projects/{pid}/tasks/today`
  2. Inspect response
- **Expected Result**:
  - HTTP 200; `date` == today YYYY-MM-DD
  - T001 in list, `blocked: false`; T005 in list, `blocked: false` (T004 done)
  - T006 `blocked: true` (T003 not done)
  - T004 NOT in list (done)
  - Ordered by `sort_order`
- **Test Data**: F-02 (`cfa_prep.md`)

---

## Module 5: Frontend / UI (TC-23 through TC-30, 8 cases)

---

### TC-23: Home page loads showing level + today tasks + dream progress

- **ID**: TC-23
- **Module**: Frontend
- **Title**: Home page loads showing level + today tasks + dream progress
- **Priority**: P0
- **Preconditions**: UniApp running; F-01 imported; some tasks completed (nonzero XP)
- **Steps**:
  1. Launch app / navigate to Home tab
  2. Wait for API calls to resolve
  3. Inspect rendered UI
- **Expected Result**:
  - User level displayed (e.g., "Lv.1" badge)
  - Today's tasks as cards: type icon (book/repeat/file), title, XP badge, estimate
  - Dream reward progress bar visible with correct percentage
  - No stuck spinners or error toasts
- **Test Data**: F-01 (`quant_trading.md`)

---

### TC-24: Check-in button → animation plays → status updates

- **ID**: TC-24
- **Module**: Frontend
- **Title**: Check-in button → animation plays → status updates
- **Priority**: P0
- **Preconditions**: Theory/practice task in `"doing"`; user on task detail page
- **Steps**:
  1. Open task detail for a `"doing"` theory task
  2. Tap "Mark Complete" button
  3. Observe animation
  4. Observe updated state
- **Expected Result**:
  - Animation: "+<xp> XP" badge floats up + fades (~1.5s total)
  - Task status changes to done (checkmark / strikethrough)
  - Button is disabled or hidden
  - Return to today view: task no longer appears
  - Dream progress bar updates
- **Test Data**: F-03 (`rust_lang.md`), T002 (theory, 10 XP)

---

### TC-25: Output-type task — requires text input before check-in

- **ID**: TC-25
- **Module**: Frontend
- **Title**: Output-type task — requires text input before check-in
- **Priority**: P0
- **Preconditions**: An `output` type task in `"doing"` status; user on task detail page
- **Steps**:
  1. Open task detail for `"doing"` output task
  2. Observe UI: text input field visible (placeholder: "描述你的产出...")
  3. Try submitting with empty input (< 10 chars)
  4. Enter 10+ chars and submit
- **Expected Result**:
  - Text input visible with placeholder
  - Submit button disabled or shows error when < 10 chars (client-side validation)
  - Server also rejects < 10 chars with 422/400
  - Submit succeeds with >= 10 chars → check-in animation plays
  - Theory/practice tasks do NOT show text input (only button)
- **Test Data**: F-01, T008 (output type)

---

### TC-26: DSL import page: paste markdown → preview → confirm import

- **ID**: TC-26
- **Module**: Frontend
- **Title**: DSL import page: paste markdown → preview → confirm import
- **Priority**: P0
- **Preconditions**: Clean state (no projects); user on Import tab
- **Steps**:
  1. Navigate to Import tab
  2. Paste `rust_lang.md` content into text area
  3. Tap "Import" / "确认导入"
  4. Observe success toast
  5. Navigate to Projects tab
- **Expected Result**:
  - Text area accepts pasted content
  - Loading spinner during API call
  - 201: toast "Import successful: Rust语言系统学习"
  - Project appears in project list
  - 400 error: toast shows API error message
  - Empty text area + tap: client-side validation error
- **Test Data**: F-03 (`rust_lang.md`)

---

### TC-27: Dream reward page shows correct progress percentage

- **ID**: TC-27
- **Module**: Frontend
- **Title**: Dream reward page shows correct progress percentage
- **Priority**: P0
- **Preconditions**: F-01 imported (reward: "Mac Studio", price: 15000); completed T001 (10 XP) + T002 (15 XP); dream_value = 25 * 5.0 = 125
- **Steps**:
  1. Navigate to Reward tab
  2. Observe progress display
- **Expected Result**:
  - Name: "Mac Studio", Price: "15,000元"
  - Progress: `(125 / 15000) * 100` = `0.83%`
  - Text: "还差 14,875 元"
  - Completed tasks list: T001 + T002 with XP and dates (newest first)
  - Empty state (no completions): "还没有完成任务，开始学习吧！"
  - No reward defined: "未设置奖励"
- **Test Data**: F-01, completed T001 + T002

---

### TC-28: Bottom tab navigation switches between 5 tabs correctly

- **ID**: TC-28
- **Module**: Frontend
- **Title**: Bottom tab navigation switches between 5 tabs correctly
- **Priority**: P1
- **Preconditions**: UniApp running; at least 1 project imported
- **Steps**:
  1. Observe bottom tab bar (5 tabs expected)
  2. Tap each in sequence: Today → Projects → Import → Reward → Profile
  3. Verify active tab highlighted and page content changes
  4. Tap same tab again → returns to root
  5. Rapid switching: 5 taps in 3 seconds
- **Expected Result**:
  - 5 tabs: 今天 / 项目 / 导入 / 奖励 / 我的
  - Active tab highlighted correctly
  - Each page renders correct content
  - Re-tap scrolls to top / resets
  - No white screens or crashes on rapid switching
  - Tab bar stays fixed at bottom
- **Test Data**: F-01 (`quant_trading.md`)

---

### TC-29: Task detail page — all three type variants render correctly

- **ID**: TC-29
- **Module**: Frontend
- **Title**: Task detail page — all three type variants render correctly
- **Priority**: P1
- **Preconditions**: F-03 imported; one task each of theory, practice, output available
- **Steps**:
  1. Tap a `theory` task card → inspect detail page
  2. Tap a `practice` task card → inspect detail page
  3. Tap an `output` task card → inspect detail page
- **Expected Result**:
  - All pages show: title, type label, XP, estimate, check criteria
  - `theory`: shows "Mark Complete" button, NO text input
  - `practice`: shows "Mark Complete" button, NO text input
  - `output`: shows text input + submit button
  - Resource link (if present) is tappable → opens system browser
  - Resource link not present → link section hidden (no broken UI)
- **Test Data**: F-03, T003 (theory), T005 (practice), T010 (output)

---

### TC-30: Streak and level display on profile page

- **ID**: TC-30
- **Module**: Frontend
- **Title**: Streak and level display on profile page
- **Priority**: P1
- **Preconditions**: User has streak = 5, level = 2, total XP = 150; at least 1 project
- **Steps**:
  1. Navigate to Profile tab
  2. Inspect XP, level, streak displays
  3. Verify values match API response `GET /api/users/me`
  4. Check `GET /api/users/me/streak` values match display
- **Expected Result**:
  - Level correctly displayed as "Lv.2"
  - XP: "150 XP", streak: "5 days"
  - `checked_in_today` matches current state
  - `longest_streak` shown (if different from current)
  - Data refreshes after completing a task and returning to profile
- **Test Data**: F-03, sufficient completions for streak = 5, XP = 150

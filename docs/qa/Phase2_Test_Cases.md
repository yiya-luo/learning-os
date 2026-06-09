# Test Cases v2.0 — Learning OS Phase 2

Version: 2.0 | Date: 2026-06-08 | Author: QA

Total: 20 new test cases (TC-31 through TC-50). Distribution: Reward 9 | API 7 | Frontend 4.

---

## Module 6: Reward — Streak Bonus (TC-31 to TC-33)

---

### TC-31: Streak reaches 60 days — XP bonus = +75%

- **ID**: TC-31
- **Module**: Reward
- **Title**: Streak reaches 60 days — XP bonus = +75%
- **Priority**: P0
- **Preconditions**:
  - User `current_streak` == 59 (59 consecutive days of check-ins)
  - Task with `xp = 10` in `"doing"` status
  - Reward module `calculate_xp()` available
- **Steps**:
  1. Simulate 59 backdated daily check-in records for the user
  2. Verify `current_streak` == `59`
  3. Call `calculate_xp(task_xp=10, current_streak=59)` to confirm pre-transition bonus (50% tier)
  4. Perform today's check-in on the 10 XP task (streak advances from 59 → 60)
  5. Inspect `xp_earned` and `streak_bonus` in the response
- **Expected Result**:
  - Pre-check: `calculate_xp(10, 59)` returns `15` (10 * 1.50 = 15, floor)
  - Post-check: `streak` == `60`
  - `xp_earned` == `17` (10 * 1.75 = 17.5 → floor to 17)
  - `streak_bonus` == `75`
  - `streak_bonus_title` == `"两个月"`
- **Test Data**: Synthetic backdated check-in records 59 days; a 10 XP task

---

### TC-32: Streak reaches 100 days — XP bonus = +100%

- **ID**: TC-32
- **Module**: Reward
- **Title**: Streak reaches 100 days — XP bonus = +100%
- **Priority**: P0
- **Preconditions**:
  - User `current_streak` == 99 (99 consecutive days)
  - Task with `xp = 10` in `"doing"` status
- **Steps**:
  1. Simulate 99 backdated daily check-in records for the user
  2. Verify `current_streak` == `99`
  3. Call `calculate_xp(task_xp=10, current_streak=99)` to confirm pre-transition bonus (75% tier)
  4. Perform today's check-in (streak advances from 99 → 100)
  5. Inspect response fields
- **Expected Result**:
  - Pre-check: `calculate_xp(10, 99)` returns `17` (10 * 1.75 = 17.5 → floor to 17)
  - Post-check: `streak` == `100`
  - `xp_earned` == `20` (10 * 2.00 = 20, exact)
  - `streak_bonus` == `100`
  - `streak_bonus_title` == `"百日英雄"`
- **Test Data**: Synthetic backdated check-in records 99 days; a 10 XP task

---

### TC-33: Bonus XP rounded down (floor, not round)

- **ID**: TC-33
- **Module**: Reward
- **Title**: Bonus XP rounded down (floor, not round)
- **Priority**: P1
- **Preconditions**:
  - Reward module `calculate_xp()` available
  - Various streak values available via backdated records or direct function calls
- **Steps**:
  1. Call `calculate_xp(3, 7)` — 3 * 1.10 = 3.3
  2. Call `calculate_xp(1, 7)` — 1 * 1.10 = 1.1
  3. Call `calculate_xp(7, 60)` — 7 * 1.75 = 12.25
  4. Call `calculate_xp(1, 100)` — 1 * 2.00 = 2.00
  5. Call `calculate_xp(11, 15)` — 11 * 1.20 = 13.2
- **Expected Result**:
  - `calculate_xp(3, 7)` returns `3` (3.3 floored, not rounded to 3)
  - `calculate_xp(1, 7)` returns `1` (1.1 floored, not rounded to 1)
  - `calculate_xp(7, 60)` returns `12` (12.25 floored, not rounded to 12)
  - `calculate_xp(1, 100)` returns `2` (2.00 exact)
  - `calculate_xp(11, 15)` returns `13` (13.2 floored, not rounded to 13)
  - All results computed via Python `int()` cast or equivalent floor operation
- **Test Data**: N/A (pure function calls)

---

## Module 7: Reward — Easter Egg System (TC-34 to TC-36)

---

### TC-34: 1000 check-ins — easter egg triggers ~5% (+-2% tolerance)

- **ID**: TC-34
- **Module**: Reward
- **Title**: 1000 check-ins — easter egg triggers ~5% (+-2% tolerance)
- **Priority**: P2
- **Preconditions**:
  - `random.seed()` can be reset for reproducibility
  - `process_task_completed()` is callable in a loop
  - Sufficient tasks available for repeated check-ins (or mocked `random.random`)
- **Steps**:
  1. Set `random.seed(42)` for deterministic output
  2. Execute 1000 `process_task_completed()` calls (simulate 1000 check-ins)
  3. Count the number of calls where `easter_egg` is not null in the response
  4. Calculate trigger rate: `count / 1000 * 100`
- **Expected Result**:
  - Trigger count is between 30 and 70 (3%–7%, allowing +-2% tolerance around 5%)
  - With `seed(42)`, count ≈ 49–52 (approximately 5%)
  - Each trigger response includes a non-null `easter_egg` dict with valid `type`
- **Test Data**: 1000 synthetic check-ins with controlled random seed

---

### TC-35: Easter egg bonus_xp returns +5, +10, or +15 only

- **ID**: TC-35
- **Module**: Reward
- **Title**: Easter egg bonus_xp returns +5, +10, or +15 only
- **Priority**: P1
- **Preconditions**:
  - Easter egg system initialized
  - Mocked random to force Extra XP type (category A), then iterate over XP values
- **Steps**:
  1. Force Easter egg type to Extra XP (mock `random.randint(0, 99)` to return a value in 0–39)
  2. Run 300 Easter egg XP rolls with fixed seed
  3. Collect all `bonus_xp` values returned
  4. Assert on value distribution
- **Expected Result**:
  - All returned `bonus_xp` values are in `{5, 10, 15}` only
  - No other values appear (no 0, no 20, no negative)
  - Distribution is roughly equal across 5/10/15 (each ~33% +-10% tolerance, 300 trials)
- **Test Data**: Controlled random seed, 300 Extra XP rolls

---

### TC-36: Easter egg resource type returns valid resource with title/url/description

- **ID**: TC-36
- **Module**: Reward
- **Title**: Easter egg resource type returns valid resource with title/url/description
- **Priority**: P1
- **Preconditions**:
  - Easter egg system initialized
  - `EASTER_EGG_RESOURCES` pool loaded (10 resources defined in spec Section 5)
  - Mocked random to force Resource type (category B)
- **Steps**:
  1. Force Easter egg type to Resource (mock `random.randint(0, 99)` to return a value in 40–79)
  2. Call Easter egg resource selection without user tags
  3. Inspect returned resource dict
  4. Repeat 50 times, verify each returned resource
- **Expected Result**:
  - Each returned resource has keys: `"title"`, `"url"`, `"description"` as non-empty strings
  - `"url"` starts with `http://` or `https://`
  - All returned resources belong to the `EASTER_EGG_RESOURCES` pool
  - Without tags: resources are drawn from the full pool (any of the 10 resources may appear)
  - With matching user tags (e.g., `["python"]`): resources are filtered to matching ones first; returned resource has at least one matching tag
- **Test Data**: Full resource pool (10 entries); optional tag list `["python", "algorithm"]`

---

## Module 8: Reward — Achievements (TC-37 to TC-39)

---

### TC-37: First checkin — ACH001 "初出茅庐" earned

- **ID**: TC-37
- **Module**: Reward
- **Title**: First checkin — ACH001 "初出茅庐" earned
- **Priority**: P0
- **Preconditions**:
  - Fresh user with 0 total check-ins (`total_checkins` == 0)
  - Task in `"doing"` status, no prior completions
  - Achievement table is empty for this user
- **Steps**:
  1. Verify user has 0 completed tasks and 0 prior check-ins
  2. Complete a check-in on any task via `process_task_completed()`
  3. Inspect the response for achievement unlocks
  4. Query the `achievements` table for this user
- **Expected Result**:
  - Response includes `achievements` list containing `{"key": "ACH001", "name": "初出茅庐", "xp_bonus": 10}`
  - `xp_earned` includes +10 XP from the achievement bonus
  - `achievements` table has 1 row for this user: `achievement_key = "ACH001"`
  - `GET /api/users/me/achievements` includes ACH001 with non-null `earned_at`
- **Test Data**: Fresh user, any task

---

### TC-38: Streak reaches 30 — ACH006 "月度战士" earned

- **ID**: TC-38
- **Module**: Reward
- **Title**: Streak reaches 30 — ACH006 "月度战士" earned
- **Priority**: P0
- **Preconditions**:
  - User `current_streak` == 29
  - ACH001–ACH005 already unlocked (or at least ACH006 not yet unlocked)
  - Task in `"doing"` status
- **Steps**:
  1. Simulate 29 consecutive backdated check-ins (streak = 29)
  2. Confirm `current_streak` == `29` and ACH006 is not unlocked
  3. Perform today's check-in (streak advances 29 → 30)
  4. Inspect response and query achievement table
- **Expected Result**:
  - `streak` == `30`
  - Response includes `achievements` list containing `{"key": "ACH006", "name": "月度战士", "xp_bonus": 50}`
  - `xp_earned` includes +50 XP from ACH006 bonus
  - Achievement table has a row for this user with `achievement_key = "ACH006"`
  - ACH005 ("一周坚持") was already unlocked at streak = 7 on an earlier day
- **Test Data**: 29 backdated check-in records; any task

---

### TC-39: Same achievement does not trigger twice (idempotency)

- **ID**: TC-39
- **Module**: Reward
- **Title**: Same achievement does not trigger twice (idempotency)
- **Priority**: P0
- **Preconditions**:
  - User has already earned ACH001 (first checkin completed previously)
  - User has `total_checkins` >= 1
  - `Achievement` table has row `(user_id, "ACH001")`
- **Steps**:
  1. Query achievement table: confirm `ACH001` already exists for the user
  2. Perform a second check-in on a different task
  3. Inspect the response's `achievements` list
  4. Query achievement table again, count rows with `achievement_key = "ACH001"`
- **Expected Result**:
  - Second check-in response does NOT include ACH001 in `achievements` list
  - No `UNIQUE constraint` violation or database error (the `>=` check + `already_unlocked` skip prevents re-insert)
  - Achievement table still has exactly 1 row with `achievement_key = "ACH001"` for this user
  - `unlocked_at` timestamp is unchanged from the first unlock
- **Test Data**: User with ACH001 already earned; any additional task

---

## Module 9: API — Heatmap (TC-40 to TC-42)

---

### TC-40: GET /api/users/me/heatmap returns 365 days

- **ID**: TC-40
- **Module**: API
- **Title**: GET /api/users/me/heatmap returns 365 days
- **Priority**: P0
- **Preconditions**:
  - FastAPI server running
  - Authenticated user with some check-in history
  - Default `days` parameter (365)
- **Steps**:
  1. Send `GET /api/users/me/heatmap` (no query params)
  2. Inspect the `heatmap` array in the response
  3. Send `GET /api/users/me/heatmap?days=30` and compare
- **Expected Result**:
  - HTTP 200
  - Default request: `heatmap` array has exactly 365 entries
  - Entries ordered by date descending (newest first)
  - Each entry has keys: `date` (YYYY-MM-DD), `count` (integer >= 0), `xp` (integer >= 0)
  - `days=30` request: returns exactly 30 entries
  - `days=0` or `days=731`: HTTP 422 ValidationError
- **Test Data**: Any authenticated user

---

### TC-41: Heatmap stats include correct active days count

- **ID**: TC-41
- **Module**: API
- **Title**: Heatmap stats include correct active days count
- **Priority**: P1
- **Preconditions**:
  - User with known check-in history: 5 distinct days with check-ins, current streak = 3, longest streak = 4
  - Known total check-in count and total XP
- **Steps**:
  1. Create user with check-ins on dates: D, D-1, D-2, D-5, D-7 (5 active days, 3-day current streak ending today, 4-day historical streak)
  2. Set XP values: 20, 30, 10, 50, 40 (total XP = 150)
  3. Call `GET /api/users/me/heatmap?days=10`
  4. Inspect `stats` block in the response
- **Expected Result**:
  - HTTP 200
  - `stats.total_days_active` == `5`
  - `stats.current_streak` == `3`
  - `stats.longest_streak` == `4`
  - `stats.total_checkins` == `5` (or sum of multi-checkin days)
  - `stats.average_xp_per_day` == `30.0` (150 / 5)
  - `stats.best_day.date` is the date with 50 XP, `stats.best_day.xp` == `50`
- **Test Data**: User with controlled check-in dates and XP values

---

### TC-42: Zero-count days return count=0, xp=0 (no gaps)

- **ID**: TC-42
- **Module**: API
- **Title**: Zero-count days return count=0, xp=0 (no gaps)
- **Priority**: P1
- **Preconditions**:
  - User with sparse check-in history (e.g., only 3 days out of 30 have check-ins)
  - `GET /api/users/me/heatmap?days=30`
- **Steps**:
  1. Create user with check-ins only on D, D-5, D-10
  2. Call `GET /api/users/me/heatmap?days=30`
  3. Verify every calendar day in the 30-day range is present in the array
  4. Inspect entries for days without check-ins
- **Expected Result**:
  - HTTP 200
  - `heatmap` array has exactly 30 entries (one per calendar day)
  - Days with no check-ins have `count: 0` and `xp: 0`
  - Days with check-ins have correct positive values
  - No date gaps between consecutive entries
  - Dates are sequential: if entry[i].date == "2026-06-08", entry[i+1].date == "2026-06-07"
- **Test Data**: User with 3 check-in days in a 30-day window

---

## Module 10: API — DAG and Stage (TC-43 to TC-45)

---

### TC-43: GET /api/projects/{pid}/dag returns correct nodes and edges

- **ID**: TC-43
- **Module**: API
- **Title**: GET /api/projects/{pid}/dag returns correct nodes and edges
- **Priority**: P0
- **Preconditions**:
  - FastAPI server running
  - F-01 (`quant_trading.md`) imported as project
  - All tasks at default status (pending)
- **Steps**:
  1. Call `GET /api/projects/{pid}/dag`
  2. Inspect `nodes`, `edges`, and `stages` arrays
  3. Verify node count, edge count, and stage count match the project
- **Expected Result**:
  - HTTP 200
  - `nodes` array has 17 entries (all tasks in F-01)
  - Each node includes: `id`, `title`, `type` (one of "theory"/"practice"/"output"), `status`, `xp`, `stage_id`, `stage_title`, `sort_order`
  - `edges` array represents all dependency relationships: e.g., `{"from": "T004", "to": "T005"}`
  - `edges` count matches the number of `depends` declarations in F-01
  - `stages` array has 4 entries, sorted by `sort_order`
  - Nodes within each stage are topologically sorted
- **Test Data**: F-01 (`quant_trading.md`), 17 tasks, 4 stages

---

### TC-44: DAG stage summaries show correct progress %

- **ID**: TC-44
- **Module**: API
- **Title**: DAG stage summaries show correct progress %
- **Priority**: P1
- **Preconditions**:
  - F-01 imported; Stage S1 "基础准备" has 4 tasks (T001–T004)
  - T001 and T002 completed (`"done"`), T003 in `"doing"`, T004 `"pending"`
- **Steps**:
  1. Complete T001 and T002 via check-in
  2. Start T003 (status → "doing")
  3. Call `GET /api/projects/{pid}/dag`
  4. Inspect the `stages` array for "基础准备"
- **Expected Result**:
  - HTTP 200
  - Stage "基础准备": `task_count` == `4`, `done_count` == `2`
  - `progress` == `0.5` (2 / 4)
  - Other stages with 0 done tasks: `progress` == `0.0`
  - Progress is a float between 0.0 and 1.0 inclusive
- **Test Data**: F-01, S1 with 2 tasks done

---

### TC-45: GET stage detail returns prev/next stage IDs for navigation

- **ID**: TC-45
- **Module**: API
- **Title**: GET stage detail returns prev/next stage IDs for navigation
- **Priority**: P0
- **Preconditions**:
  - F-01 imported with 4 stages: S1 "基础准备", S2 "数据获取与处理", S3 "策略开发", S4 "风险管理与实盘"
- **Steps**:
  1. Call `GET /api/projects/{pid}/stages/{S1_id}`
  2. Inspect `prev_stage_id`, `next_stage_id` and their titles
  3. Call `GET /api/projects/{pid}/stages/{S2_id}` (middle stage)
  4. Call `GET /api/projects/{pid}/stages/{S4_id}` (last stage)
- **Expected Result**:
  - HTTP 200 for all calls
  - S1 (first stage): `prev_stage_id` == `null`, `prev_stage_title` == `null`; `next_stage_id` == S2 ID, `next_stage_title` == `"数据获取与处理"`
  - S2 (middle stage): `prev_stage_id` == S1 ID, `prev_stage_title` == `"基础准备"`; `next_stage_id` == S3 ID, `next_stage_title` == `"策略开发"`
  - S4 (last stage): `prev_stage_id` == S3 ID, `prev_stage_title` == `"策略开发"`; `next_stage_id` == `null`, `next_stage_title` == `null`
  - Each response includes `tasks` array with all tasks in that stage, sorted by `sort_order`
  - Invalid project UUID or stage UUID: HTTP 404
- **Test Data**: F-01 (`quant_trading.md`), 4 stages

---

### TC-46: PATCH /api/users/me/theme dark-light-dark correctly toggles

- **ID**: TC-46
- **Module**: API
- **Title**: PATCH /api/users/me/theme dark-light-dark correctly toggles
- **Priority**: P1
- **Preconditions**:
  - FastAPI server running
  - Authenticated user, default theme assumed `"dark"`
- **Steps**:
  1. Call `PATCH /api/users/me/theme` with `{"theme": "light"}`
  2. Inspect response
  3. Call `PATCH /api/users/me/theme` with `{"theme": "dark"}`
  4. Inspect response
  5. Call `PATCH /api/users/me/theme` with `{"theme": "system"}` (invalid)
- **Expected Result**:
  - Step 1: HTTP 200, `{"theme": "light"}`
  - Step 2: light theme persisted (verified by re-fetching user profile)
  - Step 3: HTTP 200, `{"theme": "dark"}`
  - Step 4: dark theme persisted
  - Step 5: HTTP 422, error detail indicating `"value must be 'dark' or 'light'"`
  - Theme value persists across requests (not session-only)
- **Test Data**: Authenticated user

---

## Module 11: Frontend — Heatmap Page and Learning Map (TC-47 to TC-48)

---

### TC-47: Heatmap page loads with 7x52 grid and correct color scale

- **ID**: TC-47
- **Module**: Frontend
- **Title**: Heatmap page loads with 7x52 grid and correct color scale
- **Priority**: P0
- **Preconditions**:
  - UniApp running
  - User with ~120 active days across the past year
  - Heatmap data available via API
- **Steps**:
  1. Navigate to "成长" tab (4th position in tab bar)
  2. Wait for heatmap data to load
  3. Inspect the rendered grid, stats, and legend
  4. Tap a cell with check-in count > 0
- **Expected Result**:
  - Page loads without errors; skeleton shown during loading
  - Grid: 7 rows (Mon–Sun) x 52 columns layout
  - Weekday labels (一–日) visible on the left, sticky during horizontal scroll
  - Month labels (1月–12月) shown below the grid
  - Colors correspond to check-in count:
    - 0: `#1A1D22` (dark)
    - 1: `#0e4429` (light green)
    - 2: `#006d32`
    - 3: `#26a641`
    - 4+: `#39d353` (bright green)
  - Stats section shows: active days count, longest streak, total XP, average XP/day
  - Legend row shown with color squares and labels
  - Tapping a cell: tooltip appears showing date, tasks completed count, XP earned
  - Current day cell has a subtle ring highlight (1px `#4A9EFF` border)
  - Horizontal scroll works for the 728px-wide grid on a 375px screen
- **Test Data**: User with 120 active days

---

### TC-48: Tap stage node — expand shows child tasks with slide-down animation

- **ID**: TC-48
- **Module**: Frontend
- **Title**: Tap stage node — expand shows child tasks with slide-down animation
- **Priority**: P0
- **Preconditions**:
  - F-01 imported with stages and tasks
  - Learning map page rendered with StageTree component
  - At least one stage in `"open"` status
- **Steps**:
  1. Navigate to Learning Map (学习地图) page
  2. Observe StageNode components rendered vertically
  3. Tap on an `"open"` status stage node's circle or title area
  4. Observe the expand animation
  5. Inspect the revealed child task rows
  6. Tap the same stage node again to collapse
- **Expected Result**:
  - On tap: stage circle scales 1 → 1.05 → 1 (150ms spring bounce)
  - Child task container slides down with 300ms `ease-out` animation
  - Child tasks fade in with staggered delay (each +50ms)
  - Each child task row shows: status icon (✅/○), task name, type badge (📖/✏️/✍️), XP (⚡), estimate (⏱)
  - Completed tasks shown with strikethrough and muted color
  - 56px row height, 32px indentation from stage circle
  - On second tap: tasks fade out, container collapses with 200ms `ease-in`
  - Expanded state does not affect other stage nodes
  - Locked stages do not expand on tap (no child task reveal)
- **Test Data**: F-01 (`quant_trading.md`)

---

## Module 12: Frontend — Animation and Theme (TC-49 to TC-50)

---

### TC-49: After checkin, XP and dream value texts animate toward dream progress bar

- **ID**: TC-49
- **Module**: Frontend
- **Title**: After checkin, XP and dream value texts animate toward dream progress bar
- **Priority**: P1
- **Preconditions**:
  - UniApp running; user on home page
  - A task was just completed via check-in (API response returned successfully)
  - DreamMiniProgress component visible on home page
- **Steps**:
  1. Complete a check-in from the task page
  2. Navigate to home page (or observe if already on home page)
  3. Watch the fly-in animation after check-in API resolves
  4. Observe timing sequence: text appearance → flight → destination → progress bar update
- **Expected Result**:
  - At ~0ms: XP text ("+{xp} XP") appears at center-bottom area, blue color (#3B82F6), bold, 20px
  - At ~100ms: Dream value text ("+{dream_value} 梦想值") appears staggered below XP text, gold color (#FFD700)
  - 100–900ms: Both texts fly toward top-right dream mini-progress card area
    - XP text leads, dream text follows
    - Text size shrinks (20px → 12px) during flight
    - Opacity transitions: 0 → 1 → 0.8 → 0
  - At ~900ms: Texts near destination, opacity starts decreasing
  - At ~1100ms: Dream progress bar begins filling from old% to new%
    - Duration: 400ms `cubic-bezier(0.25, 0.1, 0.25, 1)`
    - Gold glow (`box-shadow`) at fill tip during animation
  - At ~1500ms: Animation complete, texts gone, progress bar at final value
  - Total animation duration: 1500ms
  - Haptic feedback: light pulse at 0ms and 1100ms
- **Test Data**: Any completed task with XP and dream value

---

### TC-50: Toggle theme switch — all pages transition between dark/light mode

- **ID**: TC-50
- **Module**: Frontend
- **Title**: Toggle theme switch — all pages transition between dark/light mode
- **Priority**: P1
- **Preconditions**:
  - UniApp running
  - User on Profile page
  - Theme initially set to `"dark"`
- **Steps**:
  1. Navigate to Profile tab
  2. Locate the theme toggle row ("深色模式" with toggle switch)
  3. Verify toggle is in ON state (dark mode active)
  4. Tap the toggle switch to turn OFF (light mode)
  5. Observe page transition
  6. Navigate to Home, Task, Heatmap, and Reward pages
  7. Return to Profile, tap toggle back to ON (dark mode)
  8. Close and reopen app — verify theme persists
- **Expected Result**:
  - Theme toggle renders as: 48x28px pill with 22x22px white knob
  - ON (dark): track `#22C55E` (green), knob right (translateX: 22px)
  - OFF (light): track `#444A54` (grey), knob left (translateX: 2px)
  - Transition: knob moves with 200ms `ease-out`, track color transitions simultaneously
  - All page backgrounds transition between dark and light colors
  - Transition speed: background-color 300ms, color 200ms, border-color 300ms, box-shadow 300ms
  - All pages (Home, Map, Task, Heatmap, Reward, Profile) reflect the theme change
  - Heatmap `--heatmap-0` cell color differs between dark (#161B22) and light mode
  - `localStorage` stores `"learning-os-theme"` key as `"dark"` or `"light"`
  - `<html data-theme>` attribute set correctly
  - App restart: theme persists (read from localStorage on mount)
  - Toggle switch position correctly reflects stored theme on app launch
- **Test Data**: Any authenticated user

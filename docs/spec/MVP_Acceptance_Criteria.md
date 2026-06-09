# MVP Acceptance Criteria — Phase 1

Version: 1.0 | Date: 2026-06-08

---

## AC-1: Import DSL → Parse Success

**Priority:** P0 (blocks all other features)

### Given
- User has a valid DSL Markdown file conforming to DSL Spec v1.0
- User is on the "Import Plan" page in the UniApp frontend

### When
- User selects the `.md` file and taps "Import"
- Frontend sends `POST /api/v1/plans/import` with the file
- Backend parses the DSL and returns the parsed plan structure

### Then
- Backend returns HTTP 201 with the created plan JSON including:
  - `id` (UUID)
  - `title`, `description`, `deadline`, `reward`, `reward_price`
  - `stages[]` each with `title`, `index`, `tasks[]`
  - Each task includes `id`, `title`, `type`, `xp`, `estimate`, `depends`, `check`, `resource`
- Frontend displays "Import successful: <title>" toast
- Plan is persisted in SQLite

### Pass Condition
- Valid DSL file → 201 + correct JSON structure within 2 seconds
- All fields from DSL are mapped correctly (spot-check 3 random fields)

### Fail Condition
- Any 5xx error on valid input
- Missing or mis-typed field in response (e.g. `xp` returned as string)
- Response time > 5 seconds for a 50-task plan

---

## AC-2: Display Today's Tasks

**Priority:** P0

### Given
- A plan has been imported with at least 5 tasks
- 3 of those tasks have NO unmet dependencies (ready to do)
- 2 tasks depend on those 3 (blocked)
- Today's date is within the plan's deadline window

### When
- User opens the app home page (today view)
- Frontend calls `GET /api/v1/tasks/today?plan_id=<id>`

### Then
- Backend returns exactly the 3 ready tasks (dependencies satisfied, not yet completed)
- The 2 blocked tasks are NOT returned
- Each task in response includes: `id`, `title`, `type`, `xp`, `estimate`, `check`, `resource`
- Tasks are ordered by their appearance order in the DSL
- Frontend renders each task with its type icon (book/repeat/file), title, and XP badge

### Pass Condition
- Only satisfiable tasks appear
- Completed tasks do not appear
- Blocked tasks do not appear

### Fail Condition
- A completed task appears in today's list
- A blocked task appears before its dependency is completed
- Empty response when ready tasks exist
- Task order differs from DSL order

---

## AC-3: Task Detail Page

**Priority:** P0

### Given
- User sees a task in today's list
- Task can be of type `theory`, `practice`, or `output`

### When
- User taps a task card
- Frontend navigates to task detail page and calls `GET /api/v1/tasks/<task_id>`

### Then
- Page shows all task fields: title, type, XP, estimate, check criteria, resource link
- For `theory` and `practice` type: shows a "Mark Complete" button
- For `output` type: shows a text input field (placeholder: "描述你的产出...") and a submit button
- Resource link is tappable and opens in system browser
- "Mark Complete" button triggers `POST /api/v1/tasks/<task_id>/checkin`

### Pass Condition
- All three type variants render correctly with correct UI elements
- Resource URL opens in external browser
- Output type requires text input (cannot submit empty — min 10 chars enforced both client and server)

### Fail Condition
- `theory` task shows text input (wrong UI)
- `output` task shows only a button without text input
- Resource link is not tappable
- Submit succeeds with < 10 chars for output type (server must also validate)

---

## AC-4: Check-in → XP Increase → Dream Progress Update

**Priority:** P0

### Given
- User has an incomplete task
- Plan has a dream reward defined (`reward: "Mac Studio"`, `reward_price: 15000`)
- User is at the task detail page

### When
- User completes the check-in (button for theory/practice, text submit for output)
- Request: `POST /api/v1/tasks/<task_id>/checkin`
- Backend marks task complete, adds XP to user's total

### Then
- Response includes: `xp_earned`, `total_xp`, `dream_progress_pct` (e.g. 0.067 if XP is 10/15000)
- Frontend shows animation: "+<xp> XP" badge appearing
- Dream progress bar updates in real-time
- Task disappears from today's list on next fetch

### Pass Condition
- XP correctly accumulates across multiple check-ins (check: 3 tasks of 10 XP each → total_xp = 30)
- Dream progress = `floor((total_xp / reward_price) * 10000) / 100` percent
- Completed task no longer appears in today's tasks
- Check-in is idempotent: second check-in on same task returns 409 Conflict

### Fail Condition
- XP not accumulating (total_xp resets to 0 on second check-in)
- Dream progress > 100% for any input
- Same task can be checked in twice with 200 status
- Dream progress shown when no reward is defined (should be hidden/absent)

---

## AC-5: Dream Reward Page

**Priority:** P0

### Given
- Plan has reward defined with price
- User has completed some tasks (total_xp > 0)
- User navigates to the reward page: `GET /api/v1/plans/<plan_id>/reward`

### When
- Page loads

### Then
- Shows reward name (e.g. "Mac Studio")
- Shows reward price in CNY (e.g. "15,000元")
- Shows current XP / price ratio as a progress bar with percentage
- Shows "还差 <remaining_price> 元" (remaining = reward_price - total_xp)
- Shows list of completed tasks that contributed to this XP (task title + XP earned + completed date)
- Progress bar is visually accurate (e.g. 10 XP toward 15000 = 0.06% bar width)

### Pass Condition
- Percentage matches `(total_xp / reward_price) * 100` rounded to 2 decimal places
- Completed tasks list sorted by completion date (newest first)
- Empty state: if no tasks completed, shows "还没有完成任务，开始学习吧！"

### Fail Condition
- Progress bar width does not match actual percentage (visual bug)
- Progress > 100% displayed (should cap at 100% visually)
- Reward page errors out when reward is not defined (should show "未设置奖励")
- Task completion dates are missing or null in the list

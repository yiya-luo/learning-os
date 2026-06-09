# Learning OS — System Architecture v1.0

## 1. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Learning OS                                     │
│                                                                              │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │ Markdown │───▶│   Parser     │───▶│  Task Engine  │───▶│ Reward Engine │  │
│  │   DSL    │    │  (import)    │    │ (state mach.) │    │ (XP + Dreams) │  │
│  └──────────┘    └──────┬───────┘    └──────┬───────┘    └───────┬───────┘  │
│                         │                   │                    │          │
│                         ▼                   ▼                    ▼          │
│                    ┌──────────────────────────────────────────────────┐     │
│                    │                  SQLite                           │     │
│                    │   users | projects | stages | tasks | checkins    │     │
│                    └──────────────────────┬───────────────────────────┘     │
│                                           │                                  │
│                                           ▼                                  │
│                              ┌─────────────────────────┐                    │
│                              │      REST API Layer     │                    │
│                              │   FastAPI + Pydantic    │                    │
│                              └────────────┬────────────┘                    │
│                                           │                                  │
│                                           ▼                                  │
│                              ┌─────────────────────────┐                    │
│                              │   UniApp Frontend       │                    │
│                              │   (Vue 3 + Vite)        │                    │
│                              └─────────────────────────┘                    │
└─────────────────────────────────────────────────────────────────────────────┘

Data Flow:
  Markdown DSL → Parser → Parsed JSON → Task Engine (state machine)
                                              │
                                        TaskCompletedEvent
                                              │
                                              ▼
                                        Reward Engine (XP / Dream points)
                                              │
                                              ▼
                                         REST API → UniApp Frontend
```

## 2. Component Descriptions

### 2.1 Parser (`backend/parser/`)

**Responsibility**: Convert Markdown DSL into a structured, validated JSON representation.

**Input**: Raw Markdown string (DSL format).
**Output**: `ParsedProject` — a Pydantic model containing `Project`, `Stage[]`, and `Task[]`.

**Key sub-modules**:
- `markdown_parser.py` — Line-by-line parser recognizing `#`, `##`, `###`, `- [ ]`, `- [~]`, `- [x]` markers.
- `dsl_validator.py` — Validates referential integrity (dependency `T001` actually exists), XP sums, task counts.
- `schemas.py` — Pydantic models for the parsed output.

### 2.2 Task Engine (`backend/engine/task_engine.py`)

**Responsibility**: Manage task lifecycle as a finite state machine.

```
  ┌─────────┐   start()   ┌─────────┐   checkin()   ┌──────┐
  │ pending │────────────▶│  doing  │──────────────▶│ done │
  └─────────┘             └─────────┘               └──────┘
```

**Rules**:
- `pending → doing`: requires `start()` call. A task with unmet dependencies (`depends`) is blocked.
- `doing → done`: requires `checkin()` call. Fires `TaskCompletedEvent`.
- Tasks cannot skip states.

### 2.3 Reward Engine (`backend/engine/reward_engine.py`)

**Responsibility**: Compute XP gains and Dream rewards when tasks complete.

**Triggers**: Subscribes to `TaskCompletedEvent`.

**Logic**:
- `xp_earned = task.base_xp * streak_multiplier`
- `dream_value = task.base_xp * 0.1` (10% conversion)
- Update `users.xp` and `users.level = floor(xp / 100) + 1`
- Record `checkins` row.

### 2.4 API Layer (`backend/api/`)

**Responsibility**: Expose RESTful endpoints via FastAPI.

**Structure**:
- `api/projects.py` — Project CRUD + import.
- `api/tasks.py` — Task list, detail, start, checkin.
- `api/progress.py` — XP, streak, reward progress.
- `api/users.py` — User profile.

**Dependencies**: Injected via FastAPI `Depends()` — `get_db()` for SQLite session, `get_task_engine()`, `get_reward_engine()`.

### 2.5 Frontend (`frontend/`)

**Responsibility**: UniApp (Vue 3) cross-platform UI.

**Pages**: project list, stage list, today's tasks, check-in, progress dashboard, user profile.

**API client**: `frontend/src/api/` — thin wrapper around `uni.request`.

## 3. Technology Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Backend framework | FastAPI (Python 3.11) | Async native, auto OpenAPI docs, Pydantic validation, lightweight. |
| ORM / DB access | Raw SQLite via `sqlite3` + context managers | No ORM overhead; SQLite is single-file; easy to test. |
| Database | SQLite | Zero-config, embedded, sufficient for single-user local app. Docker volume mounts the `.db` file. |
| Frontend framework | UniApp (Vue 3) | Cross-platform (iOS / Android / H5) from single codebase. |
| API spec | OpenAPI 3.0 | Auto-generated by FastAPI; serves as living contract. |
| Containerization | Docker (single container) | Simple deployment; SQLite file mounted as volume. |

## 4. Directory Structure

```
backend/
├── main.py                  # FastAPI app entry, CORS, lifespan
├── config.py                # Settings (DB path, log level)
├── db.py                    # SQLite connection, init_db(), get_db()
├── parser/
│   ├── __init__.py
│   ├── markdown_parser.py   # DSL → dict
│   ├── dsl_validator.py     # Semantic validation
│   └── schemas.py           # ParsedProject, ParsedStage, ParsedTask
├── engine/
│   ├── __init__.py
│   ├── task_engine.py       # start(), checkin(), get_today_tasks()
│   ├── reward_engine.py     # handle_task_completed(event)
│   └── events.py            # TaskCompletedEvent (dataclass)
├── api/
│   ├── __init__.py
│   ├── projects.py          # /api/projects/*
│   ├── tasks.py             # /api/tasks/*
│   ├── progress.py          # /api/users/me/xp, /streak, etc.
│   ├── users.py             # /api/users/me
│   └── deps.py              # get_db, get_task_engine, get_reward_engine
├── models/
│   ├── __init__.py
│   └── schemas.py           # Pydantic response/request models
└── tests/
    ├── test_parser.py
    ├── test_task_engine.py
    ├── test_reward_engine.py
    └── test_api.py
```

## 5. Key Data Flow Scenarios

### 5.1 Import DSL Flow

```
POST /api/projects/import { markdown: "# Project\n## Stage 1\n..." }

  1. API Layer receives markdown string
  2. Calls parser.markdown_parser.parse(markdown) → dict
  3. Calls parser.dsl_validator.validate(dict) → raises ValidationError or returns ParsedProject
  4. API Layer inserts Project row, Stage rows, Task rows in a transaction
  5. Returns 201 { project_id, stage_count, task_count }
```

### 5.2 Check-in Flow

```
POST /api/tasks/{tid}/checkin

  1. API Layer fetches task from DB (must exist, status must be "doing")
  2. Calls task_engine.checkin(task) → validates state, resolves dependencies
  3. task_engine fires TaskCompletedEvent(task_id, xp, user_id)
  4. reward_engine.handle_task_completed(event):
     a. Compute xp_earned (with streak multiplier)
     b. Compute dream_value
     c. UPDATE users SET xp += xp_earned, level = ...
     d. INSERT INTO checkins (task_id, user_id, xp_earned, dream_value_earned, checked_at)
  5. Returns 200 { xp_earned, new_total_xp, level, dream_earned }
```

### 5.3 Get Today's Tasks Flow

```
GET /api/projects/{pid}/tasks/today

  1. API Layer calls task_engine.get_today_tasks(project_id)
  2. Engine queries tasks WHERE project_id = pid AND status IN ('pending','doing')
  3. Engine resolves dependency chain:
     - Returns tasks whose depends[] are all "done"
     - Marks blocked tasks with "blocked": true
  4. Sorts by sort_order
  5. Returns 200 { date, tasks: [...] }
```

## 6. Error Handling Strategy

| Layer | Error Type | HTTP Status | Example |
|-------|-----------|-------------|---------|
| API | Invalid input (Pydantic validation) | 422 | `{"detail": "title is required"}` |
| Parser | DSL syntax error | 400 | `{"error": "PARSE_ERROR", "line": 5, "message": "..."}` |
| Parser | DSL validation error | 400 | `{"error": "VALIDATION_ERROR", "message": "T001 not found"}` |
| Engine | Invalid state transition | 409 | `{"error": "INVALID_TRANSITION", "current": "pending", "required": "doing"}` |
| Engine | Dependency not met | 409 | `{"error": "DEPENDENCY_BLOCKED", "blocked_by": ["T001"]}` |
| DB | Not found | 404 | `{"detail": "Project not found"}` |
| DB | Integrity error | 500 | `{"detail": "Internal server error"}` |

**Global error handler**: FastAPI exception handlers for `ValidationError`, `IntegrityError`, `NotFoundError`, `InvalidStateError`.

## 7. Module Independence & Testability

Each engine is a pure-Python module with **zero framework dependencies**. They accept plain data and return plain data. The API layer is the only component that depends on FastAPI.

### Parser — test in isolation

```python
def test_parse_single_stage():
    from parser.markdown_parser import parse
    result = parse("# My Project\n## Stage 1\n### T001 theory 20\nTitle")
    assert result["project"]["title"] == "My Project"
    assert len(result["stages"]) == 1
    assert len(result["stages"][0]["tasks"]) == 1
```

### Task Engine — test in isolation

```python
def test_start_task_transitions_pending_to_doing():
    from engine.task_engine import TaskEngine
    engine = TaskEngine(mock_db_session)
    task = Task(id="T001", status="pending", depends=[])
    engine.start(task)
    assert task.status == "doing"
```

### Reward Engine — test in isolation

```python
def test_completed_event_awards_xp():
    from engine.reward_engine import RewardEngine
    from engine.events import TaskCompletedEvent
    engine = RewardEngine(mock_db_session)
    user = User(xp=0, level=1, streak=1)
    event = TaskCompletedEvent(task_id="T001", xp=20, user_id="u1")
    result = engine.handle(event)
    assert result.xp_earned == 20
    assert result.new_total_xp == 20
```

### API Layer — test with FastAPI TestClient

```python
def test_create_project():
    response = client.post("/api/projects", json={"title": "Test"})
    assert response.status_code == 201
```

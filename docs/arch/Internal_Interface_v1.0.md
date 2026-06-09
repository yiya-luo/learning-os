# Learning OS — Internal Module Interfaces v1.0

## 1. Module Overview and Dependencies

```
┌──────────┐     ┌──────────────┐     ┌───────────────┐
│  Parser  │────▶│ Task Engine   │────▶│ Reward Engine │
│          │     │              │     │               │
└────┬─────┘     └──────┬───────┘     └───────┬───────┘
     │                  │                     │
     ▼                  ▼                     ▼
┌────────────────────────────────────────────────────┐
│                    API Layer                       │
│  (imports all three modules, injects into routes)  │
└────────────────────────────────────────────────────┘
```

**Rule**: Parser, Task Engine, and Reward Engine have **zero** imports from FastAPI, `backend.api`, or each other. They are plain Python modules that accept data and return data.

---

## 2. Parser Interface

### 2.1 `parser.markdown_parser`

```python
# backend/parser/markdown_parser.py

def parse(markdown: str) -> dict:
    """
    Parse a Markdown DSL string into a raw dictionary.

    Args:
        markdown: Raw DSL string.

    Returns:
        dict with keys: project, stages

    Raises:
        ParseError: If the DSL has syntax errors (malformed lines, missing required fields).
    """
    ...
```

**Input**: Raw Markdown string.

**Output** (raw dict, before validation):

```json
{
  "project": {
    "title": "30天 Python 入门",
    "description": "从零开始掌握 Python 基础，每天一小步。"
  },
  "stages": [
    {
      "title": "第一阶段：基础语法",
      "description": "掌握 Python 基本语法和数据类型。",
      "tasks": [
        {
          "dsl_id": "T001",
          "title": "变量与数据类型",
          "type": "theory",
          "xp": 20,
          "estimate": 30,
          "depends": [],
          "check": "能说出 Python 四种基本数据类型的区别",
          "resource": "https://docs.python.org/3/tutorial/introduction.html"
        },
        {
          "dsl_id": "T003",
          "title": "编写第一个计算器",
          "type": "practice",
          "xp": 30,
          "estimate": 45,
          "depends": ["T001"],
          "check": "实现加减乘除四则运算",
          "resource": ""
        }
      ]
    }
  ]
}
```

**Error type**:

```python
class ParseError(Exception):
    def __init__(self, line: int, message: str):
        self.line = line
        self.message = message
```

### 2.2 `parser.dsl_validator`

```python
# backend/parser/dsl_validator.py

def validate(raw: dict) -> ParsedProject:
    """
    Validate the parsed dict for semantic correctness.

    Checks:
      - All dependency references (depends[]) exist as dsl_ids.
      - No circular dependencies.
      - Every stage has at least 1 task.
      - XP values are positive integers.
      - Project has at least 1 stage.

    Args:
        raw: Output of markdown_parser.parse().

    Returns:
        ParsedProject: Validated and typed Pydantic model.

    Raises:
        ValidationError: If any semantic rule is violated.
    """
    ...
```

**Error type**:

```python
class ValidationError(Exception):
    def __init__(self, message: str):
        self.message = message
```

### 2.3 `parser.schemas` — Pydantic Models

```python
# backend/parser/schemas.py

from pydantic import BaseModel, Field
from typing import Literal

class ParsedTask(BaseModel):
    dsl_id: str
    title: str
    type: Literal["theory", "practice", "output"]
    xp: int = Field(gt=0)
    estimate: int = Field(default=30, gt=0)
    depends: list[str] = Field(default_factory=list)
    check: str = ""
    resource: str = ""

class ParsedStage(BaseModel):
    title: str
    description: str = ""
    tasks: list[ParsedTask] = Field(min_length=1)

class ParsedProject(BaseModel):
    title: str
    description: str = ""
    stages: list[ParsedStage] = Field(min_length=1)
```

---

## 3. Task Engine Interface

### 3.1 `engine.events` — Event Definitions

```python
# backend/engine/events.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

@dataclass
class TaskCompletedEvent:
    """Fired when a task transitions from doing → done."""
    task_id: str
    xp: int
    user_id: str
    timestamp: datetime = field(default_factory=datetime.now)

# Event bus: a simple list of callbacks
_subscribers: list[Callable[[TaskCompletedEvent], None]] = []

def subscribe(handler: Callable[[TaskCompletedEvent], None]) -> None:
    """Register a handler to be called on every TaskCompletedEvent."""
    _subscribers.append(handler)

def publish(event: TaskCompletedEvent) -> None:
    """Fire event to all subscribers."""
    for handler in _subscribers:
        handler(event)
```

### 3.2 `engine.task_engine`

```python
# backend/engine/task_engine.py

class TaskEngine:
    """
    Manages task state transitions.

    Constructor takes a DB session factory, not a framework object.
    """

    def __init__(self, db_session_factory):
        self._db = db_session_factory

    def can_start(self, task: dict) -> tuple[bool, list[str]]:
        """
        Check if a task is startable.

        Args:
            task: Dict with keys: id, status, depends (JSON string list).

        Returns:
            (can_start, blocked_by_ids):
              - (True, []): task can be started.
              - (False, ["T001"]): task is blocked because T001 is not done.
        """
        ...

    def start(self, task_id: str) -> dict:
        """
        Transition task from pending → doing.

        Args:
            task_id: UUID of the task.

        Returns:
            dict with keys: id, status, previous_status, started_at

        Raises:
            TaskNotFoundError: task_id does not exist.
            InvalidStateError: task is not in 'pending' status.
            DependencyBlockedError: dependencies are not all 'done'.
        """
        ...

    def checkin(self, task_id: str, user_id: str = "u1") -> dict:
        """
        Transition task from doing → done. Fires TaskCompletedEvent.

        Args:
            task_id: UUID of the task.
            user_id: UUID of the checking-in user (default "u1").

        Returns:
            dict with keys:
                id, status, previous_status, completed_at,
                xp_earned, dream_value_earned, new_total_xp,
                new_level, xp_to_next_level, streak

        Side effects:
            Publishes TaskCompletedEvent → Reward Engine picks it up.

        Raises:
            TaskNotFoundError: task_id does not exist.
            InvalidStateError: task is not in 'doing' status.
        """
        ...

    def get_today_tasks(self, project_id: str) -> dict:
        """
        Get actionable tasks for today.

        Returns tasks with status 'pending' or 'doing'. Tasks whose
        depends[] tasks are not all 'done' get blocked=true.

        Returns:
            dict with keys: date (str), tasks (list of dict).

        Example:
            {
              "date": "2026-06-08",
              "tasks": [
                { "id": "t1", "title": "...", "status": "doing", "blocked": false, ... },
                { "id": "t2", "title": "...", "status": "pending", "blocked": true,
                  "blocked_by": ["t1"], ... }
              ]
            }
        """
        ...
```

**Error types**:

```python
class TaskNotFoundError(Exception):
    def __init__(self, task_id: str):
        self.task_id = task_id

class InvalidStateError(Exception):
    def __init__(self, current_status: str, required_status: str):
        self.current_status = current_status
        self.required_status = required_status

class DependencyBlockedError(Exception):
    def __init__(self, blocked_by: list[str]):
        self.blocked_by = blocked_by
```

---

## 4. Reward Engine Interface

### 4.1 `engine.reward_engine`

```python
# backend/engine/reward_engine.py

from engine.events import TaskCompletedEvent

class RewardEngine:
    """
    Computes XP gains and dream value on task completion.

    Constructor takes a DB session factory.
    Registers itself as a subscriber to TaskCompletedEvent.
    """

    def __init__(self, db_session_factory):
        self._db = db_session_factory
        subscribe(self.handle_task_completed)  # auto-register

    def handle_task_completed(self, event: TaskCompletedEvent) -> dict:
        """
        Process a TaskCompletedEvent.

        1. Fetch user's current streak.
        2. Compute xp_earned = task.xp * streak_multiplier.
           - streak 1-6: 1.0x
           - streak 7-13: 1.2x
           - streak 14-20: 1.5x
           - streak 21+: 2.0x
        3. Compute dream_value = floor(task.xp * 0.1)
        4. Update user: xp += xp_earned, level = floor(xp / 100) + 1
        5. Record checkin row.
        6. Update project progress = done_count / total_count.

        Args:
            event: TaskCompletedEvent with task_id, xp, user_id, timestamp.

        Returns:
            dict with keys:
                xp_earned, dream_value_earned, new_total_xp, new_level,
                xp_to_next_level, streak, project_progress

        Example:
            >>> event = TaskCompletedEvent(task_id="t1", xp=20, user_id="u1")
            >>> reward_engine.handle_task_completed(event)
            {
                "xp_earned": 20,
                "dream_value_earned": 2,
                "new_total_xp": 350,
                "new_level": 4,
                "xp_to_next_level": 50,
                "streak": 7,
                "project_progress": 0.35
            }
        """
        ...

    def compute_streak(self, user_id: str) -> dict:
        """
        Calculate streak based on checkin history.
        Streak = consecutive days with at least 1 checkin, going backwards from today.

        Returns:
            dict with keys: current_streak, longest_streak, checked_in_today, last_checkin_date
        """
        ...
```

---

## 5. API → Parser Integration

**Call site**: `backend/api/projects.py` → `POST /api/projects/import`

```python
# Inside the route handler:
from parser.markdown_parser import parse, ParseError
from parser.dsl_validator import validate, ValidationError

@router.post("/api/projects/import")
def import_project(body: ImportRequest, db = Depends(get_db)):
    try:
        raw = parse(body.markdown)           # Step 1: parse markdown → dict
        parsed = validate(raw)               # Step 2: validate → ParsedProject
    except ParseError as e:
        raise HTTPException(status_code=400, detail={
            "error": "PARSE_ERROR", "line": e.line, "message": e.message
        })
    except ValidationError as e:
        raise HTTPException(status_code=400, detail={
            "error": "VALIDATION_ERROR", "message": e.message
        })

    # Step 3: persist
    project_id = str(uuid.uuid4())
    db.execute("INSERT INTO projects ...", (project_id, parsed.title, ...))

    for stage_order, stage in enumerate(parsed.stages):
        stage_id = str(uuid.uuid4())
        db.execute("INSERT INTO stages ...", (stage_id, project_id, stage.title, ...))
        for task_order, task in enumerate(stage.tasks):
            task_id = str(uuid.uuid4())
            db.execute("INSERT INTO tasks ...", (
                task_id, task.dsl_id, stage_id, project_id,
                task.title, task.type, task.xp, task.estimate,
                json.dumps(task.depends), task.check, task.resource, task_order
            ))

    db.commit()
    return {"project_id": project_id, ...}
```

---

## 6. Engine → Reward Integration (Event-Driven)

```python
# During app startup (main.py lifespan):
engine = TaskEngine(db_session_factory)
reward = RewardEngine(db_session_factory)

# When checkin() is called:
#   task_engine.checkin(task_id)
#     → updates task.status = "done"
#     → publish(TaskCompletedEvent(task_id, xp, user_id))
#         → reward_engine.handle_task_completed(event)  # auto-invoked via subscribe()
```

The Reward Engine registers itself in `__init__` via `subscribe()`. No explicit wiring needed after construction.

---

## 7. Summary: What Each Module Imports

| Module | Imports from | Exposes |
|--------|-------------|---------|
| `parser.markdown_parser` | stdlib (`re`) | `parse(str) -> dict`, `ParseError` |
| `parser.dsl_validator` | `parser.schemas` | `validate(dict) -> ParsedProject`, `ValidationError` |
| `parser.schemas` | `pydantic` | `ParsedProject`, `ParsedStage`, `ParsedTask` |
| `engine.events` | stdlib (`dataclasses`, `datetime`, `typing`) | `TaskCompletedEvent`, `subscribe()`, `publish()` |
| `engine.task_engine` | `engine.events` | `TaskEngine`, `TaskNotFoundError`, `InvalidStateError`, `DependencyBlockedError` |
| `engine.reward_engine` | `engine.events` | `RewardEngine` |
| `api.*` | FastAPI, all `engine` + `parser` modules | Route handlers |

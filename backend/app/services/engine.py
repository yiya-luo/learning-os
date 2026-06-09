"""Task state machine, scheduler, and check-in logic."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class TaskStatus(str, Enum):
    PENDING = "pending"
    DOING = "doing"
    DONE = "done"


class TaskStateError(Exception):
    """Raised when an invalid state transition is attempted."""


# Valid transitions
_TRANSITIONS = {
    TaskStatus.PENDING: {TaskStatus.DOING},
    TaskStatus.DOING: {TaskStatus.DONE},
    TaskStatus.DONE: set(),
}


def can_transition(current: TaskStatus, target: TaskStatus) -> bool:
    """Check if a state transition is valid."""
    return target in _TRANSITIONS.get(current, set())


def transition(current: TaskStatus, target: TaskStatus) -> TaskStatus:
    """Execute a state transition. Raises TaskStateError if invalid."""
    if not can_transition(current, target):
        raise TaskStateError(
            f"Invalid transition: {current.value} -> {target.value}"
        )
    return target


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------


def get_available_tasks(
    project_id: str, all_tasks: list[dict]
) -> list[dict]:
    """
    Filter tasks that are available to work on:
    1. status != 'done'
    2. All depends tasks are done
    3. Sort by stage order, then task order

    Returns tasks sorted by availability priority.
    """
    done_ids = {
        t["id"] for t in all_tasks if t.get("status") == TaskStatus.DONE
    }

    def _deps_met(task: dict) -> bool:
        depends = task.get("depends", [])
        if isinstance(depends, str):
            import json
            depends = json.loads(depends) if depends else []
        return all(d in done_ids for d in depends)

    available = [
        t
        for t in all_tasks
        if t.get("status") != TaskStatus.DONE and _deps_met(t)
    ]

    available.sort(
        key=lambda t: (
            t.get("stage_order", 0),
            t.get("sort_order", 0),
        )
    )
    return available


def get_today_tasks(
    project_id: str, all_tasks: list[dict], max_minutes: int = 60
) -> list[dict]:
    """
    Get today's recommended tasks:
    1. Start with available tasks
    2. Accumulate until cumulative estimate reaches max_minutes
    3. Return the subset
    """
    available = get_available_tasks(project_id, all_tasks)
    result: list[dict] = []
    cumulative = 0
    for task in available:
        estimate = task.get("estimate")
        if estimate is None:
            # Tasks without an estimate are always included
            result.append(task)
            continue
        if cumulative + estimate <= max_minutes:
            result.append(task)
            cumulative += estimate
        else:
            # A task with an estimate exceeded the budget — skip it,
            # but keep going: later tasks without estimates still qualify.
            continue
    return result


# ---------------------------------------------------------------------------
# Check-in
# ---------------------------------------------------------------------------


@dataclass
class TaskCompletedEvent:
    task_id: str
    xp: int
    user_id: int
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CheckinResult:
    task_id: str
    xp_earned: int
    dream_value: float
    timestamp: datetime
    new_status: TaskStatus


def checkin(task: dict, user_id: int = 1) -> CheckinResult:
    """
    Complete a task:
    1. Validate task can transition (doing -> done)
    2. Create TaskCompletedEvent
    3. Return CheckinResult
    """
    current = task.get("status", "")
    if isinstance(current, str):
        current = TaskStatus(current)
    if current != TaskStatus.DOING:
        raise TaskStateError(
            f"Cannot checkin: task status is '{current.value}', expected 'doing'"
        )

    xp = task.get("xp", 0)
    now = datetime.now(timezone.utc)
    TaskCompletedEvent(
        task_id=task["id"],
        xp=xp,
        user_id=user_id,
        timestamp=now,
    )

    return CheckinResult(
        task_id=task["id"],
        xp_earned=xp,
        dream_value=round(xp * 0.1, 1),
        timestamp=now,
        new_status=TaskStatus.DONE,
    )

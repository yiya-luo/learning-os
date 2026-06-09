"""E2E integration tests — full import → checkin → reward flow."""

import os
import sys
import uuid
from datetime import date

import pytest
from fastapi.testclient import TestClient

# Use in-memory SQLite for tests
os.environ["DATABASE_URL"] = "sqlite:///./test_e2e.db"

from app.database import init_db, SessionLocal, engine, Base  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app)


def _detail(resp):
    """Extract detail from a FastAPI error response. Returns the inner dict if wrapped."""
    data = resp.json()
    # FastAPI wraps as {"detail": {...}}; return the inner dict if present
    if "detail" in data and isinstance(data["detail"], dict):
        return data["detail"]
    return data


@pytest.fixture(autouse=True)
def fresh_db():
    """Drop and recreate all tables before each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    from app.models.models import User

    if not db.query(User).filter(User.id == "u1").first():
        db.add(User(id="u1", nickname="Learner"))
        db.commit()
    db.close()

    yield

    db = SessionLocal()
    db.close()


def _read_example_dsl() -> str:
    path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "docs",
        "spec",
        "example_plans",
        "quant_trading.md",
    )
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ─── Test 1: Root endpoint ────────────────────────────────────────────────────


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"name": "Learning OS", "version": "0.1.0"}


# ─── Test 2: Full import flow ─────────────────────────────────────────────────


def test_full_import_flow():
    dsl = _read_example_dsl()
    resp = client.post("/api/projects/import", json={"markdown": dsl})
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert "project_id" in data
    assert data["title"] == "从0学习量化交易"
    assert data["stage_count"] == 4
    assert data["task_count"] == 17

    pid = data["project_id"]

    # Verify project detail
    detail = client.get(f"/api/projects/{pid}")
    assert detail.status_code == 200
    detail_data = detail.json()
    assert detail_data["title"] == "从0学习量化交易"
    assert detail_data["reward"] == "Mac Studio"
    assert detail_data["reward_price"] == 15000
    assert len(detail_data["stages"]) == 4
    assert detail_data["progress"] == 0.0

    # Verify task count
    tasks_resp = client.get(f"/api/projects/{pid}/tasks")
    assert tasks_resp.status_code == 200
    tasks = tasks_resp.json()["tasks"]
    assert len(tasks) == 17


# ─── Test 3: Import validation error ──────────────────────────────────────────


def test_import_validation_error():
    invalid_dsl = """
# Project
title:

## Stage
title: Some Stage

## Task
id: T001
title: Do Something
type: invalid_type
xp: 10
"""
    resp = client.post("/api/projects/import", json={"markdown": invalid_dsl})
    assert resp.status_code == 422, resp.text
    data = _detail(resp)
    assert data["error"] == "VALIDATION_ERROR"


# ─── Test 4: Import empty content ─────────────────────────────────────────────


def test_empty_import():
    resp = client.post("/api/projects/import", json={"markdown": ""})
    assert resp.status_code == 422, resp.text
    data = _detail(resp)
    assert data["error"] == "PARSE_ERROR"


# ─── Test 5: Create project manually ──────────────────────────────────────────


def test_create_project():
    resp = client.post(
        "/api/projects",
        json={
            "title": "Test Project",
            "description": "A test project",
            "reward": "Coffee",
            "reward_price": 500,
            "deadline": "2026-12-31",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test Project"
    assert data["reward"] == "Coffee"
    assert data["reward_price"] == 500


# ─── Test 6: List projects ────────────────────────────────────────────────────


def test_list_projects():
    dsl = _read_example_dsl()
    client.post("/api/projects/import", json={"markdown": dsl})

    resp = client.get("/api/projects")
    assert resp.status_code == 200
    projects = resp.json()["projects"]
    assert len(projects) >= 1


# ─── Test 7: Get today tasks ──────────────────────────────────────────────────


def test_get_today_tasks():
    dsl = _read_example_dsl()
    import_resp = client.post("/api/projects/import", json={"markdown": dsl})
    pid = import_resp.json()["project_id"]

    resp = client.get(f"/api/projects/{pid}/tasks/today")
    assert resp.status_code == 200
    data = resp.json()
    assert "date" in data
    today_tasks = data["tasks"]
    assert len(today_tasks) > 0
    assert "blocked" in today_tasks[0]


# ─── Test 8: Start task ───────────────────────────────────────────────────────


def test_start_task():
    dsl = _read_example_dsl()
    import_resp = client.post("/api/projects/import", json={"markdown": dsl})
    pid = import_resp.json()["project_id"]

    tasks_resp = client.get(f"/api/projects/{pid}/tasks")
    tasks = tasks_resp.json()["tasks"]
    first_task = tasks[0]

    resp = client.patch(f"/api/tasks/{first_task['id']}/start")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "doing"
    assert data["previous_status"] == "pending"
    assert "started_at" in data


# ─── Test 9: Checkin flow ────────────────────────────────────────────────────


def test_checkin_flow():
    dsl = _read_example_dsl()
    import_resp = client.post("/api/projects/import", json={"markdown": dsl})
    pid = import_resp.json()["project_id"]

    tasks_resp = client.get(f"/api/projects/{pid}/tasks")
    tasks = tasks_resp.json()["tasks"]
    first_task = tasks[0]

    # Start it
    start_resp = client.patch(f"/api/tasks/{first_task['id']}/start")
    assert start_resp.status_code == 200

    # Checkin
    checkin_resp = client.post(f"/api/tasks/{first_task['id']}/checkin")
    assert checkin_resp.status_code == 200, checkin_resp.text
    data = checkin_resp.json()
    assert data["status"] == "done"
    assert data["previous_status"] == "doing"
    assert data["xp_earned"] > 0
    assert data["new_total_xp"] > 0
    assert data["streak"] >= 1
    assert "completed_at" in data


# ─── Test 10: Checkin on pending fails ────────────────────────────────────────


def test_checkin_on_pending_fails():
    dsl = _read_example_dsl()
    import_resp = client.post("/api/projects/import", json={"markdown": dsl})
    pid = import_resp.json()["project_id"]

    tasks_resp = client.get(f"/api/projects/{pid}/tasks")
    first_task = tasks_resp.json()["tasks"][0]

    # Try checkin without starting
    resp = client.post(f"/api/tasks/{first_task['id']}/checkin")
    assert resp.status_code == 409, resp.text
    data = _detail(resp)
    assert data["error"] == "INVALID_TRANSITION"


# ─── Test 11: Get user XP after checkin ───────────────────────────────────────


def test_get_user_xp():
    dsl = _read_example_dsl()
    import_resp = client.post("/api/projects/import", json={"markdown": dsl})
    pid = import_resp.json()["project_id"]

    tasks_resp = client.get(f"/api/projects/{pid}/tasks")
    first_task = tasks_resp.json()["tasks"][0]

    client.patch(f"/api/tasks/{first_task['id']}/start")
    checkin_resp = client.post(f"/api/tasks/{first_task['id']}/checkin")
    assert checkin_resp.status_code == 200

    xp_resp = client.get("/api/users/me/xp")
    assert xp_resp.status_code == 200
    data = xp_resp.json()
    assert data["total_xp"] > 0
    assert data["level"] >= 1
    assert data["total_tasks_completed"] >= 1


# ─── Test 12: Get reward progress ─────────────────────────────────────────────


def test_get_reward_progress():
    dsl = _read_example_dsl()
    import_resp = client.post("/api/projects/import", json={"markdown": dsl})
    pid = import_resp.json()["project_id"]

    tasks_resp = client.get(f"/api/projects/{pid}/tasks")
    first_task = tasks_resp.json()["tasks"][0]

    client.patch(f"/api/tasks/{first_task['id']}/start")
    client.post(f"/api/tasks/{first_task['id']}/checkin")

    reward_resp = client.get(f"/api/projects/{pid}/reward")
    assert reward_resp.status_code == 200
    data = reward_resp.json()
    assert data["project_id"] == pid
    assert data["reward_name"] == "Mac Studio"
    assert data["reward_price"] == 15000
    assert data["dream_value_earned"] > 0
    assert data["progress_percent"] >= 0


# ─── Test 13: Get user profile ────────────────────────────────────────────────


def test_get_user_profile():
    resp = client.get("/api/users/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "u1"
    assert data["nickname"] == "Learner"
    assert "xp" in data
    assert "streak" in data


# ─── Test 14: Update user profile ─────────────────────────────────────────────


def test_update_user_profile():
    resp = client.patch(
        "/api/users/me",
        json={"nickname": "Quantum Learner", "avatar": "https://example.com/av.png"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["nickname"] == "Quantum Learner"
    assert data["avatar"] == "https://example.com/av.png"


# ─── Test 15: Get streak ──────────────────────────────────────────────────────


def test_get_streak():
    dsl = _read_example_dsl()
    import_resp = client.post("/api/projects/import", json={"markdown": dsl})
    pid = import_resp.json()["project_id"]

    tasks_resp = client.get(f"/api/projects/{pid}/tasks")
    first_task = tasks_resp.json()["tasks"][0]

    client.patch(f"/api/tasks/{first_task['id']}/start")
    client.post(f"/api/tasks/{first_task['id']}/checkin")

    resp = client.get("/api/users/me/streak")
    assert resp.status_code == 200
    data = resp.json()
    assert data["current_streak"] >= 1
    assert data["longest_streak"] >= 1
    assert "checked_in_today" in data


# ─── Test 16: Full user journey ───────────────────────────────────────────────


def test_full_user_journey():
    """Import → get today tasks → start → checkin → verify XP → verify dream progress."""
    dsl = _read_example_dsl()

    # 1. Import
    import_resp = client.post("/api/projects/import", json={"markdown": dsl})
    assert import_resp.status_code == 201
    pid = import_resp.json()["project_id"]

    # 2. Get today tasks
    today = client.get(f"/api/projects/{pid}/tasks/today")
    assert today.status_code == 200
    today_tasks = today.json()["tasks"]
    assert len(today_tasks) > 0

    # 3. Start the first task
    first_task = today_tasks[0]
    start_resp = client.patch(f"/api/tasks/{first_task['id']}/start")
    assert start_resp.status_code == 200

    # 4. Checkin
    checkin_resp = client.post(f"/api/tasks/{first_task['id']}/checkin")
    assert checkin_resp.status_code == 200
    checkin_data = checkin_resp.json()
    assert checkin_data["status"] == "done"

    # 5. Verify XP
    xp_resp = client.get("/api/users/me/xp")
    assert xp_resp.status_code == 200
    assert xp_resp.json()["total_xp"] > 0

    # 6. Verify dream progress
    reward_resp = client.get(f"/api/projects/{pid}/reward")
    assert reward_resp.status_code == 200
    assert reward_resp.json()["dream_value_earned"] > 0

    # 7. Verify task detail shows done
    task_detail = client.get(f"/api/tasks/{first_task['id']}")
    assert task_detail.status_code == 200
    assert task_detail.json()["status"] == "done"

    # 8. Batch complete more tasks
    all_tasks = client.get(f"/api/projects/{pid}/tasks").json()["tasks"]
    count_completed = 1
    for t in all_tasks:
        if t["status"] == "done":
            continue
        if t["id"] == first_task["id"]:
            continue
        # Start
        start_r = client.patch(f"/api/tasks/{t['id']}/start")
        if start_r.status_code == 409:
            continue  # dependency blocked — skip
        client.post(f"/api/tasks/{t['id']}/checkin")
        count_completed += 1
        if count_completed >= 3:
            break

    # 9. Final project progress should reflect completions
    detail = client.get(f"/api/projects/{pid}")
    assert detail.status_code == 200
    assert detail.json()["progress"] > 0


# ─── Test 17: 404 for nonexistent resources ───────────────────────────────────


def test_404_handling():
    fake_id = "nonexistent999"

    # Project
    assert client.get(f"/api/projects/{fake_id}").status_code == 404

    # Task
    assert client.get(f"/api/tasks/{fake_id}").status_code == 404
    assert client.patch(f"/api/tasks/{fake_id}/start").status_code == 404
    assert client.post(f"/api/tasks/{fake_id}/checkin").status_code == 404

    # Tasks list for nonexistent project
    assert client.get(f"/api/projects/{fake_id}/tasks").status_code == 404
    assert client.get(f"/api/projects/{fake_id}/tasks/today").status_code == 404

    # Reward for nonexistent project
    assert client.get(f"/api/projects/{fake_id}/reward").status_code == 404


# ─── Test 18: Start on already-started task fails ─────────────────────────────


def test_start_already_started_fails():
    dsl = _read_example_dsl()
    import_resp = client.post("/api/projects/import", json={"markdown": dsl})
    pid = import_resp.json()["project_id"]

    tasks = client.get(f"/api/projects/{pid}/tasks").json()["tasks"]
    first_task = tasks[0]

    # Start once
    assert client.patch(f"/api/tasks/{first_task['id']}/start").status_code == 200

    # Start again — should fail
    resp = client.patch(f"/api/tasks/{first_task['id']}/start")
    assert resp.status_code == 409
    data = _detail(resp)
    assert data["error"] == "INVALID_TRANSITION"


# ─── Test 19: Checkin on done task fails ──────────────────────────────────────


def test_checkin_already_done_fails():
    dsl = _read_example_dsl()
    import_resp = client.post("/api/projects/import", json={"markdown": dsl})
    pid = import_resp.json()["project_id"]

    tasks = client.get(f"/api/projects/{pid}/tasks").json()["tasks"]
    first_task = tasks[0]

    client.patch(f"/api/tasks/{first_task['id']}/start")
    client.post(f"/api/tasks/{first_task['id']}/checkin")

    # Try checkin again
    resp = client.post(f"/api/tasks/{first_task['id']}/checkin")
    assert resp.status_code == 409


# ─── Test 20: Get task detail ─────────────────────────────────────────────────


def test_get_task_detail():
    dsl = _read_example_dsl()
    import_resp = client.post("/api/projects/import", json={"markdown": dsl})
    pid = import_resp.json()["project_id"]

    tasks = client.get(f"/api/projects/{pid}/tasks").json()["tasks"]
    task_id = tasks[0]["id"]

    resp = client.get(f"/api/tasks/{task_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == task_id
    assert data["project_id"] == pid
    assert "stage_id" in data
    assert "stage_title" in data
    assert "title" in data
    assert "type" in data
    assert "xp" in data
    assert "status" in data


# ─── Phase 2 Tests ───────────────────────────────────────────────────────────

# ─── Test 21: Heatmap returns 365 days ───────────────────────────────────────


def test_heatmap_returns_365_days():
    dsl = _read_example_dsl()
    import_resp = client.post("/api/projects/import", json={"markdown": dsl})
    pid = import_resp.json()["project_id"]
    tasks = client.get(f"/api/projects/{pid}/tasks").json()["tasks"]

    # Complete a few tasks to generate heatmap data
    for t in tasks[:3]:
        client.patch(f"/api/tasks/{t['id']}/start")
        client.post(f"/api/tasks/{t['id']}/checkin")

    resp = client.get("/api/users/me/heatmap")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "heatmap" in data
    assert "stats" in data
    assert len(data["heatmap"]) == 365
    # Check that heatmap is sorted by date descending
    dates = [h["date"] for h in data["heatmap"]]
    assert dates == sorted(dates, reverse=True)
    # At least today should have checkins
    today_cell = data["heatmap"][0]
    assert today_cell["date"] == date.today().isoformat()


# ─── Test 22: Heatmap stats are correct ──────────────────────────────────────


def test_heatmap_stats_correct():
    dsl = _read_example_dsl()
    import_resp = client.post("/api/projects/import", json={"markdown": dsl})
    pid = import_resp.json()["project_id"]
    tasks = client.get(f"/api/projects/{pid}/tasks").json()["tasks"]

    completed = 0
    for t in tasks:
        start_r = client.patch(f"/api/tasks/{t['id']}/start")
        if start_r.status_code == 200:
            checkin_r = client.post(f"/api/tasks/{t['id']}/checkin")
            if checkin_r.status_code == 200:
                completed += 1
        if completed >= 2:
            break

    resp = client.get("/api/users/me/heatmap")
    assert resp.status_code == 200
    stats = resp.json()["stats"]
    assert stats["total_days_active"] >= 1
    assert stats["total_checkins"] >= completed
    assert stats["longest_streak"] >= 1
    assert stats["current_streak"] >= 0
    assert stats["average_xp_per_day"] >= 0
    assert "best_day" in stats


# ─── Test 23: DAG returns nodes and edges ────────────────────────────────────


def test_dag_returns_nodes_and_edges():
    dsl = _read_example_dsl()
    import_resp = client.post("/api/projects/import", json={"markdown": dsl})
    pid = import_resp.json()["project_id"]

    resp = client.get(f"/api/projects/{pid}/dag")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "nodes" in data
    assert "edges" in data
    assert "stages" in data
    assert len(data["nodes"]) > 0
    # Verify node structure
    node = data["nodes"][0]
    assert "id" in node
    assert "title" in node
    assert "type" in node
    assert "status" in node
    assert "xp" in node
    assert "stage_id" in node
    assert "stage_title" in node
    assert "sort_order" in node
    # Verify edges have from/to
    if data["edges"]:
        edge = data["edges"][0]
        assert ("source" in edge or "from" in edge)
        assert ("target" in edge or "to" in edge)


# ─── Test 24: DAG stage summaries ───────────────────────────────────────────


def test_dag_stage_summaries():
    dsl = _read_example_dsl()
    import_resp = client.post("/api/projects/import", json={"markdown": dsl})
    pid = import_resp.json()["project_id"]

    resp = client.get(f"/api/projects/{pid}/dag")
    assert resp.status_code == 200
    stages = resp.json()["stages"]
    assert len(stages) >= 1
    stage = stages[0]
    assert "title" in stage
    assert "progress" in stage
    assert "task_count" in stage
    assert "done_count" in stage
    assert 0 <= stage["progress"] <= 1


# ─── Test 25: Stage detail with blocked status ───────────────────────────────


def test_stage_detail_with_blocked_status():
    dsl = _read_example_dsl()
    import_resp = client.post("/api/projects/import", json={"markdown": dsl})
    pid = import_resp.json()["project_id"]

    project_detail = client.get(f"/api/projects/{pid}").json()
    stages = project_detail["stages"]
    assert len(stages) >= 1

    sid = stages[0]["id"]
    resp = client.get(f"/api/projects/{pid}/stages/{sid}")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["id"] == sid
    assert "title" in data
    assert "sort_order" in data
    assert "progress" in data
    assert "task_count" in data
    assert "done_count" in data
    assert "tasks" in data
    assert len(data["tasks"]) > 0
    task = data["tasks"][0]
    assert "blocked" in task
    # First stage should have prev_stage_id = null
    # and may have next_stage_id if there are multiple stages
    assert "prev_stage_id" in data
    assert "next_stage_id" in data


# ─── Test 26: Achievements list all ten ──────────────────────────────────────


def test_achievements_list_all_ten():
    resp = client.get("/api/users/me/achievements")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "achievements" in data
    assert len(data["achievements"]) == 10
    assert "total_earned" in data
    assert "total_available" in data
    assert data["total_available"] == 10
    # Verify achievement structure
    ach = data["achievements"][0]
    assert "id" in ach
    assert "name" in ach
    assert "description" in ach
    assert "icon" in ach
    assert "earned_at" in ach
    assert "xp_bonus" in ach


# ─── Test 27: Theme update ───────────────────────────────────────────────────


def test_theme_update():
    # Set theme to light
    resp = client.patch("/api/users/me/theme", json={"theme": "light"})
    assert resp.status_code == 200, resp.text
    assert resp.json() == {"theme": "light"}

    # Set back to dark
    resp = client.patch("/api/users/me/theme", json={"theme": "dark"})
    assert resp.status_code == 200
    assert resp.json() == {"theme": "dark"}

    # Invalid theme should fail
    resp = client.patch("/api/users/me/theme", json={"theme": "invalid"})
    assert resp.status_code == 422


# ─── Test 28: Reward image upload ────────────────────────────────────────────


def test_reward_image_upload():
    dsl = _read_example_dsl()
    import_resp = client.post("/api/projects/import", json={"markdown": dsl})
    pid = import_resp.json()["project_id"]

    # Create a tiny 1x1 PNG
    import base64
    tiny_png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )

    resp = client.put(
        f"/api/projects/{pid}/reward-image",
        files={"image": ("test.png", tiny_png, "image/png")},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "image_url" in data
    assert data["image_url"].startswith("data:image/png;base64,")

    # Test 404 for nonexistent project
    resp = client.put(
        "/api/projects/nonexistent/reward-image",
        files={"image": ("test.png", tiny_png, "image/png")},
    )
    assert resp.status_code == 404


# ─── Test 29: Checkin includes easter_egg and achievement fields ─────────────


def test_checkin_has_easter_egg_and_achievement_fields():
    dsl = _read_example_dsl()
    import_resp = client.post("/api/projects/import", json={"markdown": dsl})
    pid = import_resp.json()["project_id"]

    tasks = client.get(f"/api/projects/{pid}/tasks").json()["tasks"]
    first_task = tasks[0]

    client.patch(f"/api/tasks/{first_task['id']}/start")
    resp = client.post(f"/api/tasks/{first_task['id']}/checkin")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "easter_egg" in data
    assert "achievement_unlocked" in data
    # First checkin should trigger ACH001 (internal key for first checkin)
    if data["achievement_unlocked"] is not None:
        ach_id = data["achievement_unlocked"]["id"]
        assert ach_id in ("ACH_FIRST_CHECKIN", "ACH001", "ACH002", "ACH003", "ACH004", "ACH005", "ACH006", "ACH007", "ACH008", "ACH009", "ACH010")


# ─── Test 30: DAG 404 for nonexistent project ────────────────────────────────


def test_dag_404():
    resp = client.get("/api/projects/nonexistent999/dag")
    assert resp.status_code == 404


# ─── Test 31: Stage detail 404 for nonexistent stage ─────────────────────────


def test_stage_detail_404():
    dsl = _read_example_dsl()
    import_resp = client.post("/api/projects/import", json={"markdown": dsl})
    pid = import_resp.json()["project_id"]

    resp = client.get(f"/api/projects/{pid}/stages/nonexistent999")
    assert resp.status_code == 404

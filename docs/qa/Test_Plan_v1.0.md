# Test Plan v1.0 — Learning OS Phase 1 MVP

Version: 1.0 | Date: 2026-06-08 | Author: QA

---

## 1. Test Scope

### 1.1 In Scope

| Module | Scope Description |
|--------|-------------------|
| Parser | Markdown DSL import, field parsing, validation (all error codes E001–E011), dependency graph construction, forward references, ID format enforcement |
| Task Engine | State machine (pending → doing → done), dependency resolution, today's task selection, cumulative estimate cap, illegal transition rejection, duplicate check-in idempotency |
| Reward Engine | XP accumulation, level calculation, streak multiplier (7/15/30-day thresholds), streak break detection, dream value computation, dream progress percentage |
| API Layer | All REST endpoints defined in API Contract v1.0 (Projects, Tasks, Progress, User), correct HTTP status codes, response schema conformance, error format validation |
| Frontend | Bottom tab navigation, home page (today tasks + level + dream), check-in flow with animation, DSL import page (paste → preview → confirm), dream reward progress page, task detail page (three type variants) |

### 1.2 Out of Scope

- Performance / load testing (>10 concurrent users)
- Security penetration testing
- Offline / sync behavior
- Multiple user / multi-tenant scenarios
- Cross-platform compatibility testing beyond H5 (no iOS/Android native builds for Phase 1)
- Accessibility (a11y) compliance
- Backup / restore functionality
- Multi-language / i18n support

---

## 2. Test Strategy

### 2.1 Unit Tests (per module)

Each engine module is tested in isolation with no framework dependencies, as defined in Architecture v1.0 Section 7.

| Module | Test File | Target Coverage | Approach |
|--------|-----------|-----------------|----------|
| Parser | `backend/tests/test_parser.py` | >= 90% line coverage | Input: raw markdown strings. Output: validate ParsedProject structure or error codes |
| Task Engine | `backend/tests/test_task_engine.py` | >= 90% line coverage | Inject mock DB session; assert state transitions and dependency behavior |
| Reward Engine | `backend/tests/test_reward_engine.py` | >= 90% line coverage | Inject mock user state; verify XP/level/streak calculations |
| DSL Validator | `backend/tests/test_dsl_validator.py` | >= 90% line coverage | Feed valid/invalid parsed dicts; assert error lists |

### 2.2 Integration Tests (API)

Use FastAPI `TestClient` to test the full HTTP layer with real SQLite.

| Area | Test File | Key Endpoints |
|------|-----------|---------------|
| Project API | `backend/tests/test_api_projects.py` | POST /api/projects, GET /api/projects, POST /api/projects/import, GET /api/projects/{pid} |
| Task API | `backend/tests/test_api_tasks.py` | GET /api/projects/{pid}/tasks, GET /api/tasks/{tid}, PATCH /api/tasks/{tid}/start, POST /api/tasks/{tid}/checkin |
| Progress API | `backend/tests/test_api_progress.py` | GET /api/users/me/xp, GET /api/users/me/streak, GET /api/projects/{pid}/reward |
| User API | `backend/tests/test_api_users.py` | GET /api/users/me, PATCH /api/users/me |

### 2.3 E2E Tests (User Journey)

Three critical user journeys tested end-to-end using the FastAPI TestClient with a fresh SQLite database per test:

1. **Journey 1 — Import & Learn**: Import quant_trading.md → verify today tasks → complete T001 → verify XP / dream progress → verify T001 is gone from today
2. **Journey 2 — Dependency Chain**: Import cfa_prep.md → verify T001 is available, T005 is blocked → complete T004 → verify T005 is now available → complete T005
3. **Journey 3 — Full Streak Cycle**: Complete tasks on consecutive simulated dates → verify streak increments → skip a day → check-in → verify streak resets to 1

---

## 3. Test Environment

| Item | Specification |
|------|---------------|
| Language | Python 3.11 |
| Web Framework | FastAPI (latest stable) |
| Database | SQLite (file-based, created with `:memory:` for test isolation) |
| Test Runner | pytest >= 7.4 |
| HTTP Client | `httpx.AsyncClient` (built into FastAPI TestClient) |
| Mocking | `unittest.mock` (stdlib, no external mocking lib) |
| Fixtures | pytest fixtures for pre-seeded databases, DSL file content |
| CI | Automated via pytest on every push; 3 test fixtures as `.md` files |

---

## 4. Test Data

Three example DSL plans serve as test fixtures. All are stored in `docs/spec/example_plans/`.

| Fixture | File | Tasks | Stages | Lines | Dependencies | Use Case |
|---------|------|-------|--------|-------|--------------|----------|
| F-01 | `quant_trading.md` | 17 | 4 | 182 | Multi-chain, T013 has dual deps | Full flow, large DSL, API integration |
| F-02 | `cfa_prep.md` | 14 | 3 | 146 | T009 dual-deps (T007,T008), T011 triple-deps | Dependency chain testing, today-tasks filtering |
| F-03 | `rust_lang.md` | 14 | 3 | 154 | Linear chain stages 1→2, dual-deps for T010 | Smoke tests, quick parser validation |

See `docs/qa/Test_Data.md` for detailed fixture descriptions.

---

## 5. Risk Areas

| Risk | Severity | Mitigation |
|------|----------|------------|
| Parser edge cases (circular deps, dangling refs, forward refs, self-ref) | High | Dedicated TC-06, plus fuzz test: randomize dependency order in DSL, verify detection |
| State machine transitions — illegal moves (done→doing, pending→done, duplicate check-in) | High | TC-10 covers explicit illegal transition; each state transition has a dedicated unit test |
| XP calculation — streak multiplier applied incorrectly, dream value formula wrong | Medium | TC-15 through TC-21 cover all known scenarios; unit tests use exact expected values |
| Large DSL performance — parser must complete in < 2s for 500+ tasks | Medium | TC-08; if threshold exceeded, profile with cProfile and optimize parsing loop |
| Streak boundary conditions — timezone, partial check-in, DST transitions | Low | Use server timezone consistently; store dates as UTC; streak logic treats "has check-in today" as boolean |
| Cumulative estimate cap — edge case where exactly 60 min of tasks available | Low | TC-14 covers exact-60 scenario; verify boundary behavior |
| Concurrent access — two requests to checkin same task simultaneously | Low | Use SQLite WAL mode + row-level locking; idempotency check in application layer |

---

## 6. Entry / Exit Criteria

### 6.1 Entry Criteria

- [ ] Parser module implemented and passes smoke test (imports without error)
- [ ] Task Engine module implemented with start() and checkin() signatures
- [ ] Reward Engine module implemented with handle_task_completed(event)
- [ ] FastAPI app boots and at least one endpoint returns 200
- [ ] SQLite schema initialized (all tables exist)
- [ ] Three test fixture DSL files placed in `docs/spec/example_plans/`
- [ ] pytest configured with `backend/tests/` as test directory

### 6.2 Exit Criteria ("Done")

- [ ] All 30 test cases (TC-01 through TC-30) pass
- [ ] Unit test line coverage >= 90% for Parser, Task Engine, Reward Engine
- [ ] All three E2E user journeys pass end-to-end
- [ ] Zero P0 defects open
- [ ] All P1 defects have documented workarounds
- [ ] API responses conform to API Contract v1.0 (spot-checked with example values)
- [ ] Parser handles all 11 error codes (E001–E011) with correct line numbers
- [ ] Test results documented with pass/fail counts and coverage report

---

## 7. Defect Severity Classification

| Severity | Name | Definition | Examples |
|----------|------|------------|----------|
| P0 | Blocker | Prevents core user flow; no workaround; blocks release | Import returns 500 on valid DSL; check-in awards 0 XP; today tasks includes done tasks |
| P1 | Major | Feature works incorrectly; workaround exists but is painful | Wrong XP calculation on edge case; streak bonus off by 1; error message missing line number |
| P2 | Minor | Cosmetic or non-blocking; does not affect data correctness | Toast message wording imprecise; animation timing slightly off; progress bar rounding at 99.9% |

### 7.1 Defect Logging Template

```
ID: BUG-XXX
Severity: P0 / P1 / P2
Module: Parser / Engine / Reward / API / Frontend
Related TC: TC-XX
Title: [Brief description]
Steps to Reproduce:
  1. ...
  2. ...
Expected: ...
Actual: ...
Test Data: F-0X (which fixture)
Environment: Python 3.11 / SQLite / Ubuntu
```

---

## 8. Test Schedule

| Phase | Duration | Activity |
|-------|----------|----------|
| Phase 1: Unit Tests | Day 1–2 | Write and execute Parser + Validator tests (TC-01–08) |
| Phase 2: Engine Tests | Day 2–3 | Write and execute Task Engine + Reward Engine tests (TC-09–21) |
| Phase 3: Integration Tests | Day 3–4 | Write and execute API layer tests (TC-22–25) |
| Phase 4: E2E + UI | Day 4–5 | E2E journeys + Frontend manual verification (TC-26–30) |
| Phase 5: Regression | Day 5 | Full suite re-run; coverage report; defect triage |

---

## Appendix A: References

- DSL Spec v1.0 — `docs/spec/DSL_Spec_v1.0.md`
- MVP Acceptance Criteria — `docs/spec/MVP_Acceptance_Criteria.md`
- API Contract v1.0 — `docs/arch/API_Contract_v1.0.yaml`
- Architecture v1.0 — `docs/arch/Architecture_v1.0.md`
- Test Cases — `docs/qa/Test_Cases_v1.0.md`
- Test Data — `docs/qa/Test_Data.md`

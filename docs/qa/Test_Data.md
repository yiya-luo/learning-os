# Test Data v1.0 — Learning OS Phase 1 MVP

Version: 1.0 | Date: 2026-06-08 | Author: QA

Three DSL fixture files serve as standardized test data across all test levels (unit, integration, E2E).

---

## Fixture Summary

| Fixture ID | File | Tasks | Stages | Dependencies | Size | Primary Use |
|------------|------|-------|--------|-------------|------|-------------|
| F-01 | `quant_trading.md` | 17 | 4 | 16 edges | Large (182 lines) | Full flow, API integration, hierarchy |
| F-02 | `cfa_prep.md` | 14 | 3 | 14 edges | Medium (146 lines) | Dependency chains, today-tasks filtering |
| F-03 | `rust_lang.md` | 14 | 3 | 14 edges | Medium (154 lines) | Quick smoke tests, linear chains |

All fixtures are stored at: `docs/spec/example_plans/`

---

## F-01: quant_trading.md — Full Flow Testing

### Purpose

The largest and most complex fixture. Used for:
- End-to-end import + check-in + progress verification
- Stage hierarchy validation (4 stages)
- Multi-dependency resolution (T013 depends on T012 AND T006)
- Full API response schema conformance
- Dream reward with nontrivial price (15000 CNY)

### Structure

```
Project: 从0学习量化交易 (deadline: 180 days, reward: Mac Studio / 15000 CNY)
├── Stage 0: 基础准备 (4 tasks)
│   ├── T001: practice | 10 XP | 60 min | no deps
│   ├── T002: theory   | 15 XP | 120 min | no deps
│   ├── T003: theory   | 10 XP | 90 min | no deps
│   └── T004: practice | 20 XP | 180 min | deps: T001
├── Stage 1: 数据获取与处理 (4 tasks)
│   ├── T005: practice | 15 XP | 120 min | deps: T004
│   ├── T006: practice | 20 XP | 120 min | deps: T005
│   ├── T007: practice | 25 XP | 180 min | deps: T006
│   └── T008: output   | 20 XP | 120 min | deps: T007
├── Stage 2: 策略开发 (5 tasks)
│   ├── T009: practice | 25 XP | 180 min | deps: T007
│   ├── T010: practice | 30 XP | 240 min | deps: T009
│   ├── T011: output   | 25 XP | 180 min | deps: T010
│   ├── T012: theory   | 30 XP | 240 min | deps: T002
│   └── T013: practice | 35 XP | 300 min | deps: T012,T006  ← dual dep
└── Stage 3: 风险管理与实盘 (4 tasks)
    ├── T014: theory   | 20 XP | 120 min | deps: T009
    ├── T015: practice | 30 XP | 240 min | deps: T014,T010  ← dual dep
    ├── T016: output   | 50 XP | 480 min | deps: T015
    └── T017: output   | 40 XP | 360 min | deps: T016
```

### Key Test Properties

| Property | Value | Useful For |
|----------|-------|------------|
| Total XP | 425 | XP accumulation across many check-ins |
| Longest dep chain | T001→T004→T005→T006→T007→T009→T010→T011 (7 hops) | Dependency chain traversal |
| Tasks with no deps | T001, T002, T003 (3 tasks) | Initial available tasks |
| Dual-dependency tasks | T013 (T012,T006), T015 (T014,T010) | Multi-dep resolution |
| Output-type tasks | T008, T011, T016, T017 | Output check-in flow (text required) |
| Max XP task | T016 (50 XP) | Large XP award testing |
| Max estimate task | T016 (480 min) | Estimate display edge case |

---

## F-02: cfa_prep.md — Dependency Chain Testing

### Purpose

Specifically designed for testing dependency resolution logic:
- Linear single-dependency chains
- Forward references (task depends on a later-numbered task)
- Triple-dependency task (T011 depends on T010, T006, T001)
- Tasks with NO dependencies scattered across stages

### Structure

```
Project: CFA Level I 备考计划 (deadline: 120 days, reward: 机械键盘 / 800 CNY)
├── Stage 0: 基础阶段 (5 tasks)
│   ├── T001: theory   | 20 XP | 300 min | no deps
│   ├── T002: theory   | 25 XP | 360 min | no deps
│   ├── T003: theory   | 20 XP | 300 min | no deps
│   ├── T004: theory   | 30 XP | 480 min | no deps
│   └── T005: theory   | 30 XP | 480 min | deps: T004
├── Stage 1: 强化阶段 (6 tasks)
│   ├── T006: theory   | 15 XP | 240 min | deps: T003
│   ├── T007: theory   | 25 XP | 300 min | deps: T005
│   ├── T008: theory   | 25 XP | 360 min | deps: T002
│   ├── T009: theory   | 15 XP | 240 min | deps: T007,T008  ← dual dep
│   ├── T010: theory   | 20 XP | 300 min | deps: T009
│   └── T011: output   | 40 XP | 300 min | deps: T010,T006,T001  ← triple dep
└── Stage 2: 冲刺阶段 (3 tasks)
    ├── T012: practice | 20 XP | 240 min | deps: T011
    ├── T013: practice | 15 XP | 180 min | deps: T011
    └── T014: output   | 10 XP | 120 min | deps: T012,T013  ← dual dep
```

### Key Test Properties

| Property | Value | Useful For |
|----------|-------|------------|
| Tasks with no deps | T001, T002, T003, T004 (4 tasks) | Initial available task pool (larger than F-01) |
| Triple-dependency task | T011 (depends on T010, T006, T001) | Verifying all deps must be done |
| Last task dep chain | T001→T011→T012→T014 and T001→T011→T013→T014 | End-to-end dependency resolution |
| Total XP | 310 | Mid-range XP accumulation |
| Reward price | 800 CNY | Small reward price — progress moves faster |

### Dependency Availability Matrix

| Step | Action | Newly Available | Still Blocked |
|------|--------|-----------------|---------------|
| Start | (initial state) | T001, T002, T003, T004 | T005 (needs T004), T006 (needs T003), T007 (needs T005), T008 (needs T002), T009 (needs T007,T008), T010 (needs T009), T011 (needs T010,T006,T001) |
| 1 | Complete T004 | T005 | T006, T007, T008, T009, T010, T011 |
| 2 | Complete T005 | T007 | T006, T008, T009, T010, T011 |
| 3 | Complete T003 | T006 | T008, T009, T010, T011 |
| 4 | Complete T002 | T008 | T009, T010, T011 |
| 5 | Complete T007, T008 | T009 | T010, T011 |
| 6 | Complete T001, T006, T009 | T010 | T011 |
| 7 | Complete T010 | T011 (now all 3 deps met!) | — |
| 8 | Complete T011 | T012, T013 | T014 |

---

## F-03: rust_lang.md — Quick Smoke Tests

### Purpose

Compact fixture for fast iteration during development:
- Linear chain across stages (sequential dependencies)
- Small XP values (quick to verify calculation)
- Balanced mix of types (theory, practice, output)
- Good for streak testing (small tasks, quick to simulate)

### Structure

```
Project: Rust语言系统学习 (deadline: 90 days, reward: HHKB键盘 / 1200 CNY)
├── Stage 0: 基础入门 (5 tasks)
│   ├── T001: practice | 5 XP  | 60 min  | no deps
│   ├── T002: theory   | 10 XP | 120 min | deps: T001
│   ├── T003: theory   | 20 XP | 180 min | deps: T002
│   ├── T004: theory   | 15 XP | 150 min | deps: T003
│   └── T005: practice | 15 XP | 180 min | deps: T004
├── Stage 1: 核心进阶 (5 tasks)
│   ├── T006: theory   | 15 XP | 150 min | deps: T005
│   ├── T007: theory   | 25 XP | 240 min | deps: T006
│   ├── T008: theory   | 15 XP | 150 min | deps: T007
│   ├── T009: theory   | 20 XP | 180 min | deps: T007
│   └── T010: output   | 30 XP | 300 min | deps: T008,T009  ← dual dep
└── Stage 2: 实战项目 (4 tasks)
    ├── T011: theory   | 20 XP | 180 min | deps: T009
    ├── T012: practice | 25 XP | 240 min | deps: T011
    ├── T013: practice | 20 XP | 180 min | deps: T012
    └── T014: output   | 50 XP | 600 min | deps: T013,T010  ← dual dep
```

### Key Test Properties

| Property | Value | Useful For |
|----------|-------|------------|
| Min XP | 5 (T001) | Smallest possible XP award |
| Max XP | 50 (T014) | Large XP, large estimate |
| Longest linear chain | T001→T002→T003→T004→T005→T006→T007 (6 hops) | Sequential dependency testing |
| Total XP | 285 | Moderate total |
| Reward price | 1200 CNY | Medium reward price |
| Dual-dependency tasks | T010 (T008,T009), T014 (T013,T010) | Multi-dep at end of chain |

### Available Tasks at Each Step

| Step | Complete | Available (no deps, not done) |
|------|----------|-------------------------------|
| Start | — | T001 |
| 1 | T001 | T002 |
| 2 | T002 | T003 |
| 3 | T003 | T004 |
| 4 | T004 | T005 |
| 5 | T005 | T006 |
| 6 | T006 | T007 |
| 7 | T007 | T008, T009 |
| 8 | T008, T009 | T010, T011 |
| 9 | T010, T011 | T012 |
| 10 | T012 | T013 |
| 11 | T013 | T014 |
| 12 | T014 | (all done) |

---

## Field Coverage Matrix

Which fixture covers which DSL field:

| Field | F-01 (quant_trading) | F-02 (cfa_prep) | F-03 (rust_lang) |
|-------|---------------------|-----------------|-------------------|
| `title` (Project) | Yes (long, Chinese) | Yes (medium) | Yes (medium) |
| `description` | Yes (long, multi-clause) | Yes (medium) | Yes (medium) |
| `reward` | Yes ("Mac Studio") | Yes ("机械键盘") | Yes ("HHKB键盘") |
| `reward_price` | Yes (15000) | Yes (800) | Yes (1200) |
| `deadline` | Yes (180) | Yes (120) | Yes (90) |
| `id` (Task) | T001–T017 | T001–T014 | T001–T014 |
| `title` (Task) | All populated | All populated | All populated |
| `type: theory` | T002, T003, T012, T014 | T001–T010 | T002–T004, T006–T009, T011 |
| `type: practice` | T001, T004–T007, T009, T010, T013, T015 | T012, T013 | T001, T005, T012, T013 |
| `type: output` | T008, T011, T016, T017 | T011, T014 | T010, T014 |
| `xp` | 10–50 range | 10–40 range | 5–50 range |
| `estimate` | 60–480 range | 120–480 range | 60–600 range |
| `depends` (single) | T004, T005, T006, T007, T009, T010, T011, T016, T017 | T005, T006, T007, T008, T010, T012, T013 | T002, T003, T004, T005, T006, T007, T008, T011, T012, T013 |
| `depends` (multi) | T013 (2), T015 (2) | T009 (2), T011 (3), T014 (2) | T010 (2), T014 (2) |
| `check` | All tasks have check criteria | All tasks have check criteria | All tasks have check criteria |
| `resource` | T001, T002, T004, T005, T011 | T001, T002 | T001, T002, T007, T010, T011, T012, T013 |
| No `depends` (root tasks) | T001, T002, T003 | T001, T002, T003, T004 | T001 |
| No `resource` | T003, T008, T009, T010, T012–T017 | T003–T014 | T003–T006, T008, T009, T014 |

---

## Generating Test Data Programmatically

For tests that require large or specific data patterns that the example fixtures don't cover (e.g., TC-08: 500 tasks), generate DSL content at runtime:

```python
def generate_large_dsl(task_count: int = 500, stages: int = 20) -> str:
    """Generate a valid DSL string with `task_count` tasks across `stages` stages."""
    lines = [
        "# Project",
        "title: Generated Large Plan",
        f"description: Auto-generated test plan with {task_count} tasks across {stages} stages",
        "deadline: 365",
        "",
        "---",
        "",
    ]
    tasks_per_stage = task_count // stages
    tid = 1

    for s in range(stages):
        lines.append(f"## Stage")
        lines.append(f"title: Stage {s + 1}")
        lines.append("")
        for _ in range(tasks_per_stage):
            lines.append(f"## Task")
            lines.append(f"id: T{tid:03d}")
            lines.append(f"title: Generated Task {tid}")
            lines.append(f"type: theory")
            lines.append(f"xp: 10")
            lines.append("")
            tid += 1

    return "\n".join(lines)
```

---

## Loading Fixtures in Tests

```python
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent.parent.parent / "docs" / "spec" / "example_plans"

def load_fixture(name: str) -> str:
    """Load a test fixture by filename."""
    path = FIXTURE_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Fixture not found: {path}")
    return path.read_text(encoding="utf-8")

# Usage:
# f01 = load_fixture("quant_trading.md")
# f02 = load_fixture("cfa_prep.md")
# f03 = load_fixture("rust_lang.md")
```

# Bug Reports — Learning OS Phase 1 MVP

Version: 1.0 | Date: 2026-06-08 | Author: QA

This directory tracks all defects found during Phase 1 testing. Each bug gets its own file: `BUG-XXX.md`.

---

## Bug Report Template

Use the following format for each bug. Create one file per bug named `BUG-XXX.md` (zero-padded three-digit number, e.g., `BUG-001.md`).

```markdown
# BUG-XXX: [Brief Title]

| Field | Value |
|-------|-------|
| **Bug ID** | BUG-XXX |
| **Severity** | P0 / P1 / P2 |
| **Module** | Parser / Engine / Reward / API / Frontend |
| **Related TC** | TC-XX |
| **Reported By** | QA |
| **Reported Date** | YYYY-MM-DD |
| **Status** | Open / In Progress / Fixed / Verified / Won't Fix |
| **Assigned To** | — |
| **Environment** | Python 3.11 / SQLite / Ubuntu / FastAPI TestClient |

## Summary

[One sentence describing the bug.]

## Steps to Reproduce

1. ...
2. ...
3. ...

## Expected Result

[What should happen per spec.]

## Actual Result

[What actually happens — include error messages, stack traces, screenshots if applicable.]

## Test Data

F-XX ([fixture name]) or inline DSL

## Root Cause

[Filled by developer after investigation.]

## Fix

[Filled by developer — commit hash or description.]

## Verification

- [ ] Fix confirmed in commit ______
- [ ] Related TC re-run and passing
- [ ] No regression in other TCs
```

---

## Severity Reference

| Severity | Definition | Examples |
|----------|------------|----------|
| P0 | Blocker — prevents core user flow, no workaround | Import 500 on valid DSL, check-in awards 0 XP, today tasks includes done |
| P1 | Major — feature broken, workaround exists | Wrong XP on edge case, streak off by 1, error missing line number |
| P2 | Minor — cosmetic, non-blocking | Toast wording, animation timing, progress bar rounding |

---

## Bug Lifecycle

```
Open → In Progress → Fixed → Verified (closed)
  │                     │
  └── Won't Fix         └── Reopened (back to Open)
```

---

## Current Bug Count

| Status | P0 | P1 | P2 | Total |
|--------|----|----|----|
| Open | 0 | 0 | 0 | 0 |
| In Progress | 0 | 0 | 0 | 0 |
| Fixed | 0 | 0 | 0 | 0 |
| Verified | 0 | 0 | 0 | 0 |
| Won't Fix | 0 | 0 | 0 | 0 |
| **Total** | **0** | **0** | **0** | **0** |

*Bugs will be filed as test execution progresses. Zero bugs exist at the time of test plan creation since no code has been tested yet.*

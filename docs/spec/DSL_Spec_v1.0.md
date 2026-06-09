# DSL Specification v1.0 — Learning OS

## Overview

Learning OS DSL (Domain Specific Language) is a Markdown-based format for defining learning plans. A
DSL document describes a project composed of stages, each containing tasks with dependencies, XP
rewards, and completion criteria.

This spec is the single source of truth for the parser implementation.

---

## 2. Document Structure

A DSL document has three hierarchical levels:

```
# Project
...
---
# Stage
...
---
## Task
...
```

- `#` (H1) — exactly one per document: the Project
- `#` (H2) — zero or more: Stage boundaries
- `##` (H3) — zero or more per Stage: Task definitions

Horizontal rules (`---`) separate Project, Stages, and between Stages. The first `---` marks the
end of the Project block and the start of Stages.

---

## 3. Project Block — H1

The document must begin with exactly one `# Project` heading, followed by YAML-style fields.

### 3.1 Fields

| Field | Type | Required | Valid Values / Range | Description |
|-------|------|----------|---------------------|-------------|
| `title` | string, ≤200 chars | **Required** | Non-empty, trimmed | Human-readable project name |
| `description` | string, ≤2000 chars | **Required** | Non-empty, trimmed | What the user will learn |
| `reward` | string, ≤200 chars | Optional | Non-empty, trimmed | Name of the dream reward (e.g. "Mac Studio") |
| `reward_price` | integer | Optional | 1–99999999 (CNY, rounded to yuan) | Price of the reward in CNY |
| `deadline` | integer | **Required** | 1–1095 (days) | Total project duration in calendar days from import date |

#### 3.1.1 Field Format Rules

- Each field is on its own line: `field_name: value`
- Fields are parsed case-sensitively (all lowercase).
- Trailing whitespace on values is stripped.
- Unknown fields are ignored by the parser (forward-compatible).
- Order of fields within the Project block is not enforced, but the canonical order above is
  recommended.

#### 3.1.2 Validation Rules

- `title` must be non-empty after trimming.
- `description` must be non-empty after trimming.
- `reward_price` may be omitted if `reward` is omitted. If `reward` is present, `reward_price` is
  still optional (price shown as "--" in UI).
- `deadline` is measured from the date the DSL is imported, not from a fixed calendar date.

#### 3.1.3 Example

```
# Project
title: 从0学习量化交易
description: 系统学习量化交易的理论、工具与实践，构建自己的交易策略
reward: Mac Studio
reward_price: 15000
deadline: 180
```

---

## 4. Stage Block — H2

A Stage groups related tasks. Stages appear after the first `---`.

### 4.1 Fields

| Field | Type | Required | Valid Values / Range | Description |
|-------|------|----------|---------------------|-------------|
| `title` | string, ≤200 chars | **Required** | Non-empty, trimmed | Name of the stage |

### 4.2 Rules

- A Stage begins with `## Stage` followed by fields, and ends at the next `## Stage` or the end of
  the document.
- Stages are implicitly ordered by their appearance in the file.
- Stages do NOT have explicit IDs — the parser assigns ordinal indices (0-based).
- A document with zero Stages is valid (all tasks are ungrouped).

### 4.3 Example

```
## Stage
title: 基础理论
```

---

## 5. Task Block — H3

A Task is the smallest unit of work. Tasks appear under their parent Stage (or as top-level items
if no Stage is defined).

### 5.1 Fields

| Field | Type | Required | Valid Values / Range | Description |
|-------|------|----------|---------------------|-------------|
| `id` | string, ≤20 chars | **Required** | Pattern: `T\d{3}` (e.g. T001) | Unique task identifier within the document |
| `title` | string, ≤200 chars | **Required** | Non-empty, trimmed | Short task description |
| `type` | enum | **Required** | `theory` \| `practice` \| `output` | Learning activity type |
| `xp` | integer | **Required** | 1–100 | Experience points awarded on completion |
| `estimate` | integer | Optional | 1–1440 (minutes) | Estimated time to complete |
| `depends` | string, ≤500 chars | Optional | Comma-separated `T\d{3}` IDs, no spaces after commas | Task IDs that must be completed before this one. Empty or absent = no dependencies. |
| `check` | string, ≤500 chars | Optional | Non-empty, trimmed | Human-readable completion criteria |
| `resource` | string, ≤2000 chars | Optional | Valid URL (http/https) or empty | Reference material link |

### 5.2 Field Format Rules

- Same line format as Project fields: `field_name: value`
- Unknown fields are ignored (forward-compatible).

### 5.3 Validation Rules

- `id` must match `T` followed by exactly 3 digits. IDs must be unique within the document.
- `type` must be exactly one of: `theory`, `practice`, `output`.
- `xp` is an integer 1–100. The parser rejects 0 and negative values.
- `depends` references must resolve to `id` values of other Tasks in the same document. Forward
  references (T005 depending on T010) are allowed — the dependency graph is resolved after parsing
  all tasks. Self-references (`depends: T001` on Task T001) are rejected.
- `depends` values with spaces (e.g. `T001, T002`) are trimmed per-ID, so `T001,T002` and
  `T001, T002` are equivalent.
- Dependency cycles are detected and rejected at parse time.
- `resource` must be a valid HTTP/HTTPS URL if non-empty, or omitted entirely.

### 5.4 Task Type Semantics

| Type | Meaning | Check-in UI Requirement |
|------|---------|------------------------|
| `theory` | Reading, watching, studying concepts | Confirm button only |
| `practice` | Coding, exercises, drills | Confirm button only |
| `output` | Producing a deliverable (code, doc, video) | Text input required (describe what was produced, min 10 chars) |

### 5.5 Example

```
## Task
id: T001
title: Python基础语法复习
type: theory
xp: 10
estimate: 60
check: 完成Python官方教程前5章
resource: https://docs.python.org/3/tutorial/
```

---

## 6. Complete Document Example

```
# Project
title: Rust语言学习
description: 系统学习Rust编程语言，掌握所有权、生命周期等核心概念
reward: 机械键盘
reward_price: 800
deadline: 90

---

## Stage
title: 基础入门

## Task
id: T001
title: 安装Rust工具链
type: practice
xp: 5
estimate: 30

## Task
id: T002
title: 阅读Rust Book第1-3章
type: theory
xp: 10
estimate: 120
depends: T001
resource: https://doc.rust-lang.org/book/

---

## Stage
title: 核心概念

## Task
id: T003
title: 所有权与借用
type: theory
xp: 20
estimate: 180
depends: T002
check: 能用自己的话解释所有权规则

## Task
id: T004
title: 实现一个链表
type: output
xp: 30
estimate: 120
depends: T003
check: 提交可编译运行的链表实现代码
```

---

## 7. Parser Behavior

### 7.1 Import Flow

1. Read the Markdown file as UTF-8 text.
2. Split on `---` to separate Project from Stages/Tasks.
3. Parse Project block fields.
4. For each Stage/Task block, parse as Stage (if heading is `## Stage`) or Task (if heading is
   `## Task`).
5. Associate Tasks with their most recent parent Stage (if any).
6. Build the dependency graph.
7. Validate:
   - Required fields present
   - Types and ranges
   - ID uniqueness
   - Dependency resolution (no dangling refs, no cycles)
   - URLs well-formed
8. On success: return the parsed structure. On failure: return a list of all errors (not just the
   first one encountered).

### 7.2 Error Format

Each parse error includes:
- Line number (1-based)
- Field or element name
- Error code (see Appendix A)
- Human-readable message

### 7.3 Graceful Degradation

- Unknown fields are silently ignored (not errors).
- Extra `---` separators are ignored.
- Blank lines between fields are ignored.
- Lines starting with `#` that are not `# Project`, `## Stage`, or `## Task` headings are treated as
  comments and ignored.

---

## Appendix A: Error Codes

| Code | Name | Description |
|------|------|-------------|
| E001 | MISSING_REQUIRED_FIELD | A required field is absent |
| E002 | INVALID_TYPE | Field value has wrong type (e.g. string where int expected) |
| E003 | INVALID_RANGE | Value outside allowed range |
| E004 | DUPLICATE_ID | Two tasks share the same `id` |
| E005 | DANGLING_DEPENDENCY | A `depends` value does not match any task `id` |
| E006 | DEPENDENCY_CYCLE | Tasks form a circular dependency |
| E007 | INVALID_URL | `resource` field is not a valid HTTP/HTTPS URL |
| E008 | SELF_DEPENDENCY | Task lists itself in `depends` |
| E009 | INVALID_ID_FORMAT | Task `id` does not match `T\d{3}` pattern |
| E010 | MISSING_PROJECT | Document does not start with `# Project` |
| E011 | INVALID_ENUM_VALUE | Field value not in allowed enum (e.g. type not theory/practice/output) |

---

## Appendix B: Data Model (Parser Output)

```python
@dataclass
class Project:
    title: str
    description: str
    reward: str | None
    reward_price: int | None
    deadline: int       # days
    stages: list[Stage]

@dataclass
class Stage:
    title: str
    index: int          # ordinal, 0-based
    tasks: list[Task]

@dataclass
class Task:
    id: str             # e.g. "T001"
    title: str
    type: Literal["theory", "practice", "output"]
    xp: int             # 1-100
    estimate: int | None   # minutes
    depends: list[str]     # e.g. ["T001", "T003"]
    check: str | None
    resource: str | None
```

"""Markdown DSL parser for Learning OS import."""

from __future__ import annotations

import re
from collections import OrderedDict
from dataclasses import dataclass


@dataclass
class ParseError:
    line: int
    message: str
    severity: str  # "error" | "warning"


# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

_RE_H1 = re.compile(r"^#\s+(.+)$")
_RE_H2 = re.compile(r"^##\s+(.+)$")
_RE_H3 = re.compile(r"^###\s+(.+)$")
_RE_KEYVAL = re.compile(r"^([a-z_]+):\s*(.*?)\s*$")
_RE_TASK_ID = re.compile(r"^T\d{3}$")
_RE_HR = re.compile(r"^---\s*$")

# Free-form task heading: ### T001 theory 30 Task Title
_RE_FREE_TASK = re.compile(r"^(T\d{3})\s+(theory|practice|output)\s+(\d+)\s+(.+)$")


# ---------------------------------------------------------------------------
# Normalizer — converts free-form markdown to standard DSL
# ---------------------------------------------------------------------------

def normalize_markdown(content: str) -> str:
    """If the markdown is in free-form format, convert it to standard DSL.

    Free-form format:
        # Plan Title
        Plan description

        ## Stage Name
        Stage description

        ### T001 theory 30 Task Title
        Task description
        > Completion criteria
        * https://resource-url

    Standard DSL format (what parse_markdown expects):
        # Project
        title: Plan Title
        description: Plan description
        deadline: 30
        ---
        ## Stage
        title: Stage Name

        ### Task
        id: T001
        title: Task Title
        type: theory
        estimate: 30
        xp: 20
        check: Completion criteria
        resource: https://resource-url
    """
    lines = content.split("\n")

    # Quick check: if it already starts with # Project, pass through
    for line in lines:
        stripped = line.strip()
        if stripped == "":
            continue
        if _RE_H1.match(stripped):
            _, text = stripped.split(" ", 1) if " " in stripped else ("", "")
            text = _RE_H1.match(stripped).group(1).strip()
            if text == "Project":
                return content
            break
        break

    # Free-form detected — convert
    output: list[str] = []
    total_estimate = 0
    task_count = 0

    i = 0
    project_title = ""
    project_desc = ""

    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        h1 = _RE_H1.match(stripped)
        h2 = _RE_H2.match(stripped)
        h3 = _RE_H3.match(stripped)

        if h1 and not project_title:
            project_title = h1.group(1).strip()
            i += 1
            # Collect description lines until next heading
            desc_parts = []
            while i < len(lines):
                nline = lines[i].strip()
                if nline == "" or _RE_HR.match(nline):
                    i += 1
                    continue
                if _RE_H1.match(nline) or _RE_H2.match(nline) or _RE_H3.match(nline):
                    break
                if not _RE_KEYVAL.match(nline):
                    desc_parts.append(nline)
                else:
                    break
                i += 1
            project_desc = " ".join(desc_parts) if desc_parts else project_title
            continue

        elif h2:
            stage_title = h2.group(1).strip()
            output.append("## Stage")
            output.append(f"title: {stage_title}")
            output.append("")
            i += 1
            # Skip stage description lines
            while i < len(lines):
                nline = lines[i].strip()
                if nline == "" or _RE_HR.match(nline):
                    i += 1
                    continue
                if _RE_H1.match(nline) or _RE_H2.match(nline) or _RE_H3.match(nline):
                    break
                if not _RE_KEYVAL.match(nline) and not nline.startswith(">") and not nline.startswith("*"):
                    i += 1
                    continue
                break
            continue

        elif h3:
            heading_text = h3.group(1).strip()
            m = _RE_FREE_TASK.match(heading_text)
            if m:
                tid, ttype, estimate, ttitle = m.groups()
                task_count += 1
                total_estimate += int(estimate)
                output.append("### Task")
                output.append(f"id: {tid}")
                output.append(f"title: {ttitle}")
                output.append(f"type: {ttype}")
                output.append(f"estimate: {estimate}")
                output.append(f"xp: {_estimate_xp(ttype)}")
                i += 1
                # Collect task body: description, > check, * resource
                while i < len(lines):
                    nline = lines[i].strip()
                    if nline == "":
                        i += 1
                        continue
                    if _RE_H1.match(nline) or _RE_H2.match(nline) or _RE_H3.match(nline):
                        break
                    if nline.startswith("> "):
                        output.append(f"check: {nline[2:]}")
                    elif nline.startswith("* "):
                        url = nline[2:].strip()
                        if url.startswith("http"):
                            output.append(f"resource: {url}")
                    i += 1
                output.append("")
                continue
            else:
                # Heading like "### Task" with key:value body — already standard
                output.append(f"### {heading_text}")
                i += 1
                continue
        else:
            i += 1
            continue

    # Build the final normalized output
    deadline = max(1, total_estimate // 60) if total_estimate > 0 else 30
    header = [
        "# Project",
        f"title: {project_title}",
        f"description: {project_desc}",
        f"deadline: {deadline}",
        "---",
        "",
    ]

    return "\n".join(header + output)


def _estimate_xp(task_type: str) -> int:
    if task_type == "output":
        return 30
    if task_type == "practice":
        return 20
    return 15


def _extract_heading(line: str) -> tuple[int, str] | None:
    """Return (level, text) for a markdown heading, or None."""
    m = _RE_H3.match(line)
    if m:
        return (3, m.group(1).strip())
    m = _RE_H2.match(line)
    if m:
        return (2, m.group(1).strip())
    m = _RE_H1.match(line)
    if m:
        return (1, m.group(1).strip())
    return None


def _parse_fields(lines: list[str]) -> dict[str, str]:
    """Parse YAML-style key: value lines into a dict."""
    fields: dict[str, str] = OrderedDict()
    for line in lines:
        m = _RE_KEYVAL.match(line)
        if m:
            key = m.group(1)
            value = m.group(2)
            fields[key] = value
    return fields


def parse_markdown(content: str) -> dict:
    """Parse a Markdown DSL string into a structured dict.

    Returns a dict with 'project' and 'stages' keys.
    """
    raw_lines = content.split("\n")
    # Strip trailing empty lines
    while raw_lines and raw_lines[-1].strip() == "":
        raw_lines.pop()

    # Pre-process: build a list of (line_number, stripped_line) for non-blank lines
    lineno_to_index: list[tuple[int, str]] = []
    for i, line in enumerate(raw_lines):
        stripped = line.rstrip("\r")
        lineno_to_index.append((i + 1, stripped))

    project_block_lines: list[str] = []
    # Remaining blocks: each is (heading_level, heading_text, start_line, [body_lines])
    blocks: list[tuple[int, str, int, list[str]]] = []

    # Phase 1: find project header and collect its body
    parse_idx = 0
    found_project = False

    while parse_idx < len(lineno_to_index):
        ln, line = lineno_to_index[parse_idx]
        stripped = line.strip()

        if stripped == "":
            parse_idx += 1
            continue

        heading = _extract_heading(stripped)
        if heading is not None:
            level, text = heading
            if level == 1 and text == "Project" and not found_project:
                found_project = True
                parse_idx += 1
                # Collect project body lines (until --- or next ## / ### heading)
                while parse_idx < len(lineno_to_index):
                    bln, body_line = lineno_to_index[parse_idx]
                    bs = body_line.strip()
                    if bs == "":
                        parse_idx += 1
                        continue
                    if _RE_HR.match(bs):
                        parse_idx += 1
                        break  # --- ends project block
                    # Check if it's a heading of any level
                    bheading = _extract_heading(bs)
                    if bheading is not None:
                        break  # new heading ends project block
                    if _RE_KEYVAL.match(bs):
                        project_block_lines.append(bs)
                    parse_idx += 1
                continue
            elif level in (2, 3):
                heading_text = text
                block_start = ln
                parse_idx += 1
                body: list[str] = []
                while parse_idx < len(lineno_to_index):
                    bln, body_line = lineno_to_index[parse_idx]
                    bs = body_line.strip()
                    if bs == "":
                        parse_idx += 1
                        continue
                    if _RE_HR.match(bs):
                        parse_idx += 1
                        continue  # skip separators within blocks
                    bheading = _extract_heading(bs)
                    if bheading is not None:
                        break
                    if _RE_KEYVAL.match(bs):
                        body.append(bs)
                    parse_idx += 1
                blocks.append((level, heading_text, block_start, body))
                continue
            else:
                # Unknown heading, skip
                parse_idx += 1
                continue
        else:
            # Not a heading, not in any block — skip
            parse_idx += 1

    if not found_project:
        return {"error": "MISSING_PROJECT", "line": 1, "message": "Document must begin with # Project"}

    # Phase 2: parse project fields
    pfields = _parse_fields(project_block_lines)

    # Phase 3: parse stages and tasks from blocks
    stages: list[dict] = []
    current_stage: dict | None = None

    for block_level, heading_text, start_ln, body_lines in blocks:
        fields = _parse_fields(body_lines)

        # Determine if this is a stage or task
        is_task = False
        heading_lower = heading_text.lower()

        # It's a task if the heading says "Task" OR if it has an id field matching T\d{3}
        if heading_lower == "task":
            is_task = True
        elif "id" in fields and _RE_TASK_ID.match(fields.get("id", "")):
            is_task = True

        if is_task:
            task = _build_task(start_ln, fields)
            if current_stage is not None:
                current_stage.setdefault("tasks", []).append(task)
            else:
                # Tasks outside any stage — create a default stage
                current_stage = {"title": "", "tasks": []}
                stages.append(current_stage)
                current_stage["tasks"].append(task)
        else:
            # Stage
            stage_title = fields.get("title", heading_text)
            current_stage = {"title": stage_title, "tasks": []}
            stages.append(current_stage)

    # Re-index stages
    for i, stage in enumerate(stages):
        stage["index"] = i

    # Phase 4: build project dict
    project: dict = {
        "title": pfields.get("title", ""),
        "description": pfields.get("description", ""),
        "reward": pfields.get("reward", None),
        "reward_price": _parse_int(pfields.get("reward_price", "")),
        "deadline": _parse_int(pfields.get("deadline", "0")),
    }

    return {"project": project, "stages": stages}


def _build_task(line: int, fields: dict[str, str]) -> dict:
    """Build a task dict from parsed fields."""
    depends_raw = fields.get("depends", "")
    depends: list[str] = []
    if depends_raw:
        depends = [d.strip() for d in depends_raw.split(",") if d.strip()]

    return {
        "id": fields.get("id", ""),
        "title": fields.get("title", ""),
        "type": fields.get("type", "theory"),
        "xp": _parse_int(fields.get("xp", "10")),
        "estimate": _parse_int(fields.get("estimate", "")) if fields.get("estimate", "") else None,
        "depends": depends if depends else None,
        "check": fields.get("check", None) if fields.get("check", "") else None,
        "resource": fields.get("resource", None) if fields.get("resource", "") else None,
    }


def _parse_int(val: str) -> int | None:
    """Parse an integer from a string, returning None if not parseable."""
    if val is None or val == "":
        return None
    try:
        return int(val)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

_VALID_TYPES = {"theory", "practice", "output"}


def validate_dsl(parsed: dict) -> list[ParseError]:
    """Validate parsed DSL structure. Returns list of ParseErrors."""
    errors: list[ParseError] = []

    if "error" in parsed:
        errors.append(ParseError(line=parsed.get("line", 1), message=parsed["message"], severity="error"))
        return errors

    project = parsed.get("project", {})
    stages = parsed.get("stages", [])

    # Project validation
    if not project.get("title"):
        errors.append(ParseError(line=1, message="E001: project.title is required", severity="error"))
    if not project.get("description"):
        errors.append(ParseError(line=1, message="E001: project.description is required", severity="error"))
    if project.get("deadline") is None:
        errors.append(ParseError(line=1, message="E001: project.deadline is required", severity="error"))
    elif isinstance(project.get("deadline"), int) and not (1 <= project["deadline"] <= 1095):
        errors.append(ParseError(
            line=1,
            message=f"E003: project.deadline must be 1-1095, got {project['deadline']}",
            severity="error",
        ))

    rp = project.get("reward_price")
    if rp is not None:
        if isinstance(rp, int):
            if rp <= 0:
                errors.append(ParseError(line=1, message=f"E003: project.reward_price must be > 0, got {rp}", severity="error"))

    # Task validation
    all_ids: set[str] = set()
    task_entries: list[dict] = []  # (task_dict, stage_index)

    for si, stage in enumerate(stages):
        for task in stage.get("tasks", []):
            tid = task.get("id", "")
            task_type = task.get("type", "")

            # Required fields
            if not tid:
                errors.append(ParseError(line=1, message="E001: task.id is required", severity="error"))
            elif not _RE_TASK_ID.match(tid):
                errors.append(ParseError(line=1, message=f"E009: invalid task id format '{tid}'", severity="error"))

            if not task.get("title"):
                errors.append(ParseError(line=1, message=f"E001: task.title is required for task '{tid}'", severity="error"))

            if task_type not in _VALID_TYPES:
                errors.append(ParseError(
                    line=1,
                    message=f"E011: task type must be one of {_VALID_TYPES}, got '{task_type}' for task '{tid}'",
                    severity="error",
                ))

            # XP validation
            xp = task.get("xp", 0)
            if isinstance(xp, int):
                if xp < 1:
                    errors.append(ParseError(line=1, message=f"E003: task.xp must be >= 1, got {xp} for task '{tid}'", severity="error"))
                elif xp > 100:
                    errors.append(ParseError(line=1, message=f"E003: task.xp must be <= 100, got {xp} for task '{tid}'", severity="error"))

            # Estimate validation
            est = task.get("estimate")
            if est is not None and isinstance(est, int) and est <= 0:
                errors.append(ParseError(line=1, message=f"E003: task.estimate must be > 0, got {est} for task '{tid}'", severity="error"))

            # Duplicate ID
            if tid and tid in all_ids:
                errors.append(ParseError(line=1, message=f"E004: duplicate task id '{tid}'", severity="error"))
            elif tid:
                all_ids.add(tid)

            # Resource URL validation
            resource = task.get("resource")
            if resource:
                if not (resource.startswith("http://") or resource.startswith("https://")):
                    errors.append(ParseError(line=1, message=f"E007: invalid resource URL '{resource}' for task '{tid}'", severity="error"))

            task_entries.append((task, si))

    # Dependency validation
    for task, _ in task_entries:
        tid = task.get("id", "")
        depends = task.get("depends")
        if not depends:
            continue
        for dep_id in depends:
            if dep_id == tid:
                errors.append(ParseError(line=1, message=f"E008: self-dependency '{tid}' depends on itself", severity="error"))
            elif dep_id not in all_ids:
                errors.append(ParseError(line=1, message=f"E005: dangling dependency '{tid}' depends on '{dep_id}' which does not exist", severity="error"))

    # Circular dependency detection (DFS)
    if not any(e.message.startswith("E005") or e.message.startswith("E008") for e in errors):
        cycle_errors = _detect_circular_deps(task_entries)
        errors.extend(cycle_errors)

    return errors


def _detect_circular_deps(tasks: list[tuple[dict, int]]) -> list[ParseError]:
    """Detect circular dependencies using DFS."""
    errors: list[ParseError] = []

    # Build adjacency list
    adj: dict[str, list[str]] = {}
    for task, _ in tasks:
        tid = task.get("id", "")
        if not tid:
            continue
        deps = task.get("depends") or []
        adj[tid] = [d for d in deps if d]

    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {tid: WHITE for tid in adj}

    def dfs(node: str, path: list[str]) -> bool:
        color[node] = GRAY
        path.append(node)
        for neighbor in adj.get(node, []):
            if neighbor not in color:
                continue  # dangling dep already reported
            if color[neighbor] == GRAY:
                cycle_start = path.index(neighbor)
                cycle = " -> ".join(path[cycle_start:] + [neighbor])
                errors.append(ParseError(line=1, message=f"E006: circular dependency detected: {cycle}", severity="error"))
                return False
            if color[neighbor] == WHITE:
                if not dfs(neighbor, path):
                    return False
        path.pop()
        color[node] = BLACK
        return True

    for node in adj:
        if color[node] == WHITE:
            dfs(node, [])

    return errors

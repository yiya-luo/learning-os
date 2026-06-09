"""Tests for the Markdown DSL parser."""

import pytest
from app.services.parser import parse_markdown, validate_dsl, ParseError


# ---------------------------------------------------------------------------
# Helper: build a minimal valid DSL document
# ---------------------------------------------------------------------------

def _dsl(project_lines: str = "", stages_blocks: str = "") -> str:
    """Build a DSL document from project fields and stage/task blocks."""
    lines = ["# Project"]
    if project_lines:
        lines.append(project_lines.strip())
    else:
        lines.append("title: Test Project")
        lines.append("description: A test")
        lines.append("deadline: 30")
    lines.append("")
    if stages_blocks:
        lines.append(stages_blocks.strip())
    return "\n".join(lines)


# ===================================================================
# Tests
# ===================================================================


class TestValidParsing:
    """Tests for successful parsing of valid DSL documents."""

    def test_complete_dsl(self):
        """Test 1: Valid complete DSL parsing."""
        content = _dsl(
            "title: Rust学习\ndescription: 学习Rust\ndeadline: 90\nreward: 机械键盘\nreward_price: 800",
            """---
## Stage
title: 基础入门

## Task
id: T001
title: 安装Rust
type: practice
xp: 5
estimate: 30

## Task
id: T002
title: 读Rust Book
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
title: 所有权
type: theory
xp: 20
estimate: 180
depends: T002
check: 能解释所有权规则

## Task
id: T004
title: 实现链表
type: output
xp: 30
estimate: 120
depends: T003
check: 提交可编译代码""",
        )
        result = parse_markdown(content)

        assert "error" not in result, f"Unexpected error: {result.get('message')}"
        assert result["project"]["title"] == "Rust学习"
        assert result["project"]["reward"] == "机械键盘"
        assert result["project"]["reward_price"] == 800
        assert result["project"]["deadline"] == 90
        assert len(result["stages"]) == 2

        s1 = result["stages"][0]
        assert s1["title"] == "基础入门"
        assert s1["index"] == 0
        assert len(s1["tasks"]) == 2
        assert s1["tasks"][0]["id"] == "T001"
        assert s1["tasks"][0]["type"] == "practice"
        assert s1["tasks"][1]["depends"] == ["T001"]

        errors = validate_dsl(result)
        assert len(errors) == 0

    def test_task_all_fields(self):
        """Test 9: Task with all fields present."""
        content = _dsl(stages_blocks="""---
## Stage
title: S1

## Task
id: T001
title: Full Task
type: output
xp: 25
estimate: 60
depends: T002
check: Complete the exercise
resource: https://example.com/ref""")
        result = parse_markdown(content)
        task = result["stages"][0]["tasks"][0]
        assert task["id"] == "T001"
        assert task["title"] == "Full Task"
        assert task["type"] == "output"
        assert task["xp"] == 25
        assert task["estimate"] == 60
        assert task["depends"] == ["T002"]
        assert task["check"] == "Complete the exercise"
        assert task["resource"] == "https://example.com/ref"

    def test_task_minimal_fields(self):
        """Test 10: Task with only required fields (id, title, type, xp)."""
        content = _dsl(stages_blocks="""---
## Stage
title: S1

## Task
id: T001
title: Minimal
type: theory
xp: 10""")
        result = parse_markdown(content)
        task = result["stages"][0]["tasks"][0]
        assert task["id"] == "T001"
        assert task["title"] == "Minimal"
        assert task["type"] == "theory"
        assert task["xp"] == 10
        assert task["estimate"] is None
        assert task["depends"] is None
        assert task["check"] is None

    def test_depends_chain(self):
        """Test 11: depends chain T001 -> T002 -> T003."""
        content = _dsl(stages_blocks="""---
## Stage
title: S1

## Task
id: T001
title: First
type: theory
xp: 10

## Task
id: T002
title: Second
type: practice
xp: 20
depends: T001

## Task
id: T003
title: Third
type: output
xp: 30
depends: T002""")
        result = parse_markdown(content)
        tasks = result["stages"][0]["tasks"]
        assert tasks[0]["depends"] is None
        assert tasks[1]["depends"] == ["T001"]
        assert tasks[2]["depends"] == ["T002"]
        errors = validate_dsl(result)
        assert len(errors) == 0

    def test_resource_url_field(self):
        """Test 14: resource URL field."""
        content = _dsl(stages_blocks="""---
## Stage
title: S1

## Task
id: T001
title: With Resource
type: theory
xp: 10
resource: https://docs.python.org/3/tutorial/""")
        result = parse_markdown(content)
        assert result["stages"][0]["tasks"][0]["resource"] == "https://docs.python.org/3/tutorial/"

    def test_check_special_chars(self):
        """Test 15: check field with special characters."""
        content = _dsl(stages_blocks="""---
## Stage
title: S1

## Task
id: T001
title: Spec Chars
type: output
xp: 10
check: 完成Python官方教程前5章，包含: (1) 数据类型, (2) 控制流 & 函数定义; 运行通过率 >= 95%""")
        result = parse_markdown(content)
        task = result["stages"][0]["tasks"][0]
        assert "Python" in task["check"]
        assert ">=" in task["check"]
        assert "95%" in task["check"]

    def test_stages_without_stage_headings(self):
        """Tasks can exist without explicit stage headings."""
        content = _dsl(stages_blocks="""---
## Task
id: T001
title: Standalone Task
type: theory
xp: 10""")
        result = parse_markdown(content)
        assert len(result["stages"]) == 1
        assert result["stages"][0]["tasks"][0]["id"] == "T001"


class TestParseErrors:
    """Tests for error detection in invalid DSL documents."""

    def test_empty_file(self):
        """Test 2: Empty file should return MISSING_PROJECT error."""
        result = parse_markdown("")
        assert "error" in result
        assert result["error"] == "MISSING_PROJECT"

    def test_missing_project_title(self):
        """Test 3: Missing project title."""
        content = _dsl("description: Desc\ndeadline: 30")
        result = parse_markdown(content)
        errors = validate_dsl(result)
        assert any("project.title" in e.message for e in errors)

    def test_missing_task_id(self):
        """Test 4: Missing task id."""
        content = _dsl(stages_blocks="""---
## Task
title: No ID
type: theory
xp: 10""")
        result = parse_markdown(content)
        errors = validate_dsl(result)
        assert any("task.id" in e.message for e in errors)

    def test_invalid_task_type(self):
        """Test 5: Invalid task type."""
        content = _dsl(stages_blocks="""---
## Stage
title: S1

## Task
id: T001
title: Bad Type
type: unknown
xp: 10""")
        result = parse_markdown(content)
        errors = validate_dsl(result)
        assert any("E011" in e.message for e in errors)

    def test_circular_dependency(self):
        """Test 6: Circular dependency detection."""
        content = _dsl(stages_blocks="""---
## Stage
title: S1

## Task
id: T001
title: Task 1
type: theory
xp: 10
depends: T002

## Task
id: T002
title: Task 2
type: theory
xp: 10
depends: T001""")
        result = parse_markdown(content)
        errors = validate_dsl(result)
        assert any("E006" in e.message for e in errors)

    def test_nested_stages(self):
        """Test 7: Nested stages (multiple stages works fine)."""
        content = _dsl(stages_blocks="""---
## Stage
title: Stage 1

## Task
id: T001
title: Task 1
type: theory
xp: 10

---
## Stage
title: Stage 2

## Task
id: T002
title: Task 2
type: theory
xp: 10""")
        result = parse_markdown(content)
        assert len(result["stages"]) == 2
        errors = validate_dsl(result)
        assert len(errors) == 0

    def test_multiple_projects(self):
        """Test 8: Multiple projects — second # Project is treated as unknown heading."""
        content = _dsl() + "\n\n# Project\ntitle: Second\ndescription: Another\ndeadline: 10"
        result = parse_markdown(content)
        # Should parse the first project only; second # Project is ignored
        assert result["project"]["title"] == "Test Project"

    def test_xp_below_1(self):
        """Test 12: XP below 1."""
        content = _dsl(stages_blocks="""---
## Stage
title: S1

## Task
id: T001
title: Low XP
type: theory
xp: 0""")
        result = parse_markdown(content)
        errors = validate_dsl(result)
        assert any("task.xp" in e.message and "<= 1" not in e.message and ">= 1" in e.message for e in errors)

    def test_xp_above_100(self):
        """Test 13: XP above 100."""
        content = _dsl(stages_blocks="""---
## Stage
title: S1

## Task
id: T001
title: High XP
type: theory
xp: 150""")
        result = parse_markdown(content)
        errors = validate_dsl(result)
        assert any("xp" in e.message and "100" in e.message for e in errors)

    def test_dangling_dependency(self):
        """Dangling dependency references non-existent task."""
        content = _dsl(stages_blocks="""---
## Stage
title: S1

## Task
id: T001
title: Task 1
type: theory
xp: 10
depends: T999""")
        result = parse_markdown(content)
        errors = validate_dsl(result)
        assert any("E005" in e.message for e in errors)

    def test_self_dependency(self):
        """Self-dependency is rejected."""
        content = _dsl(stages_blocks="""---
## Stage
title: S1

## Task
id: T001
title: Task 1
type: theory
xp: 10
depends: T001""")
        result = parse_markdown(content)
        errors = validate_dsl(result)
        assert any("E008" in e.message for e in errors)

    def test_invalid_id_format(self):
        """Task id must match T\\d{3} pattern."""
        content = _dsl(stages_blocks="""---
## Stage
title: S1

## Task
id: ABC
title: Bad ID
type: theory
xp: 10""")
        result = parse_markdown(content)
        errors = validate_dsl(result)
        assert any("E009" in e.message for e in errors)

    def test_invalid_resource_url(self):
        """Resource must be a valid HTTP/HTTPS URL."""
        content = _dsl(stages_blocks="""---
## Stage
title: S1

## Task
id: T001
title: Bad URL
type: theory
xp: 10
resource: ftp://invalid.com""")
        result = parse_markdown(content)
        errors = validate_dsl(result)
        assert any("E007" in e.message for e in errors)

    def test_deadline_out_of_range(self):
        """Deadline must be 1-1095."""
        content = _dsl("title: Test\ndescription: Desc\ndeadline: 2000")
        result = parse_markdown(content)
        errors = validate_dsl(result)
        assert any("deadline" in e.message and "2000" in e.message for e in errors)

    def test_duplicate_task_id(self):
        """Duplicate task IDs are rejected."""
        content = _dsl(stages_blocks="""---
## Stage
title: S1

## Task
id: T001
title: First
type: theory
xp: 10

## Task
id: T001
title: Duplicate
type: theory
xp: 20""")
        result = parse_markdown(content)
        errors = validate_dsl(result)
        assert any("E004" in e.message for e in errors)

    def test_forward_dependency_references(self):
        """Forward dependency references are allowed (T002 depends on T001 where T001 defined later)."""
        content = _dsl(stages_blocks="""---
## Stage
title: S1

## Task
id: T002
title: Second
type: theory
xp: 10
depends: T001

## Task
id: T001
title: First
type: theory
xp: 10""")
        result = parse_markdown(content)
        errors = validate_dsl(result)
        # No dangling dep error since T001 exists (just defined later)
        assert not any("E005" in e.message for e in errors)

    def test_comma_depends_with_spaces(self):
        """depends field tolerates spaces after commas."""
        content = _dsl(stages_blocks="""---
## Stage
title: S1

## Task
id: T001
title: First
type: theory
xp: 10

## Task
id: T002
title: Second
type: theory
xp: 10
depends: T001, T001""")
        result = parse_markdown(content)
        # T002 depends on T001 twice is fine (not a cycle, just duplicate dep)
        task = result["stages"][0]["tasks"][1]
        assert task["depends"] == ["T001", "T001"]

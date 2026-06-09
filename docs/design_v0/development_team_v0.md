# Learning OS 虚拟开发团队（v0）

> 组建日期：2026-06-08
> 项目阶段：MVP → Phase 2 → Phase 3

---

# Team Overview

| 层级 | 角色 | 代号 | 优先级 | 核心交付物 |
|------|------|------|--------|-----------|
| 产品层 | 产品经理 | PM | P0 | PRD / DSL 规格 / 验收标准 |
| 产品层 | UX/UI 设计师 | UXD | P0 | UI 设计稿 / 交互原型 |
| 技术层 | 系统架构师 | ARCH | P0 | 技术架构文档 / API 契约 / 数据模型 |
| 技术层 | 后端工程师 | BE | P0 | FastAPI 服务 / 全部 REST API |
| 技术层 | 前端工程师 | FE | P0 | UniApp 页面 / 状态管理 |
| 核心引擎 | DSL Parser 工程师 | PARSE | P0 | Markdown DSL → JSON 解析器 |
| 核心引擎 | Task Engine 工程师 | TASK | P0 | 任务状态机 / 调度器 |
| 核心引擎 | Reward System 工程师 | REWARD | P0 | XP 系统 / 梦想值系统 |
| 质量 | QA 工程师 | QA | P0 | 测试用例 / 集成测试 / Bug 报告 |
| DevOps | DevOps 工程师 | OPS | P1 | CI/CD / 部署脚本 / 环境配置 |

**团队总人数：10 人**
**协作模式：DSL 驱动开发（DSL-Driven Development）**

---

# Roles

---

## Product Manager（PM）

**代号：PM**
**优先级：P0**

### 职责说明

- 定义 DSL 完整规格（`# Project` / `# Stage` / `## Task` 的结构与字段）
- 编写可执行的 Acceptance Criteria（每个功能模块的验收条件）
- 管理 Product Backlog，按 Phase 1/2/3 排优先级
- 确保所有工程师理解 DSL 协议，DSL 是唯一输入标准
- 在开发过程中裁决功能边界（什么做、什么不做）
- 编写 `DSL_Spec_v1.0.md` 作为团队唯一事实来源（Single Source of Truth）

### 当前任务（Phase 1）

1. **输出 DSL 正式规格文档** —— 定义每个字段的类型、必填/可选、取值范围
2. **输出 MVP 验收标准清单** —— 5 条核心验收条件（导入 → 解析 → 展示 → 打卡 → 进度）
3. **编写 3 个示例 DSL 文件**（量化交易 / CFA 备考 / Rust 学习）作为团队测试 Fixture
4. **与 ARCH 对齐数据模型**，确保 DSL 字段 1:1 映射到数据库 Schema

### 输入依赖

- 产品设计文档 v0（已有）
- UI 设计文档 v0（已有）
- 技术选型方案 v0（已有）

### 输出结果

| 文件 | 说明 |
|------|------|
| `docs/spec/DSL_Spec_v1.0.md` | DSL 正式字段规格 |
| `docs/spec/MVP_Acceptance_Criteria.md` | MVP 验收标准 |
| `docs/spec/example_plans/` | 3 个示例 DSL `.md` 文件 |
| `docs/spec/Product_Backlog.md` | 三阶段 Product Backlog |

### 当前优先级

**P0** —— DSL 规格是一切开发的前提，PM 必须第一个完成交付。

---

## UX/UI Designer（UXD）

**代号：UXD**
**优先级：P0**

### 职责说明

- 基于 UI 设计文档 v0，输出可交付的页面设计稿
- 设计 5 个核心页面的布局、配色、组件规格
- 定义打卡交互动画（XP 飞入、梦想进度条动画）的参数
- 与 FE 对齐组件粒度：每个页面拆分为哪些 Vue 组件
- 确保"梦想永远可见、成长比任务重要"的设计原则落地

### 当前任务（Phase 1）

1. **输出 5 个核心页面线框图**（首页 / 学习地图 / 今日任务 / 梦想奖励 / 我的）
2. **设计打卡动画规格** —— 时序、粒子参数、震动强度（精确到 ms）
3. **输出组件树** —— 每个页面的 Vue 组件拆分方案，与 FE 对接
4. **输出色板 / 字体 / 间距 Token 表** —— CSS 变量级别

### 输入依赖

- UI 设计文档 v0（已有）
- PM 的 DSL 规格（理解 Task 类型与状态，才能设计对应 UI）

### 输出结果

| 文件 | 说明 |
|------|------|
| `docs/design/UI_Spec_v1.0.md` | 页面设计规格（含线框图描述） |
| `docs/design/Animation_Spec_v1.0.md` | 动画参数规格 |
| `docs/design/Component_Tree.md` | 前端组件树 |
| `docs/design/Design_Tokens.css` | CSS 变量定义文件 |

### 当前优先级

**P0** —— FE 等待设计稿才能开工，必须在 FE 之前完成核心页面规格。

---

## System Architect（ARCH）

**代号：ARCH**
**优先级：P0**

### 职责说明

- 设计系统整体架构：前端 → API Gateway → Service Layer → DB
- 定义所有 REST API 契约（路径、方法、请求体、响应体、状态码）
- 设计数据库 Schema（SQLite → 可迁移至 PostgreSQL）
- 定义模块间接口：Parser → Task Engine → Reward Engine 的数据流
- 确保每个模块可独立测试（通过 Mock 接口实现）
- 技术选型最终确认与风险评审

### 当前任务（Phase 1）

1. **输出系统架构图** —— 模块拓扑 + 数据流向
2. **输出完整 REST API 契约** —— 每个 Endpoint 的 OpenAPI 3.0 定义
3. **输出数据库 Schema DDL** —— 含索引、约束
4. **定义模块间内部接口** —— Parser 输出 JSON Schema / Engine 输入 JSON Schema
5. **编写 `architecture.md`** 作为技术团队唯一架构参考

### 输入依赖

- PM 的 DSL 规格（数据模型必须对齐 DSL 字段）
- 技术选型方案 v0（已有）

### 输出结果

| 文件 | 说明 |
|------|------|
| `docs/arch/Architecture_v1.0.md` | 系统架构文档 |
| `docs/arch/API_Contract_v1.0.yaml` | OpenAPI 3.0 契约 |
| `docs/arch/DB_Schema_v1.0.sql` | DDL 脚本 |
| `docs/arch/Internal_Interface_v1.0.md` | 模块间接口定义 |

### 当前优先级

**P0** —— BE / FE / PARSE / TASK / REWARD 全部依赖 ARCH 的接口契约才能并行开发。

---

## DSL Parser Engineer（PARSE）

**代号：PARSE**
**优先级：P0（最高）**

### 职责说明

- 实现 Markdown DSL 解析器，将 `.md` 文本解析为结构化 JSON
- 解析层次：`# Project` → `# Stage` → `## Task`，提取所有字段（id / title / type / xp / estimate / depends / check / resource）
- 支持解析前置依赖（`depends: T001`），构建 Task DAG
- 输入校验：非法 DSL 格式必须返回明确错误信息
- 解析结果作为 Task Engine 的输入

### 当前任务（Phase 1）

1. **实现 `parser.py`** —— 规则解析器，按行解析 Markdown 层级
2. **定义 Parser 输出 JSON Schema** —— 与 ARCH 对齐
3. **编写 Parser 单元测试** —— 覆盖：正常 DSL / 空文件 / 缺少必填字段 / 循环依赖 / 嵌套 Stage
4. **编写 `POST /api/projects/import` 的 Parser 部分**

### 具体工程任务

```text
Task 1: 实现 parse_markdown(content: str) -> dict
  - 按 \n 分割行
  - 识别 # / ## / ### 层级
  - 提取 YAML-style 字段（key: value）
  - 构建嵌套 Project → Stage[] → Task[] 结构

Task 2: 实现 validate_dsl(parsed: dict) -> list[Error]
  - 必填字段检查：Project.title / Task.id / Task.title / Task.type
  - type 枚举检查：theory / practice / output
  - depends 引用完整性检查
  - 循环依赖检测（DFS）
  - XP 范围检查：10 ≤ xp ≤ 50

Task 3: 编写 15+ 单元测试用例
  - test_parse_valid_dsl()
  - test_parse_empty_file()
  - test_parse_missing_project_title()
  - test_parse_missing_task_id()
  - test_parse_invalid_task_type()
  - test_parse_circular_dependency()
  - test_parse_nested_stages()
  - test_parse_multiple_projects()
  - test_parse_task_with_all_fields()
  - test_parse_task_with_minimal_fields()
  - test_parse_depends_chain()
  - test_validate_xp_range()
  - test_output_json_schema_compliance()
  - test_parse_resource_field()
  - test_parse_check_field()
```

### 输入依赖

- PM 的 DSL 规格文档（字段定义）
- ARCH 的 Parser 输出 JSON Schema

### 输出结果

| 文件 | 说明 |
|------|------|
| `backend/app/services/parser.py` | DSL 解析器实现 |
| `backend/tests/test_parser.py` | 解析器单元测试 |
| `docs/spec/Parser_Output_Schema.json` | 解析输出 JSON Schema |

### 当前优先级

**P0（最高）** —— Parser 是整个系统的入口，所有下游模块（Task Engine / Reward System / FE）都依赖 Parsed JSON。

---

## Task Engine Engineer（TASK）

**代号：TASK**
**优先级：P0（最高，与 PARSE 并列）**

### 职责说明

- 实现任务状态机：`pending → doing → done`
- 实现今日任务调度器：筛选未完成 + 依赖已满足 + 时间 ≤ 60min 的任务
- 实现打卡逻辑：状态变更 + 触发 XP 计算 + 触发梦想值更新
- 管理任务依赖：前置任务未完成时，不允许将任务状态改为 `doing`
- 提供 Task CRUD API

### 当前任务（Phase 1）

1. **实现 `engine.py`** —— Task 状态机 + 调度逻辑
2. **实现 Task API Endpoints** —— CRUD + 打卡
3. **实现任务依赖 DAG 遍历** —— 只暴露"可执行任务"
4. **编写 Engine 单元测试** —— 覆盖所有状态转换路径

### 具体工程任务

```text
Task 1: 实现 TaskStateMachine
  - 合法转换：pending → doing → done
  - 非法转换：done → doing（拒绝）、pending → done（拒绝，必须先 doing）
  - 状态变更时发射 Event（用于 Reward System 订阅）

Task 2: 实现 TaskScheduler.get_today_tasks(project_id) -> list[Task]
  - 筛选 status != 'done' 的任务
  - 筛选 depends 全部满足的任务
  - 按 Stage 顺序排序
  - 累计 estimate ≤ 60 分钟截断

Task 3: 实现 checkin(task_id) -> CheckinResult
  - 验证状态可转换
  - 更新 status → done
  - 发射 TaskCompletedEvent(task_id, xp, timestamp)
  - 返回打卡结果（含 XP、梦想值增量）

Task 4: 实现 Task CRUD API
  GET    /api/projects/{pid}/tasks          # 获取所有任务
  GET    /api/projects/{pid}/tasks/today     # 获取今日任务
  GET    /api/tasks/{tid}                    # 获取任务详情
  PATCH  /api/tasks/{tid}/start             # 开始任务（pending → doing）
  POST   /api/tasks/{tid}/checkin            # 完成任务打卡
```

### 输入依赖

- PARSE 的输出（Parsed JSON → 初始化 Task 表）
- ARCH 的 API 契约 + DB Schema
- PM 的 DSL 规格（理解 Task 字段含义）

### 输出结果

| 文件 | 说明 |
|------|------|
| `backend/app/services/engine.py` | 任务状态机 + 调度器 |
| `backend/app/api/task.py` | Task REST API |
| `backend/tests/test_engine.py` | Engine 单元测试 |

### 当前优先级

**P0（最高）** —— Task Engine 是系统的核心状态管理者，打卡闭环依赖此模块。

---

## Reward System Engineer（REWARD）

**代号：REWARD**
**优先级：P0**

### 职责说明

- 实现 XP 系统：完成任务获得 XP，XP 累积升级
- 实现梦想值系统：XP → 梦想值换算（1 XP ≈ 1 元成长价值，可配置）
- 实现等级系统：Lv1 ~ Lv6，每级 XP 阈值
- 实现连续打卡（Streak）逻辑
- 订阅 TaskCompletedEvent，自动计算奖励

### 当前任务（Phase 1）

1. **实现 `reward.py`** —— XP 计算 + 梦想值 + 等级 + Streak
2. **实现 Reward API Endpoints**
3. **编写 Reward 单元测试** —— 覆盖 XP 边界、等级跃迁、Streak 中断

### 具体工程任务

```text
Task 1: 实现 XP 计算器
  xp_gained = task.xp  # 直接取 Task 定义的 XP 值
  连续打卡 bonus：
    7天 +10%
    15天 +20%
    30天 +50%

Task 2: 实现等级系统
  Lv1（新手）：0-99 XP
  Lv2（学习者）：100-299 XP
  Lv3（工程师）：300-599 XP
  Lv4（研究员）：600-999 XP
  Lv5（独立开发者）：1000-1999 XP
  Lv6（长期主义者）：2000+ XP

Task 3: 实现梦想值系统
  dream_value += xp_gained * DREAM_MULTIPLIER（默认 5.0，可配置）
  梦想进度 = accumulated_dream_value / total_reward_price * 100%

Task 4: 实现 Streak 系统
  - 每天至少完成 1 个 Task → streak + 1
  - 当天无完成 → streak = 0（允许断签）
  - streak 存储为独立字段

Task 5: 实现 Reward API
  GET  /api/users/me/xp           # 获取当前 XP + 等级
  GET  /api/users/me/streak       # 获取连续打卡天数
  GET  /api/projects/{pid}/reward # 获取梦想进度
```

### 输入依赖

- TASK 的 TaskCompletedEvent（事件订阅）
- ARCH 的 API 契约 + DB Schema
- PM 的 DSL 规格（Task 中的 xp 字段）

### 输出结果

| 文件 | 说明 |
|------|------|
| `backend/app/services/reward.py` | XP + 梦想值 + 等级 + Streak 系统 |
| `backend/app/api/progress.py` | Reward REST API |
| `backend/tests/test_reward.py` | Reward 单元测试 |

### 当前优先级

**P0** —— 打卡闭环的最后一步，没有奖励反馈就没有用户留存。

---

## Backend Engineer（BE）

**代号：BE**
**优先级：P0**

### 职责说明

- 搭建 FastAPI 项目骨架
- 实现非核心 CRUD API（Project / User / Stage）
- 集成 PARSE / TASK / REWARD 三个核心模块到 API 路由
- 实现 SQLite 数据库初始化与迁移
- 编写 E2E API 测试（从导入 DSL 到打卡完成的全链路）

### 当前任务（Phase 1）

1. **初始化 FastAPI 项目** —— 目录结构 / 依赖管理 / 配置
2. **实现 Project CRUD API**
3. **实现 User API**（注册 / 获取信息）
4. **实现 `POST /api/projects/import`** —— 整合 Parser → 写入 DB → 返回任务树
5. **编写全链路集成测试**

### 具体工程任务

```text
Task 1: 项目骨架搭建
  backend/
    main.py              # FastAPI 入口
    app/
      __init__.py
      config.py           # 配置管理
      database.py         # SQLite 连接
      api/
        __init__.py
        project.py        # Project CRUD
        task.py           # Task 路由（集成 TASK 模块）
        progress.py       # Progress 路由（集成 REWARD 模块）
        user.py           # User 路由
      services/
        __init__.py
        parser.py         # （集成 PARSE 模块）
        engine.py         # （集成 TASK 模块）
        reward.py         # （集成 REWARD 模块）
      models/
        __init__.py
        models.py         # SQLAlchemy / Pydantic Models
  tests/
    test_api_e2e.py       # 全链路测试
  requirements.txt
  pyproject.toml

Task 2: 实现 API Endpoints
  POST   /api/projects                        # 创建项目
  GET    /api/projects                        # 获取项目列表
  GET    /api/projects/{pid}                  # 获取项目详情
  POST   /api/projects/import                 # 导入 DSL Markdown
  GET    /api/projects/{pid}/stages           # 获取 Stage 树
  GET    /api/users/me                        # 获取当前用户
  PATCH  /api/users/me                        # 更新用户信息

Task 3: 集成 DSL 导入全链路
  POST /api/projects/import
  1. 接收 Markdown 文本
  2. 调用 parser.parse_markdown()
  3. 调用 parser.validate_dsl()
  4. 写入 Project / Stage / Task 表
  5. 返回完整任务树 JSON
```

### 输入依赖

- ARCH 的 API 契约 + DB Schema
- PARSE / TASK / REWARD 模块的 Python 接口
- 前端不需要等待所有 API 完成，可以并行用 Mock 数据开发

### 输出结果

| 文件 | 说明 |
|------|------|
| `backend/` | 完整 FastAPI 项目 |
| `backend/tests/test_api_e2e.py` | 全链路 E2E 测试 |
| `backend/requirements.txt` | Python 依赖清单 |

### 当前优先级

**P0** —— BE 是 PARSE / TASK / REWARD 的集成点，也是 FE 的 API 提供方。

---

## Frontend Engineer（FE）

**代号：FE**
**优先级：P0**

### 职责说明

- 搭建 UniApp (Vue 3) 项目骨架
- 实现 5 个核心页面：首页 / 学习地图 / 今日任务 / 梦想奖励 / 我的
- 实现 Pinia 状态管理（ProjectState / TaskState / UserState / RewardState）
- 实现 DSL 导入页面（Markdown 粘贴 + 预览）
- 实现打卡交互（动画 + API 调用）

### 当前任务（Phase 1）

1. **初始化 UniApp 项目** —— 目录结构 / Pinia / 路由 / 底部 Tab
2. **实现首页** —— 用户等级卡片 + 今日任务列表 + 梦想进度条
3. **实现今日任务页** —— 任务列表 + 打卡按钮 + 打卡动画
4. **实现 DSL 导入页** —— 文本输入框 + 解析预览 + 确认导入
5. **实现学习地图页** —— Stage/Task 树形展示
6. **实现梦想奖励页** —— 奖励图片 + 进度条 + 进度文字

### 具体工程任务

```text
Task 1: UniApp 项目初始化
  frontend/
    pages/
      home/index.vue        # 首页
      map/index.vue         # 学习地图
      task/index.vue        # 今日任务
      reward/index.vue      # 梦想奖励
      profile/index.vue     # 我的
      import/index.vue      # DSL 导入
    store/
      project.ts            # ProjectState
      task.ts               # TaskState
      user.ts               # UserState
      reward.ts             # RewardState
    components/
      TaskCard.vue          # 任务卡片组件
      ProgressBar.vue       # 进度条组件
      CheckinAnimation.vue  # 打卡动画组件
      StageTree.vue         # Stage 树组件
      DreamProgress.vue     # 梦想进度组件
    utils/
      api.ts                # API 请求封装
    App.vue
    pages.json              # 页面配置 + TabBar

Task 2: 页面实现（按 P0 顺序）
  1. home/index.vue         # 第一优先 —— 用户打开小程序看到的第一屏
  2. task/index.vue         # 任务详情 + 打卡
  3. import/index.vue       # DSL 导入入口
  4. reward/index.vue       # 梦想奖励
  5. map/index.vue          # 学习地图

Task 3: 打卡动画实现
  - 点击【完成打卡】→ 按钮 Loading 态（≤300ms）
  - 调用 POST /api/tasks/{tid}/checkin
  - 成功 → 粒子动画 "+30 XP" "+150 梦想值"（2s）
  - 进度条平滑过渡
  - 失败 → Toast 错误信息

Task 4: DSL 导入页面
  - 大文本输入框（placeholder 含 DSL 格式提示）
  - 支持粘贴 Markdown
  - 点击"预览"→ 调用解析 API 显示结构化预览
  - 点击"确认导入"→ 调用 POST /api/projects/import
  - 成功 → 跳转首页
```

### 输入依赖

- UXD 的设计稿 / 组件树
- ARCH 的 API 契约（FE 可先用 Mock Server 并行开发）
- BE 的 API（后期联调）

### 输出结果

| 文件 | 说明 |
|------|------|
| `frontend/` | 完整 UniApp 项目 |
| `frontend/store/` | Pinia 状态管理 |
| `frontend/pages/` | 6 个页面 |
| `frontend/components/` | 5 个公共组件 |

### 当前优先级

**P0** —— FE 是用户唯一接触面，MVP 必须有完整可用的 5 个页面。

---

## QA Engineer（QA）

**代号：QA**
**优先级：P0**

### 职责说明

- 编写 MVP 测试计划（Test Plan）
- 设计测试用例矩阵（覆盖正常路径 + 边界 + 错误路径）
- 手工 / 自动化测试 DSL 导入 → 解析 → 打卡全链路
- 验证 DSL 规格一致性：所有 DSL 示例文件都能被正确解析
- 报告 Bug，追踪修复状态

### 当前任务（Phase 1）

1. **编写 Test Plan** —— 按模块拆分测试范围
2. **编写 Test Case 矩阵** —— 至少 30 条
3. **准备测试数据** —— 基于 PM 的 3 个示例 DSL
4. **执行 Phase 1 全链路测试** —— 阻塞发布的 Bug = 0

### 测试用例矩阵（核心）

```text
模块：DSL Parser
  TC-01: 导入完整合法的 DSL → 解析成功，返回任务树
  TC-02: 导入空文件 → 返回错误 "DSL 内容为空"
  TC-03: 导入缺少 Project title 的 DSL → 返回错误
  TC-04: 导入 Task 缺少 id → 返回错误
  TC-05: 导入 Task type 非法值 → 返回错误
  TC-06: 导入含循环依赖的 DSL → 返回错误
  TC-07: 导入含嵌套 Stage 的 DSL → 正确解析层级
  TC-08: 导入超大 DSL（500+ Task）→ 解析时间 < 2s

模块：Task Engine
  TC-09: pending → doing → done 正常转换
  TC-10: done → doing 非法转换 → 返回错误
  TC-11: 有未满足依赖的 Task → 不可设为 doing
  TC-12: 依赖全部完成后 → Task 可执行
  TC-13: 今日任务只显示未完成 + 依赖满足的任务
  TC-14: 今日任务累计时间 ≤ 60 分钟

模块：Reward System
  TC-15: 完成 20 XP 任务 → 获得 20 XP
  TC-16: 连续打卡 7 天 → XP bonus +10%
  TC-17: 断签 → streak = 0
  TC-18: XP 达到 100 → 升级为 Lv2
  TC-19: 梦想值 = XP × DREAM_MULTIPLIER

模块：API
  TC-20: POST /api/projects/import 全链路成功
  TC-21: POST /api/tasks/{tid}/checkin 全链路成功
  TC-22: GET /api/projects/{pid}/tasks/today 返回正确任务列表

模块：前端
  TC-23: 首页加载显示用户等级 + 今日任务
  TC-24: 打卡按钮点击 → 动画播放 → 状态更新
  TC-25: DSL 导入页粘贴 Markdown → 预览 → 确认导入
  TC-26: 梦想奖励页显示正确进度
  TC-27: 学习地图正确展示 Stage/Task 树
  TC-28: 底部 Tab 切换正常
  TC-29: 网络错误时 Toast 提示
  TC-30: 深色/浅色模式切换
```

### 输入依赖

- PM 的验收标准
- PM 的示例 DSL 文件
- 所有工程师的交付物

### 输出结果

| 文件 | 说明 |
|------|------|
| `docs/qa/Test_Plan_v1.0.md` | 测试计划 |
| `docs/qa/Test_Cases_v1.0.md` | 测试用例矩阵 |
| `docs/qa/Bug_Reports/` | Bug 报告 |

### 当前优先级

**P0** —— QA 在 Phase 1 最后执行验收，但测试计划和用例必须在开发开始前准备好（TDD 模式）。

---

## DevOps Engineer（OPS）

**代号：OPS**
**优先级：P1**

### 职责说明

- 搭建 CI/CD Pipeline（GitHub Actions）
- 配置开发环境一键启动脚本
- 后端 API 自动部署（开发环境）
- 前端 UniApp 构建与发布流程

### 当前任务（Phase 1）

1. **编写 `docker-compose.yml`** —— 一键启动后端 + 数据库
2. **编写 GitHub Actions CI** —— 每次 Push 自动跑 Parser / Engine / Reward 单元测试
3. **编写开发环境设置脚本** —— `scripts/setup.sh`

### 具体工程任务

```text
Task 1: Docker 化后端
  Dockerfile（Python 3.11 + FastAPI）
  docker-compose.yml（backend + sqlite volume）

Task 2: CI Pipeline
  .github/workflows/ci.yml
  步骤：
    - checkout
    - setup python
    - pip install -r requirements.txt
    - pytest backend/tests/
    - lint: ruff check backend/

Task 3: 开发脚本
  scripts/setup.sh    # 初始化 venv + pip install
  scripts/dev.sh      # 启动开发服务器
  scripts/test.sh     # 运行全部测试
```

### 输入依赖

- 后端项目结构（BE）
- 技术选型方案 v0

### 输出结果

| 文件 | 说明 |
|------|------|
| `Dockerfile` | 后端容器化 |
| `docker-compose.yml` | 一键部署 |
| `.github/workflows/ci.yml` | CI Pipeline |
| `scripts/` | 开发脚本 |

### 当前优先级

**P1** —— Phase 1 可手动运行，但 CI 能加速 PARSE / TASK / REWARD 的测试反馈循环。

---

# Development Plan

---

## Phase 1（MVP）—— 闭环验证

**目标：能导入 DSL → 能解析任务 → 能打卡 → 能看到进度**

**工期：7 天（按 v0 技术方案）**

### Day 1-2：设计 + 基础设施

| 角色 | 任务 | 交付物 |
|------|------|--------|
| PM | 编写 DSL 规格 v1.0 | `DSL_Spec_v1.0.md` |
| PM | 编写 3 个示例 DSL | `example_plans/*.md` |
| PM | 编写验收标准 | `MVP_Acceptance_Criteria.md` |
| UXD | 输出 5 个页面设计稿 | `UI_Spec_v1.0.md` |
| UXD | 输出组件树 | `Component_Tree.md` |
| ARCH | 输出架构文档 | `Architecture_v1.0.md` |
| ARCH | 输出 API 契约 | `API_Contract_v1.0.yaml` |
| ARCH | 输出 DB Schema DDL | `DB_Schema_v1.0.sql` |
| BE | FastAPI 项目骨架 | `backend/` 目录 |
| FE | UniApp 项目骨架 + 首页 UI | `frontend/` 目录 |
| OPS | Docker + CI 配置 | `docker-compose.yml` / CI |

### Day 3-4：核心引擎开发（P0 最高）

| 角色 | 任务 | 交付物 |
|------|------|--------|
| PARSE | 实现 `parser.py` | 完整解析器 |
| PARSE | 编写 Parser 单元测试 | `test_parser.py` |
| TASK | 实现 `engine.py` | 状态机 + 调度器 |
| TASK | 编写 Engine 单元测试 | `test_engine.py` |
| REWARD | 实现 `reward.py` | XP + 梦想 + 等级 |
| REWARD | 编写 Reward 单元测试 | `test_reward.py` |
| QA | 编写 Test Plan + Test Cases | 测试文档 |

### Day 5：后端集成 + 前端核心页面

| 角色 | 任务 | 交付物 |
|------|------|--------|
| BE | 集成 PARSE + TASK + REWARD 到 API | 完整 API |
| BE | 实现 `POST /api/projects/import` | DSL 导入 API |
| BE | 编写 E2E 测试 | `test_api_e2e.py` |
| FE | 实现 DSL 导入页面 | `import/index.vue` |
| FE | 实现今日任务页面 | `task/index.vue` |
| FE | 实现打卡交互 + 动画 | `CheckinAnimation.vue` |

### Day 6：前端全部页面 + 联调

| 角色 | 任务 | 交付物 |
|------|------|--------|
| FE | 实现梦想奖励页 | `reward/index.vue` |
| FE | 实现学习地图页 | `map/index.vue` |
| FE | 实现个人中心页 | `profile/index.vue` |
| FE | 前后端联调 | 全页面 API 对接 |
| BE | Bug 修复 | 联调中的问题修复 |

### Day 7：测试 + 修复 + 发布

| 角色 | 任务 | 交付物 |
|------|------|--------|
| QA | 执行全链路测试 30 条用例 | Bug 报告 |
| ALL | Bug 修复 | 阻塞 Bug = 0 |
| PM | MVP 验收 | 通过 / 不通过 |
| OPS | 部署 MVP 版本 | 可访问的测试环境 |

### Phase 1 验收标准

```
□ 粘贴 Markdown DSL → 点击导入 → 成功创建项目
□ 首页显示今日任务列表（依赖已满足、未完成的）
□ 点击 Task → 查看详情（理论 / 实践 / 输出）
□ 点击【完成打卡】→ 动画播放 → XP 增加 → 梦想进度更新
□ 梦想奖励页显示正确进度百分比
```

---

## Phase 2（增强）—— 体验升级

**目标：XP 系统 → 梦想奖励 → 学习地图可视化**

**工期：7 天**

### 任务拆分

| 角色 | 任务 | 详细说明 |
|------|------|----------|
| PM | 定义 XP 等级表 + 梦想值换算公式 | 精确到数值 |
| UXD | 设计学习地图交互（节点展开/收起/高亮依赖线） | 技能树 UI |
| UXD | 设计成长热力图 UI | GitHub 绿点风格 |
| ARCH | 设计数据分析接口（热力图数据聚合） | `GET /api/users/me/heatmap` |
| BE | 实现热力图数据 API | 按日期聚合打卡记录 |
| BE | 实现 Stage 进度 API | Stage 内 Task 完成率 |
| FE | 学习地图交互增强 | 树节点展开/收起/依赖连线动画 |
| FE | 成长热力图页面 | 日历热力图 |
| FE | 打卡后梦想飞入动画（首页） | XP 数字飞到梦想进度条 |
| REWARD | Streak bonus 完善 | 7/15/30 天 bonus 逻辑 |
| REWARD | 随机彩蛋实现 | 5% 概率触发额外 XP |
| PARSE | 支持 reward 字段解析 | DSL 中的 reward 块 |
| TASK | 支持 Task 依赖可视化 | 依赖 DAG 数据 API |
| QA | Phase 2 全链路测试 | 新增 20 条测试用例 |
| OPS | 数据库备份脚本 | SQLite 定时备份 |

### Phase 2 验收标准

```
□ 学习地图正确展示 Stage/Task 树形结构，依赖关系可见
□ 连续打卡 7 天获得 XP bonus
□ 梦想值随打卡平滑增长，进度条动画流畅
□ 成长热力图显示过去 30 天打卡记录
□ 随机彩蛋正常触发（概率 5%）
```

---

## Phase 3（高级）—— 智能与洞察

**目标：AI 鼓励系统 → 数据分析 → 成长可视化**

**工期：10 天**

### 任务拆分

| 角色 | 任务 | 详细说明 |
|------|------|----------|
| PM | 定义 AI 鼓励文案分类规则 | 成长型/奖励型/未来型/回顾型/彩蛋型 |
| PM | 定义数据分析指标 | 完成率 / 学习时长 / 效率曲线 |
| UXD | 设计成长时间轴 UI | 里程碑事件展示 |
| UXD | 设计 AI 鼓励弹窗样式 | 5 种类型不同样式 |
| UXD | 设计数据分析看板 | 折线图 / 柱状图 / 雷达图 |
| ARCH | 设计 AI 鼓励系统接口 | 触发规则引擎 |
| BE | 实现 AI 鼓励触发规则引擎 | streak / milestone / 随机 |
| BE | 实现数据分析聚合 API | SQL 聚合 + 缓存 |
| BE | 集成 AI 模型调用（可选） | OpenAI / Claude 生成鼓励文案 |
| FE | 实现 AI 鼓励弹窗组件 | 5 种类型 + 动画 |
| FE | 实现成长时间轴页 | 里程碑 + 日志列表 |
| FE | 实现数据分析看板 | echarts 图表 |
| REWARD | 实现隐藏成就系统 | 里程碑触发条件 |
| QA | Phase 3 全链路测试 | 新增 25 条用例 |

### Phase 3 验收标准

```
□ 完成任务后弹出 AI 鼓励文案（随机选择类型）
□ 连续学习 30 天触发特殊鼓励弹窗
□ 数据分析看板显示学习趋势图
□ 成长时间轴展示里程碑事件
□ 隐藏成就按条件触发（首次/连续/总量）
```

---

# Task Dependency Graph

```
                          PM（DSL 规格）
                         /      |      \
                        /       |       \
                   ARCH      UXD      PARSE（依赖 DSL 字段定义）
                  /  |  \       \          \
                 /   |   \       \          \
               BE   TASK  REWARD  FE       TASK（依赖 Parser 输出 Schema）
               |    /  \      \    \         /
               |   /    \      \    \       /
               +--+------+------+----+-----+
                  |                    |
               QA（依赖所有模块交付）  OPS（依赖 BE 项目结构）
                  |
               PM（验收）


Phase 1 核心依赖链（关键路径）：

  PM → ARCH → { PARSE, TASK, REWARD } → BE → FE → QA → 验收

  关键路径分析：
    1. PM 必须先完成 DSL 规格（阻塞 ARCH + PARSE）
    2. ARCH 必须先完成 API 契约 + DB Schema（阻塞 BE + TASK + REWARD）
    3. PARSE 必须先完成（阻塞 TASK 集成测试、BE 集成 Import API）
    4. TASK 必须先完成（阻塞 REWARD 的事件订阅、BE 集成 Task API）
    5. BE 集成完成（阻塞 FE 联调）
    6. FE 页面完成（阻塞 QA 全链路测试）
    7. QA 通过（阻塞 PM 验收）

  可并行工作：
    - UXD 与 PM 并行（都从 v0 文档出发）
    - PARSE / TASK / REWARD 拿到 ARCH 接口契约后可并行开发
    - FE 在拿到 UXD 设计稿 + ARCH API 契约后可 Mock 并行开发
    - OPS 不阻塞任何关键路径，可在 Day 1 独立完成


Phase 1 → Phase 2 依赖：

  Phase 1 通过验收
       ↓
  Phase 2 启动
       ↓
  REWARD（Streak Bonus + 彩蛋）依赖 Phase 1 REWARD 基础
  FE（学习地图增强）依赖 Phase 1 FE 地图基础页面
  BE（热力图 API）依赖 Phase 1 DB 中的打卡记录积累


Phase 2 → Phase 3 依赖：

  Phase 2 通过验收
       ↓
  Phase 3 启动
       ↓
  ARCH（AI 鼓励接口）依赖 Phase 2 REWARD 的用户 XP/Streak 数据
  BE（数据分析聚合）依赖 Phase 2 DB 中足够的打卡历史数据（≥30 天）
  FE（数据分析看板）依赖 BE 聚合 API


团队协作沟通节点（Standup 节奏）：

  每日：
    09:00 - 全队 Standup（15min），每人回答：
      昨天完成了什么？
      今天要做什么？
      被谁阻塞 / 阻塞了谁？

  关键里程碑检查点：
    Day 2 结束：PM + ARCH + UXD 交付设计文档（设计冻结）
    Day 4 结束：PARSE + TASK + REWARD 模块独立测试通过（引擎冻结）
    Day 5 结束：BE API 集成完成 + FE 核心页面完成（集成完成）
    Day 7 结束：QA 全链路测试通过 + PM 验收通过（MVP 发布）
```

---

# DSL 协议（附：团队开发的唯一契约）

以下 DSL 格式是整个团队协作的核心契约，PM 输出的 `DSL_Spec_v1.0.md` 必须精确到每个字段的类型和约束。

```markdown
# Project
title: 从0学习量化交易
description: 180天系统学习量化交易
reward: Mac Studio
reward_price: 15000
deadline: 2026-12-31

---

# Stage
title: 金融基础

---

## Task
id: T001
title: 理解收益率计算
type: theory
xp: 20
estimate: 30
depends: 
check: 能解释 simple return 和 log return 的区别
resource: https://example.com/returns

---

## Task
id: T002
title: 下载AAPL历史数据
type: practice
xp: 30
estimate: 45
depends: T001
check: 成功获取 AAPL 5年日线数据
resource: 

---

# Stage
title: 数据获取

---

## Task
id: T003
title: 理解API鉴权方式
type: theory
xp: 15
estimate: 20
depends: 
check: 能说出 OAuth 2.0 的四种授权模式
resource: https://oauth.net/2/

---

## Task
id: T004
title: 接入数据源API
type: practice
xp: 40
estimate: 60
depends: T002, T003
check: 成功从 API 拉取 10 只股票的日线数据
resource: 

---

## Task
id: T005
title: 编写数据清洗脚本
type: output
xp: 25
estimate: 30
depends: T004
check: 脚本无报错，输出标准化 DataFrame
resource: 
```

**每一个 Task 字段说明（Parser 验收标准）：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string (T\d+) | 是 | 唯一标识 |
| `title` | string | 是 | 任务标题 |
| `type` | enum(theory\|practice\|output) | 是 | 任务类型 |
| `xp` | int (10-50) | 是 | 经验值奖励 |
| `estimate` | int (分钟) | 否 | 预计耗时 |
| `depends` | string (逗号分隔的 ID) | 否 | 前置依赖任务 |
| `check` | string | 否 | 完成检查标准 |
| `resource` | string (URL) | 否 | 学习资源链接 |

---

**文档版本：v0**
**下次更新：PM 完成 DSL_Spec_v1.0.md 后，更新本文档中的 DSL 规格引用**

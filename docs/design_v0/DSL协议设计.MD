# Learning OS Markdown DSL 规范（v0）

---

# 一、设计目标

这个 DSL 不是“文档格式”，而是：

> **学习任务的结构化指令语言**

必须满足：

```text id="dsl-1"
① AI可生成
② 程序可解析
③ 可扩展
④ 可版本升级
⑤ 不依赖特定领域（量化 / CFA / Rust通用）
```

---

# 二、整体结构

标准结构如下：

```markdown id="dsl-2"
# Project

# Stage

## Task
```

---

## 层级关系

```text id="dsl-3"
Project
  └── Stage
        └── Task
```

---

# 三、Project（项目层）

## 定义

```text id="dsl-4"
一个长期学习目标
```

---

## 标准格式

```markdown id="dsl-5"
# Project

id: P001
title: 从0构建量化交易系统
description: 学习金融数据、回测系统与策略开发
duration: 180d

reward:
  name: Mac Studio
  value: 15000
  reason: 用于AI量化研究
```

---

## 字段说明

| 字段          | 说明   |
| ----------- | ---- |
| id          | 唯一标识 |
| title       | 项目名称 |
| description | 项目描述 |
| duration    | 预计周期 |
| reward      | 终极奖励 |

---

# 四、Stage（阶段层）

## 定义

```text id="dsl-6"
项目中的学习阶段
```

---

## 标准格式

```markdown id="dsl-7"
# Stage

id: S001
title: 金融基础
order: 1

description: 学习基本金融概念与市场机制
```

---

## 特点

* 必须属于某个 Project
* 按顺序执行
* 可并行扩展（未来版本）

---

# 五、Task（任务层，核心）

## 定义

```text id="dsl-8"
最小执行单元（用户真正每天做的事情）
```

---

## 标准格式

```markdown id="dsl-9"
## Task

id: T001
title: 理解收益率计算
type: theory
xp: 20
estimate: 30m

content:
  - 阅读收益率定义
  - 理解log return

check:
  - 能解释收益率
  - 完成笔记

output:
  - markdown笔记

depends:
  - T000
```

---

## Task类型（关键）

| type      | 含义   |
| --------- | ---- |
| theory    | 理论学习 |
| practice  | 实践   |
| project   | 小项目  |
| review    | 复习   |
| challenge | 挑战任务 |

---

# 六、Task核心字段说明

---

## 6.1 depends（依赖）

```yaml id="dsl-10"
depends:
  - T001
  - T002
```

含义：

> 必须完成前置任务才能解锁

---

## 6.2 xp（成长值）

```text id="dsl-11"
xp: 20
```

用于：

* 成长系统
* 等级系统
* 激励系统

---

## 6.3 estimate（时间）

```text id="dsl-12"
estimate: 30m
```

用于：

* 控制每日负载
* 防止任务过重

---

## 6.4 check（完成标准）

```yaml id="dsl-13"
check:
  - 能解释概念
  - 能完成计算
```

核心作用：

> 判断任务是否完成的“软标准”

---

## 6.5 output（输出物）

```yaml id="dsl-14"
output:
  - notebook.md
  - code.py
```

用于：

* 强制实践
* 防止纯阅读

---

# 七、完整示例（标准DSL）

```markdown id="dsl-15"
# Project

id: P001
title: 量化交易系统
duration: 180d

reward:
  name: Mac Studio
  value: 15000

---

# Stage

id: S001
title: 金融基础
order: 1

---

## Task

id: T001
title: 收益率与log return
type: theory
xp: 20
estimate: 30m

content:
  - 学习收益率定义
  - 理解log return

check:
  - 能解释收益率区别

output:
  - notes.md

depends: []
```

---

# 八、DSL解析规则（Parser规范）

---

## 8.1 解析目标

```text id="dsl-16"
Markdown → JSON Graph
```

---

## 8.2 转换结构

```json id="dsl-17"
{
  "project": {},
  "stages": [],
  "tasks": [],
  "graph": {
    "dependencies": []
  }
}
```

---

## 8.3 解析规则

### 规则1：层级识别

```text id="dsl-18"
# Project → Project对象
# Stage → Stage对象
## Task → Task对象
```

---

### 规则2：依赖图

```text id="dsl-19"
depends → DAG（有向无环图）
```

---

### 规则3：任务状态初始化

```text id="dsl-20"
默认：
pending
```

---

# 九、执行语义（Execution Semantics）

---

## 9.1 Task状态机

```text id="dsl-21"
pending
   ↓
doing
   ↓
done
```

---

## 9.2 状态触发

| 行为   | 状态变化            |
| ---- | --------------- |
| 开始任务 | pending → doing |
| 打卡完成 | doing → done    |
| 失败   | doing → pending |

---

# 十、奖励语义（Reward Semantics）

---

## 10.1 XP计算

```text id="dsl-22"
完成Task → XP增加
```

---

## 10.2 梦想值映射

```text id="dsl-23"
1 XP ≈ 1 元梦想价值（可配置）
```

---

## 10.3 阶段奖励

```text id="dsl-24"
完成 Stage → bonus XP
```

---

# 十一、DSL扩展机制（非常重要）

---

## 11.1 可扩展字段

允许新增：

```yaml id="dsl-25"
difficulty: medium
tags: [quant, finance]
milestone: true
```

---

## 11.2 版本控制

```text id="dsl-26"
version: v1.0
```

未来升级：

* v1.1（加入AI自动调度）
* v2.0（支持自动生成任务）

---

# 十二、AI生成约束（关键）

---

## AI必须遵守：

```text id="dsl-27"
1. 必须有Project
2. 必须有Stage
3. 每个Stage ≥ 3 Task
4. 每个Task ≤ 60分钟
5. 必须理论 + 实践交替
6. 必须包含depends结构
```

---

## AI禁止：

```text id="dsl-28"
❌ 不允许模糊任务（如“学习一下Python”）
❌ 不允许无依赖结构
❌ 不允许没有输出物
```

---

# 十三、DSL设计原则

---

## 原则1：结构优先

不是自然语言，是结构数据。

---

## 原则2：任务最小化

每个 Task ≤ 60分钟

---

## 原则3：强实践导向

必须有 output

---

## 原则4：依赖驱动学习

必须 DAG

---

## 原则5：AI生成，人类执行

---

# 十四、DSL一句话定义

> Learning OS DSL 是一个用于描述长期学习路径的结构化任务语言，它将学习拆解为 Project → Stage → Task 的有向依赖图，并支持执行、打卡与成长反馈。

---

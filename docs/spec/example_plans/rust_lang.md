# Project
title: Rust语言系统学习
description: 从零开始系统学习Rust编程语言，掌握所有权模型、生命周期、trait系统、异步编程等核心概念，最终能独立开发高性能CLI工具
reward: HHKB键盘
reward_price: 1200
deadline: 90

---

## Stage
title: 基础入门

## Task
id: T001
title: 安装Rust工具链与开发环境
type: practice
xp: 5
estimate: 60
check: 安装rustup、rustc、cargo，配置VSCode的rust-analyzer插件，运行cargo new hello_world成功
resource: https://www.rust-lang.org/tools/install

## Task
id: T002
title: Rust Book 第1-3章：变量与基础类型
type: theory
xp: 10
estimate: 120
depends: T001
check: 理解变量绑定、可变性、标量类型、复合类型，完成每章课后练习
resource: https://doc.rust-lang.org/book/

## Task
id: T003
title: Rust Book 第4章：所有权
type: theory
xp: 20
estimate: 180
depends: T002
check: 能用Stack/Heap解释所有权转移、Clone vs Copy、借用规则，手写10个所有权示例代码并通过编译

## Task
id: T004
title: Rust Book 第5-6章：结构体与枚举
type: theory
xp: 15
estimate: 150
depends: T003
check: 掌握struct、enum、Option、match、if let，实现一个计算几何图形面积的结构体

## Task
id: T005
title: 基础语法综合练习
type: practice
xp: 15
estimate: 180
depends: T004
check: 用Rust重写至少3个LeetCode Easy题目（如two-sum、reverse-linked-list、valid-parentheses）

---

## Stage
title: 核心进阶

## Task
id: T006
title: Rust Book 第7-9章：模块与错误处理
type: theory
xp: 15
estimate: 150
depends: T005
check: 掌握mod、pub、use、Result、panic vs unrecoverable，构建一个多模块crate

## Task
id: T007
title: Rust Book 第10章：泛型与Trait
type: theory
xp: 25
estimate: 240
depends: T006
check: 掌握泛型约束、trait定义与实现、trait bound、impl Trait语法，实现一个泛型排序函数
resource: https://doc.rust-lang.org/book/ch10-00-generics.html

## Task
id: T008
title: Rust Book 第13章：闭包与迭代器
type: theory
xp: 15
estimate: 150
depends: T007
check: 理解Fn/FnMut/FnOnce区别、闭包捕获环境、Iterator trait、适配器模式

## Task
id: T009
title: 生命周期标注
type: theory
xp: 20
estimate: 180
depends: T007
check: 能正确标注函数签名中的生命周期参数，理解生命周期省略规则，解决至少5个借用检查器报错案例

## Task
id: T010
title: 实现一个Mini grep
type: output
xp: 30
estimate: 300
depends: T008,T009
check: 参考Rust Book第12章，实现命令行grep工具：支持文件搜索、正则匹配、彩色输出、--ignore-case标志
resource: https://doc.rust-lang.org/book/ch12-00-an-io-project.html

---

## Stage
title: 实战项目

## Task
id: T011
title: 并发编程基础
type: theory
xp: 20
estimate: 180
depends: T009
check: 理解线程、消息传递（mpsc）、共享状态（Arc+Mutex）、Send+Sync trait，写出5个并发示例
resource: https://doc.rust-lang.org/book/ch16-00-concurrency.html

## Task
id: T012
title: 异步Rust与Tokio入门
type: practice
xp: 25
estimate: 240
depends: T011
check: 理解Future trait、async/await语法、tokio runtime，实现一个异步HTTP服务器echo endpoints
resource: https://tokio.rs/tokio/tutorial

## Task
id: T013
title: 数据库交互：SQLx + SQLite
type: practice
xp: 20
estimate: 180
depends: T012
check: 实现CRUD操作的CLI工具：编译时SQL检查、migration管理、连接池配置
resource: https://github.com/launchbadge/sqlx

## Task
id: T014
title: 构建CLI项目管理工具
type: output
xp: 50
estimate: 600
depends: T013,T010
check: 完整CLI应用：项目管理（CRUD）、任务跟踪、Markdown导出、SQLite持久化，包含完整的--help和错误处理

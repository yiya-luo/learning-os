# Project
title: CFA Level I 备考计划
description: 系统备考CFA一级考试，覆盖道德、数量、经济学、财务报表分析、公司金融、权益、固定收益、衍生品、另类投资、组合管理十大科目
reward: 机械键盘
reward_price: 800
deadline: 120

---

## Stage
title: 基础阶段

## Task
id: T001
title: 道德与职业准则 (Ethics) 学习
type: theory
xp: 20
estimate: 300
check: 完成GIPS与Code of Ethics全部准则记忆，刷完课后题正确率>70%
resource: https://www.cfainstitute.org/

## Task
id: T002
title: 数量方法 (Quantitative Methods)
type: theory
xp: 25
estimate: 360
check: 掌握时间价值、假设检验、回归分析，完成100道练习题
resource: https://www.cfainstitute.org/

## Task
id: T003
title: 经济学 (Economics)
type: theory
xp: 20
estimate: 300
check: 理解供需弹性、货币政策传导、汇率决定理论，完成80道练习题

## Task
id: T004
title: 财务报表分析 (FSA) — 上
type: theory
xp: 30
estimate: 480
check: 掌握三大报表勾稽关系、收入确认、资产计量，完成120道练习题

## Task
id: T005
title: 财务报表分析 (FSA) — 下
type: theory
xp: 30
estimate: 480
depends: T004
check: 掌握财务比率分析、盈利质量、现金流量分析，完成120道练习题

---

## Stage
title: 强化阶段

## Task
id: T006
title: 公司金融 (Corporate Finance)
type: theory
xp: 15
estimate: 240
depends: T003
check: 掌握资本预算、WACC、资本结构理论，完成80道练习题

## Task
id: T007
title: 权益投资 (Equity)
type: theory
xp: 25
estimate: 300
depends: T005
check: 掌握DDM、FCF估值、相对估值法、行业分析框架，完成100道练习题

## Task
id: T008
title: 固定收益 (Fixed Income)
type: theory
xp: 25
estimate: 360
depends: T002
check: 掌握久期凸性、收益率曲线、信用分析、ABS/MBS特征，完成100道练习题

## Task
id: T009
title: 衍生品 (Derivatives)
type: theory
xp: 15
estimate: 240
depends: T007,T008
check: 掌握期权定价（二叉树+BSM）、期货套利、互换定价，完成80道练习题

## Task
id: T010
title: 另类投资与组合管理
type: theory
xp: 20
estimate: 300
depends: T009
check: 掌握对冲基金策略、私募股权、房地产投资、现代组合理论、资产配置，完成100道练习题

## Task
id: T011
title: 全科目综合模拟考试
type: output
xp: 40
estimate: 300
depends: T010,T006,T001
check: 完成2套完整MOCK考试（上下午各120题），正确率>70%，输出错题分析报告

---

## Stage
title: 冲刺阶段

## Task
id: T012
title: 高频错题回顾
type: practice
xp: 20
estimate: 240
depends: T011
check: 收集MOCK中所有错题，按科目分类整理错题本，重新做一遍正确率>90%

## Task
id: T013
title: 道德科目专项突破
type: practice
xp: 15
estimate: 180
depends: T011
check: 完成CFA官方道德样本案例50个，区分Standard I-VII的适用场景

## Task
id: T014
title: 考前最后冲刺
type: output
xp: 10
estimate: 120
depends: T012,T013
check: 完成考前知识梳理思维导图，标记各科目重点公式和易错点

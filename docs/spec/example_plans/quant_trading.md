# Project
title: 从0学习量化交易
description: 系统学习量化交易的理论、工具与实践，从零基础到构建自己的交易策略并回测验证，掌握金融数据分析、策略开发与风险管理的完整技能栈
reward: Mac Studio
reward_price: 15000
deadline: 180

---

## Stage
title: 基础准备

## Task
id: T001
title: 搭建Python数据分析环境
type: practice
xp: 10
estimate: 60
check: 安装Python 3.10+、Jupyter Lab、pandas、numpy、matplotlib，运行import验证
resource: https://docs.python.org/3/tutorial/

## Task
id: T002
title: 金融市场基础概念
type: theory
xp: 15
estimate: 120
check: 能解释股票、ETF、期货、期权的定义与区别
resource: https://www.investopedia.com/

## Task
id: T003
title: 量化交易概述
type: theory
xp: 10
estimate: 90
check: 写出量化交易的定义、与传统交易的区别、至少3种常见策略类型

## Task
id: T004
title: pandas金融数据处理入门
type: practice
xp: 20
estimate: 180
depends: T001
check: 完成DataFrame创建、时间序列索引、rolling/groupby操作、缺失值处理
resource: https://pandas.pydata.org/docs/

---

## Stage
title: 数据获取与处理

## Task
id: T005
title: 股票行情数据获取
type: practice
xp: 15
estimate: 120
depends: T004
check: 使用akshare或tushare获取A股日线数据，保存为CSV
resource: https://akshare.akfamily.xyz/

## Task
id: T006
title: 数据清洗与预处理
type: practice
xp: 20
estimate: 120
depends: T005
check: 处理复权因子、停牌填充、异常值检测，输出清洗后的OHLCV数据

## Task
id: T007
title: 技术指标计算
type: practice
xp: 25
estimate: 180
depends: T006
check: 实现MA、MACD、RSI、布林带、ATR计算函数，与主流软件结果对比误差<0.1%

## Task
id: T008
title: 金融数据可视化
type: output
xp: 20
estimate: 120
depends: T007
check: 输出一张包含K线图、成交量、MACD、RSI子图的可交互图表

---

## Stage
title: 策略开发

## Task
id: T009
title: 双均线交叉策略
type: practice
xp: 25
estimate: 180
depends: T007
check: 实现双均线策略信号生成，包含买卖点标记和持仓状态管理

## Task
id: T010
title: 策略回测框架
type: practice
xp: 30
estimate: 240
depends: T009
check: 实现回测引擎：包含滑点模拟、手续费计算、净值曲线跟踪

## Task
id: T011
title: 回测绩效分析
type: output
xp: 25
estimate: 180
depends: T010
check: 输出年化收益率、最大回撤、夏普比率、胜率、盈亏比，生成回测报告PDF
resource: https://www.quantopian.com/

## Task
id: T012
title: 多因子选股模型
type: theory
xp: 30
estimate: 240
depends: T002
check: 理解并写出至少5个常见因子（动量、市值、波动率、价值、质量）的定义和计算方法

## Task
id: T013
title: 因子IC分析与组合
type: practice
xp: 35
estimate: 300
depends: T012,T006
check: 计算因子IC序列、IC_IR、因子相关性矩阵，实现等权与IC加权多因子打分

---

## Stage
title: 风险管理与实盘

## Task
id: T014
title: 仓位管理策略
type: theory
xp: 20
estimate: 120
depends: T009
check: 理解凯利公式、风险平价、固定比例仓位管理，比较三种方法的优缺点

## Task
id: T015
title: 风险指标监控
type: practice
xp: 30
estimate: 240
depends: T014,T010
check: 实现实时VaR计算、最大回撤监控、波动率锥，每日自动输出风险报告

## Task
id: T016
title: 策略实盘模拟
type: output
xp: 50
estimate: 480
depends: T015
check: 完成30天模拟盘交易记录，包含每日复盘笔记和策略调整决策日志

## Task
id: T017
title: 量化交易系统整合
type: output
xp: 40
estimate: 360
depends: T016
check: 提交一个完整的自动化交易系统：数据更新→信号生成→风险校验→下单执行→绩效跟踪

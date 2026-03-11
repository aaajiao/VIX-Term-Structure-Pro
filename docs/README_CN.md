# VIX Term Structure Pro v7.11

[![TradingView](https://img.shields.io/badge/TradingView-Indicator-blue?logo=tradingview)](https://www.tradingview.com/scripts/)
[![Pine Script](https://img.shields.io/badge/Pine%20Script-v6-brightgreen)](https://www.tradingview.com/pine-script-reference/v6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **[English](../README.md)** | 中文

VIX Term Structure Pro 是一个基于 TradingView Pine Script v6 的波动率结构指标，用统一的评分、信号、仪表盘和提醒系统来解读 VIX 期限结构、市场情绪与波动区间。

## 项目概览

这个项目当前是一个单文件 Pine 指标，核心原则只有一条：

- `Score` 必须是纯 VIX 结构指标。
- 趋势只影响信号展示和统计口径，不直接改变 `Score`。
- 为了跨图表一致性，VIX 结构相关输入优先使用固定外部符号。

当前脚本状态：

- 主文件：`vix.pine`
- Pine 版本：`//@version=6`
- 指标标题：`VIX Term Structure Pro [v7.11]`
- 主要使用场景：TradingView 上的 `SPY`、`QQQ`、`IWM` 及相关指数图表

## 仓库结构

| 路径 | 作用 |
|:--|:--|
| `vix.pine` | 主指标源码 |
| `README.md` | 英文文档 |
| `docs/README_CN.md` | 中文文档 |
| `chart_guide.png` | 仪表盘 / 图表示意图 |
| `zscore_guide.png` | Z-Score 解释图 |

## 指标是怎么工作的

### Score 使用的核心因子

当前评分系统组合了以下客观 VIX 结构因子：

- 期限结构 Z-Score
- VX1 / VX2 升水或倒挂
- VIX / VX1 basis
- SKEW
- Put/Call Ratio
- 可选 VVIX
- VX1 成交量高量 / 爆量
- 可选动量确认
- 可选周线 MTF 对齐

趋势不进入 score。趋势只影响：

- `BUY DIP` 是否被过滤成 `NO TRADE`
- 信号统计所使用的参考指数

### 外部数据源

为了保持跨图表一致性，脚本使用固定符号：

| 因子 | 符号 |
|:--|:--|
| VIX | 默认 `CBOE:VIX` |
| 近月期货 | `CBOE:VX1!` |
| 次月期货 | `CBOE:VX2!` |
| SKEW | `CBOE:SKEW` |
| Put/Call Ratio | 默认 `INDEX:CPCI` |
| VVIX | `CBOE:VVIX` |
| 趋势 / 统计参考 | `SP:SPX`、`NASDAQ:NDX`、`TVC:RUT` |

自动识别规则：

- `QQQ` / `NDX` / `NQ` 类图表使用 `NASDAQ:NDX`
- `IWM` / `RUT` / `RTY` 类图表使用 `TVC:RUT`
- 其他图表默认使用 `SP:SPX`

## 信号模型

### 信号分级

| 信号 | 分数区间 | 含义 |
|:--|:--|:--|
| `CRASH BUY` | `>= 6` | 极端恐慌 |
| `STRONG BUY` | `>= 5` | 高质量买点 |
| `BUY DIP` | `>= min_score_buy` 且 `< 5` | 较弱买点 |
| `NEUTRAL` | 中性区间 | 暂无优势 |
| `SELL/HEDGE` | `<= -2` 且 `> -5` | 对冲 / 降风险 |
| `STRONG SELL` | `<= -5` 且 `> -6` | 强卖出信号 |
| `EUPHORIA` | `<= -6` | 极端贪婪 |

### 过滤状态

这些状态是展示层结果，不是另一套 score 公式：

| 状态 | 含义 |
|:--|:--|
| `WAIT (Vol)` | 买入分数达标，但波动区间过于危险 |
| `WAIT (Mom)` | 买入分数达标，但动量确认失败 |
| `HOLD (Vol)` | 卖出分数达标，但当前波动区间不支持卖出 |
| `HOLD (Mom)` | 卖出分数达标，但动量确认失败 |
| `NO TRADE` | 启用趋势过滤后，买入侧在熊市趋势下被屏蔽 |

### 两种“确认”概念

当前脚本里有两个不同层面的确认：

- `Confirmed Signals Only`：控制图表上显示的信号是否等待当前 bar 收盘
- `Alert Timing Mode`：控制智能提醒是“预览型”还是“确认型”

这两个概念在 v7.11 里已经被明确分开。

## 智能提醒

### v7.11 默认行为

默认配置：

- `Smart Alert = ON`
- `Alert Timing Mode = Confirmed Daily Structure`
- `After-Hours Alert Policy = Allow if source confirms`
- `Alert Frequency = Real-time`

这套默认值的含义是：

- 确认型提醒允许在日线外部数据晚到时盘后触发
- 预览型提醒尽可能早发出
- 消息本身会明确标注这次提醒属于哪一种时序

### 提醒时序模式

| 模式 | 含义 |
|:--|:--|
| `Confirmed Daily Structure` | 只在日线结构源确认后发提醒 |
| `Preview / Earliest Possible` | 保留尽早触发的预览行为 |

如果你在预览模式下把 `VIX Timeframe` 设为 `Chart`：

- 只有 VIX 会跟随图表周期
- 其他结构因子仍可能保持日线
- 仪表盘里的 `PREVIEW*` 就表示这种 hybrid 模式

### 盘后策略

| 策略 | 行为 |
|:--|:--|
| `Allow if source confirms` | 若确认版日线数据收盘后才最终完成，允许继续发提醒 |
| `Regular Session Only` | 常规交易时段外全部拦截 |

### 为什么会在收盘后提醒

这在某些情况下是设计内行为，不一定是 bug。

因为 score 依赖多个日线外部源，例如：

- `CBOE:VIX`
- `CBOE:VX1!`
- `CBOE:VX2!`
- `CBOE:SKEW`
- `INDEX:CPCI`
- 可选 `CBOE:VVIX`

这些数据源不保证在图表收盘的同一时刻完成最终更新。因此在 `Confirmed Daily Structure` 模式下，脚本可能会等到这些数据真正确认后才发出 `[CONFIRMED]` 提醒，这就可能发生在收盘后。

### 提醒消息格式

```text
Symbol: [Side] [Timing] [Level][Upgrade] -> [Triggered Labels] | [Context]

SPY: BUY [CONFIRMED] [Lv2] -> STRONG | Score:5.2 Z:-2.1 VIX:19(NORM) | Confirmed
QQQ: BUY [PREVIEW] [Lv1] -> DIP | Score:4.0 Z:-1.8 VIX:28(HIGH) | Hybrid preview daily+chart
```

提醒状态机当前包含：

- `Lv1` 到 `Lv3` 的等级优先级
- 用 `varip` 做同一 bar 内去重
- 预览模式保留跨 bar 升级提醒
- 确认模式按结构日去重
- 以图表 bar 为单位的自适应冷却

## 仪表盘与图形输出

### Mobile 模式

两行布局：

| 行 | 内容 |
|:--|:--|
| 1 | 当前信号 + 分数 |
| 2 | 提醒模式 + VIX 显示 |

### Full 模式

十四行布局：

| 区域 | 内容 |
|:--|:--|
| Header | 标题 + safe / preview 模式 |
| Signal | 当前信号 + 分数进度条 |
| Market | SPX / NDX / RUT 趋势、VIX 区间、提醒模式、成交量 |
| Structure | 期限结构 Z + contango |
| Stats | 滚动信号次数和平均收益 |

### 图形元素

脚本当前可以显示：

- 期限结构 Z-Score
- 缩放后的 SKEW 曲线
- 智能成交量柱
- 买卖标签
- 深色分组式仪表盘

## 关键参数分组

### Data Sources

- `Trading Safe Mode`
- `VIX Symbol`
- `VIX Timeframe`
- `Put/Call Ratio Symbol`
- `Manual Trend Source`

### Strategy Mode

- 信号灵敏度：`High`、`Normal`、`Low`
- 市场趋势过滤
- 自动识别指数
- 趋势均线模式：`Fixed`、`Adaptive`、`KAMA`

### Signal Confirmation

- 图表信号是否按收盘确认
- 动量确认
- 周线 MTF 确认
- 信号展示冷却

### Statistics and Alerts

- 滚动统计回看年数
- 各级买入信号的收益周期
- 智能提醒时序模式
- 盘后策略
- 提醒冷却基础值
- 提醒频率

### Advanced

- VIX 区间阈值
- 自适应百分位阈值
- 自适应 Z-Score 回看长度
- SKEW 模式
- 成交量均值长度
- 可选 VVIX 阈值

## 推荐使用方式

### 保守型日线用法

适合大多数用户：

- 图表：`SPY`、`QQQ`、`IWM`
- 周期：日线
- `Trading Safe Mode = ON`
- `Alert Timing Mode = Confirmed Daily Structure`
- `After-Hours Alert Policy = Allow if source confirms`
- `Use Momentum Confirmation = ON`
- `Use Weekly MTF Confirmation = OFF`，或只在你需要更严格过滤时开启

### 盘中预览用法

只建议给理解 hybrid 时序的用户：

- 图表：`SPY` / `QQQ`
- 周期：`15m` 或 `1h`
- `VIX Timeframe = Chart`
- `Alert Timing Mode = Preview / Earliest Possible`
- 若你完全不想盘后提醒，可再加 `Regular Session Only`

## 验证流程

这个仓库没有本地 Pine 编译器。

所有验证都要在 TradingView 完成：

1. 把 `vix.pine` 粘贴到 Pine Editor。
2. 确认脚本能编译通过。
3. 在 `SPY`、`QQQ`、`IWM` 上分别加载。
4. 检查 `Full` 和 `Mobile` 两种仪表盘布局。
5. 检查信号标签、趋势过滤、统计参考指数是否符合预期。
6. 分别测试：
   - `Confirmed Daily Structure`
   - `Preview / Earliest Possible`
   - `Regular Session Only`
7. 观察盘后确认提醒是否与日线外部源的晚到更新一致。

## 当前版本重点

### v7.11

- 明确区分确认型与预览型提醒
- 新增盘后提醒策略
- 提醒消息增加 `[CONFIRMED]` / `[PREVIEW]`
- 确认模式按结构日去重
- 仪表盘显示当前提醒模式

### v7.10

- Score 完整实现跨图表一致
- 趋势惩罚从 Score 中移除
- 周线 MTF 对齐改用 `SP:SPX`
- 统计参考指数与 auto-detect 保持一致

### v7.9

- NA 与 warmup 处理更稳健
- Safe 模式下仪表盘显示实时 VIX

## 限制说明

- Pine 只能在 TradingView 上做真实验证。
- 外部日线数据可能晚于图表收盘更新。
- `VIX Timeframe = Chart` 并不代表整套模型都变成盘中实时，只是 VIX 这一路变成图表周期。
- 统计是滚动窗口统计，不是完整策略回测。

## License

MIT License

## 免责声明

本项目仅用于研究和教育用途，不构成投资建议。

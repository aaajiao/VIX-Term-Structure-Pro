# VIX Term Structure Pro v7.13

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
- 指标标题：`VIX Term Structure Pro [v7.13]`
- 历史执行窗口：`calc_bars_count=5000`
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

当启用自适应阈值时，PCR 的百分位阈值会直接进入 score。启用 VVIX 后，所选的 `VVIX Threshold Mode` 也会直接进入 score。

趋势不进入 score。趋势只影响：

- `🟡 BUY DIP` 是否被过滤成 `🚫 NO TRADE`
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
| `🚨 CRASH BUY` | `>= 6` | 极端恐慌 |
| `🟢 STRONG BUY` | `>= 5` | 高质量买点 |
| `🟡 BUY DIP` | `>= min_score_buy` 且 `< 5` | 较弱买点 |
| `⏸ NEUTRAL` | 中性区间 | 暂无优势 |
| `🟠 SELL/HEDGE` | `<= -2` 且 `> -5` | 对冲 / 降风险 |
| `🔴 STRONG SELL` | `<= -5` 且 `> -6` | 强卖出信号 |
| `🔥 EUPHORIA` | `<= -6` | 极端贪婪 |

### 过滤状态

这些状态是展示层结果，不是另一套 score 公式：

| 状态 | 含义 |
|:--|:--|
| `✋ WAIT (Vol)` | 买入分数达标，但波动区间过于危险 |
| `✋ WAIT (Mom)` | 买入分数达标，但动量确认失败 |
| `✋ WAIT (Core)` | 买入分数达标，但缺少核心恐慌确认 |
| `☕ HOLD (Vol)` | 卖出分数达标，但当前波动区间不支持卖出 |
| `✋ HOLD (Mom)` | 卖出分数达标，但动量确认失败 |
| `✋ HOLD (Core)` | 卖出分数达标，但缺少核心贪婪确认 |
| `🚫 NO TRADE` | 启用趋势过滤后，买入侧在熊市趋势下被屏蔽 |

### 卖出严格度

卖出侧现在有两个明确模式：

- `Balanced (Legacy)`：保持之前的卖出 / 对冲过滤逻辑
- `High Win-Rate`：`🔴 STRONG SELL` 和 `🟠 SELL/HEDGE` 必须通过核心贪婪确认

核心贪婪确认满足以下任一即可：

- VIX / VX1 basis 偏冷
- Put/Call Ratio 偏冷
- SKEW 偏高
- contango 高于 `10%`
- 可选 VVIX 偏冷

### 两种“确认”概念

当前脚本里有两个不同层面的确认：

- `Confirmed Signals Only`：控制图表上显示的信号是否等待当前 bar 收盘
- `Alert Timing Mode`：控制智能提醒是“预览型”还是“确认型”

这两个概念是彼此独立的控制项。

### 统计模型

滚动统计被有意限制在精确 `1D` 图表上。

- 非 `1D` 图表会显示 `1D ONLY`，而不是胜率数字
- 只统计已确认的最终买入 / 卖出信号
- `N` 表示已经完成收益评估的样本数，不是全部历史信号数
- 买入胜率口径使用 `Ref > 0`
- 卖出胜率口径使用 `Ref <= 0`
- 卖出平均收益保持原始远期收益，数值越负代表顶部 / 对冲越有效
- `Wxx%` 表示固定持有周期下、已完成样本的胜率
- 统计最长只允许 `19` 年，因为 `19*252 + 60 = 4848`，仍在 `5000` bars 预算内

## 智能提醒

### 默认行为

默认配置：

- `Smart Alert = ON`
- `Alert Timing Mode = Confirmed Daily Structure`
- `After-Hours Alert Policy = Allow if source confirms`
- `Alert Frequency = Real-time`

这套默认值的含义是：

- 确认型提醒基于上一完整结构日，并只在下一次常规时段机会发出一次
- 预览型提醒尽可能早发出
- 消息本身会明确标注这次提醒属于哪一种时序

### 提醒时序模式

| 模式 | 含义 |
|:--|:--|
| `Confirmed Daily Structure` | 对上一完整结构日做一次快照，并在下一次常规时段机会只发一次 |
| `Preview / Earliest Possible` | 保留尽早触发的预览行为 |

如果你在预览模式下把 `VIX Timeframe` 设为 `Chart`：

- 只有 VIX 显示、实时波动区间门控、自适应趋势均线长度选择（即实时趋势过滤）与自适应提醒冷却会跟随图表周期
- 评分及其结构因子始终基于日线数据计算（自 v7.13 起）
- 仪表盘里的 `PREVIEW*` 就表示这种 hybrid 模式

### 盘后策略

| 策略 | 行为 |
|:--|:--|
| `Allow if source confirms` | 预览模式下，若输入晚到，收盘后仍可继续提醒 |
| `Regular Session Only` | 预览提醒按交易所定义的常规交易时段拦截；即使图表开启 extended hours，盘前盘后也不提醒 |

对于 extended-hours 的 `1m` 图，preview 模式下所有非常规时段（盘前/盘后）的新边缘现在都会消费当天方向锁，避免同方向同级别在常规时段外每分钟反复提醒。
方向锁与冷却记账已改为回滚安全的 `varip` 状态，实时 bar 更新不会把“已发过”的状态冲掉。

### 为什么 confirmed 不再在收盘后继续触发

`Confirmed Daily Structure` 现在会等一整个结构日完成，再在下一次常规时段机会发出一次提醒。它不再使用盘后 `1m` bar 去反复重算同一个日线切换。

因为 score 依赖多个日线外部源，例如：

- `CBOE:VIX`
- `CBOE:VX1!`
- `CBOE:VX2!`
- `CBOE:SKEW`
- `INDEX:CPCI`
- 可选 `CBOE:VVIX`

这些数据源不保证在图表收盘的同一时刻完成最终更新。这个时点仍会影响预览提醒，但 confirmed 现在会消费掉完整结构日，然后等下一次常规时段 bar，再发一次，不会在盘后 `1m` 上反复回放。

TradingView 的提醒运行在服务器侧快照上。只要你改了 alert timing 或盘后策略，必须删除并重新创建提醒，服务器才会拿到新的脚本逻辑和输入值。

### 提醒消息格式

```text
Symbol: [Side] [Timing] [Level][Upgrade] → [Triggered Labels] | [Context] [Trend] | [Mode]

SPY: 🟢 BUY [CONFIRMED] [Lv2] → 🟢STRONG | Score:5.2 Z:-2.1 VIX:19(NORM) 🟢SPX 🟢NDX 🔴RUT | Confirmed
QQQ: 🟢 BUY [PREVIEW] [Lv1] → 🟡DIP | Score:4.0 Z:-1.8 VIX:28(HIGH) 🟢SPX 🟢NDX 🔴RUT | Hybrid preview hybrid daily+chart
```

提醒状态机当前包含：

- `Lv1` 到 `Lv3` 的等级优先级
- 用 `varip` 做同一 bar 内去重
- 预览模式保留跨 bar 升级提醒
- 预览模式加入日内方向锁：同方向同级别同一交易日最多一次，仅严格升级可再次提醒
- 预览模式的 extended 时段新边缘也会消费这把方向锁，避免盘后 `1m` 重复刷提醒
- 方向锁/冷却/发送记账改为回滚安全 `varip`，防止实时 bar 回滚造成重复触发
- 确认模式按结构日快照并只发一次
- 预览模式保留以图表 bar 为单位的自适应冷却
- 被冷却或时段策略拦截的信号会被直接丢弃，不会延后补发

## 仪表盘与图形输出

### Mobile 模式

两行布局：

| 行 | 内容 |
|:--|:--|
| 1 | 当前信号 + 分数 |
| 2 | 提醒模式 + VIX 显示 |

### Full 模式

十六行布局：

| 区域 | 内容 |
|:--|:--|
| Header | 标题 + safe / preview 模式 |
| Signal | 当前信号 + 分数进度条 |
| Market | SPX / NDX / RUT 趋势、VIX 区间、提醒模式、成交量 |
| Structure | 期限结构 Z + contango |
| Stats | 仅 `1D` 图表显示的买卖两侧已评估样本数、胜率和平均收益 |

### 图形元素

脚本当前可以显示：

- 期限结构 Z-Score
- 缩放后的 SKEW 曲线
- 智能成交量柱
- `🚨` / `🟢` / `🟡` / `🔥` / `🔴` / `🟠` 标签
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
- 卖出严格度：`Balanced (Legacy)` 或 `High Win-Rate`
- 市场趋势过滤
- 自动识别指数
- 趋势均线模式：`Fixed`、`Adaptive`、`KAMA`

### Signal Confirmation

- 图表信号是否按收盘确认
- 动量确认
- 周线 MTF 确认
- 信号展示冷却

### Statistics and Alerts

- 滚动统计回看年数（`1-19Y`，且仅 `1D` 图表统计）
- 买卖对应分级复用的收益周期
- 智能提醒时序模式
- 盘后策略
- 提醒冷却基础值
- 提醒频率

### Advanced

- VIX 区间阈值
- 自适应百分位阈值
- 自适应 Z-Score 回看长度
- Z 回看切换的波动滞回带
- SKEW 模式
- 成交量均值长度
- 可选 VVIX 阈值

## 推荐使用方式

### 保守型日线用法

适合大多数用户：

- 图表：`SPY`、`QQQ`、`IWM`
- 周期：日线
- 如果你想看胜率统计，请使用精确 `1D` 图表
- `Trading Safe Mode = ON`
- `Alert Timing Mode = Confirmed Daily Structure`
- 如果你想让顶部信号更少但更准，可用 `Sell Signal Strictness = High Win-Rate`
- `Use Momentum Confirmation = ON`
- `Use Weekly MTF Confirmation = OFF`，或只在你需要更严格过滤时开启

### 盘中预览用法

只建议给理解 hybrid 时序的用户：

- 图表：`SPY` / `QQQ`
- 周期：`15m` 或 `1h`
- `VIX Timeframe = Chart`
- `Alert Timing Mode = Preview / Earliest Possible`
- 若你完全不想盘后提醒，可再加 `Regular Session Only`，这样 extended hours 的 `1m` 也会被拦住

## 验证流程

这个仓库没有本地 Pine 编译器。

所有验证都要在 TradingView 完成：

1. 把 `vix.pine` 粘贴到 Pine Editor。
2. 确认脚本能编译通过。
3. 在 `SPY`、`QQQ`、`IWM` 上分别加载。
4. 检查 `Full` 和 `Mobile` 两种仪表盘布局。
5. 检查信号标签、买卖两侧 `1D` 统计输出、趋势过滤和统计参考指数是否符合预期。
6. 分别测试：
   - `Confirmed Daily Structure`
   - `Preview / Earliest Possible`
   - `Regular Session Only`
   - 任何影响提醒时序或 session 的输入改动后，都要在 TradingView 里删掉旧提醒并重建
7. 在 `Balanced (Legacy)` 与 `High Win-Rate` 之间切换，确认需要时会显示 `✋ HOLD (Core)`。
8. 在 ETF 的盘中图上确认 `Confirmed Daily Structure` 对同一个完整结构日最多只发一次，不会在盘后 `1m` 上重复。
9. 在预览模式下确认 `Regular Session Only` 仍能拦住 extended hours 的盘后提醒。
10. 在预览模式 + `Allow if source confirms` + extended-hours `1m` 下，确认同方向同级别在同一交易日内不会重复提醒；只有 `Lv1 -> Lv2 -> Lv3` 升级时才会再次提醒。
11. 在加密货币 `1D` 图表和上市时间较短标的的 `1D` 图表上，确认 score/Z 渲染正常（v7.13 从 SPX 日线网格取值；这些图表上的数值与 v7.12 有意不同）。

## v7.13 更新内容

- **评分与图表周期解耦**：`Score` 及其门控因子（Z-Score、动量、核心确认、周线 MTF 对齐）现在通过 `request.security()` tuple 统一在 `SP:SPX` 日线上下文中计算。盘中图表读取的日线数值与 `1D` 图表完全一致。`Trading Safe Mode = ON` 时，历史K线使用已完成交易日，实时K线跟踪发展中的当日值；OFF 时，历史盘中K线显示当日最终值（重绘语义与 v7.12 一致，数值已改为日线口径）。高于 `1D` 的图表每根K线采样一个日线值。注意：非美股交易日历的 `1D` 图表和上市时间较短的标的现在读取的是 SPX 网格数值，与 v7.12 不同——见已知限制。
- **confirmed 提醒锚点一致性**：在盘中图表上，confirmed 结构日 ID 与整套 confirmed 快照（score、Z、VIX、SKEW、波动区间、趋势、动量与核心门控——含 `BUY DIP` 的趋势过滤门控）现在来自专用的已完成结构日数据源——逐元素 `[1]` 偏移 + 固定 `lookahead_on`。实时与历史K线看到完全相同的已完成日数据，且默认配置下 confirmed 路径不再受 `Trading Safe Mode` 开关影响（周线 MTF 与 24 小时符号的例外见已知限制）。`1D` 及以上图表保留之前的当根收盘语义。
- **自适应 Z 回看滞回带**：新增 `Vol Regime Hysteresis Band` 输入（Advanced 分组，默认 `0.0` = v7.12 行为，建议试验值 `2.0`）。VIX 必须高于 `阈值 + 带宽` 才切换到高波动回看期，回落到 `阈值 - 带宽` 及以下才切回，避免 VIX 在阈值附近徘徊时回看期来回切换。
- **冷却语义澄清**：被提醒冷却或时段策略拦截的信号会被直接丢弃，不会延后补发。高波动期减半后的冷却现在以 `1` 根K线为下限，`Alert Cooldown Base = 1` 不会再被整除截断成 0。
- **死代码清理**：删除了未使用的 `spx_day_id` 请求和旧的 `lookahead_off` confirmed 锚点；结构日 ID 现在是一个共享表达式，同时供日线上下文请求和图表日 ID 复用。

## 当前能力重点

- 卖出严格度模式支持更干净、更高胜率的顶部筛选
- 核心贪婪确认可以把卖出侧拦截为 `✋ HOLD (Core)`
- 精确 `1D` 图表同时提供买入侧与卖出侧滚动统计
- 卖出图表标签、提醒与统计统一基于最终过滤后的卖出信号
- confirmed 提醒现在会对完整结构日做一次快照，并在下一次常规时段只发一次
- score 及其门控因子统一在 `SP:SPX` 日线上下文计算，盘中图表与 `1D` 图表的评分语义一致
- confirmed 提醒消费的已完成结构日快照在实时与历史K线上完全一致
- `Regular Session Only` 仍按交易所常规时段约束预览提醒
- preview 提醒新增日内方向锁：同方向同级别同日只发一次，仅升级可再次触发

## 已知限制

- Pine 只能在 TradingView 上做真实验证。
- 外部日线数据可能晚于图表收盘更新。
- `VIX Timeframe = Chart` 并不代表整套模型都变成盘中实时：自 v7.13 起它只影响仪表盘 VIX 显示、实时波动区间门控、自适应趋势均线长度选择（即实时趋势过滤）与自适应提醒冷却——评分始终基于日线结构数据计算。
- 评分在 `SP:SPX` 日线网格上计算。在非美股交易日历的 `1D` 图表上（加密货币、外汇），滚动窗口不再包含周末K线；在上市时间较短的标的上，预热数据来自 SPX 的数十年历史。这些图表读取的评分与 v7.12 不同（属于有意改进）。
- confirmed 路径与 `Trading Safe Mode` 开关的解耦只在默认配置下成立：开启 `Use Weekly MTF Confirmation` 后，周线 MTF 腿在周线上下文内采样日线数据，开关仍会改变已完成周内被采样的具体交易日（开=每周最后一个日线值/周五，关=第一个/周一），confirmed 评分可能相差 ±1——请保持安全模式开启。该解耦同时假设 VIX / Put-Call / 手动趋势符号遵循美股交易日历；24 小时日历的自定义符号会让 confirmed 快照在开关间偏移一天。
- 统计是滚动窗口统计，不是完整策略回测。
- 胜率统计被有意限制为仅 `1D` 图表可见。
- `CBOE:VX1!` / `CBOE:VX2!` 是连续合约，移仓换月日会切换合约；期限结构读数（contango、basis、Z-Score）在移仓日附近可能出现人为尖峰。
- `Regular Session Only` 对期货等 24 小时交易品种无效：这些品种的 `session.ismarket` 恒为 `true`，不会拦截任何提醒。请在有明确常规时段的股票 / ETF 图表上使用。
- 指数自动识别基于图表代码的子串匹配（`QQQ` / `NDX` / `NQ`、`IWM` / `RUT` / `RTY`），包含这些子串的非常规代码可能被路由到错误的参考指数。

## License

MIT License

## 免责声明

本项目仅用于研究和教育用途，不构成投资建议。

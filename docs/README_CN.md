# VIX Term Structure Pro v7.14

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
- 指标标题：`VIX Term Structure Pro [v7.14]`
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
| `tests/` | Python 回归模型与 Pine 源码连接检查；不是 Pine 编译器 |

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

所有必需结构输入与已启用因子都必须有有效数据和足够历史。条件不满足时，`Score` 显示不可用（`N/A`），不产生信号；缺失数据不会当作中性因子计分。未启用的可选 VVIX 或 MTF 不会阻止就绪。智能成交量数值及其评分贡献与 `Score` 来自同一套日线数据。

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

- 精确代码 `QQQ`、`QQQM`、`TQQQ`、`SQQQ`、`QLD`、`QID`、`NDX`，以及根代码为 `NQ` 或 `MNQ` 的期货，使用 `NASDAQ:NDX`
- 精确代码 `IWM`、`UWM`、`TWM`、`TNA`、`TZA`、`RUT`，以及根代码为 `RTY` 或 `M2K` 的期货，使用 `TVC:RUT`
- 其他图表默认使用 `SP:SPX`

识别使用 ETF/指数的精确代码与期货根代码，不使用任意子串；例如 `CNQ` 仍使用 `SP:SPX`。

## 信号模型

### 信号分级

| 信号 | 分数区间 | 含义 |
|:--|:--|:--|
| `🚨 CRASH BUY` | `>= 6` | 极端恐慌 |
| `🟢 STRONG BUY` | `>= 5` 且 `< 6` | 强买入结构 |
| `🟡 BUY DIP` | `>= min_score_buy` 且 `< 5` | 较弱买点 |
| `⏸ NEUTRAL` | 中性区间 | 暂无优势 |
| `🟠 SELL/HEDGE` | `<= -2` 且 `> -5` | 对冲 / 降风险 |
| `🔴 STRONG SELL` | `<= -5` 且 `> -6` | 强卖出信号 |
| `🔥 EUPHORIA` | `<= -6` | 极端贪婪 |

### 过滤状态

这些状态是展示层结果，不是另一套 score 公式：

| 状态 | 含义 |
|:--|:--|
| `DATA N/A / 数据不足` | 必需结构数据或因子预热未完成；所有信号被阻止 |
| `WAIT Vol/波动` | 买入分数达标，但波动区间过于危险 |
| `WAIT Mom/动量` | 买入分数达标，但动量确认失败 |
| `WAIT Z/结构` | BUY DIP 分数达标，但 Z 尚未通过恐慌阈值 |
| `WAIT Core/核心` | 买入分数达标，但缺少核心恐慌确认 |
| `WAIT Trend / 趋势缺失` | BUY DIP 需要趋势过滤，但所选趋势参考数据不可用 |
| `HOLD Vol/波动` | 卖出分数达标，但当前波动区间不支持卖出 |
| `HOLD Mom/动量` | 卖出分数达标，但动量确认失败 |
| `HOLD Core/核心` | 卖出分数达标，但缺少核心贪婪确认 |
| `🚫 NO TRADE` | 启用趋势过滤后，买入侧在熊市趋势下被屏蔽 |

仪表盘的状态原因与信号资格共用同一套门控。趋势数据缺失显示为灰色/未知，不会默认为牛市。BUY DIP 展示冷却只由最终有效信号消耗，因此被过滤的结构不会压掉下一次有效上穿。

仪表盘的结构标签描述当前满足条件的评分区间。新的图表标记还需要首次穿越阈值，并通过适用的展示冷却；分数 tooltip 会说明这一差别。

### 卖出严格度

卖出侧现在有两个明确模式：

- `Balanced (Legacy)`：保持之前的卖出 / 对冲过滤逻辑
- `High Win-Rate`：`🔴 STRONG SELL` 和 `🟠 SELL/HEDGE` 必须通过核心贪婪确认

`High Win-Rate` 是保留的选项名称，不代表已经用实证证明收益或胜率更高。

核心贪婪确认满足以下任一即可：

- VIX / VX1 basis 偏冷
- Put/Call Ratio 偏冷
- SKEW 偏高
- contango 高于 `10%`
- 可选 VVIX 偏冷

### 确认与时序控制

当前脚本有三个时序控制项：

- `Trading Safe Mode = ON`：避免历史未来数据泄漏；实时路径仍读取发展中的高周期数据，因此这些值可能继续变化，并在重载后重绘。OFF 允许历史预览显示当时尚不可知的数据。
- `Confirmed Signals Only = ON`：盘中图表的 `Score`、Z 与图表信号使用上一完整日线结构快照；`1D` 及以上图表的信号等待当前图表 K 线收盘。OFF 保留发展中的日线图表路径。
- `Alert Timing Mode`：单独选择智能提醒的数据与时序，使用预览或已完成日线结构。

v7.14 保留默认值与输入选项字符串：Safe Mode 默认 ON，`Confirmed Signals Only` 默认 OFF，提醒时序默认 `Confirmed Daily Structure`。使用周线 MTF 时请保持 Safe Mode ON；下文的嵌套请求日历限制仍然适用。

### 统计模型

滚动统计要求精确 `1D` 图表、交易所时区为 `America/New_York`，且标的类型为股票、基金或指数。期货、加密货币、外汇、其他周期与其他交易所时区不显示胜率统计。

- 不支持的图表显示周期/日历提示，而不是胜率数字
- 只统计已确认的最终买入 / 卖出信号
- `N` 只统计持有期终点 K 线已收盘，且起点/终点参考价格均有效并严格为正的样本
- 两个收益端点始终使用同一参考标的；手动参考缺失时不会退回 SPX
- 窗口按信号入场日期覆盖最近 `回看年数 * 252` 个图表交易日；每种持有期使用 `回看 bars - 持有 bars` 长度的评估窗口
- 已评估样本数为零的分级显示 `N/A`，不会显示容易误解的 `0%` 胜率
- 买入胜率口径使用 `Ref > 0`
- 卖出胜率口径使用 `Ref <= 0`
- 卖出平均收益保持原始远期收益，数值越负代表顶部 / 对冲越有效
- `Wxx%` 表示固定持有周期下、已完成样本的胜率
- 统计仍以 `19` 年为上限，保持在 `5000` bars 执行/缓冲预算内；就绪判断累计实际执行且已收盘的 K 线

## 智能提醒

### 默认行为

默认配置：

- `Smart Alert = ON`
- `Alert Timing Mode = Confirmed Daily Structure`
- `After-Hours Alert Policy = Allow if source confirms`
- `Alert Frequency = Real-time`

这套默认值的含义是：

- 盘中确认型提醒使用上一完整结构日，可在第一根常规时段 K 线发送；图表包含盘前 K 线也无需额外等待
- `1D` 及以上图表保留当根收盘时发送的语义
- 预览型提醒尽可能早发出
- 消息本身会明确标注这次提醒属于哪一种时序

### 提醒时序模式

| 模式 | 含义 |
|:--|:--|
| `Confirmed Daily Structure` | 盘中：上一完整结构日，在首根符合条件的常规时段 K 线发一次；`1D` 及以上：图表 K 线收盘 |
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
QQQ: 🟢 BUY [PREVIEW] [Lv1] → 🟡DIP | Score:4.0 Z:-1.8 VIX:20(NORM) 🟢SPX 🟢NDX 🔴RUT | Hybrid preview hybrid daily+chart
```

提醒状态机当前包含：

- `Lv1` 到 `Lv3` 的等级优先级
- 用 `varip` 做同一 bar 内去重
- 预览模式保留跨 bar 升级提醒
- 预览模式加入日内方向锁：同方向同级别同一交易日最多一次，仅严格升级可再次提醒
- 预览模式的 extended 时段新边缘也会消费这把方向锁，避免盘后 `1m` 重复刷提醒
- 方向锁/冷却/发送记账改为回滚安全 `varip`，防止实时 bar 回滚造成重复触发
- `Once Per Bar` 显式使用买卖两侧共用的一次发送配额；被拦截的第二次调用会保留观察记账，但不会错误推进实际发送冷却
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
| Header | 标题 + `CLOSED D / 已完成`、`LIVE D / 发展中` 或 `⚠️PREVIEW / 预览` |
| Signal | 当前信号 + 分数进度条 |
| Market | SPX / NDX / RUT 趋势、VIX 区间、提醒模式、成交量 |
| Structure | 期限结构 Z + contango |
| Stats | 符合条件的 `1D` 图表显示买卖两侧已评估样本数、胜率和平均收益 |

分数单元格的 tooltip 展示因子贡献、所选来源与当前评分对应的结构日期。日期标识计算周期，不是数据供应商的更新时间。Full 保持十六行；Mobile 保持两行及现有提醒模式行，由分数 tooltip 标明所选评分来源。

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

- 盘中图表信号使用已完成日线，或在 `1D` 及以上等待图表收盘
- 动量确认
- 周线 MTF 确认
- 信号展示冷却

### Statistics and Alerts

- 滚动统计回看年数（`1-19Y`，仅符合条件的纽约时区股票/基金/指数 `1D` 图表统计）
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
- 使用 `Sell Signal Strictness = High Win-Rate` 可要求两个较低卖出分级通过核心贪婪确认
- `Use Momentum Confirmation = ON`
- `Use Weekly MTF Confirmation = OFF`，或只在你需要更严格过滤时开启

### 盘中预览用法

只建议给理解 hybrid 时序的用户：

- 图表：`SPY` / `QQQ`
- 周期：`15m` 或 `1h`
- `VIX Timeframe = Chart`
- 发展中的图表预览使用 `Confirmed Signals Only = OFF`；ON 则改用已完成日线图表信号，智能提醒时序仍可单独选择
- `Alert Timing Mode = Preview / Earliest Possible`
- 若你完全不想盘后提醒，可再加 `Regular Session Only`，这样 extended hours 的 `1m` 也会被拦住

## 验证流程

这个仓库没有本地 Pine 编译器。在仓库根目录运行标准库回归测试：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

这些测试检查数值/状态转换模型与 Pine 源码连接关系，不执行 Pine、不编译 TradingView 请求、不测量性能，也不能证明实时交易时段行为。仍需在 TradingView 完成以下验证：

| 检查项 | TradingView 操作与预期 |
|:--|:--|
| 编译与请求预算 | 将 `vix.pine` 粘贴到 Pine Editor，在 `1m`、`30m`、`1D` 加载。分别开关 VVIX、周线 MTF，并使用互不相同的自定义 VIX/PCR/手动趋势源。检查嵌套展开后的请求数符合套餐限制；兼容目标为 40。 |
| 已完成图表路径 | 在 SPY/QQQ/IWM 盘中图开启 `Confirmed Signals Only`，比较重载前后的 Score/Z/信号，并检查 tooltip 中的已完成结构日期。`1D` 信号仍等待收盘。 |
| 发展中图表路径 | 关闭图表确认信号，对比 Safe Mode ON/OFF；发展中的 HTF 值可能变化，OFF 的历史预览可能使用未来数据。 |
| 首根常规时段提醒 | 对比仅常规时段与包含盘前盘后的 `1m`/`30m` ETF 图表。确认型提醒可在首根符合条件的常规 K 线发送，无需再等一根图表 K 线，并继续按结构日去重。 |
| 预览发送 | 测试两种频率、两种时段策略、重复 tick 和同一根 K 线中的反向事件。Once Per Bar 最多发送一条；被阻止的事件不会错误推进实际发送冷却，也不会排队补发。 |
| 数据与结构门控 | 测试不可用的自定义源、历史不足、趋势缺失和两种卖出严格度。检查 Score 不可用/无信号、灰色未知趋势与对应 WAIT/HOLD 原因。被过滤的 BUY DIP 不得消耗展示冷却。 |
| 统计 | 在符合条件的 `1D` 股票/基金/指数图检查已完成终点、有效正价格、入场日期窗口边界和零样本 `N/A`。不支持的日历/周期须隐藏统计；缺失手动参考不得把 SPX 混入收益区间。 |
| 路由 | 检查 QQQ/QQQM、IWM、NQ/MNQ、RTY/M2K 与 `CNQ`，核对趋势/统计参考与文档中的精确规则一致。 |
| 显示一致性 | 检查 Full/Mobile、分数因子/日期 tooltip、日线成交量及绘图。用上市时间较短的标的与加密货币图检查结构预热不依赖图表年龄；加密货币统计仍不可用。 |

修改脚本代码或输入后，应删除并重建 TradingView 提醒，以刷新服务器快照。以上是验证清单，不代表已经通过 TradingView 编译或实盘提醒测试。

## v7.14 更新内容

- **确认语义明确**：盘中确认型图表信号、Score 与 Z 使用已完成日线快照；Safe Mode 明确区分历史未来数据保护与仍可能发生的 HTF 实时重绘。智能提醒时序仍单独选择。
- **数据就绪与原因一致**：必需因子和已启用可选因子必须就绪；结构数据缺失时不产生信号。缺失趋势数据阻止需要趋势过滤的 BUY DIP，并显示未知状态。结构原因包含 Z 与趋势数据门控，被过滤的 BUY DIP 不再消耗展示冷却。
- **日线因子可检查**：成交量与评分共用日线数据；现有分数单元格 tooltip 展示因子贡献与结构日期，不增加表格行数，也不把日期当作供应商更新时间。
- **提醒发送修正**：包含盘前数据的图表可在首根常规时段发送确认型提醒。Once Per Bar 显式追踪共用发送配额，不再把被静默限频的调用记为已发送；保留事件丢弃语义。
- **统计资格与计数**：统计要求符合条件的纽约时区股票/基金/指数 `1D` 图表、有效正价格端点、同一参考标的和已收盘终点。窗口按信号入场日期计算，空样本分级显示 `N/A`。
- **精确代码识别与回归检查**：ETF/指数精确代码和期货根代码避免 `CNQ` 一类子串误匹配。标准库测试覆盖数值/状态行为和源码连接；TradingView 编译及实时验证仍是独立要求。默认值与输入选项字符串保持不变。

## v7.13 更新内容

- **评分与图表周期解耦**：`Score` 及其门控因子（Z-Score、动量、核心确认、周线 MTF 对齐）现在通过 `request.security()` tuple 统一在 `SP:SPX` 日线上下文中计算。盘中图表读取的日线数值与 `1D` 图表完全一致。`Trading Safe Mode = ON` 时，历史K线使用已完成交易日，实时K线跟踪发展中的当日值；OFF 时，历史盘中K线显示当日最终值（重绘语义与 v7.12 一致，数值已改为日线口径）。高于 `1D` 的图表每根K线采样一个日线值。注意：非美股交易日历的 `1D` 图表和上市时间较短的标的现在读取的是 SPX 网格数值，与 v7.12 不同——见已知限制。
- **confirmed 提醒锚点一致性**：在盘中图表上，confirmed 结构日 ID 与整套 confirmed 快照（score、Z、VIX、SKEW、波动区间、趋势、动量与核心门控——含 `BUY DIP` 的趋势过滤门控）现在来自专用的已完成结构日数据源——逐元素 `[1]` 偏移 + 固定 `lookahead_on`。实时与历史K线看到完全相同的已完成日数据，且默认配置下 confirmed 路径不再受 `Trading Safe Mode` 开关影响（周线 MTF 与 24 小时符号的例外见已知限制）。`1D` 及以上图表保留之前的当根收盘语义。
- **自适应 Z 回看滞回带**：新增 `Vol Regime Hysteresis Band` 输入（Advanced 分组，默认 `0.0` = v7.12 行为，建议试验值 `2.0`）。VIX 必须高于 `阈值 + 带宽` 才切换到高波动回看期，回落到 `阈值 - 带宽` 及以下才切回，避免 VIX 在阈值附近徘徊时回看期来回切换。
- **冷却语义澄清**：被提醒冷却或时段策略拦截的信号会被直接丢弃，不会延后补发。高波动期减半后的冷却现在以 `1` 根K线为下限，`Alert Cooldown Base = 1` 不会再被整除截断成 0。
- **死代码清理**：删除了未使用的 `spx_day_id` 请求和旧的 `lookahead_off` confirmed 锚点；结构日 ID 现在是一个共享表达式，同时供日线上下文请求和图表日 ID 复用。

## 当前能力重点

- 卖出严格度模式支持更严格的顶部信号过滤
- 核心贪婪确认可以把卖出侧拦截为 `HOLD Core/核心`
- 符合条件的纽约时区股票/基金/指数 `1D` 图表同时提供买入侧与卖出侧滚动统计
- 图表标签与统计使用最终图表事件；预览提醒消费这些事件，确认提醒则将共享过滤条件应用于独立的日线转换
- confirmed 提醒现在会对完整结构日做一次快照，并在下一次常规时段只发一次
- score 及其门控因子统一在 `SP:SPX` 日线上下文计算，盘中图表与 `1D` 图表的评分语义一致
- confirmed 提醒消费的已完成结构日快照在实时与历史K线上完全一致
- `Regular Session Only` 仍按交易所常规时段约束预览提醒
- preview 提醒新增日内方向锁：同方向同级别同日只发一次，仅升级可再次触发

## 已知限制

- Pine 只能在 TradingView 上做真实验证。
- 外部日线数据可能晚于图表收盘更新。
- Safe Mode 本身不会冻结发展中的日线值。盘中已完成图表信号需开启 `Confirmed Signals Only`；图表信号确认与智能提醒时序分别控制。
- `VIX Timeframe = Chart` 并不代表整套模型都变成盘中实时：自 v7.13 起它只影响仪表盘 VIX 显示、实时波动区间门控、自适应趋势均线长度选择（即实时趋势过滤）与自适应提醒冷却——评分始终基于日线结构数据计算。
- 评分在 `SP:SPX` 日线网格上计算。在非美股交易日历的 `1D` 图表上（加密货币、外汇），滚动窗口不再包含周末K线；在上市时间较短的标的上，预热数据来自 SPX 的数十年历史。这些图表读取的评分与 v7.12 不同（属于有意改进）。
- confirmed 路径与 `Trading Safe Mode` 开关的解耦只在默认配置下成立：开启 `Use Weekly MTF Confirmation` 后，周线 MTF 腿在周线上下文内采样日线数据，开关仍会改变已完成周内被采样的具体交易日（开=每周最后一个日线值/周五，关=第一个/周一），confirmed 评分可能相差 ±1——请保持安全模式开启。该解耦同时假设 VIX / Put-Call / 手动趋势符号遵循美股交易日历；24 小时日历的自定义符号会让 confirmed 快照在开关间偏移一天。
- 统计是滚动窗口统计，不是完整策略回测。
- 胜率统计要求精确 `1D`、交易所时区 `America/New_York`、股票/基金/指数类型；这是保守的适用范围限制，不会自动对齐任意交易日历。
- 自定义手动参考可能使用不同交易日期或收盘时间，尤其是 24 小时交易品种。图表符合统计资格不意味着参考日历会自动对齐；解读收益时应选择与图表日线时段兼容的参考标的。
- `CBOE:VX1!` / `CBOE:VX2!` 是连续合约，移仓换月日会切换合约；期限结构读数（contango、basis、Z-Score）在移仓日附近可能出现人为尖峰。
- 时段门控使用图表交易所定义的常规时段。期货可能把延长的电子盘视为常规时段；此设置不会给所有品种强制套用美股现货时间。
- 自动识别仅支持所列 ETF/指数代码与期货根代码。未列出的产品退回 SPX；需要时请选择手动参考。

## License

MIT License

## 免责声明

本项目仅用于研究和教育用途，不构成投资建议。

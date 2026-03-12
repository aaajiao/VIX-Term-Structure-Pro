# VIX Term Structure Pro v7.12

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
- 指标标题：`VIX Term Structure Pro [v7.12]`
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
| `Regular Session Only` | 按交易所定义的常规交易时段拦截；即使图表开启 extended hours，盘前盘后也不提醒 |

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

如果你切到 `Regular Session Only`，被拦下的盘后信号会直接记为已处理，不会在下一根 `1m` K 线或下一次允许提醒的时段里重新回放。

TradingView 的提醒运行在服务器侧快照上。只要你改了 alert timing 或盘后策略，必须删除并重新创建提醒，服务器才会拿到新的脚本逻辑和输入值。

### 提醒消息格式

```text
Symbol: [Side] [Timing] [Level][Upgrade] -> [Triggered Labels] | [Context]

SPY: 🟢 BUY [CONFIRMED] [Lv2] -> 🟢STRONG | Score:5.2 Z:-2.1 VIX:19(NORM) | Confirmed
QQQ: 🟢 BUY [PREVIEW] [Lv1] -> 🟡DIP | Score:4.0 Z:-1.8 VIX:28(HIGH) | Hybrid preview daily+chart
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
- `After-Hours Alert Policy = Allow if source confirms`
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
8. 在 `Allow if source confirms` 下，观察盘后确认提醒是否与日线外部源的晚到更新一致。
9. 确认 `Regular Session Only` 不会在下一根盘后 `1m` K 线或下一次常规时段 bar 上重放同一条被拦截信号。

## 当前能力重点

- 卖出严格度模式支持更干净、更高胜率的顶部筛选
- 核心贪婪确认可以把卖出侧拦截为 `✋ HOLD (Core)`
- 精确 `1D` 图表同时提供买入侧与卖出侧滚动统计
- 卖出图表标签、提醒与统计统一基于最终过滤后的卖出信号
- `Regular Session Only` 现在按交易所常规时段判定，并且不会重放被盘后拦下的同一信号

## 限制说明

- Pine 只能在 TradingView 上做真实验证。
- 外部日线数据可能晚于图表收盘更新。
- `VIX Timeframe = Chart` 并不代表整套模型都变成盘中实时，只是 VIX 这一路变成图表周期。
- 统计是滚动窗口统计，不是完整策略回测。
- 胜率统计被有意限制为仅 `1D` 图表可见。

## License

MIT License

## 免责声明

本项目仅用于研究和教育用途，不构成投资建议。

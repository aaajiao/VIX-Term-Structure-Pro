# VIX Term Structure Pro v7.11

[![TradingView](https://img.shields.io/badge/TradingView-Indicator-blue?logo=tradingview)](https://www.tradingview.com/scripts/)
[![Pine Script](https://img.shields.io/badge/Pine%20Script-v6-brightgreen)](https://www.tradingview.com/pine-script-reference/v6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **[🇺🇸 English](../README.md)** | 🇨🇳 中文

---

### 🌟 概述
VIX Term Structure Pro 是一款高级多因子市场择时指标，结合 VIX 期货期限结构分析、自适应波动率区间检测和全面的市场广度监控，生成高精度的买卖信号。

### 🚦 信号系统

#### 三级信号逻辑

| 信号 | 评分 | 含义 | 操作建议 |
|:--|:--|:--|:--|
| 🚨 **CRASH BUY** | ≥ 6 | 极端恐慌，罕见机会 | 积极入场 |
| 🟢 **STRONG BUY** | ≥ 5 | 多因子共振 | 建仓 |
| 🟡 **BUY DIP** | ≥ 4 | 逢低吸纳 | 加仓 |
| ⚪ **NEUTRAL** | -2~4 | 无明确信号 | 观望 / 持有 |
| 🟠 **SELL/HEDGE** | ≤ -2 | 检测到自满或贪婪 | 减仓/对冲 |
| 🔴 **STRONG SELL** | ≤ -5 | 强烈看跌信号 | 卖出 |
| 🔥 **EUPHORIA** | ≤ -6 | 极度贪婪，市场过热 | 清仓 |

#### 过滤状态

| 状态 | 显示 | 条件 | 含义 |
|:--|:--|:--|:--|
| **WAIT** | `✋ WAIT` | 高波动或动量未确认 | **买入侧**: 评分高但风险也高。等待更好的入场时机。 |
| **HOLD** | `☕ HOLD` | 低波动或动量未确认 | **卖出侧**: 评分低但趋势强劲。暂不卖出。 |
| **NO TRADE** | `🐻 WAIT` | 熊市趋势过滤 | **熊市**: 过滤信号以保护本金。 |

### 📋 仪表盘

**v7.8 重设计**: 采用深色主题，动态信号高亮，提供两种显示模式。

#### 📱 移动模式 (2行)
专为手机屏幕设计。

| 行 | 内容 | 示例 |
|:--|:--|:--|
| **1** | **信号 + 评分** | `🟢 STRONG BUY +5` |
| **2** | **提醒模式 + VIX** | `CONFIRMED / 18.2ʳᵗ` |

*(如果被过滤，第1行显示原因: `✋ WAIT: Need ≥4`)*

#### 🖥️ 完整模式 (14行)
全面的市场分析。

| 区域 | 内容 |
|:--|:--|
| **HEADER** | 标题 + 模式 (`🛡️SAFE` 或 `⚠️PREVIEW`) |
| **SIGNAL** | **当前信号** + **评分进度条** (█░░░░) |
| **MARKET** | 趋势状态 (SPX/NDX/RUT) + VIX 区间 + 提醒模式 + 成交量状态 |
| **STRUCTURE** | 期限结构 Z-Score + 升水率 (Contango %) |
| **STATS** | 历史信号统计: `🚨3 +8.2% 🟢5 +4.1% / 🟡12 +1.8%` |

### 🔔 智能警报系统

系统采用 **等级 (Lv1-3)** 优先级机制配合以图表 bar 为单位的 **自适应冷却**。

#### 提醒时序模式

- **Confirmed Daily Structure**（默认）: 仅在日线结构源确认后报警。若 TradingView 的日线外部源更新较晚，提醒可能在收盘后到达。消息会带 `[CONFIRMED]` 标签。
- **Preview / Earliest Possible**: 保留尽早提醒的行为。如果 `VIX Timeframe = Chart`，则只有 VIX 跟随图表周期，其他结构因子仍可能是日线，所以消息会标记为预览，并可能显示 `hybrid daily+chart`。
- **面板标签**: `PREVIEW*` 表示 hybrid preview 模式，即只有 VIX 跟随图表周期，其他结构因子仍依赖日线确认。

#### 盘后策略

- **Allow if source confirms**（默认）: 如果确认版日线源在收盘后才最终到位，允许继续发提醒。
- **Regular Session Only**: 只在常规交易时段内提醒，盘前盘后全部拦截。

#### 为什么会在收盘后提醒

本指标的 Score 依赖多个日线外部数据源，例如 `CBOE:VIX`、`CBOE:VX1!`、`CBOE:VX2!`、`CBOE:SKEW`、`INDEX:CPCI` 以及可选的 `CBOE:VVIX`。这些数据源不保证和图表收盘时刻完全同步完成，因此当 TradingView 晚一些才刷新日线确认值时，`[CONFIRMED]` 提醒在收盘后出现是合理行为，不代表脚本重绘或乱报。

#### 触发场景

| 场景 | 触发条件 | 输出示例 |
|:--|:--|:--|
| **首次触发** | 信号出现 | `SPY: 🟢 BUY [CONFIRMED] [Lv2] ...` |
| **升级 ⬆️** | 信号变强 | `SPY: 🟢 BUY [PREVIEW] [Lv2]⬆️ ...` |
| **收盘后确认** | 日线结构源晚到 | `SPY: 🟢 BUY [CONFIRMED] [Lv1] ... | Confirmed source update after close` |

#### 自适应冷却

- **HIGH VOL (>25)**: **0.5x** 冷却 (恐慌期报警更频繁)
- **NORMAL (15-25)**: **1.0x** 冷却 (标准)
- **LOW VOL (<15)**: **2.0x** 冷却 (平静市场减少噪音)

#### 警报格式

```text
Symbol: [Side] [Timing] [Level][Upgrade] | [Context]
----------------------------------------------------
SPY: 🟢 BUY [CONFIRMED] [Lv2] → 🟢STRONG | Score:5.2 Z:-2.1 VIX:19(NORM) | Confirmed
QQQ: 🟢 BUY [PREVIEW] [Lv1]⬆️ → 🟡DIP | Score:4.0 Z:-1.8 VIX:28(HIGH) | Hybrid preview daily+chart
```

### 📝 更新日志

#### v7.11 (Current)
- **🔔 提醒时序审计**:
  - 新增 `Alert Timing Mode`：`Confirmed Daily Structure` 与 `Preview / Earliest Possible`。
  - 新增 `After-Hours Alert Policy`：`Allow if source confirms` 与 `Regular Session Only`。
  - 提醒消息增加 `[CONFIRMED]` / `[PREVIEW]` 标签，并明确标识收盘后源更新。
  - 仪表盘新增提醒模式状态，便于识别 hybrid preview 行为。

#### v7.10
- **📊 跨图表 Score 一致性**:
  - Score 现在是**纯 VIX 结构客观指标**——在所有图表品种（QQQ、SPY、IWM 等）上完全一致。
  - 移除 Score 中的 `-2` 趋势惩罚。趋势过滤仅影响信号展示（BUY DIP → NO TRADE）。
  - Weekly MTF Z-Score 改用固定 `SP:SPX` 日历对齐，消除跨图表差异。
- **📈 统计收益跟随 Auto-Detect 指数**:
  - 信号回报统计改用对应指数（QQQ→NDX, IWM→RUT, 其他→SPX）。
  - 确保过滤逻辑和统计口径一致。
- **🔧 修复 CW10003 警告**:
  - 将 `ta.percentile_linear_interpolation` 从三元运算符提取到全局作用域。

#### v7.9
- **🛡️ 生产交易稳健性改进**:
  - SKEW Z-Score 计算添加除零保护。
  - 趋势均线比较添加完整 NA 检查 (SPX/NDX/RUT/Manual)。
  - Weekly MTF 回退逻辑优化（开启 `use_mtf_confirm` 时更严格）。
  - 百分位计算添加 Warmup 期保护。
- **🎯 实时 VIX 显示**:
  - Safe 模式下仪表盘显示实时 VIX 值（`ʳᵗ` 标记）。
  - 信号计算保持无重绘。

#### v7.8
- **🎨 仪表盘重设计**:
  - 新增 **移动模式** (2行) 与 **完整模式** (13行)。
  - 添加可视化 **评分进度条**。
  - 深色主题与动态背景色。
- **🛡️ 实盘安全模式**:
  - 默认开启 `lookahead_off` 防止重绘。
  - 区分 `🛡️SAFE` (安全) 与 `⚠️PREVIEW` (预览) 状态。
- **🔔 智能警报 v2 更新**:
  - 新增 **跨K线升级** 检测 (如 DIP → STRONG)。
  - 包含过滤后信号的警报 (WAIT/HOLD 状态)。

### ⚠️ 免责声明
本指标仅供教育参考，不构成投资建议。过往表现不代表未来收益。

### 📄 许可证
MIT License

# VIX Term Structure Pro v7.9

[![TradingView](https://img.shields.io/badge/TradingView-Indicator-blue?logo=tradingview)](https://www.tradingview.com/scripts/)
[![Pine Script](https://img.shields.io/badge/Pine%20Script-v6-brightgreen)](https://www.tradingview.com/pine-script-reference/v6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🇺🇸 English

### 🌟 Overview
VIX Term Structure Pro is an advanced multi-factor market timing indicator that combines VIX futures term structure analysis, adaptive volatility regime detection, and comprehensive market breadth monitoring to generate high-precision buy/sell signals.

### 🚦 Signal System

#### Three-Tier Signal Logic

| Signal | Score | Meaning | Action |
|:--|:--|:--|:--|
| 🚨 **CRASH BUY** | ≥ 6 | Extreme panic, rare opportunity | Aggressive Entry |
| 🟢 **STRONG BUY** | ≥ 5 | Multi-factor confluence | Build Position |
| 🟡 **BUY DIP** | ≥ 4 | Accumulate on weakness | Add to Position |
| ⚪ **NEUTRAL** | -2~4 | No clear signal | Wait / Hold |
| 🟠 **SELL/HEDGE** | ≤ -2 | Complacency or greed detected | Reduce/Hedge |
| 🔴 **STRONG SELL** | ≤ -5 | Strong bearish signals | Sell |
| 🔥 **EUPHORIA** | ≤ -6 | Extreme greed, market overheated | Exit All |

#### Filtered States

| Status | Display | Condition | Meaning |
|:--|:--|:--|:--|
| **WAIT** | `✋ WAIT` | High Vol or Momentum not confirmed | **Buy Side**: Score is high but risk is too high. Wait for better entry. |
| **HOLD** | `☕ HOLD` | Low Vol or Momentum not confirmed | **Sell Side**: Score is low but trend is strong. Don't sell yet. |
| **NO TRADE** | `🐻 WAIT` | Bear Market Trend Filter | **Bear Market**: Signals filtered to preserve capital. |

### 📋 Dashboard

**v7.8 Redesign**: Features a dark theme, dynamic signal highlighting, and two display modes.

#### 📱 Mobile Mode (2 Rows)
Designed for phone screens.

| Row | Content | Example |
|:--|:--|:--|
| **1** | **Signal + Score** | `🟢 STRONG BUY +5` |
| **2** | **VIX Status** | `🟡 VIX:18 NORMAL` |

*(If filtered, Row 1 shows reason: `✋ WAIT: Need ≥4`)*

#### 🖥️ Full Mode (13 Rows)
Comprehensive market analysis.

| Section | Content |
|:--|:--|
| **HEADER** | Title + Mode (`🛡️SAFE` or `⚠️PREVIEW`) |
| **SIGNAL** | **Current Signal** + **Score Progress Bar** (█░░░░) |
| **MARKET** | Trend Status (SPX/NDX/RUT) + VIX Regime + Volume Status |
| **STRUCTURE** | Term Structure Z-Score + Contango % |
| **STATS** | Historical Signal Stats: `🚨3 +8.2% 🟢5 +4.1% / 🟡12 +1.8%` |

### 🔔 Smart Alert System

The system uses a **Level (Lv1-3)** priority mechanism with **Adaptive Cooldown**.

#### Trigger Scenarios

| Scenario | Trigger | Example Output |
|:--|:--|:--|
| **First Entry** | Signal appears | `SPY: 🟡 BUY DIP +4 ...` |
| **Upgrade ⬆️** | Signal gets stronger | `SPY: 🟢 STRONG BUY +5 ⬆️ ...` |
| **Downgrade ⬇️** | Signal gets weaker | `SPY: 🟡 BUY DIP +4 ⬇️ ...` |

#### Adaptive Cooldown

- **HIGH VOL (>25)**: **0.5x** Cooldown (Alerts faster during panic)
- **NORMAL (15-25)**: **1.0x** Cooldown (Standard)
- **LOW VOL (<15)**: **2.0x** Cooldown (Reduces noise in calm markets)

#### Alert Message Format

```text
Symbol: [Signal] [Level] [Direction] | [Context]
------------------------------------------------
SPY: 🟢 STRONG BUY [Lv2] ⬆️ | Score:5.2 Z:-2.1 VIX:19(NORM)
QQQ: ✋ WAIT (High Vol)     | Score:4.0 Z:-1.8 VIX:28(HIGH)
```

### 📝 Changelog

#### v7.9 (Current)
- **🛡️ Robustness Improvements for Production Trading**:
  - Added division-by-zero guard for SKEW Z-Score calculation.
  - Added complete NA checks for trend MA comparisons (SPX/NDX/RUT/Manual).
  - Improved Weekly MTF fallback logic (stricter when `use_mtf_confirm=true`).
  - Added warmup period protection for percentile calculations.
- **🎯 Real-time VIX Display**:
  - Dashboard shows real-time VIX value (`ʳᵗ` indicator) in Safe Mode.
  - Signal calculations remain non-repainting.

#### v7.8
- **🎨 Dashboard Redesign**:
  - New **Mobile Mode** (2 rows) vs **Full Mode** (13 rows).
  - Visual **Score Progress Bar** added.
  - Dark theme with dynamic background colors.
- **🛡️ Trading Safe Mode**:
  - Default `lookahead_off` to prevent repainting.
  - Distinct `🛡️SAFE` vs `⚠️PREVIEW` indicators.
- **🔔 Smart Alert v2 Updates**:
  - Added **Cross-Bar Upgrade** detection (e.g., DIP → STRONG).
  - Included filtered signal alerts (WAIT/HOLD status).

### ⚠️ Disclaimer
This indicator is for educational purposes only. It does not constitute financial advice. Past performance does not guarantee future results.

### 📄 License
MIT License

---

## 🇨🇳 中文

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
| **2** | **VIX 状态** | `🟡 VIX:18 NORMAL` |

*(如果被过滤，第1行显示原因: `✋ WAIT: Need ≥4`)*

#### 🖥️ 完整模式 (13行)
全面的市场分析。

| 区域 | 内容 |
|:--|:--|
| **HEADER** | 标题 + 模式 (`🛡️SAFE` 或 `⚠️PREVIEW`) |
| **SIGNAL** | **当前信号** + **评分进度条** (█░░░░) |
| **MARKET** | 趋势状态 (SPX/NDX/RUT) + VIX 区间 + 成交量状态 |
| **STRUCTURE** | 期限结构 Z-Score + 升水率 (Contango %) |
| **STATS** | 历史信号统计: `🚨3 +8.2% 🟢5 +4.1% / 🟡12 +1.8%` |

### 🔔 智能警报系统

系统采用 **等级 (Lv1-3)** 优先级机制配合 **自适应冷却**。

#### 触发场景

| 场景 | 触发条件 | 输出示例 |
|:--|:--|:--|
| **首次触发** | 信号出现 | `SPY: 🟡 BUY DIP +4 ...` |
| **升级 ⬆️** | 信号变强 | `SPY: 🟢 STRONG BUY +5 ⬆️ ...` |
| **降级 ⬇️** | 信号变弱 | `SPY: 🟡 BUY DIP +4 ⬇️ ...` |

#### 自适应冷却

- **HIGH VOL (>25)**: **0.5x** 冷却 (恐慌期报警更频繁)
- **NORMAL (15-25)**: **1.0x** 冷却 (标准)
- **LOW VOL (<15)**: **2.0x** 冷却 (平静市场减少噪音)

#### 警报格式

```text
Symbol: [Signal] [Level] [Direction] | [Context]
------------------------------------------------
SPY: 🟢 STRONG BUY [Lv2] ⬆️ | Score:5.2 Z:-2.1 VIX:19(NORM)
QQQ: ✋ WAIT (High Vol)     | Score:4.0 Z:-1.8 VIX:28(HIGH)
```

### 📝 更新日志

#### v7.9 (Current)
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

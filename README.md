# VIX Term Structure Pro v7.8

[![TradingView](https://img.shields.io/badge/TradingView-Indicator-blue?logo=tradingview)](https://www.tradingview.com/scripts/)
[![Pine Script](https://img.shields.io/badge/Pine%20Script-v6-brightgreen)](https://www.tradingview.com/pine-script-reference/v6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Professional VIX-based Market Sentiment & Timing Indicator**
**专业的 VIX 市场情绪与择时指标**

---

## 🌟 Overview | 概述

**English:**
VIX Term Structure Pro is an advanced multi-factor market timing indicator that combines VIX futures term structure analysis, adaptive volatility regime detection, and comprehensive market breadth monitoring to generate high-precision buy/sell signals.

**中文：**
VIX Term Structure Pro 是一款高级多因子市场择时指标，结合 VIX 期货期限结构分析、自适应波动率区间检测和全面的市场广度监控，生成高精度的买卖信号。

---

## 🚦 Signal System | 信号系统

### Three-Tier Signal Logic | 三级信号逻辑

| Signal | Score | Meaning (English) | 含义 (中文) | Action |
|:--|:--|:--|:--|:--|
| 🚨 **CRASH BUY** | ≥ 6 | Extreme panic, rare opportunity | 极端恐慌，罕见机会 | Aggressive Entry |
| 🟢 **STRONG BUY** | ≥ 5 | Multi-factor confluence | 多因子共振 | Build Position |
| 🟡 **BUY DIP** | ≥ 4 | Accumulate on weakness | 逢低吸纳 | Add to Position |
| ⚪ **NEUTRAL** | -2~4 | No clear signal | 无明确信号 | Wait / Hold |
| 🟠 **SELL/HEDGE** | ≤ -2 | Complacency or greed detected | 检测到自满或贪婪 | Reduce/Hedge |
| 🔴 **STRONG SELL** | ≤ -5 | Strong bearish signals | 强烈看跌信号 | Sell |
| 🔥 **EUPHORIA** | ≤ -6 | Extreme greed, market overheated | 极度贪婪，市场过热 | Exit All |

### Filtered States | 过滤状态

| Status | Display | Condition | Meaning |
|:--|:--|:--|:--|
| **WAIT** | `✋ WAIT` | High Vol or Momentum not confirmed | **Buy Side**: Score is high but risk is too high. Wait for better entry. |
| **HOLD** | `☕ HOLD` | Low Vol or Momentum not confirmed | **Sell Side**: Score is low but trend is strong. Don't sell yet. |
| **NO TRADE** | `🐻 WAIT` | Bear Market Trend Filter | **Bear Market**: Signals filtered to preserve capital. |

---

## 📋 Dashboard | 仪表盘

**v7.8 Redesign**: Features a dark theme, dynamic signal highlighting, and two display modes.
**v7.8 重设计**: 采用深色主题，动态信号高亮，提供两种显示模式。

### 📱 Mobile Mode (2 Rows) | 移动模式
Designed for phone screens. / 专为手机屏幕设计。

| Row | Content | Example |
|:--|:--|:--|
| **1** | **Signal + Score** | `🟢 STRONG BUY +5` |
| **2** | **VIX Status** | `🟡 VIX:18 NORMAL` |

*(If filtered, Row 1 shows reason: `✋ WAIT: Need ≥4`)*

### 🖥️ Full Mode (13 Rows) | 完整模式
Comprehensive market analysis. / 全面的市场分析。

| Section | Content |
|:--|:--|
| **HEADER** | Title + Mode (`🛡️SAFE` or `⚠️PREVIEW`) |
| **SIGNAL** | **Current Signal** + **Score Progress Bar** (█░░░░) |
| **MARKET** | Trend Status (SPX/NDX/RUT) + VIX Regime + Volume Status |
| **STRUCTURE** | Term Structure Z-Score + Contango % |
| **STATS** | Historical Signal Stats: `🚨3 +8.2% 🟢5 +4.1% / 🟡12 +1.8%` |

---

## 🔔 Smart Alert System | 智能警报系统

The system uses a **Level (Lv1-3)** priority mechanism with **Adaptive Cooldown**.
系统采用 **等级 (Lv1-3)** 优先级机制配合 **自适应冷却**。

### Trigger Scenarios | 触发场景

| Scenario | Trigger | Example Output |
|:--|:--|:--|
| **First Entry** | Signal appears | `SPY: 🟡 BUY DIP +4 ...` |
| **Upgrade ⬆️** | Signal gets stronger | `SPY: 🟢 STRONG BUY +5 ⬆️ ...` |
| **Downgrade ⬇️** | Signal gets weaker | `SPY: 🟡 BUY DIP +4 ⬇️ ...` |

### Adaptive Cooldown | 自适应冷却

- **HIGH VOL (>25)**: **0.5x** Cooldown (Alerts faster during panic)
- **NORMAL (15-25)**: **1.0x** Cooldown (Standard)
- **LOW VOL (<15)**: **2.0x** Cooldown (Reduces noise in calm markets)

### Alert Message Format | 警报格式

```text
Symbol: [Signal] [Level] [Direction] | [Context]
------------------------------------------------
SPY: 🟢 STRONG BUY [Lv2] ⬆️ | Score:5.2 Z:-2.1 VIX:19(NORM)
QQQ: ✋ WAIT (High Vol)     | Score:4.0 Z:-1.8 VIX:28(HIGH)
```

---

## 📝 Changelog | 更新日志

### v7.8 (Current)
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

---

## ⚠️ Disclaimer | 免责声明

**English:** This indicator is for educational purposes only. It does not constitute financial advice. Past performance does not guarantee future results.
**中文：** 本指标仅供教育参考，不构成投资建议。过往表现不代表未来收益。

## 📄 License | 许可证
MIT License

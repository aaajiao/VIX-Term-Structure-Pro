# VIX Term Structure Pro v7.11

[![TradingView](https://img.shields.io/badge/TradingView-Indicator-blue?logo=tradingview)](https://www.tradingview.com/scripts/)
[![Pine Script](https://img.shields.io/badge/Pine%20Script-v6-brightgreen)](https://www.tradingview.com/pine-script-reference/v6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 🇺🇸 English | **[🇨🇳 中文](docs/README_CN.md)**

---

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
| **2** | **Alert Mode + VIX** | `CONFIRMED / 18.2ʳᵗ` |

*(If filtered, Row 1 shows reason: `✋ WAIT: Need ≥4`)*

#### 🖥️ Full Mode (14 Rows)
Comprehensive market analysis.

| Section | Content |
|:--|:--|
| **HEADER** | Title + Mode (`🛡️SAFE` or `⚠️PREVIEW`) |
| **SIGNAL** | **Current Signal** + **Score Progress Bar** (█░░░░) |
| **MARKET** | Trend Status (SPX/NDX/RUT) + VIX Regime + Alert Mode + Volume Status |
| **STRUCTURE** | Term Structure Z-Score + Contango % |
| **STATS** | Historical Signal Stats: `🚨3 +8.2% 🟢5 +4.1% / 🟡12 +1.8%` |

### 🔔 Smart Alert System

The system uses a **Level (Lv1-3)** priority mechanism with **Adaptive Cooldown** measured in chart bars.

#### Alert Timing Modes

- **Confirmed Daily Structure** (default): Alerts only when the daily VIX structure inputs are confirmed. This may still arrive after the regular close if TradingView receives late daily source updates. Messages are tagged with `[CONFIRMED]`.
- **Preview / Earliest Possible**: Keeps the earliest-possible behavior. If `VIX Timeframe = Chart`, only VIX is chart-timeframe; the rest of the structure inputs can still be daily, so messages are tagged as preview and may say `hybrid daily+chart`.
- **Dashboard label**: `PREVIEW*` means hybrid preview mode, where VIX is chart-timeframe but other structure inputs still rely on daily confirmation.

#### After-Hours Policy

- **Allow if source confirms** (default): Accepts post-close alerts when confirmed daily inputs settle late.
- **Regular Session Only**: Blocks alerts outside the regular session if you only want intraday or close-time notifications.

#### Why an alert can appear after the close

This indicator's score depends on several daily external sources such as `CBOE:VIX`, `CBOE:VX1!`, `CBOE:VX2!`, `CBOE:SKEW`, `INDEX:CPCI`, and optional `CBOE:VVIX`. Those feeds are not guaranteed to finalize at the exact same moment as the chart close, so a `[CONFIRMED]` alert can legitimately arrive after the market close when TradingView refreshes those daily values.

#### Trigger Scenarios

| Scenario | Trigger | Example Output |
|:--|:--|:--|
| **First Entry** | Signal appears | `SPY: 🟢 BUY [CONFIRMED] [Lv2] ...` |
| **Upgrade ⬆️** | Signal gets stronger | `SPY: 🟢 BUY [PREVIEW] [Lv2]⬆️ ...` |
| **Post-Close Confirm** | Daily sources finalize late | `SPY: 🟢 BUY [CONFIRMED] [Lv1] ... | Confirmed source update after close` |

#### Adaptive Cooldown

- **HIGH VOL (>25)**: **0.5x** Cooldown (Alerts faster during panic)
- **NORMAL (15-25)**: **1.0x** Cooldown (Standard)
- **LOW VOL (<15)**: **2.0x** Cooldown (Reduces noise in calm markets)

#### Alert Message Format

```text
Symbol: [Side] [Timing] [Level][Upgrade] | [Context]
----------------------------------------------------
SPY: 🟢 BUY [CONFIRMED] [Lv2] → 🟢STRONG | Score:5.2 Z:-2.1 VIX:19(NORM) | Confirmed
QQQ: 🟢 BUY [PREVIEW] [Lv1]⬆️ → 🟡DIP | Score:4.0 Z:-1.8 VIX:28(HIGH) | Hybrid preview daily+chart
```

### 📝 Changelog

#### v7.11 (Current)
- **🔔 Alert Timing Audit**:
  - Added explicit `Alert Timing Mode`: `Confirmed Daily Structure` vs `Preview / Earliest Possible`.
  - Added `After-Hours Alert Policy` with `Allow if source confirms` and `Regular Session Only`.
  - Alert messages now include `[CONFIRMED]` / `[PREVIEW]` tags and call out post-close source updates.
  - Dashboard now exposes the active alert mode to make hybrid preview behavior visible.

#### v7.10
- **📊 Cross-Chart Score Consistency**:
  - Score is now a **pure VIX structure metric** — identical across all chart symbols (QQQ, SPY, IWM, etc.).
  - Removed `-2` trend penalty from Score. Trend filter now only affects signal display (BUY DIP → NO TRADE).
  - Weekly MTF Z-Score uses fixed `SP:SPX` calendar alignment instead of `syminfo.tickerid`.
- **📈 Auto-Detect Stats Returns**:
  - Signal return statistics now use the auto-detected index (QQQ→NDX, IWM→RUT, others→SPX).
  - Ensures filter logic and stats reference are consistent.
- **🔧 Fix CW10003 Warnings**:
  - Extracted `ta.percentile_linear_interpolation` calls from ternary operators to global scope.

#### v7.9
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

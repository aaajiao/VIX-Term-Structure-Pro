# VIX Term Structure Pro v7.12

[![TradingView](https://img.shields.io/badge/TradingView-Indicator-blue?logo=tradingview)](https://www.tradingview.com/scripts/)
[![Pine Script](https://img.shields.io/badge/Pine%20Script-v6-brightgreen)](https://www.tradingview.com/pine-script-reference/v6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> English | **[中文](docs/README_CN.md)**

VIX Term Structure Pro is a TradingView Pine Script v6 indicator for reading VIX term structure, volatility regime, and sentiment extremes with a single score-driven dashboard and alert system.

## Overview

This project is a single-file Pine indicator centered on one design rule:

- `Score` is a pure VIX structure metric.
- Trend context affects signal display and statistics reference, but it does not change `Score`.
- Cross-chart behavior is kept consistent by using fixed external symbols for VIX structure inputs.

Current script:

- Main file: `vix.pine`
- Pine version: `//@version=6`
- Indicator title: `VIX Term Structure Pro [v7.12]`
- Historical execution window: `calc_bars_count=5000`
- Primary use case: SPY / QQQ / IWM / index charts on TradingView

## Repository Layout

| Path | Purpose |
|:--|:--|
| `vix.pine` | Main indicator source |
| `README.md` | English documentation |
| `docs/README_CN.md` | Chinese documentation |
| `chart_guide.png` | Dashboard / chart reference image |
| `zscore_guide.png` | Z-Score interpretation image |

## How the Indicator Works

### Core Inputs Used in the Score

The score combines objective VIX structure factors:

- Term structure Z-Score
- VX1/VX2 contango or backwardation
- VIX/VX1 basis
- SKEW
- Put/Call Ratio
- Optional VVIX
- VX1 volume spike / high volume context
- Optional momentum confirmation
- Optional weekly MTF alignment

When adaptive thresholds are enabled, PCR percentile thresholds now feed the score directly. When VVIX integration is enabled, the selected `VVIX Threshold Mode` also feeds the score directly.

Trend is not part of the score. Trend only affects:

- `🟡 BUY DIP` display filtering (`🚫 NO TRADE` in bear trend)
- auto-detected reference index for statistics

### External Data Sources

The indicator uses fixed symbols for cross-chart consistency:

| Factor | Symbol |
|:--|:--|
| VIX | `CBOE:VIX` by default |
| Front futures | `CBOE:VX1!` |
| Second futures | `CBOE:VX2!` |
| SKEW | `CBOE:SKEW` |
| Put/Call Ratio | `INDEX:CPCI` by default |
| VVIX | `CBOE:VVIX` |
| Trend / stats references | `SP:SPX`, `NASDAQ:NDX`, `TVC:RUT` |

Auto-detect routing:

- QQQ / NDX / NQ-family charts use `NASDAQ:NDX`
- IWM / RUT / RTY-family charts use `TVC:RUT`
- Everything else uses `SP:SPX`

## Signal Model

### Signal Tiers

| Signal | Score Zone | Meaning |
|:--|:--|:--|
| `🚨 CRASH BUY` | `>= 6` | Extreme panic |
| `🟢 STRONG BUY` | `>= 5` | High-conviction buy setup |
| `🟡 BUY DIP` | `>= min_score_buy` and `< 5` | Weaker buy setup |
| `⏸ NEUTRAL` | Between buy/sell zones | No directional edge |
| `🟠 SELL/HEDGE` | `<= -2` and `> -5` | Hedge / trim risk |
| `🔴 STRONG SELL` | `<= -5` and `> -6` | Strong sell setup |
| `🔥 EUPHORIA` | `<= -6` | Extreme greed |

### Filtered States

These are display states, not separate score formulas:

| State | Why It Appears |
|:--|:--|
| `✋ WAIT (Vol)` | Buy score is high enough, but volatility regime is too risky |
| `✋ WAIT (Mom)` | Buy score is high enough, but momentum confirmation failed |
| `✋ WAIT (Core)` | Buy score is high enough, but no core panic confirmation is present |
| `☕ HOLD (Vol)` | Sell score is low enough, but volatility regime does not justify selling |
| `✋ HOLD (Mom)` | Sell score is low enough, but momentum confirmation failed |
| `✋ HOLD (Core)` | Sell score is low enough, but no core euphoria confirmation is present |
| `🚫 NO TRADE` | Buy-side setup is filtered by bear trend when trend filter is enabled |

### Sell Strictness

Sell-side behavior now has two explicit modes:

- `Balanced (Legacy)`: preserves the previous sell / hedge filtering
- `High Win-Rate`: requires core euphoria confirmation for `🔴 STRONG SELL` and `🟠 SELL/HEDGE`

Core euphoria confirmation is satisfied when at least one of these is true:

- basis is calm
- put/call ratio is calm
- elevated SKEW
- contango above `10%`
- optional VVIX is calm

### Confirmation Layers

There are two separate ideas in the script:

- `Confirmed Signals Only`: controls whether displayed chart signals wait for bar close
- `Alert Timing Mode`: controls whether smart alerts are preview-style or confirmation-style

They are intentionally treated as separate controls.

### Statistics Model

Rolling statistics are intentionally limited to exact `1D` charts.

- non-`1D` charts display `1D ONLY` instead of win-rate numbers
- only confirmed final buy and sell signals are counted
- only evaluated samples are counted in `N`
- buy-side wins use `Ref > 0`
- sell-side wins use `Ref <= 0`
- sell-side average return stays raw; more negative is better for top / hedge calls
- `Wxx%` is the fixed-horizon win rate for completed samples
- stats lookback is capped at `19` years because `19*252 + 60 = 4848`, which stays inside the `5000`-bar execution / buffer budget

## Smart Alerts

### Default Behavior

Default settings:

- `Smart Alert = ON`
- `Alert Timing Mode = Confirmed Daily Structure`
- `After-Hours Alert Policy = Allow if source confirms`
- `Alert Frequency = Real-time`

This default means:

- confirmed alerts are based on the previous completed structure day and emit once on the next regular-session opportunity
- preview alerts try to fire as early as possible
- the alert message tells you which mode produced the alert

### Alert Timing Modes

| Mode | Meaning |
|:--|:--|
| `Confirmed Daily Structure` | Snapshot one completed structure day and emit once on the next regular-session opportunity |
| `Preview / Earliest Possible` | Preserve earliest-possible behavior for intraday previews |

If `VIX Timeframe = Chart` in preview mode:

- only VIX follows the chart timeframe
- other structure inputs can still remain daily
- dashboard label `PREVIEW*` means this hybrid mode is active

### After-Hours Policy

| Policy | Behavior |
|:--|:--|
| `Allow if source confirms` | Preview mode may still alert after the close if inputs update late |
| `Regular Session Only` | Preview alerts are blocked outside the exchange-defined regular session, even if the chart shows extended hours |

For extended-hours `1m` charts, preview-mode non-regular-session edges now also consume the same-day side latch. That prevents the same side and same level from replaying every minute outside regular hours.
The latch and cooldown bookkeeping use rollback-safe `varip` state so realtime updates cannot undo already-sent alert state.

### Why Confirmed No Longer Fires After The Close

`Confirmed Daily Structure` now waits for one completed structure day and then emits once during the next regular session. It no longer uses after-hours `1m` bars to keep re-evaluating the same daily transition.

The score depends on daily external sources such as:

- `CBOE:VIX`
- `CBOE:VX1!`
- `CBOE:VX2!`
- `CBOE:SKEW`
- `INDEX:CPCI`
- optional `CBOE:VVIX`

Those feeds do not always finalize at the exact same time as the chart close. That timing still matters for preview alerts, but confirmed alerts now consume the completed structure day and wait for the next regular-session bar instead of replaying across after-hours `1m` bars.

TradingView alerts run from a server-side snapshot of the script and its inputs. After changing alert timing or after-hours policy, delete and recreate the alert so the server picks up the new logic.

### Alert Message Format

```text
Symbol: [Side] [Timing] [Level][Upgrade] -> [Triggered Labels] | [Context]

SPY: 🟢 BUY [CONFIRMED] [Lv2] -> 🟢STRONG | Score:5.2 Z:-2.1 VIX:19(NORM) | Confirmed
QQQ: 🟢 BUY [PREVIEW] [Lv1] -> 🟡DIP | Score:4.0 Z:-1.8 VIX:28(HIGH) | Hybrid preview daily+chart
```

Alert state machine behavior:

- level-based priority (`Lv1` to `Lv3`)
- intrabar dedup with `varip`
- cross-bar upgrade detection in preview mode
- preview-mode side latch: same-side same-level alerts emit at most once per chart day, only strict level upgrades can re-emit
- preview-mode extended-session edges also consume that same-day latch, preventing after-hours `1m` replay spam
- rollback-safe `varip` state keeps side-latch/cooldown/send bookkeeping stable across realtime-bar updates
- confirmed-mode snapshot and single emit per structure day
- adaptive cooldown measured in chart bars for preview mode

## Dashboard and Plotting

### Mobile Mode

Two rows:

| Row | Content |
|:--|:--|
| 1 | Current signal + score |
| 2 | Alert mode + VIX display |

### Full Mode

Sixteen rows:

| Section | Content |
|:--|:--|
| Header | Indicator title + safe/preview mode |
| Signal | Current signal + score bar |
| Market | SPX / NDX / RUT trend, VIX regime, alert mode, volume |
| Structure | Term structure Z + contango |
| Stats | `1D`-only evaluated sample counts, win rate, and average returns for both buy and sell tiers |

### Visual Elements

The script can display:

- term structure Z-Score
- scaled SKEW line
- smart volume columns
- `🚨` / `🟢` / `🟡` / `🔥` / `🔴` / `🟠` labels on the chart
- dark dashboard with grouped sections

## Key Configuration Groups

### Data Sources

- `Trading Safe Mode`
- `VIX Symbol`
- `VIX Timeframe`
- `Put/Call Ratio Symbol`
- `Manual Trend Source`

### Strategy Mode

- signal sensitivity: `High`, `Normal`, `Low`
- sell signal strictness: `Balanced (Legacy)` or `High Win-Rate`
- market trend filter
- auto-detect index
- trend MA mode: `Fixed`, `Adaptive`, `KAMA`

### Signal Confirmation

- chart-signal bar-close confirmation
- momentum confirmation
- weekly MTF confirmation
- signal display cooldown

### Statistics and Alerts

- rolling stats lookback (`1-19Y`, `1D` stats only)
- return periods reused by matching buy / sell tiers
- smart alert timing mode
- after-hours policy
- alert cooldown base
- alert frequency

### Advanced

- VIX regime thresholds
- adaptive percentile thresholds
- adaptive Z-score lookbacks
- SKEW mode
- volume average length
- optional VVIX thresholds

## Recommended Usage

### Conservative Daily Workflow

Recommended for most users:

- chart: `SPY`, `QQQ`, or `IWM`
- timeframe: daily
- use an exact `1D` chart if you want win-rate stats
- `Trading Safe Mode = ON`
- `Alert Timing Mode = Confirmed Daily Structure`
- `Sell Signal Strictness = High Win-Rate` if you want fewer, cleaner top signals
- `Use Momentum Confirmation = ON`
- `Use Weekly MTF Confirmation = OFF` or ON only if you want stricter filtering

### Intraday Preview Workflow

Recommended only if you understand hybrid timing:

- chart: `SPY` / `QQQ`
- timeframe: `15m` or `1h`
- `VIX Timeframe = Chart`
- `Alert Timing Mode = Preview / Earliest Possible`
- add `Regular Session Only` if you want no post-close alerts, including extended-hours `1m` bars

## Validation Workflow

There is no local Pine compiler in this repository.

Validation must be done in TradingView:

1. Paste `vix.pine` into the Pine Editor.
2. Confirm the script compiles with no syntax errors.
3. Apply it to `SPY`, `QQQ`, and `IWM`.
4. Check dashboard layout in both `Full` and `Mobile`.
5. Verify signal labels, trend filter behavior, buy/sell `1D` stats output, and stats reference alignment.
6. Test smart alerts with:
   - `Confirmed Daily Structure`
   - `Preview / Earliest Possible`
   - `Regular Session Only`
   - recreate the TradingView alert after each input change that affects timing/session behavior
7. Switch `Sell Signal Strictness` between `Balanced (Legacy)` and `High Win-Rate` and confirm `✋ HOLD (Core)` appears when expected.
8. On an intraday ETF chart, verify `Confirmed Daily Structure` emits at most once for the same completed structure day and does not repeat across after-hours `1m` bars.
9. In preview mode, verify `Regular Session Only` still blocks after-hours alerts on extended-hours `1m` bars.
10. In preview mode with `Allow if source confirms` on extended-hours `1m`, verify same-side same-level alerts do not repeat within one chart day; only `Lv1 -> Lv2 -> Lv3` upgrades can emit again.

## Current Highlights

- sell-side strictness mode supports cleaner high-win-rate top signals
- core euphoria confirmation can gate sell signals with `✋ HOLD (Core)`
- exact `1D` charts include rolling buy-side and sell-side statistics
- sell plots, alerts, and stats all use the final filtered sell signals
- confirmed alerts now snapshot one structure day and emit once during the next regular session
- `Regular Session Only` still keys off the exchange regular session for preview alerts
- preview alerts now latch same-side same-level sends per chart day and only re-emit on strict upgrades

## Limitations

- Pine can only be truly validated on TradingView.
- External daily sources may update later than the chart close.
- `VIX Timeframe = Chart` does not make the whole model intraday; it only changes the VIX leg.
- Statistics are rolling and reference-index based, not a full broker-grade backtest.
- Win-rate statistics are intentionally `1D`-only.

## License

MIT License

## Disclaimer

This project is for research and educational use. It is not financial advice.

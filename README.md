# VIX Term Structure Pro v7.14

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
- Indicator title: `VIX Term Structure Pro [v7.14]`
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
| `tests/` | Python regression models and Pine source-wiring checks; not a Pine compiler |

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

Every required structure input and enabled factor must have valid data and sufficient history. Until that gate is satisfied, `Score` is unavailable (`N/A`) and no signal is produced; missing values are not treated as neutral factor contributions. Disabled optional VVIX or MTF does not block readiness. Smart volume values and their contribution come from the same daily payload as `Score`.

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

- Exact tickers `QQQ`, `QQQM`, `TQQQ`, `SQQQ`, `QLD`, `QID`, `NDX`, and futures with root `NQ` or `MNQ` use `NASDAQ:NDX`
- Exact tickers `IWM`, `UWM`, `TWM`, `TNA`, `TZA`, `RUT`, and futures with root `RTY` or `M2K` use `TVC:RUT`
- Everything else uses `SP:SPX`

Matching uses exact ETF/index names and futures roots, not arbitrary substrings: `CNQ`, for example, stays with `SP:SPX`.

## Signal Model

### Signal Tiers

| Signal | Score Zone | Meaning |
|:--|:--|:--|
| `🚨 CRASH BUY` | `>= 6` | Extreme panic |
| `🟢 STRONG BUY` | `>= 5` and `< 6` | Strong buy setup |
| `🟡 BUY DIP` | `>= min_score_buy` and `< 5` | Weaker buy setup |
| `⏸ NEUTRAL` | Between buy/sell zones | No directional edge |
| `🟠 SELL/HEDGE` | `<= -2` and `> -5` | Hedge / trim risk |
| `🔴 STRONG SELL` | `<= -5` and `> -6` | Strong sell setup |
| `🔥 EUPHORIA` | `<= -6` | Extreme greed |

### Filtered States

These are display states, not separate score formulas:

| State | Why It Appears |
|:--|:--|
| `DATA N/A / 数据不足` | Required structure data or factor warmup is incomplete; all signals are blocked |
| `WAIT Vol/波动` | Buy score is high enough, but volatility regime is too risky |
| `WAIT Mom/动量` | Buy score is high enough, but momentum confirmation failed |
| `WAIT Z/结构` | BUY DIP score is high enough, but Z has not passed its panic threshold |
| `WAIT Core/核心` | Buy score is high enough, but no core panic confirmation is present |
| `WAIT Trend / 趋势缺失` | BUY DIP requires trend filtering, but the selected trend reference is unavailable |
| `HOLD Vol/波动` | Sell score is low enough, but volatility regime does not justify selling |
| `HOLD Mom/动量` | Sell score is low enough, but momentum confirmation failed |
| `HOLD Core/核心` | Sell score is low enough, but no core euphoria confirmation is present |
| `🚫 NO TRADE` | Buy-side setup is filtered by bear trend when trend filter is enabled |

Dashboard setup reasons and signal eligibility share the same gates. Missing trend data appears grey/unknown rather than bullish. BUY DIP display cooldown is consumed only by a final eligible signal, so a filtered setup does not suppress the next valid crossing.

A dashboard setup label describes the current eligible score zone. A new chart marker additionally requires a fresh threshold crossing and any applicable display cooldown; the score tooltip explains this distinction.

### Sell Strictness

Sell-side behavior now has two explicit modes:

- `Balanced (Legacy)`: preserves the previous sell / hedge filtering
- `High Win-Rate`: requires core euphoria confirmation for `🔴 STRONG SELL` and `🟠 SELL/HEDGE`

`High Win-Rate` is the preserved option name, not an empirical promise of higher returns or win rate.

Core euphoria confirmation is satisfied when at least one of these is true:

- basis is calm
- put/call ratio is calm
- elevated SKEW
- contango above `10%`
- optional VVIX is calm

### Confirmation Layers

There are three timing controls:

- `Trading Safe Mode = ON` prevents historical future leakage. It still reads developing higher-timeframe values in the live path, so those values can change and repaint after reload. OFF permits historical preview values that were not yet available at that time.
- `Confirmed Signals Only = ON`: on intraday charts, displayed `Score`, Z and chart signals use the previous completed daily structure snapshot. On `1D` and higher charts, signals wait for chart-bar close. OFF retains the developing daily chart path.
- `Alert Timing Mode` separately chooses the smart-alert data and timing: preview or completed daily structure.

Defaults and input option strings are preserved in v7.14: Safe Mode is ON, `Confirmed Signals Only` is OFF, and alert timing is `Confirmed Daily Structure`. Keep Safe Mode ON when using weekly MTF; the nested-request calendar caveats below still apply.

### Statistics Model

Rolling statistics require an exact `1D` chart whose exchange timezone is `America/New_York` and whose symbol type is stock, fund or index. Futures, crypto, forex, other timeframes and other exchange timezones do not show win-rate statistics.

- unsupported charts display a timeframe/calendar notice instead of win-rate numbers
- only confirmed final buy and sell signals are counted
- `N` counts only samples whose holding-period exit bar has closed and whose entry/exit reference prices are valid and strictly positive
- the selected reference identity remains fixed across both endpoints; an unavailable manual reference does not fall back to SPX
- the window is based on signal entry dates over the last `lookback years * 252` chart trading days; each holding period uses an evaluation window of `lookback bars - hold bars`
- tiers with zero evaluated samples display `N/A`, not a misleading `0%` win rate
- buy-side wins use `Ref > 0`
- sell-side wins use `Ref <= 0`
- sell-side average return stays raw; more negative is better for top / hedge calls
- `Wxx%` is the fixed-horizon win rate for completed samples
- stats lookback remains capped at `19` years within the `5000`-bar execution / buffer budget; readiness counts actually executed, closed bars

## Smart Alerts

### Default Behavior

Default settings:

- `Smart Alert = ON`
- `Alert Timing Mode = Confirmed Daily Structure`
- `After-Hours Alert Policy = Allow if source confirms`
- `Alert Frequency = Real-time`

This default means:

- on intraday charts, confirmed alerts use the previous completed structure day and can emit on the first regular-session bar, including when the chart has premarket bars
- on `1D` and higher charts, confirmed alerts retain same-bar-close timing
- preview alerts try to fire as early as possible
- the alert message tells you which mode produced the alert

### Alert Timing Modes

| Mode | Meaning |
|:--|:--|
| `Confirmed Daily Structure` | Intraday: previous completed structure day, once at the first eligible regular-session bar; `1D` and higher: chart-bar close |
| `Preview / Earliest Possible` | Preserve earliest-possible behavior for intraday previews |

If `VIX Timeframe = Chart` in preview mode:

- only the VIX display, the live VIX regime gates, the adaptive trend-MA length selection (and thus the live trend filter), and the adaptive alert cooldown follow the chart timeframe
- the score and its structure inputs are always evaluated on daily data (since v7.13)
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
Symbol: [Side] [Timing] [Level][Upgrade] → [Triggered Labels] | [Context] [Trend] | [Mode]

SPY: 🟢 BUY [CONFIRMED] [Lv2] → 🟢STRONG | Score:5.2 Z:-2.1 VIX:19(NORM) 🟢SPX 🟢NDX 🔴RUT | Confirmed
QQQ: 🟢 BUY [PREVIEW] [Lv1] → 🟡DIP | Score:4.0 Z:-1.8 VIX:20(NORM) 🟢SPX 🟢NDX 🔴RUT | Hybrid preview hybrid daily+chart
```

Alert state machine behavior:

- level-based priority (`Lv1` to `Lv3`)
- intrabar dedup with `varip`
- cross-bar upgrade detection in preview mode
- preview-mode side latch: same-side same-level alerts emit at most once per chart day, only strict level upgrades can re-emit
- preview-mode extended-session edges also consume that same-day latch, preventing after-hours `1m` replay spam
- rollback-safe `varip` state keeps side-latch/cooldown/send bookkeeping stable across realtime-bar updates
- `Once Per Bar` uses one explicit shared dispatch quota for both sides; a blocked second call is observed but does not falsely advance actual-send cooldown bookkeeping
- confirmed-mode snapshot and single emit per structure day
- adaptive cooldown measured in chart bars for preview mode
- signals blocked by cooldown or session policy are discarded, never deferred or re-sent

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
| Header | Indicator title + `CLOSED D / 已完成`, `LIVE D / 发展中`, or `⚠️PREVIEW / 预览` |
| Signal | Current signal + score bar |
| Market | SPX / NDX / RUT trend, VIX regime, alert mode, volume |
| Structure | Term structure Z + contango |
| Stats | Evaluated sample counts, win rate and average returns for both sides on eligible `1D` charts |

The score cell tooltip shows factor contributions, selected source and the structure date behind the displayed score. The date identifies the calculation period, not a provider update timestamp. Full remains sixteen rows. Mobile remains two rows with its existing alert-mode row; its score tooltip identifies the selected score source.

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

- completed-day intraday chart signals, or chart-close confirmation on `1D` and higher
- momentum confirmation
- weekly MTF confirmation
- signal display cooldown

### Statistics and Alerts

- rolling stats lookback (`1-19Y`, eligible New York stock/fund/index `1D` charts only)
- return periods reused by matching buy / sell tiers
- smart alert timing mode
- after-hours policy
- alert cooldown base
- alert frequency

### Advanced

- VIX regime thresholds
- adaptive percentile thresholds
- adaptive Z-score lookbacks
- vol regime hysteresis band for Z lookback switching
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
- `Sell Signal Strictness = High Win-Rate` to require core euphoria confirmation on the two lower sell tiers
- `Use Momentum Confirmation = ON`
- `Use Weekly MTF Confirmation = OFF` or ON only if you want stricter filtering

### Intraday Preview Workflow

Recommended only if you understand hybrid timing:

- chart: `SPY` / `QQQ`
- timeframe: `15m` or `1h`
- `VIX Timeframe = Chart`
- `Confirmed Signals Only = OFF` for developing chart previews; ON selects completed-day chart signals while smart alert timing remains separately selectable
- `Alert Timing Mode = Preview / Earliest Possible`
- add `Regular Session Only` if you want no post-close alerts, including extended-hours `1m` bars

## Validation Workflow

There is no local Pine compiler in this repository. Run the standard-library regression suite from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

These tests check numerical/state-transition models and Pine source wiring. They do not execute Pine, compile TradingView requests, measure performance, or prove live session behavior. TradingView validation remains required:

| Check | TradingView procedure and expected result |
|:--|:--|
| Compile and request budget | Paste `vix.pine` into Pine Editor; load on `1m`, `30m` and `1D`. Repeat with VVIX on/off, weekly MTF on/off and distinct custom VIX/PCR/manual trend sources. Check nested expanded request usage stays within the applicable plan limit; the compatibility target is 40. |
| Completed chart path | On SPY/QQQ/IWM intraday charts, turn `Confirmed Signals Only` ON and compare Score/Z/signals before and after reload. Check the tooltip's completed structure date. On `1D`, signals still wait for close. |
| Developing chart path | Turn confirmed chart signals OFF and compare Safe Mode ON/OFF; developing HTF values may change, and OFF historical previews may use future values. |
| First regular-session alert | Compare regular-only and extended-hours `1m`/`30m` ETF charts. Confirmed alerts may emit on the first eligible regular bar without waiting an extra chart bar, then remain deduplicated for that structure day. |
| Preview dispatch | Exercise both frequency options, both session policies, repeated ticks and opposite-side events in one bar. Verify Once Per Bar sends at most one message and blocked events do not create false actual-send cooldowns or deferred messages. |
| Data and setup gates | Test unavailable custom sources, insufficient history, missing trend data and both sell strictness modes. Verify Score unavailable/no signals, grey unknown trends, and the appropriate WAIT/HOLD reason. A filtered BUY DIP must not consume display cooldown. |
| Statistics | On eligible `1D` stock/fund/index charts check completed exits, positive valid endpoints, entry-date window boundaries and zero-sample `N/A`. Confirm unsupported calendars/timeframes hide statistics and a missing manual reference never mixes SPX into a return. |
| Routing | Check QQQ/QQQM, IWM, NQ/MNQ, RTY/M2K and `CNQ`; compare the trend/statistics reference against the documented exact routing. |
| Visual consistency | Check Full/Mobile, score factor/date tooltips, daily volume and plots. Use a recently listed symbol and a crypto chart to inspect structure warmup independently of chart age; crypto statistics remain unavailable. |

Delete and recreate TradingView alerts after changing script code or inputs so the server-side snapshot is refreshed. The procedures above are a validation checklist, not a claim that TradingView compilation or live alert tests have passed.

## What's New in v7.14

- **Explicit confirmation semantics**: intraday confirmed chart signals, Score and Z use completed daily snapshots; Safe Mode now clearly describes historical future-leak protection and the remaining developing-HTF repaint behavior. Smart-alert timing stays separately selected.
- **Data readiness and consistent reasons**: required factors and enabled optional factors must be ready; unavailable structure data produces no signal. Missing trend data blocks filtered BUY DIP and shows unknown status. Setup reasons include Z and trend-data gates, and filtered BUY DIP no longer consumes display cooldown.
- **Daily factor inspection**: volume and score share their daily payload, while existing score-cell tooltips expose factor contributions and structure dates without adding rows or claiming a provider update time.
- **Alert dispatch correction**: confirmed alerts can emit on the first regular-session bar of an extended-hours chart. Once Per Bar explicitly tracks its shared send quota instead of recording silently throttled calls as sent; discarded-event semantics are preserved.
- **Statistics eligibility and accounting**: statistics require eligible New York stock/fund/index `1D` charts, valid positive endpoints, one reference identity and closed exits. Windows use signal entry dates; empty tiers display `N/A`.
- **Exact symbol routing and regression checks**: explicit ETF/index names and futures roots prevent substring false matches such as `CNQ`. Standard-library tests cover numerical/state behavior and source wiring; TradingView compilation and realtime verification remain separate requirements. Defaults and input option strings are preserved.

## What's New in v7.13

- **Timeframe-independent score**: `Score` and its gating factors (Z-Score, momentum, core confirmations, weekly MTF alignment) are now evaluated in the `SP:SPX` daily context through a `request.security()` tuple. Intraday charts read the same daily values as a `1D` chart. With `Trading Safe Mode = ON`, historical bars use completed trading days and the realtime bar tracks the developing day; with safe mode OFF, historical intraday bars show same-day final values (repaint semantics as in v7.12; the values themselves are now daily-context). Charts above `1D` sample one daily value per chart bar. Note that `1D` charts off the US trading calendar and recently listed tickers now read SPX-grid values that differ from v7.12 — see Known Limitations.
- **Consistent confirmed-alert anchor**: on intraday charts, the confirmed structure-day id and the full confirmed snapshot (score, Z, VIX, SKEW, regime, trend, momentum and core gates — including the trend-filter gate on `BUY DIP`) now come from a dedicated completed-structure-day source using a per-element `[1]` offset with hardcoded `lookahead_on`. Live and historical bars see identical completed-day data, and in the default configuration the confirmed path no longer depends on the `Trading Safe Mode` toggle (see Known Limitations for the weekly-MTF and 24-hour-symbol caveats). `1D` and higher charts keep the previous same-bar-close behavior.
- **Adaptive Z lookback hysteresis**: new `Vol Regime Hysteresis Band` input (Advanced group, default `0.0` = v7.12 behavior, suggested experiment value `2.0`). VIX must rise above `threshold + band` to switch to the high-vol lookback and fall back to `threshold - band` or below to switch back, preventing lookback flip-flop when VIX hovers near the threshold.
- **Cooldown semantics clarified**: signals blocked by the alert cooldown or session policy are discarded, never deferred or re-sent later. The halved high-vol cooldown is now floored at `1` bar, so `Alert Cooldown Base = 1` can no longer truncate to a zero cooldown.
- **Dead code cleanup**: removed the unused `spx_day_id` request and the legacy `lookahead_off` confirmed anchor; the structure-day id is now a single shared expression reused by the daily-context requests and the chart-day id.

## Current Highlights

- sell-side strictness mode supports stricter top-signal filtering
- core euphoria confirmation can gate sell signals with `HOLD Core/核心`
- eligible New York stock/fund/index `1D` charts include rolling buy-side and sell-side statistics
- chart plots and stats use final chart events; Preview alerts consume those events, while Confirmed alerts apply the shared setup gates to independent daily transitions
- confirmed alerts now snapshot one structure day and emit once during the next regular session
- the score and its gates are evaluated in the `SP:SPX` daily context, so intraday charts match `1D` score semantics
- confirmed alerts consume a completed-structure-day snapshot that is identical on live and historical bars
- `Regular Session Only` still keys off the exchange regular session for preview alerts
- preview alerts now latch same-side same-level sends per chart day and only re-emit on strict upgrades

## Known Limitations

- Pine can only be truly validated on TradingView.
- External daily sources may update later than the chart close.
- Safe Mode alone does not freeze developing daily values. Completed intraday chart signals require `Confirmed Signals Only = ON`; chart-signal confirmation and smart-alert timing are separate.
- `VIX Timeframe = Chart` does not make the whole model intraday; since v7.13 it only affects the dashboard VIX display, the live VIX regime gates, the adaptive trend-MA length selection (and thus the live trend filter), and the adaptive alert cooldown — the score itself is always computed on daily structure data.
- The score is evaluated on the `SP:SPX` daily grid. On `1D` charts off the US trading calendar (crypto, forex) the rolling windows no longer include weekend bars, and on recently listed tickers the warmup comes from decades of SPX history, so those charts read different (intentionally improved) score values than v7.12.
- Confirmed-path independence from `Trading Safe Mode` holds for the default configuration. With `Use Weekly MTF Confirmation` enabled, the weekly MTF leg samples its daily inputs inside a weekly context, so the toggle still changes which day of the completed week is sampled (ON = last daily bar / Friday, OFF = first / Monday) and can shift the confirmed score by ±1 — keep Safe Mode ON. It also assumes the VIX / Put-Call / manual-trend symbols follow the US equity trading calendar; 24-hour-calendar custom symbols shift the confirmed snapshot by one day between toggle states.
- Statistics are rolling and reference-index based, not a full broker-grade backtest.
- Win-rate statistics require exact `1D`, exchange timezone `America/New_York`, and stock/fund/index type; this is a conservative eligibility rule, not automatic reconciliation of arbitrary trading calendars.
- A custom manual reference can have different trading dates or close times, particularly for 24-hour instruments. Chart eligibility does not align that reference's calendar automatically; choose a reference compatible with the chart's daily session when interpreting its returns.
- `CBOE:VX1!` / `CBOE:VX2!` are continuous futures that switch contracts on roll dates; term structure readings (contango, basis, Z-Score) can spike artificially around the roll.
- Session gating uses the chart exchange's regular-session definition. Futures may treat their extended electronic session as regular; this setting does not impose US equity hours on every symbol.
- Auto-detect recognizes only the listed ETF/index names and futures roots. Unlisted products fall back to SPX; choose a manual reference when needed.

## License

MIT License

## Disclaimer

This project is for research and educational use. It is not financial advice.

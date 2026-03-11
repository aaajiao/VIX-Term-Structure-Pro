# AGENTS.md - VIX Term Structure Pro

> Guidelines for AI agents working in this TradingView Pine Script repository.

## Project Overview

| Attribute | Value |
|-----------|-------|
| **Type** | TradingView Pine Script v6 Indicator |
| **Main File** | `vix.pine` (~989 lines) |
| **Purpose** | Multi-factor VIX term structure analysis with buy/sell signals |
| **Language** | Pine Script (TradingView DSL) |
| **Version** | v7.12 |

## Repository Layout

| Path | Purpose |
|------|---------|
| `vix.pine` | Main indicator source |
| `README.md` | English product overview + changelog |
| `docs/README_CN.md` | 中文说明文档 |
| `chart_guide.png` | Dashboard / chart usage reference |
| `zscore_guide.png` | Z-Score interpretation reference |

## Build / Lint / Test Commands

**No local toolchain.** Pine Script compiles only on TradingView.

```bash
# No build/lint/test commands - all validation on TradingView
git add vix.pine && git commit -m "feat(v7.x): English / 中文"
```

### Validation Workflow

1. **Syntax**: Paste into TradingView Pine Editor → check for errors
2. **Visual**: Apply to chart → verify dashboard + signals render
3. **Backtest**: Use TradingView's built-in strategy tester

### Current v7.12 Reality Check

- `vix.pine` is currently ~989 lines
- Header is `indicator("VIX Term Structure Pro [v7.12]", ...)`
- README and Chinese docs are already aligned to `v7.12`
- No local compiler/test runner exists in this repo

## Code Style Guidelines

### Pine Script Version & Header

```pine
//@version=6
indicator("VIX Term Structure Pro [vX.X]", overlay=false, max_lines_count=500, calc_bars_count=1000)
```

### File Structure (Canonical Order)

```pine
// ========== 1. 函数定义 (Function Definitions) ==========
// ========== 2. 参数设置 (Input Parameters) ==========
// ========== 3. 数据获取 (Data Fetching) ==========
// ========== 4. 核心计算 (Core Calculations) ==========
// ========== 5. 信号逻辑 (Signal Logic) ==========
// ========== 6. 统计计算 (Statistics) ==========
// ========== 7. 绘图 (Plotting) ==========
// ========== 8. 仪表盘 (Dashboard) ==========
// ========== 9. 警报系统 (Alert System) ==========
```

### Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Variables | `snake_case` | `vix_regime`, `contango_pct` |
| Functions | `calc_*`, `f_*` prefix | `calc_z_score_points()`, `f_score_bar()` |
| Input groups | `grp_` prefix | `grp_data`, `grp_strategy` |
| Booleans | `is_*`, `has_*`, `use_*` | `is_high_vol`, `has_buy_signal`, `use_vvix` |
| Colors | `c_*` prefix | `c_header`, `c_buy_bg` |

### Input Parameters

```pine
grp_data = "📡 Data Sources"
trading_safe_mode = input.bool(true, "🛡️ Trading Safe Mode", group=grp_data, 
    tooltip="ON: 实盘安全模式 no repaint\nOFF: 预览模式 Preview mode")
```

### Pure Functions (Preferred Style)

```pine
calc_z_score_points(z_val, mid, strong) =>
    z_val < -strong ? 4 : z_val < -mid ? 2 : z_val > strong ? -4 : z_val > mid ? -2 : 0
```

### request.security() Pattern

**CRITICAL**: Always use `ignore_invalid_symbol=true` and consistent lookahead:

```pine
is_no_repaint_mode = trading_safe_mode or backtest_mode
lookahead_setting = is_no_repaint_mode ? barmerge.lookahead_off : barmerge.lookahead_on

vix = request.security(sym_vix_input, vix_tf, close, 
    lookahead=lookahead_setting, ignore_invalid_symbol=true)
```

For VIX structure components, prefer fixed symbols unless chart-dependence is intentional. Current canonical symbols in this repo include:

- `CBOE:VIX`
- `CBOE:VX1!`
- `CBOE:VX2!`
- `CBOE:SKEW`
- `CBOE:VVIX`
- `SP:SPX`
- `NASDAQ:NDX`
- `TVC:RUT`

### ta.* Functions: No Conditional Calls (CW10003)

`ta.*` functions must execute on **every bar** to maintain consistent history. Never put them inside ternary operators or `if` scopes.

```pine
// ❌ WRONG — ta.* inside ternary, history gaps cause incorrect values
pct_high = has_data ? ta.percentile_linear_interpolation(src, len, 90) : 5.0

// ✅ CORRECT — call every bar, then select
pct_high_raw = ta.percentile_linear_interpolation(src, len, 90)
pct_high = has_data ? pct_high_raw : 5.0
```

Applies to: `ta.sma`, `ta.ema`, `ta.stdev`, `ta.highest`, `ta.lowest`, `ta.percentile_*`, and any `ta.*` that references historical series.

### Multi-line Expressions

Pine Script multi-line continuation is fragile. **Prefer single-line or split into intermediate variables** over relying on indentation-based continuation.

```pine
// ❌ RISKY — multi-line ternary may fail with "end of line without line continuation"
ref = condition_a ? 
      (condition_b ? val_b : val_c) : 
      val_d

// ✅ SAFE — split into intermediate variable
inner = condition_b ? val_b : val_c
ref = condition_a ? inner : val_d
```

### Warmup / History Safety

For percentile, Z-score, regime, or other history-sensitive calculations, compute the raw series every bar and gate usage with warmup checks.

```pine
enough_history = bar_index >= lookback_len
pct_high_raw = ta.percentile_linear_interpolation(src, lookback_len, 90)
pct_high = enough_history ? pct_high_raw : na
```

## Error Handling

```pine
// NA guards - always check before calculation
valid_data = not na(vix) and not na(vx1) and not na(vx2)

// Division safety - check denominator
contango_pct = valid_data and vx1 != 0 ? ((vx2 / vx1) - 1) * 100 : 0.0

// Optional feature guard
calc_vvix_points(vvix_val, use_vvix) =>
    not use_vvix or na(vvix_val) ? 0 : vvix_val > 130 ? 1 : vvix_val < 80 ? -1 : 0
```

## Key Patterns

### Signal State Machine (3-Layer)

```pine
is_buy_raw = score >= threshold and score[1] < threshold  // Layer 1: Raw detection
is_buy = use_confirmed ? (is_buy_raw and barstate.isconfirmed) : is_buy_raw  // Layer 2: Confirmation
final_buy = is_buy and is_trend_ok and is_vol_ok  // Layer 3: Filters
```

### Cooldown Pattern

```pine
var int last_signal_bar = 0
adaptive_cooldown = vix_regime == 3 ? cooldown / 2 : vix_regime == 1 ? cooldown * 2 : cooldown
if signal_triggered and (bar_index - last_signal_bar > adaptive_cooldown)
    last_signal_bar := bar_index
```

### var vs varip

```pine
var int last_alert_bar = 0       // Persists across bars, resets on reload
varip int alert_level_sent = 0   // Resets each new bar (intra-bar dedup)
```

| Keyword | Behavior | Use Case |
|---------|----------|----------|
| `var` | Persists across bars, resets on reload | Cross-bar state (cooldown tracking) |
| `varip` | Resets each new bar | Intra-bar dedup (alert level tracking) |

### Trading Safe Mode (v7.9)

```pine
// Signal calculation: always use lookahead_off for no-repaint
vix = request.security(sym, tf, close, lookahead=lookahead_setting, ignore_invalid_symbol=true)

// Dashboard display only: real-time on last bar
vix_rt = request.security(sym, tf, close, lookahead=barmerge.lookahead_on, ignore_invalid_symbol=true)
vix_display = barstate.islast ? vix_rt : vix
```

### Optional Feature Pattern

Optional inputs may disable a feature's effect, but the surrounding data flow should remain explicit and safe.

```pine
vvix = use_vvix ? request.security("CBOE:VVIX", "D", close, lookahead=lookahead_setting, ignore_invalid_symbol=true) : na
vvix_points = calc_vvix_points(vvix, use_vvix)
```

## Documentation Standards

- **Bilingual**: ALL user-facing text in EN + CN
- **Tooltips**: `tooltip="English\n中文"`
- **Commits**: `type(v7.x): English / 中文` (types: feat | fix | docs | refactor | perf | chore)

## Files to Ignore

`.opencode/`, `.claude/`, `.DS_Store`

## Architecture Principles

### Score = Pure VIX Structure (v7.10)

Score must be an **objective VIX term structure metric**, identical across all chart symbols. Never mix chart-dependent data (trend, symbol detection) into Score.

- **Score factors**: Z-Score, contango, VIX basis, SKEW, PCR, VVIX, volume, momentum, MTF
- **NOT in Score**: trend filter, `is_bull_market`, anything derived from `syminfo.ticker`
- **Trend filter** only affects signal **display** (BUY DIP → NO TRADE), never the Score value

### Cross-Chart Consistency

Avoid `syminfo.tickerid` in `request.security()` unless intentionally chart-dependent. For VIX-derived calculations, use fixed symbols (`"SP:SPX"`, `"CBOE:VIX"`) to ensure identical results across charts.

```pine
// ❌ WRONG — weekly Z differs across QQQ/SPY due to calendar alignment
z_weekly = request.security(syminfo.tickerid, "W", z, ...)

// ✅ CORRECT — fixed symbol, consistent across all charts
z_weekly = request.security("SP:SPX", "W", z, ...)
```

`syminfo.ticker` is fine for: auto-detect logic, alert message text, display labels.

### Stats Reference Alignment

If signal filtering uses auto-detected index context, return statistics should use the same reference family:

- QQQ / NDX / NQ charts → `NASDAQ:NDX`
- IWM / RUT / RTY charts → `TVC:RUT`
- Everything else → `SP:SPX`

## Hard Constraints

1. **No Repainting** - Default `lookahead_off` for live trading safety
2. **No Breaking Changes** - Maintain backward compat for existing users
3. **Bilingual Always** - EN/CN for all user-visible strings
4. **Manual Git** - Never auto-commit; user reviews all changes
5. **No Type Coercion** - Pine Script is strongly typed; fix properly

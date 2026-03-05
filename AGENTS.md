# AGENTS.md - VIX Term Structure Pro

> Guidelines for AI agents working in this TradingView Pine Script repository.

## Project Overview

| Attribute | Value |
|-----------|-------|
| **Type** | TradingView Pine Script v6 Indicator |
| **Main File** | `vix.pine` (~825 lines) |
| **Purpose** | Multi-factor VIX term structure analysis with buy/sell signals |
| **Language** | Pine Script (TradingView DSL) |
| **Version** | v7.10 |

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

## Documentation Standards

- **Bilingual**: ALL user-facing text in EN + CN
- **Tooltips**: `tooltip="English\n中文"`
- **Commits**: `type(v7.x): English / 中文` (types: feat | fix | docs | refactor | perf | chore)

## Files to Ignore

`.opencode/`, `.claude/`, `.DS_Store`

## Hard Constraints

1. **No Repainting** - Default `lookahead_off` for live trading safety
2. **No Breaking Changes** - Maintain backward compat for existing users
3. **Bilingual Always** - EN/CN for all user-visible strings
4. **Manual Git** - Never auto-commit; user reviews all changes
5. **No Type Coercion** - Pine Script is strongly typed; fix properly

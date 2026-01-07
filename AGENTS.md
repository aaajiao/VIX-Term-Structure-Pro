# AGENTS.md - VIX Term Structure Pro

> Guidelines for AI agents working in this TradingView Pine Script repository.

## Project Overview

- **Type**: TradingView Pine Script v6 Indicator
- **Main File**: `vix.pine` (~807 lines)
- **Purpose**: Multi-factor VIX term structure analysis with buy/sell signals
- **Language**: Pine Script (domain-specific language for TradingView)

## Build / Lint / Test Commands

### No Traditional Build System

This is a Pine Script project. There is **no local build, lint, or test system**.

```bash
# Pine Script has no local toolchain
# All validation happens on TradingView platform
```

### Validation Workflow

1. **Syntax Check**: Copy code to TradingView Pine Editor, check for compilation errors
2. **Visual Test**: Apply indicator to chart, verify signals and dashboard render correctly
3. **Backtest**: Use TradingView's built-in backtesting for signal validation

### Git Workflow

```bash
git add vix.pine
git commit -m "feat(v7.x): Description in English / 中文描述"
git push origin <branch-name>
```

## Code Style Guidelines

### Pine Script Version

Always use Pine Script v6:
```pine
//@version=6
indicator("Indicator Name [vX.X]", overlay=false)
```

### File Structure

Follow this canonical section order:
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

| Type | Convention | Example |
|------|------------|---------|
| Variables | `snake_case` | `vix_regime`, `is_bull_market` |
| Functions | `snake_case` with prefix | `calc_z_score_points()`, `f_score_bar()` |
| Input groups | `grp_` prefix | `grp_data`, `grp_strategy` |
| Boolean vars | `is_` or `has_` prefix | `is_high_vol`, `has_buy_signal` |

### Input Parameter Style

```pine
grp_name = "Group Title"
param = input.bool(true, "Display Name", group=grp_name, 
    tooltip="English description\n中文描述")
```

### Function Definition Style

```pine
// Modular scoring functions - pure functions preferred
calc_z_score_points(z_val, mid, strong) =>
    z_val < -strong ? 4 : z_val < -mid ? 2 : z_val > strong ? -4 : z_val > mid ? -2 : 0
```

### Request.Security Pattern

Always use consistent lookahead settings:
```pine
lookahead_setting = is_no_repaint_mode ? barmerge.lookahead_off : barmerge.lookahead_on
vix = request.security(sym_vix_input, vix_tf, close, 
    lookahead=lookahead_setting, ignore_invalid_symbol=true)
```

## Error Handling

### Invalid Symbol Handling
Always use `ignore_invalid_symbol=true` in `request.security()`.

### NA Value Checks
```pine
valid_data = not na(vix) and not na(vx1) and not na(vx2)
calc_vvix_points(vvix_val, use_vvix) =>
    not use_vvix or na(vvix_val) ? 0 : vvix_val > 130 ? 1 : vvix_val < 80 ? -1 : 0
```

### Division Safety
```pine
contango_pct = valid_data and vx1 != 0 ? ((vx2 / vx1) - 1) * 100 : 0.0
```

## Documentation Standards

- **Bilingual**: All content must be in English AND Chinese
- **Changelog**: Version history with emoji categories (see `.agent/workflows/update-readme.md`)

### Commit Message Format
```
type(scope): English description / 中文描述
Types: feat, fix, docs, refactor, perf, chore
```

## Important Patterns

### Signal State Machine
```pine
is_buy_raw = score >= threshold and score[1] < threshold  // Raw detection
is_buy = use_confirmed ? (is_buy_raw and barstate.isconfirmed) : is_buy_raw  // Confirmation
final_buy = is_buy and is_trend_ok and is_vol_ok  // Filter layer
```

### Cooldown Pattern
```pine
var int last_signal_bar = 0
if signal_triggered and (bar_index - last_signal_bar > cooldown)
    last_signal_bar := bar_index
```

### varip vs var
```pine
var int last_alert_bar = 0       // Persists across bars, resets on reload
varip int alert_level_sent = 0   // Resets each new bar
```

## Files to Ignore

- `.claude/` - OpenCode session data
- `.DS_Store` - macOS metadata

## Key Constraints

1. **No Breaking Changes**: Maintain backward compatibility for existing users
2. **No Repainting**: Default to `lookahead_off` for trading safety
3. **Bilingual Always**: All user-facing text must have EN/CN versions
4. **Manual Git**: Never auto-commit; user reviews all changes first

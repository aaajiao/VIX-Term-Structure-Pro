# VIX Term Structure Pro v7.1 Enhanced

[![TradingView](https://img.shields.io/badge/TradingView-Indicator-blue?logo=tradingview)](https://www.tradingview.com/)
[![Pine Script](https://img.shields.io/badge/Pine%20Script-v5-brightgreen)](https://www.tradingview.com/pine-script-docs/en/v5/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Professional VIX-based Market Sentiment & Timing Indicator**

专业的 VIX 市场情绪与择时指标

---

## 🌟 Overview / 概述

VIX Term Structure Pro is an advanced multi-factor market timing indicator that combines VIX futures term structure analysis, adaptive volatility regime detection, and comprehensive market breadth monitoring to generate high-precision buy/sell signals.

VIX Term Structure Pro 是一款高级多因子市场择时指标，结合 VIX 期货期限结构分析、自适应波动率区间检测和全面的市场广度监控，生成高精度的买卖信号。

---

## 🚀 Key Features / 核心功能

### 📊 Multi-Factor Scoring System / 多因子评分系统
- **Adaptive Term Structure Z-Score**: Auto-adjusts lookback based on volatility regime / 自适应期限结构 Z 分数：根据波动率区间自动调整回望期
- **VIX/VX1 Basis with Adaptive Thresholds**: Percentile-based panic detection / VIX 现货溢价：基于百分位数的恐慌检测
- **Contango Analysis**: Futures curve shape insights / 期货升水分析：期货曲线形态洞察
- **Multi-Mode SKEW Integration**: Relative Z-Score, Percentile, or Absolute threshold modes / 多模式 SKEW 整合：相对 Z 分数、百分位数或绝对阈值模式
- **Put/Call Ratio**: Adaptive sentiment extremes detection / 看跌/看涨比率：自适应情绪极端检测
- **Smart Volume**: Normalized visualization with spike detection / 智能成交量：归一化可视化与激增检测
- **VVIX Support**: Volatility of volatility (optional) / VVIX 支持：波动率的波动率（可选）

### 🎯 Three-Tier Signal System / 三级信号系统

| Signal | Score | Description | Return Period |
|--------|-------|-------------|---------------|
| 🚨 **CRASH BUY** | ≥ 6 | Extreme panic, rare opportunity / 极端恐慌，罕见机会 | 40 days (~2 months) |
| 🟢 **STRONG BUY** | ≥ 5 | Multi-factor confluence / 多因子共振 | 20 days (~1 month) |
| 🟡 **BUY DIP** | ≥ 4 | Accumulate on weakness / 逢低吸纳 | 10 days (~2 weeks) |
| 🟠 **SELL/HEDGE** | ≤ -2 | Consider reducing risk / 考虑减仓对冲 | - |
| 🔴 **STRONG SELL** | ≤ -5 | Strong bearish signals / 强烈看跌信号 | - |
| 🔥 **EUPHORIA SELL** | ≤ -6 | Extreme greed, sell signal / 极度贪婪，卖出信号 | - |

### 🎨 Signal Confirmation / 信号确认机制

#### Momentum Confirmation / 动量确认
- **Z-Score Momentum**: Tracks rate of change in Z-Score with neutral zone filtering / Z 分数动量：追踪 Z 分数变化率，带中性区域过滤
- **Configurable Lookback**: Adjustable momentum period (1-10 bars) / 可配置回望期：可调节动量周期（1-10 根 K 线）
- **Neutral Zone**: Filters noise to avoid false signals / 中性区域：过滤噪音，避免虚假信号

#### Multi-Timeframe (MTF) Confirmation / 多时间框架确认
- **Weekly Z-Score Alignment**: Requires weekly timeframe confirmation for strongest signals / 周线 Z 分数对齐：最强信号需要周线时间框架确认
- **Optional Toggle**: Can be enabled/disabled based on trading style / 可选开关：基于交易风格可启用/禁用

### 📈 Dashboard Indicators / 仪表盘指标解读

#### Compact Mode (8 rows)
1. **Overall Bias**: Current signal recommendation
2. **AI Score**: Composite scoring (-10 to +10 scale)
3. **Market Trend**: Triple index status (SPX/NDX/RUT vs MA200)
4. **VIX Regime**: LOW VOL (<15) / NORMAL / HIGH VOL (>25)
5. **Term Struct Z**: Normalized Z-Score value
6. **Vol Status**: Smart volume spike detection
7. **Z Momentum**: Directional momentum indicator
8. **Signal Stats**: Historical signal count (🚨:N 🟢:N 🟡:N)

#### Full Mode (12-16 rows)
Includes all Compact mode data plus:
9. **Avg Return**: Split by signal tier (🚨40D / 🟢20D / 🟡10D)
10. **VIX Basis**: VIX spot premium percentage
11. **Contango %**: VX1/VX2 term structure slope
12. **SKEW Index**: Current SKEW value with color coding
13. **VVIX** (if enabled): Volatility of VIX
14. **Put/Call (Idx)**: Index put-call ratio

---

## ⚙️ Configuration / 配置选项

### 📡 Data Sources / 数据源
- **VIX Symbol**: Default `CBOE:VIX` (Alternative: `TVC:VIX`)
- **VIX Timeframe**: Daily (stable) or Chart (real-time) / 日线（稳定）或图表（实时）
- **Put/Call Ratio**: Default `INDEX:CPCI` (Index P/C), Alternative: `INDEX:PCC` (Equity P/C)
- **Manual Trend Source**: Custom symbol for trend detection when Auto-Detect is OFF

### ⚠️ Strategy Mode / 策略模式

| Mode | Sensitivity | Z Thresholds | Min Buy Score | Use Case |
|------|-------------|--------------|---------------|----------|
| **High (Scalping)** | Most sensitive | ±1.0 / ±2.0 | 2 | Short-term trades / 短线交易 |
| **Normal (Swing)** | Balanced | ±1.2 / ±2.2 | 3 | Swing trading / 波段交易 |
| **Low (Trend/Safe)** | Conservative | ±1.5 / ±2.5 | 4 | Position trading / 趋势跟踪 |

### 🛡️ Market Trend Filter / 市场趋势过滤

#### Trend MA Mode / 趋势均线模式 (v7.1 新增)

| Mode | 原理 | 优点 | 适用场景 |
|------|------|------|----------|
| **Fixed** | 固定长度 SMA/EMA | 简单直接，用户完全控制 | 偏好经典技术分析 |
| **Adaptive** (默认) | 根据 VIX 水平动态切换均线长度 | 与项目 VIX 为中心的设计一致 | 波动率驱动型交易 |
| **KAMA** | Kaufman 自适应均线，根据价格效率调整 | 对趋势反转反应更快 | 短线交易、注重价格行为 |

- **When ON**: Disables 🟡 BUY DIP signals when primary index is below trend MA
- **CRASH/STRONG BUY**: Always allowed regardless of trend (extreme panic overrides)
- **Auto-Detect Index**: Automatically selects primary index based on chart symbol
  - QQQ/NQ/NDX charts → NDX as primary
  - IWM/RUT/RTY charts → RUT as primary
  - Others → SPX as primary

### 🎯 Signal Confirmation / 信号确认
- **🔒 Confirmed Signals Only** (v7.1 新增): ON = 信号仅在K线收盘时触发（避免盘中频闪）
- **Momentum Confirmation**: Requires Z-Score momentum alignment (optional)
- **Momentum Lookback**: Default 3 bars, adjustable 1-10
- **Neutral Zone**: Default 0.05, filters minor fluctuations
- **Weekly MTF Confirmation**: Requires weekly Z-Score alignment (optional)

### 🎨 Chart Style / 图表样式
- **Show Term Struct Z-Score**: Main Z-Score line visibility
- **Show Scaled SKEW Line**: SKEW visualization (scaled to Z-Score range)
- **Show Smart Volume**: Normalized volume columns with spike highlighting
- **±1 Line Color/Style**: Customizable mid-threshold reference lines

### 📋 Dashboard / 仪表盘
- **Dashboard Mode**: Compact (8 rows) or Full (12-16 rows)
- **Dashboard Position** (v7.1 新增): Top Right / Top Left / Bottom Right / Bottom Left / Top Center / Bottom Center
- **Text Size**: Small / Normal / Large
- **Transparency**: 0-100% background transparency

### 📊 Statistics & Alerts / 统计与警报
- **Signal Statistics**: Historical signal count display (optional)
- **📈 Show Max Profit Stats** (v7.1 新增): 显示N天内最高收益（默认关闭，增加计算复杂度）
- **Stats Lookback**: 1-20 years (default 3 years)
- **Return Periods**: Configurable for each signal tier (🚨40D / 🟢20D / 🟡10D)
- **Alert Cooldown**: Minimum bars between alerts (1-20, default 5)

### ⚙️ Advanced Settings / 高级设置

#### VIX Regime Thresholds
- **Low Vol Threshold**: Default 15.0 (range: 10-20)
- **High Vol Threshold**: Default 25.0 (range: 20-40)

#### Adaptive Thresholds
- **Use Adaptive Thresholds**: Percentile-based dynamic thresholds vs fixed values
- **Adaptive Lookback**: Default 252 bars (1 year), range: 50-500

#### Z-Score Calculation
- **Use Adaptive Lookback**: Shorter lookback in high-vol periods (recommended)
- **Lookback (Low Vol)**: Default 252 bars, range: 50+
- **Lookback (High Vol)**: Default 126 bars, range: 20+
- **Vol Regime Threshold**: Default 20.0

#### SKEW Settings
- **SKEW Logic Mode**:
  - `Relative (Z-Score)`: Normalized deviation from mean (default)
  - `Percentile (Adaptive)`: Uses 90th/10th percentiles
  - `Absolute (>140)`: Fixed threshold at 140
- **SKEW Lookback Period**: Default 126 bars

#### Volume Settings
- **Volume Avg Length**: Default 20 bars for moving average

### 📈 VVIX Integration (Optional)
- **Enable VVIX**: Toggle VVIX data integration
- **VVIX Threshold Mode** (v7.1 新增):

| Mode | 原理 | 优点 | 适用场景 |
|------|------|------|----------|
| **Fixed** | 固定阈值 130/80 | 简单直观 | 市场环境稳定时 |
| **Percentile** | 使用90/10分位数 | 对极端值不敏感，不假设正态分布 | 担心极端事件污染数据时 |
| **Z-Score** (默认) | 使用±2标准差 | 与项目其他逻辑一致 | 推荐默认使用 |

- **Z-Score Threshold**: Default 2.0 (range: 1.0-3.0)
- **Fixed Panic/Calm Threshold**: Default 130.0/80.0 (only used in Fixed mode)

### 🔬 Backtest Mode / 回测模式
- **OFF (Real-time)**: Uses `lookahead_on` for current day data / 使用 lookahead_on 获取当日数据
- **ON (Historical)**: Uses `lookahead_off` to avoid future bias / 使用 lookahead_off 避免未来函数

> ⚠️ **v7.1 新增**: Live Mode 下仪表盘底部会显示“⚠️ Live Mode - Historical Repaints”警告，提醒用户历史信号可能重绘。

---

## 📖 Usage Guide / 使用指南

### Best Practices / 最佳实践

1. **Apply to major index daily charts** (SPX, SPY, QQQ, IWM) for optimal signal accuracy
   
   在主要指数日线图上使用（SPX、SPY、QQQ、IWM），信号准确度最佳

2. **Wait for daily close** before acting on signals (signals trigger on bar close)
   
   等待日线收盘后再执行信号（信号在 K 线收盘时触发）

3. **Use Strategy Mode matching your timeframe**:
   - High: For day trading VIX products
   - Normal: For swing trading SPX/QQQ
   - Low: For position building in retirement accounts
   
   使用与您的时间框架匹配的策略模式

4. **Enable Trend Filter for capital preservation** in bear markets
   
   在熊市中开启趋势过滤以保护资本

5. **Review Signal Stats** in Full dashboard mode to calibrate expectations
   
   在完整仪表盘模式中查看信号统计以校准预期

### Signal Interpretation / 信号解读

```
🚨 CRASH BUY (Score ≥ 6)
   → Extreme multi-factor panic (VIX spike + basis panic + deep Z-Score)
   → Historical: Occurs 1-3 times per year during market crashes
   → Action: Aggressive entry, high conviction
   → Return Period: 40 days (~2 months)

🟢 STRONG BUY (Score ≥ 5)
   → Multiple fear indicators align
   → Historical: Occurs 5-10 times per year
   → Action: Build positions, medium conviction
   → Return Period: 20 days (~1 month)

🟡 BUY DIP (Score ≥ 4)
   → Moderate fear detected
   → Filtered out in bear markets if Trend Filter is ON
   → Action: Add to existing positions, lower conviction
   → Return Period: 10 days (~2 weeks)

🔴 SELL/HEDGE Signals (Score ≤ -2)
   → Complacency or greed detected
   → Consider reducing exposure or hedging
   → Not as reliable as buy signals (VIX mean-reverts asymmetrically)
```

### Chart Elements / 图表元素

- **Z-Score Line**: Red (fear) to Blue (complacency) gradient
- **±1 / ±2.5 Lines**: Configurable threshold references
- **Smart Volume Columns**: 
  - Gray: Normal volume
  - Aqua: High volume (>1.5x average)
  - Yellow: Panic spike (>2.5x average)
- **Signal Labels**: Bottom (buy) and top (sell) emoji markers

---

## 📊 Historical Statistics / 历史统计

### Statistics Calculation
- **Lookback Range**: User-defined (1-20 years, default 3)
- **Signal Count**: Shows frequency of each signal tier within range
- **Average Returns**: Calculated using SPX forward returns
  - 🚨 CRASH: 40-day forward return
  - 🟢 STRONG: 20-day forward return
  - 🟡 DIP: 10-day forward return

### Return Display (Full Mode Only)
```
Avg Return Row 1: 🚨40D:+X.X% 🟢20D:+X.X%
Avg Return Row 2: 🟡10D:+X.X%
```

指标追踪信号频率和后续平均收益，可在仪表盘中查看历史统计。

---

## 🔔 Alerts / 警报

### Built-in Alert Conditions

| Alert | Trigger | Message Format |
|-------|---------|----------------|
| 🚨 Crash Buy Alert | Score ≥ 6 | Includes Score, Z-Score, VIX Basis |
| 🟢 Strong Buy Alert | Score ≥ 5 | Includes Score, Z-Score, Contango |
| 🟡 Buy Dip Alert | Score ≥ threshold | Includes Score, Z-Score, VIX Basis |
| 🔥 Euphoria Sell Alert | Score ≤ -6 | Includes Score, Z-Score, SKEW |
| 🔴 Strong Sell Alert | Score ≤ -5 | Includes Score, Z-Score |
| 🔥 VIX Basis Panic | VIX spot premium spike | Basis panic detection |

### Alert Cooldown Mechanism
- **Default**: 5 bars between alerts
- **Purpose**: Prevents spam from overlapping signals
- **Configurable**: 1-20 bars in settings

---

## 🧮 Scoring Algorithm / 评分算法

### Modular Scoring Functions

```pinescript
Total Score = 
  + Z-Score Points (-4 to +4)
  + Contango Points (-1 to +2)
  + Basis Points (-1 to +2)
  + SKEW Points (-3 to +1)
  + P/C Ratio Points (-2 to +2)
  + VVIX Points (-1 to +1, if enabled)
  + Volume Spike Bonus (+1 if extreme volume + fear)
  + Momentum Bonus (±1 if enabled and aligned)
  + MTF Bonus (±1 if enabled and weekly aligned)
  - Trend Penalty (-2 if bear market and filter ON)
```

### Point Allocation Details

**Z-Score** (adaptive thresholds based on strategy mode):
- < -2.5: +4 (extreme fear)
- < -1.5: +2 (moderate fear)
- > +2.5: -4 (extreme complacency)
- > +1.5: -2 (moderate complacency)

**Contango**:
- < 0% (backwardation): +2
- > 10%: -1

**VIX Basis** (adaptive or fixed):
- Panic level: +2
- Calm level: -1

**SKEW** (mode-dependent):
- High tail risk: -3
- Low tail risk: +1

**Put/Call Ratio** (adaptive):
- > 1.20: +2 (extreme fear)
- < 0.70: -2 (extreme greed)

---

## 📋 Changelog / 更新日志

### v7.1 Enhanced (Current)
- 🛡️ **自适应趋势过滤器**: 支持 Fixed/Adaptive/KAMA 三种模式
- 🔒 **信号确认机制**: 默认仅在K线收盘时触发信号，避免盘中频闪
- 📈 **VVIX 自适应阈值**: 支持 Fixed/Percentile/Z-Score 三种模式
- 📈 **Max Profit Stats**: 可选显示N天内最高收益（默认关闭）
- 📍 **仪表盘位置自定义**: 6种位置选项
- ⚠️ **重绘警告**: Live Mode 下显示历史信号可能重绘的警告
- 📝 **详细对比 Tooltip**: 各模式选项附带详细对比说明

### v7.0 Enhanced
- ✨ Three-tier buy/sell signal system with filtered execution
- 📊 Signal statistics with average return tracking (by tier)
- 🎯 Advanced signal confirmation (Momentum + MTF weekly)
- 🔬 Backtest Mode toggle (lookahead control)
- 🎨 Configurable ±1 Z-Score reference lines (color + style)
- ⚡ Modular scoring functions for transparency
- 🛡️ Triple index trend display (SPX + NDX + RUT)
- 🔍 Auto-detect chart symbol (SPY/QQQ/IWM) for primary trend
- 📱 Compact & Full dashboard modes with return statistics
- 🧮 Adaptive thresholds (percentile-based VIX Basis & P/C)
- 🎚️ Multi-mode SKEW (Relative / Percentile / Absolute)
- 📊 Smart Volume visualization with normalized scaling
- 🔔 Alert cooldown mechanism (prevents spam)
- 🌊 Z-Score momentum tracking with neutral zone

---

## ⚠️ Disclaimer / 免责声明

**English:**
This indicator is for educational and informational purposes only. It does not constitute financial advice. Past performance does not guarantee future results. Always do your own research and consider your risk tolerance before trading.

**中文：**
本指标仅供教育和信息参考，不构成投资建议。过往表现不代表未来收益。交易前请自行研究并评估风险承受能力。

---

## 📄 License / 许可证

MIT License - Feel free to use, modify, and share.

---

## 🤝 Contributing / 贡献

Issues and pull requests are welcome!

欢迎提交问题和贡献代码！

---

**Made with ❤️ for the trading community**

**为交易社区用心打造**

# VIX Term Structure Pro v7.0

[![TradingView](https://img.shields.io/badge/TradingView-Indicator-blue?logo=tradingview)](https://www.tradingview.com/)
[![Pine Script](https://img.shields.io/badge/Pine%20Script-v5-brightgreen)](https://www.tradingview.com/pine-script-docs/en/v5/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Professional VIX-based Market Sentiment & Timing Indicator**

专业的 VIX 市场情绪与择时指标

---

## 🌟 Overview / 概述

VIX Term Structure Pro is an advanced multi-factor market timing indicator that analyzes the VIX futures term structure, volatility regime, and market breadth to generate actionable buy/sell signals.

VIX Term Structure Pro 是一款高级多因子市场择时指标，通过分析 VIX 期货期限结构、波动率区间及市场广度，生成可操作的买卖信号。

---

## 🚀 Key Features / 核心功能

### 📊 Multi-Factor Scoring System / 多因子评分系统
- **Term Structure Z-Score**: Measures deviation from historical mean / 期限结构 Z 分数：衡量与历史均值的偏离
- **VIX/VX1 Basis**: Spot premium detection for panic signals / VIX 现货溢价：恐慌信号检测
- **Contango Analysis**: Futures curve shape insights / 期货升水分析
- **SKEW Integration**: Options skew for tail risk / SKEW 整合：尾部风险监测
- **Put/Call Ratio**: Sentiment extremes / 看跌/看涨比率：情绪极端
- **VVIX Support**: Volatility of volatility (optional) / VVIX 支持：波动率的波动率

### 🎯 Three-Tier Signal System / 三级信号系统

| Signal | Score | Description |
|--------|-------|-------------|
| 🚨 **CRASH BUY** | ≥ 6 | Extreme panic, rare opportunity / 极端恐慌，罕见机会 |
| 🟢 **STRONG BUY** | ≥ 5 | Multi-factor confluence / 多因子共振 |
| 🟡 **BUY DIP** | ≥ 4 | Accumulate on weakness / 逢低吸纳 |
| 🟠 **SELL/HEDGE** | ≤ -2 | Consider reducing risk / 考虑减仓对冲 |
| 🔴 **STRONG SELL** | ≤ -5 | Strong bearish signals / 强烈看跌信号 |
| 🔥 **EUPHORIA SELL** | ≤ -6 | Extreme greed, sell signal / 极度贪婪，卖出信号 |

### 📈 Dashboard Indicators / 仪表盘指标解读

| Indicator | Bullish 🟢 | Bearish 🔴 |
|-----------|------------|------------|
| Overall Bias | STRONG BUY / BUY DIP | STRONG SELL / SELL/HEDGE |
| AI Score | ≥ 5 (Extreme Fear) | ≤ -5 (Extreme Greed) |
| Market Trend | 🟢SPX 🟢NDX 🟢RUT (Above MA200) | 🔴SPX 🔴NDX 🔴RUT (Below MA200) |
| VIX Regime | LOW VOL (<15) | HIGH VOL (>25) |
| Term Struct Z | < -2.0 (Panic) | > 2.0 (Complacency) |

---

## ⚙️ Configuration / 配置选项

### 📡 Data Sources / 数据源
- **VIX Symbol**: Default `CBOE:VIX` (Alternative: `TVC:VIX`)
- **Put/Call Ratio**: Default `INDEX:CPCI` (Index P/C)
- **Timeframe**: Daily (stable) or Chart (real-time)

### ⚠️ Strategy Mode / 策略模式
- **High (Scalping)**: Sensitive, for short-term trades / 高敏感，短线
- **Normal (Swing)**: Balanced approach / 平衡模式
- **Low (Trend/Safe)**: Conservative, trend-following / 保守，趋势跟踪

### 🔬 Backtest Mode / 回测模式
- **OFF (Real-time)**: Shows current day data, suitable for live monitoring / 显示当日数据，适合实盘监控
- **ON (Historical)**: Uses only confirmed data, avoids look-ahead bias / 仅使用已确认数据，避免未来函数

---

## 📖 Usage Guide / 使用指南

### Best Practices / 最佳实践

1. **Apply to SPX/SPY/QQQ/IWM daily charts** for optimal signal accuracy
   
   在 SPX/SPY/QQQ/IWM 日线图上使用，信号准确度最佳

2. **Wait for next trading day** to execute signals (signals trigger on daily close)
   
   信号触发后在下一交易日执行（信号基于日线收盘）

3. **Use in conjunction with price action** for confirmation
   
   结合价格走势确认信号

4. **Enable Market Trend Filter** (MA200) for safer entries in uncertain markets
   
   开启趋势过滤（MA200）以在不确定市场中更安全入场

### Signal Interpretation / 信号解读

```
🚨 CRASH BUY (Score ≥ 6)
   → Rare extreme panic event
   → Historical average return: significant positive over 2 months
   → Consider aggressive positioning

🟢 STRONG BUY (Score ≥ 5)
   → Multiple indicators align
   → Historical average return: positive over 1 month
   → Consider building positions

🟡 BUY DIP (Score ≥ 4)
   → Moderate fear detected
   → Suitable for adding to existing positions
   → Filtered out in bear markets if Trend Filter is ON
```

---

## 📊 Historical Statistics / 历史统计

The indicator tracks signal frequency and average subsequent returns:
- **CRASH BUY**: 40-day return period (~2 months)
- **STRONG BUY**: 20-day return period (~1 month)
- **BUY DIP**: 10-day return period (~2 weeks)

指标追踪信号频率和后续平均收益，可在仪表盘中查看历史统计。

---

## 🔔 Alerts / 警报

Built-in alert conditions with cooldown mechanism to prevent spam:

| Alert | Condition |
|-------|-----------|
| Crash Buy Alert | Score ≥ 6, extreme panic |
| Strong Buy Alert | Score ≥ 5, multi-factor confluence |
| Buy Dip Alert | Score ≥ threshold |
| Euphoria Sell Alert | Score ≤ -6, extreme greed |
| Strong Sell Alert | Score ≤ -5 |
| VIX Basis Panic | VIX spot premium spike |

---

## 📋 Changelog / 更新日志

### v7.0 (Current)
- ✨ Three-tier buy/sell signal system
- 📊 Signal statistics with average return tracking
- 🔬 Backtest Mode toggle for historical testing
- 🎨 Configurable ±1 Z-Score reference lines
- ⚡ Modular scoring functions
- 🛡️ Triple index trend display (SPX + NDX + RUT / Russell 2000)
- 🔍 Auto-detect chart symbol (SPY/QQQ/IWM) for primary trend
- 📱 Compact & Full dashboard modes

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

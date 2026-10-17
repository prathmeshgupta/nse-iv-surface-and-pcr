# NSE Implied Volatility Surface & Put-Call Ratio (PCR) Dataset

[![Weekly Update](https://github.com/prathmeshgupta/nse-iv-surface-and-pcr/actions/workflows/update.yml/badge.svg)](https://github.com/prathmeshgupta/nse-iv-surface-and-pcr/actions/workflows/update.yml)
[![Format: Parquet](https://img.shields.io/badge/Format-Apache%20Parquet-blue.svg)](output/)
[![Format: CSV](https://img.shields.io/badge/Format-CSV-green.svg)](output/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An institutional quantitative dataset capturing historical **India VIX volatility dynamics**, rolling percentiles, moving averages, volatility regime classification, and exchange-wide derivative **Put-Call Ratios (PCR)**.

---

## Tables in this Repository

### 1. `output/india_vix_history.parquet` / `.csv` (Daily Historical VIX)

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `trade_date` | `string` | ISO-8601 Date (`YYYY-MM-DD`) |
| `vix_open` | `float64` | India VIX opening value |
| `vix_high` | `float64` | India VIX intraday high |
| `vix_low` | `float64` | India VIX intraday low |
| `vix_close` | `float64` | India VIX closing value |
| `vix_change_pct` | `float64` | Daily percentage change in VIX |
| `vix_ma20` | `float64` | 20-trading-day simple moving average |
| `vix_ma50` | `float64` | 50-trading-day simple moving average |
| `vix_percentile_1y` | `float64` | 252-day rolling percentile rank (0 to 100%) |
| `volatility_regime` | `string` | Classification: `EXTREME_COMPLACENCY`, `NORMAL_VOLATILITY`, `ELEVATED_RISK`, `HIGH_PANIC` |
| `source` | `string` | Data source (`NSE_INDIA_VIX`) |

### 2. `output/market_pcr_dynamics.parquet` / `.csv` (Exchange Derivative Sentiment)

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `trade_date` | `string` | ISO-8601 Date (`YYYY-MM-DD`) |
| `total_put_oi` | `int64` | Total open interest in Put options (Index + Stock) |
| `total_call_oi` | `int64` | Total open interest in Call options (Index + Stock) |
| `market_pcr_oi` | `float64` | Overall Market Put-Call Ratio ($\frac{\text{Put OI}}{\text{Call OI}}$) |
| `index_pcr_oi` | `float64` | Index options Put-Call Ratio |
| `stock_pcr_oi` | `float64` | Single stock options Put-Call Ratio |
| `fii_index_pcr` | `float64` | Foreign Institutional Investor Index Put-Call Ratio |
| `sentiment_bias` | `string` | Derivative positioning bias (`BULLISH_SUPPORT` vs `BEARISH_RESISTANCE`) |
| `source` | `string` | Data source (`NSE_PARTICIPANT_DERIVATIVES`) |

---

## Quick Start (Python)

```python
import polars as pl

# Read India VIX historical dynamics
url = "https://github.com/prathmeshgupta/nse-iv-surface-and-pcr/raw/main/output/india_vix_history.parquet"
df_vix = pl.read_parquet(url)

# Filter for elevated volatility regimes
high_vol_days = df_vix.filter(pl.col("volatility_regime").is_in(["ELEVATED_RISK", "HIGH_PANIC"]))
print(high_vol_days.select(["trade_date", "vix_close", "vix_percentile_1y", "volatility_regime"]))
```

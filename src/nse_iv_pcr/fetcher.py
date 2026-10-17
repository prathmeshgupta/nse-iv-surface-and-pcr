import datetime
import pandas as pd
import numpy as np
import yfinance as yf
from pathlib import Path
from typing import Optional, Tuple


class VolatilityPCRFetcher:
    """
    Fetches official daily India VIX dynamics and calculates exchange-wide Put-Call Ratios.
    """

    def fetch_india_vix(self, period: str = "5y") -> pd.DataFrame:
        """
        Fetches historical daily India VIX from yfinance (^INDIAVIX).
        Enriches with moving averages, percentile rank, and volatility regime.
        """
        ticker = yf.Ticker("^INDIAVIX")
        raw = ticker.history(period=period)
        if raw.empty:
            return pd.DataFrame()

        df = raw.reset_index()
        df["trade_date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

        clean = pd.DataFrame()
        clean["trade_date"] = df["trade_date"]
        clean["vix_open"] = df["Open"].round(2)
        clean["vix_high"] = df["High"].round(2)
        clean["vix_low"] = df["Low"].round(2)
        clean["vix_close"] = df["Close"].round(2)
        clean["vix_change_pct"] = (clean["vix_close"].pct_change() * 100).round(2).fillna(0.0)

        # Quantitative Enriched Features
        clean["vix_ma20"] = clean["vix_close"].rolling(20, min_periods=1).mean().round(2)
        clean["vix_ma50"] = clean["vix_close"].rolling(50, min_periods=1).mean().round(2)

        # 252-day rolling percentile rank
        def rolling_percentile(window):
            if len(window) < 2:
                return 50.0
            val = window.iloc[-1]
            return float((window < val).mean() * 100)

        clean["vix_percentile_1y"] = (
            clean["vix_close"]
            .rolling(252, min_periods=1)
            .apply(rolling_percentile, raw=False)
            .round(1)
        )

        # Volatility Regime Classification
        def classify_regime(val):
            if val < 12.0:
                return "EXTREME_COMPLACENCY"
            elif val < 17.0:
                return "NORMAL_VOLATILITY"
            elif val < 23.0:
                return "ELEVATED_RISK"
            else:
                return "HIGH_PANIC"

        clean["volatility_regime"] = clean["vix_close"].apply(classify_regime)
        clean["source"] = "NSE_INDIA_VIX"

        clean = clean.sort_values("trade_date", ascending=False).reset_index(drop=True)
        return clean

    def compute_pcr(self, participant_oi_path: Optional[Path] = None) -> pd.DataFrame:
        """
        Computes exchange-wide Put-Call Ratios from participant open interest.
        """
        if participant_oi_path is None:
            # Default location in sibling repo
            candidate = Path(__file__).resolve().parents[3] / "nse-participant-open-interest" / "output" / "participant_oi.parquet"
            if candidate.exists():
                participant_oi_path = candidate

        if not participant_oi_path or not participant_oi_path.exists():
            return pd.DataFrame()

        df_poi = pd.read_parquet(participant_oi_path)
        grouped = df_poi.groupby("trade_date")

        rows = []
        for dt, g in grouped:
            idx_call = g["option_index_call_long"].sum()
            idx_put = g["option_index_put_long"].sum()
            stk_call = g["option_stock_call_long"].sum()
            stk_put = g["option_stock_put_long"].sum()

            tot_call = idx_call + stk_call
            tot_put = idx_put + stk_put

            fii = g[g["client_type"] == "FII"]
            fii_pcr = round(fii["option_index_put_long"].sum() / max(1, fii["option_index_call_long"].sum()), 3) if not fii.empty else 1.0

            rows.append({
                "trade_date": dt,
                "total_put_oi": int(tot_put),
                "total_call_oi": int(tot_call),
                "market_pcr_oi": round(tot_put / max(1, tot_call), 3),
                "index_pcr_oi": round(idx_put / max(1, idx_call), 3),
                "stock_pcr_oi": round(stk_put / max(1, stk_call), 3),
                "fii_index_pcr": fii_pcr,
                "sentiment_bias": "BULLISH_SUPPORT" if (tot_put / max(1, tot_call)) > 1.0 else "BEARISH_RESISTANCE",
                "source": "NSE_PARTICIPANT_DERIVATIVES"
            })

        df_pcr = pd.DataFrame(rows).sort_values("trade_date", ascending=False).reset_index(drop=True)
        return df_pcr

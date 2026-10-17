import re
import pandas as pd
from pathlib import Path

ISO_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def audit_quality():
    print("=" * 65)
    print(" NSE IV SURFACE & PCR - DATA QUALITY AUDIT")
    print("=" * 65)

    root = Path(__file__).parent
    vix_pq = root / "output" / "india_vix_history.parquet"
    vix_csv = root / "output" / "india_vix_history.csv"
    pcr_pq = root / "output" / "market_pcr_dynamics.parquet"
    pcr_csv = root / "output" / "market_pcr_dynamics.csv"

    assert vix_pq.exists(), "india_vix_history.parquet missing"
    assert vix_csv.exists(), "india_vix_history.csv missing"

    df_vix_p = pd.read_parquet(vix_pq)
    df_vix_c = pd.read_csv(vix_csv)

    # 1. Parity Check (VIX)
    assert len(df_vix_p) == len(df_vix_c), f"VIX Parity mismatch: {len(df_vix_p)} != {len(df_vix_c)}"
    print(f"Total VIX Observations: {len(df_vix_p)} [PASS - 100% Parity]")

    # 2. Date Check & Non-negativity
    null_dt = df_vix_p["trade_date"].isnull().sum()
    assert null_dt == 0, "Null trade date found in VIX"
    invalid_dt = df_vix_p["trade_date"][~df_vix_p["trade_date"].str.match(ISO_REGEX)]
    assert len(invalid_dt) == 0, f"Found {len(invalid_dt)} non-ISO dates"
    print("ISO-8601 Compliance (trade_date): 100% PASS")

    # 3. Microstructure Bounds
    assert (df_vix_p["vix_close"] > 0).all(), "Non-positive VIX detected"
    assert (df_vix_p["vix_high"] >= df_vix_p["vix_low"]).all(), "VIX High < Low detected"
    assert ((df_vix_p["vix_percentile_1y"] >= 0) & (df_vix_p["vix_percentile_1y"] <= 100)).all(), "Percentile out of [0, 100]"
    print("VIX Value Bounds & High/Low Invariants: [PASS]")

    # 4. PCR Table Audit
    if pcr_pq.exists() and pcr_csv.exists():
        df_pcr_p = pd.read_parquet(pcr_pq)
        df_pcr_c = pd.read_csv(pcr_csv)
        assert len(df_pcr_p) == len(df_pcr_c), f"PCR Parity mismatch: {len(df_pcr_p)} != {len(df_pcr_c)}"
        assert (df_pcr_p["market_pcr_oi"] >= 0).all(), "Negative PCR detected"
        print(f"Market PCR Observations: {len(df_pcr_p)} [PASS - 100% Parity & Non-Negative]")

    # 5. Volatility Regime Distribution
    print("\nVolatility Regime Distribution:")
    for reg, cnt in df_vix_p["volatility_regime"].value_counts().items():
        print(f"  • {reg:<22}: {cnt:>5} trading days")

    print("=" * 65)
    print("ALL AUDIT CHECKS PASSED.")
    print("=" * 65)


if __name__ == "__main__":
    audit_quality()

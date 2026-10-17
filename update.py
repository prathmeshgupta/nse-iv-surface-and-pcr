"""
Automated Weekly Dataset Updater for nse-iv-surface-and-pcr
Can be executed locally or via GitHub Actions.
Zero credentials required.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd
from nse_iv_pcr.fetcher import VolatilityPCRFetcher

OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VIX_CSV = OUTPUT_DIR / "india_vix_history.csv"
VIX_PARQUET = OUTPUT_DIR / "india_vix_history.parquet"
PCR_CSV = OUTPUT_DIR / "market_pcr_dynamics.csv"
PCR_PARQUET = OUTPUT_DIR / "market_pcr_dynamics.parquet"


def update():
    print("[1/3] Fetching historical India VIX dynamics from Yahoo Finance...")
    fetcher = VolatilityPCRFetcher()
    vix_df = fetcher.fetch_india_vix(period="5y")
    print(f"      Retrieved {len(vix_df)} trading days of India VIX.")

    if not vix_df.empty:
        vix_df.to_csv(VIX_CSV, index=False)
        vix_df.to_parquet(VIX_PARQUET, index=False)
        print(f"      Saved {len(vix_df)} records to {VIX_CSV.name} and {VIX_PARQUET.name}.")

    print("[2/3] Calculating derivative market Put-Call Ratios...")
    pcr_df = fetcher.compute_pcr()
    if not pcr_df.empty:
        pcr_df.to_csv(PCR_CSV, index=False)
        pcr_df.to_parquet(PCR_PARQUET, index=False)
        print(f"      Saved {len(pcr_df)} PCR records to {PCR_CSV.name} and {PCR_PARQUET.name}.")

    print("[3/3] Running automated quality audit...")
    from evaluate_quality import audit_quality
    audit_quality()
    print("Update complete successfully.")


if __name__ == "__main__":
    update()

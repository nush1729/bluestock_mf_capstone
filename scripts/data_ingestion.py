#!/usr/bin/env python3
"""
Bluestock Mutual Fund Analytics — Data Ingestion Script (Day 1 Task 3)
=====================================================================
Loads all 10 raw CSV datasets using pandas and prints shape, dtypes, and head.

Usage:
    python scripts/data_ingestion.py
"""

import os
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

# List of the 10 datasets
DATASETS = [
    "01_fund_master.csv",
    "02_nav_history.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "07_scheme_performance.csv",
    "08_investor_transactions.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv"
]

def ingest_and_profile():
    print("=" * 70)
    print("BLUESTOCK MUTUAL FUND ANALYTICS — DATA INGESTION PROFILE")
    print("=" * 70)
    
    if not RAW_DATA_DIR.exists():
        print(f"Error: Raw data directory {RAW_DATA_DIR} does not exist.")
        return

    for filename in DATASETS:
        file_path = RAW_DATA_DIR / filename
        if not file_path.exists():
            # Fallback to legacy datasets directory if raw not synced yet
            legacy_path = PROJECT_ROOT / "datasets" / filename
            if legacy_path.exists():
                file_path = legacy_path
            else:
                print(f"Warning: File {filename} not found in raw data or legacy datasets.")
                continue

        print(f"\n[Loading Dataset: {filename}]")
        print("-" * 50)
        try:
            df = pd.read_csv(file_path)
            
            # Print Shape
            print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
            
            # Print Dtypes
            print("\nData Types:")
            print(df.dtypes.to_string())
            
            # Print Head
            print("\nFirst 3 rows:")
            print(df.head(3).to_string(index=False))
            print("=" * 70)
            
        except Exception as e:
            print(f"Error loading {filename}: {e}")

if __name__ == "__main__":
    ingest_and_profile()

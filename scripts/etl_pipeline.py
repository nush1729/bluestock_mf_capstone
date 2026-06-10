#!/usr/bin/env python3
"""
Bluestock Mutual Fund Analytics — Master ETL Pipeline
======================================================
Automated Extract-Transform-Load pipeline that:
  1. Reads all 10 CSV datasets dynamically
  2. Validates, cleans, and transforms data
  3. Saves cleaned data to data/processed/
  4. Creates and loads SQLite database at data/db/bluestock_mf.db

Usage:
    python scripts/etl_pipeline.py

Author: Bluestock Fintech Analytics Team
"""

import logging
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
LEGACY_DATA_DIR = PROJECT_ROOT / "datasets"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DB_DIR = PROJECT_ROOT / "data" / "db"
SQL_DIR = PROJECT_ROOT / "sql"
DB_PATH = DB_DIR / "bluestock_mf.db"

# Benchmark name mapping: fund_master benchmark → benchmark_indices index_name
BENCHMARK_MAP = {
    "NIFTY 50 TRI": "NIFTY50",
    "NIFTY 100 TRI": "NIFTY100",
    "NIFTY 500 TRI": "NIFTY500",
    "NIFTY Midcap 150 TRI": "NIFTY_MIDCAP150",
    "NIFTY Midcap 50 TRI": "NIFTY_MIDCAP150",
    "NIFTY Large Midcap 250 TRI": "NIFTY500",
    "BSE 250 SmallCap TRI": "BSE_SMALLCAP",
    "CRISIL Liquid Fund AI Index": "CRISIL_LIQUID",
    "CRISIL Short Term Bond Index": "CRISIL_LIQUID",
    "CRISIL Dynamic Gilt Index": "CRISIL_GILT",
}

# ---------------------------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------------------------
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(PROJECT_ROOT / "etl_pipeline.log", mode="w"),
    ],
)
logger = logging.getLogger("BluestockETL")


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------
def ensure_dirs():
    """Create output directories if they don't exist."""
    for d in [PROCESSED_DIR, DB_DIR]:
        d.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory ensured: {d}")


def validate_dataframe(df: pd.DataFrame, name: str, expected_cols: list = None):
    """Validate a DataFrame: check for empty data and expected columns."""
    if df.empty:
        raise ValueError(f"Dataset '{name}' is empty after loading.")
    logger.info(f"  Loaded {name}: {len(df)} rows × {len(df.columns)} cols")

    if expected_cols:
        missing = set(expected_cols) - set(df.columns)
        if missing:
            raise ValueError(f"Dataset '{name}' missing columns: {missing}")

    # Report missing values
    nulls = df.isnull().sum()
    null_cols = nulls[nulls > 0]
    if len(null_cols) > 0:
        logger.warning(f"  Missing values in {name}: {dict(null_cols)}")
    else:
        logger.info(f"  No missing values in {name}")

    # Report duplicates
    dups = df.duplicated().sum()
    if dups > 0:
        logger.warning(f"  {dups} duplicate rows in {name}")
    else:
        logger.info(f"  No duplicates in {name}")


# ===========================================================================
# EXTRACT: Read All CSV Files
# ===========================================================================
def extract_all() -> dict:
    """Read all 10 CSV files from the raw data directory."""
    logger.info("=" * 60)
    logger.info("PHASE 1: EXTRACT — Reading raw CSV files")
    logger.info("=" * 60)

    source_dir = RAW_DATA_DIR
    csv_files = sorted(source_dir.glob("[0-9][0-9]_*.csv"))
    if not csv_files and LEGACY_DATA_DIR.exists():
        source_dir = LEGACY_DATA_DIR
        csv_files = sorted(source_dir.glob("[0-9][0-9]_*.csv"))
    if len(csv_files) == 0:
        raise FileNotFoundError(f"No source CSV files found in {RAW_DATA_DIR} or {LEGACY_DATA_DIR}")

    logger.info(f"Found {len(csv_files)} source CSV files in {source_dir}")

    datasets = {}
    for fp in csv_files:
        try:
            df = pd.read_csv(fp)
            key = fp.stem  # e.g., '01_fund_master'
            datasets[key] = df
            validate_dataframe(df, key)
        except Exception as e:
            logger.error(f"Failed to read {fp.name}: {e}")
            raise

    return datasets


# ===========================================================================
# TRANSFORM: Clean and Enrich Data
# ===========================================================================
def transform_fund_master(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and transform fund master data."""
    logger.info("  Transforming: fund_master")
    df = df.copy()
    df["launch_date"] = pd.to_datetime(df["launch_date"], errors="coerce")
    df["amfi_code"] = df["amfi_code"].astype(int)
    # Add benchmark index mapping
    df["benchmark_index_name"] = df["benchmark"].map(BENCHMARK_MAP)
    return df


def transform_nav_history(df: pd.DataFrame) -> pd.DataFrame:
    """Clean NAV history: parse dates, compute daily returns, forward-fill gaps."""
    logger.info("  Transforming: nav_history")
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amfi_code"] = df["amfi_code"].astype(int)
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    bad_dates = df["date"].isna().sum()
    bad_nav = (df["nav"].isna() | (df["nav"] <= 0)).sum()
    if bad_dates or bad_nav:
        logger.warning(f"  Dropping invalid NAV rows: bad_dates={bad_dates}, bad_nav={bad_nav}")
    df = df.dropna(subset=["date", "nav"])
    df = df[df["nav"] > 0]
    dupes = df.duplicated(subset=["amfi_code", "date"]).sum()
    if dupes:
        logger.warning(f"  Removing {dupes} duplicate NAV rows by amfi_code/date")
    df = df.drop_duplicates(subset=["amfi_code", "date"], keep="last")
    df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)

    # Forward-fill daily gaps so weekends and market holidays have the prior NAV.
    full_frames = []
    for code, grp in df.groupby("amfi_code"):
        all_dates = pd.date_range(grp["date"].min(), grp["date"].max(), freq="D")
        grp = grp.set_index("date").reindex(all_dates)
        grp["amfi_code"] = code
        grp["nav"] = grp["nav"].ffill()
        grp["daily_return_pct"] = grp["nav"].pct_change() * 100
        grp = grp.reset_index().rename(columns={"index": "date"})
        full_frames.append(grp)

    result = pd.concat(full_frames, ignore_index=True)
    result["amfi_code"] = result["amfi_code"].astype(int)
    logger.info(f"  NAV history expanded from {len(df)} to {len(result)} rows (forward-filled)")
    return result


def transform_aum(df: pd.DataFrame) -> pd.DataFrame:
    """Clean AUM by fund house data."""
    logger.info("  Transforming: aum_by_fund_house")
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


def transform_sip_inflows(df: pd.DataFrame) -> pd.DataFrame:
    """Clean SIP inflows and compute missing YoY growth where possible."""
    logger.info("  Transforming: monthly_sip_inflows")
    df = df.copy()
    df["month"] = df["month"].astype(str)
    # YoY growth is NaN for first 12 months — this is expected
    logger.info(f"  SIP inflows: {df['yoy_growth_pct'].isna().sum()} months without YoY data (first year)")
    return df


def transform_category_inflows(df: pd.DataFrame) -> pd.DataFrame:
    """Clean category inflows."""
    logger.info("  Transforming: category_inflows")
    df = df.copy()
    df["month"] = df["month"].astype(str)
    return df


def transform_folio_count(df: pd.DataFrame) -> pd.DataFrame:
    """Clean folio count data."""
    logger.info("  Transforming: industry_folio_count")
    df = df.copy()
    df["month"] = df["month"].astype(str)
    return df


def transform_scheme_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Clean scheme performance data."""
    logger.info("  Transforming: scheme_performance")
    df = df.copy()
    df["amfi_code"] = df["amfi_code"].astype(int)
    numeric_cols = [
        "return_1yr_pct", "return_3yr_pct", "return_5yr_pct", "benchmark_3yr_pct",
        "alpha", "beta", "sharpe_ratio", "sortino_ratio", "std_dev_ann_pct",
        "max_drawdown_pct", "aum_crore", "expense_ratio_pct", "morningstar_rating",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    anomalies = df[df["expense_ratio_pct"].notna() & ~df["expense_ratio_pct"].between(0.1, 2.5)]
    if not anomalies.empty:
        logger.warning(f"  Expense ratio outside 0.1%-2.5%: {len(anomalies)} rows")
    return df


def transform_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Clean investor transactions."""
    logger.info("  Transforming: investor_transactions")
    df = df.copy()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df["amfi_code"] = df["amfi_code"].astype(int)
    df["amount_inr"] = pd.to_numeric(df["amount_inr"], errors="coerce")
    type_map = {
        "sip": "SIP",
        "systematic investment plan": "SIP",
        "lumpsum": "Lumpsum",
        "lump sum": "Lumpsum",
        "redemption": "Redemption",
        "redeem": "Redemption",
    }
    df["transaction_type"] = (
        df["transaction_type"].astype(str).str.strip().str.lower().map(type_map).fillna(df["transaction_type"])
    )
    invalid_dates = df["transaction_date"].isna().sum()
    invalid_amounts = (df["amount_inr"].isna() | (df["amount_inr"] <= 0)).sum()
    if invalid_dates or invalid_amounts:
        logger.warning(f"  Dropping invalid transaction rows: bad_dates={invalid_dates}, bad_amounts={invalid_amounts}")
    valid_kyc = {"Verified", "Pending", "Rejected"}
    invalid_kyc = sorted(set(df["kyc_status"].dropna()) - valid_kyc)
    if invalid_kyc:
        logger.warning(f"  Unexpected KYC statuses found: {invalid_kyc}")
    df = df.dropna(subset=["transaction_date", "amount_inr"])
    df = df[df["amount_inr"] > 0]
    return df


def transform_portfolio(df: pd.DataFrame) -> pd.DataFrame:
    """Clean portfolio holdings."""
    logger.info("  Transforming: portfolio_holdings")
    df = df.copy()
    df["portfolio_date"] = pd.to_datetime(df["portfolio_date"], errors="coerce")
    df["amfi_code"] = df["amfi_code"].astype(int)
    return df


def transform_benchmarks(df: pd.DataFrame) -> pd.DataFrame:
    """Clean benchmark indices."""
    logger.info("  Transforming: benchmark_indices")
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


def generate_date_dimension(nav_df: pd.DataFrame) -> pd.DataFrame:
    """Generate a date dimension table from NAV date range."""
    logger.info("  Generating: date dimension table")
    min_date = nav_df["date"].min()
    max_date = nav_df["date"].max()
    dates = pd.date_range(min_date, max_date, freq="D")
    dim = pd.DataFrame({"date": dates})
    dim["date_id"] = dim["date"].dt.strftime("%Y-%m-%d")
    dim["year"] = dim["date"].dt.year
    dim["month"] = dim["date"].dt.month
    dim["quarter"] = dim["date"].dt.quarter
    dim["day_of_week"] = dim["date"].dt.dayofweek
    dim["day_name"] = dim["date"].dt.day_name()
    dim["month_name"] = dim["date"].dt.month_name()
    dim["is_weekday"] = (dim["day_of_week"] < 5).astype(int)
    dim["year_month"] = dim["date"].dt.strftime("%Y-%m")
    logger.info(f"  Date dimension: {len(dim)} dates from {min_date.date()} to {max_date.date()}")
    return dim


def transform_all(datasets: dict) -> dict:
    """Apply all transformations to raw datasets."""
    logger.info("=" * 60)
    logger.info("PHASE 2: TRANSFORM — Cleaning and enriching data")
    logger.info("=" * 60)

    cleaned = {}

    cleaned["fund_master"] = transform_fund_master(datasets["01_fund_master"])
    cleaned["nav_history"] = transform_nav_history(datasets["02_nav_history"])
    cleaned["aum_by_fund_house"] = transform_aum(datasets["03_aum_by_fund_house"])
    cleaned["monthly_sip_inflows"] = transform_sip_inflows(datasets["04_monthly_sip_inflows"])
    cleaned["category_inflows"] = transform_category_inflows(datasets["05_category_inflows"])
    cleaned["industry_folio_count"] = transform_folio_count(datasets["06_industry_folio_count"])
    cleaned["scheme_performance"] = transform_scheme_performance(datasets["07_scheme_performance"])
    cleaned["investor_transactions"] = transform_transactions(datasets["08_investor_transactions"])
    cleaned["portfolio_holdings"] = transform_portfolio(datasets["09_portfolio_holdings"])
    cleaned["benchmark_indices"] = transform_benchmarks(datasets["10_benchmark_indices"])

    # Generate date dimension
    cleaned["dim_date"] = generate_date_dimension(cleaned["nav_history"])

    logger.info("All transformations complete.")
    return cleaned


# ===========================================================================
# LOAD: Save Processed CSVs and Load into SQLite
# ===========================================================================
def save_processed_csvs(cleaned: dict):
    """Save cleaned DataFrames as CSV files."""
    logger.info("=" * 60)
    logger.info("PHASE 3a: LOAD — Saving processed CSVs")
    logger.info("=" * 60)

    for name, df in cleaned.items():
        fp = PROCESSED_DIR / f"{name}.csv"
        df.to_csv(fp, index=False)
        logger.info(f"  Saved: {fp.name} ({len(df)} rows)")

        # Save copies with requested Day 2 deliverable names
        if name == "nav_history":
            clean_fp = PROCESSED_DIR / "clean_nav.csv"
            df.to_csv(clean_fp, index=False)
            logger.info(f"  Saved copy: {clean_fp.name} ({len(df)} rows)")
        elif name == "investor_transactions":
            clean_fp = PROCESSED_DIR / "clean_transactions.csv"
            df.to_csv(clean_fp, index=False)
            logger.info(f"  Saved copy: {clean_fp.name} ({len(df)} rows)")
        elif name == "scheme_performance":
            clean_fp = PROCESSED_DIR / "clean_performance.csv"
            df.to_csv(clean_fp, index=False)
            logger.info(f"  Saved copy: {clean_fp.name} ({len(df)} rows)")



def load_sqlite(cleaned: dict):
    """Create SQLite database and load all data."""
    logger.info("=" * 60)
    logger.info("PHASE 3b: LOAD — Creating SQLite database")
    logger.info("=" * 60)

    # Remove existing database
    if DB_PATH.exists():
        DB_PATH.unlink()
        logger.info(f"  Removed existing database: {DB_PATH}")

    engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

    # Execute schema SQL before appending data so declared keys/constraints remain.
    schema_file = SQL_DIR / "schema.sql"
    if schema_file.exists():
        raw_conn = sqlite3.connect(DB_PATH)
        raw_conn.executescript(schema_file.read_text())
        raw_conn.commit()
        raw_conn.close()
        logger.info("  Schema created from schema.sql")
    else:
        logger.warning("  schema.sql not found — tables will be created by pandas")

    # Table mapping: cleaned key → SQLite table name
    table_map = {
        "fund_master": "dim_fund",
        "dim_date": "dim_date",
        "nav_history": "fact_nav",
        "investor_transactions": "fact_transactions",
        "scheme_performance": "fact_performance",
        "portfolio_holdings": "fact_portfolio",
        "aum_by_fund_house": "fact_aum",
        "monthly_sip_inflows": "fact_sip_industry",
        "category_inflows": "fact_category_inflows",
        "industry_folio_count": "fact_folio_count",
        "benchmark_indices": "fact_benchmark",
    }

    # Prepare DataFrames for SQLite: convert dates to strings for storage
    for key, table_name in table_map.items():
        if key not in cleaned:
            logger.warning(f"  Skipping {key} — not found in cleaned data")
            continue

        df = cleaned[key].copy()

        # Convert datetime columns to string for SQLite compatibility
        for col in df.select_dtypes(include=["datetime64[ns]", "datetime64"]).columns:
            df[col] = df[col].dt.strftime("%Y-%m-%d")

        # Drop columns not in schema for certain tables
        if key == "fund_master":
            # Remove the helper column before loading
            if "benchmark_index_name" in df.columns:
                df = df.drop(columns=["benchmark_index_name"])

        if key == "nav_history":
            # Remove auto-increment id — let SQLite handle it
            cols_to_keep = ["amfi_code", "date", "nav", "daily_return_pct"]
            df = df[[c for c in cols_to_keep if c in df.columns]]

        try:
            df.to_sql(table_name, engine, if_exists="append", index=False)
            logger.info(f"  Loaded: {table_name} ({len(df)} rows)")
        except Exception as e:
            logger.error(f"  Failed to load {table_name}: {e}")
            raise

    # Re-create indexes after data load
    with engine.connect() as conn:
        index_statements = [
            "CREATE INDEX IF NOT EXISTS idx_fact_nav_amfi ON fact_nav(amfi_code)",
            "CREATE INDEX IF NOT EXISTS idx_fact_nav_date ON fact_nav(date)",
            "CREATE INDEX IF NOT EXISTS idx_fact_nav_amfi_date ON fact_nav(amfi_code, date)",
            "CREATE INDEX IF NOT EXISTS idx_fact_tx_amfi ON fact_transactions(amfi_code)",
            "CREATE INDEX IF NOT EXISTS idx_fact_tx_investor ON fact_transactions(investor_id)",
            "CREATE INDEX IF NOT EXISTS idx_fact_tx_date ON fact_transactions(transaction_date)",
            "CREATE INDEX IF NOT EXISTS idx_fact_bench_date ON fact_benchmark(date)",
            "CREATE INDEX IF NOT EXISTS idx_fact_bench_name ON fact_benchmark(index_name)",
        ]
        for stmt in index_statements:
            try:
                conn.execute(text(stmt))
            except Exception:
                pass
        conn.commit()
    logger.info("  Indexes created")

    # Validate loaded data
    logger.info("  Validating database...")
    with engine.connect() as conn:
        for table_name in table_map.values():
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.scalar()
            logger.info(f"    {table_name}: {count} rows")

    logger.info(f"  Database created at: {DB_PATH}")
    logger.info(f"  Database size: {DB_PATH.stat().st_size / 1024 / 1024:.2f} MB")


# ===========================================================================
# MAIN
# ===========================================================================
def main():
    """Run the complete ETL pipeline."""
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("BLUESTOCK MUTUAL FUND — ETL PIPELINE")
    logger.info(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Project root: {PROJECT_ROOT}")
    logger.info("=" * 60)

    try:
        # Step 0: Ensure directories
        ensure_dirs()

        # Step 1: Extract
        datasets = extract_all()

        # Step 2: Transform
        cleaned = transform_all(datasets)

        # Step 3: Load
        save_processed_csvs(cleaned)
        load_sqlite(cleaned)

        # Summary
        elapsed = datetime.now() - start_time
        logger.info("=" * 60)
        logger.info("ETL PIPELINE COMPLETED SUCCESSFULLY")
        logger.info(f"Elapsed time: {elapsed.total_seconds():.1f} seconds")
        logger.info(f"Processed CSVs: {PROCESSED_DIR}")
        logger.info(f"SQLite database: {DB_PATH}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"ETL PIPELINE FAILED: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

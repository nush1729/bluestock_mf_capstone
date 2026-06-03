#!/usr/bin/env python3
"""Generate capstone evidence files for ingestion, live NAV, quality, and dictionary."""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LEGACY_DATA_DIR = PROJECT_ROOT / "datasets"
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"

SCHEMES = {
    125497: "HDFC Top 100 Direct",
    119551: "SBI Bluechip",
    120503: "ICICI Bluechip",
    118632: "Nippon Large Cap",
    119092: "Axis Bluechip",
    120841: "Kotak Bluechip",
}

BUSINESS_DEFINITIONS = {
    "amfi_code": "AMFI-assigned scheme identifier used to join fund, NAV, performance, transaction, and holding data.",
    "fund_house": "Asset management company or mutual fund house managing the scheme.",
    "scheme_name": "Official scheme name and plan option.",
    "category": "Broad asset category such as Equity or Debt.",
    "sub_category": "SEBI/industry sub-category such as Large Cap, Mid Cap, Small Cap, Liquid, or Gilt.",
    "plan": "Scheme plan type, usually Regular or Direct.",
    "launch_date": "Date the scheme/plan was launched.",
    "benchmark": "Benchmark index used for performance comparison.",
    "expense_ratio_pct": "Annual recurring fund expense as a percentage of AUM.",
    "exit_load_pct": "Exit load charged on eligible redemptions, as a percentage.",
    "min_sip_amount": "Minimum permitted SIP investment amount in INR.",
    "min_lumpsum_amount": "Minimum permitted one-time investment amount in INR.",
    "fund_manager": "Named portfolio manager for the scheme.",
    "risk_category": "Scheme risk label from the source data.",
    "sebi_category_code": "Synthetic category code grouping schemes by SEBI-style category.",
    "date": "Calendar date for NAV, AUM, benchmark, or date dimension records.",
    "nav": "Net asset value per unit.",
    "daily_return_pct": "Daily percentage NAV return calculated from prior available NAV.",
    "month": "Month bucket in YYYY-MM format.",
    "sip_inflow_crore": "Industry SIP inflow during the month in INR crore.",
    "active_sip_accounts_crore": "Active SIP account count in crore.",
    "new_sip_accounts_lakh": "New SIP accounts opened during the month in lakh.",
    "sip_aum_lakh_crore": "SIP assets under management in INR lakh crore.",
    "yoy_growth_pct": "Year-over-year percentage growth.",
    "net_inflow_crore": "Net category inflow in INR crore.",
    "return_1yr_pct": "One-year scheme return percentage.",
    "return_3yr_pct": "Three-year annualized scheme return percentage.",
    "return_5yr_pct": "Five-year annualized scheme return percentage.",
    "benchmark_3yr_pct": "Three-year annualized benchmark return percentage.",
    "alpha": "Excess return relative to benchmark after risk adjustment.",
    "beta": "Sensitivity of scheme returns to benchmark movement.",
    "sharpe_ratio": "Risk-adjusted return per unit of total volatility.",
    "sortino_ratio": "Risk-adjusted return per unit of downside volatility.",
    "std_dev_ann_pct": "Annualized standard deviation of returns.",
    "max_drawdown_pct": "Largest peak-to-trough decline in percentage terms.",
    "aum_crore": "Assets under management in INR crore.",
    "morningstar_rating": "Source-provided star rating from 1 to 5.",
    "risk_grade": "Source-provided risk grade.",
    "investor_id": "Anonymized investor identifier.",
    "transaction_date": "Date of investor transaction.",
    "transaction_type": "Standardized transaction type: SIP, Lumpsum, or Redemption.",
    "amount_inr": "Transaction amount in Indian rupees.",
    "state": "Investor state.",
    "city": "Investor city.",
    "city_tier": "Investor city tier, T30 or B30.",
    "age_group": "Investor age band.",
    "gender": "Investor gender label in source data.",
    "annual_income_lakh": "Investor annual income in INR lakh.",
    "payment_mode": "Payment rail used for transaction.",
    "kyc_status": "KYC workflow status.",
    "stock_symbol": "Portfolio holding ticker symbol.",
    "stock_name": "Portfolio holding company name.",
    "sector": "Portfolio holding sector.",
    "weight_pct": "Portfolio holding weight percentage.",
    "market_value_cr": "Market value of holding in INR crore.",
    "current_price_inr": "Latest source price for the holding in INR.",
    "portfolio_date": "Portfolio disclosure date.",
    "index_name": "Benchmark index name.",
    "close_value": "Benchmark closing level.",
}


def ensure_dirs() -> None:
    for path in (RAW_DIR, PROCESSED_DIR, REPORTS_DIR):
        path.mkdir(parents=True, exist_ok=True)


def sync_raw_csvs() -> None:
    for src in sorted(LEGACY_DATA_DIR.glob("[0-9][0-9]_*.csv")):
        shutil.copy2(src, RAW_DIR / src.name)


def read_source_data() -> dict[str, pd.DataFrame]:
    return {path.stem: pd.read_csv(path) for path in sorted(RAW_DIR.glob("[0-9][0-9]_*.csv"))}


def anomalies_for(name: str, df: pd.DataFrame, datasets: dict[str, pd.DataFrame]) -> list[str]:
    notes: list[str] = []
    if df.empty:
        notes.append("Dataset is empty.")
    duplicate_count = df.duplicated().sum()
    if duplicate_count:
        notes.append(f"{duplicate_count} full duplicate rows.")
    null_cols = df.isna().sum()
    null_cols = null_cols[null_cols > 0]
    if not null_cols.empty:
        notes.append("Missing values: " + ", ".join(f"{col}={count}" for col, count in null_cols.items()))

    if name == "01_fund_master":
        notes.append(f"AMFI code range is {df['amfi_code'].min()} to {df['amfi_code'].max()}; codes are numeric scheme identifiers.")
    elif name == "02_nav_history":
        parsed_dates = pd.to_datetime(df["date"], errors="coerce")
        bad_nav = pd.to_numeric(df["nav"], errors="coerce").le(0).sum()
        if parsed_dates.isna().sum():
            notes.append(f"{parsed_dates.isna().sum()} invalid NAV dates.")
        if bad_nav:
            notes.append(f"{bad_nav} non-positive NAV values.")
        key_dupes = df.duplicated(subset=["amfi_code", "date"]).sum()
        if key_dupes:
            notes.append(f"{key_dupes} duplicate amfi_code/date rows.")
    elif name == "04_monthly_sip_inflows":
        notes.append("YoY growth is blank for the first 12 months, which is expected because no prior-year base exists.")
    elif name == "07_scheme_performance":
        ratio = pd.to_numeric(df["expense_ratio_pct"], errors="coerce")
        out = df[ratio.notna() & ~ratio.between(0.1, 2.5)]
        if not out.empty:
            notes.append(f"{len(out)} expense_ratio_pct values outside 0.1%-2.5%.")
        numeric_cols = [c for c in df.columns if c.endswith("_pct") or c in {"alpha", "beta", "sharpe_ratio", "sortino_ratio", "aum_crore"}]
        bad_numeric = [c for c in numeric_cols if pd.to_numeric(df[c], errors="coerce").isna().sum()]
        if bad_numeric:
            notes.append("Non-numeric values found in: " + ", ".join(bad_numeric))
    elif name == "08_investor_transactions":
        bad_amounts = pd.to_numeric(df["amount_inr"], errors="coerce").le(0).sum()
        if bad_amounts:
            notes.append(f"{bad_amounts} non-positive amount_inr values.")
        valid_kyc = {"Verified", "Pending", "Rejected"}
        invalid_kyc = sorted(set(df["kyc_status"].dropna()) - valid_kyc)
        if invalid_kyc:
            notes.append("Unexpected KYC statuses: " + ", ".join(invalid_kyc))
        valid_types = {"SIP", "Lumpsum", "Redemption"}
        invalid_types = sorted(set(df["transaction_type"].dropna()) - valid_types)
        if invalid_types:
            notes.append("Unexpected transaction types: " + ", ".join(invalid_types))

    if name == "01_fund_master" and "02_nav_history" in datasets:
        missing = sorted(set(df["amfi_code"]) - set(datasets["02_nav_history"]["amfi_code"]))
        if missing:
            notes.append(f"{len(missing)} fund_master AMFI codes missing from nav_history.")
        else:
            notes.append("All fund_master AMFI codes exist in nav_history.")
    return notes or ["No anomalies detected from automated checks."]


def write_ingestion_audit(datasets: dict[str, pd.DataFrame]) -> None:
    lines = [
        "# CSV Ingestion Audit",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "All 10 provided CSV datasets were loaded with Pandas from `data/raw`.",
        "",
    ]
    for name, df in datasets.items():
        lines.extend(
            [
                f"## {name}",
                "",
                f"- Shape: `{df.shape[0]} rows x {df.shape[1]} columns`",
                "- Dtypes:",
                "",
                "```text",
                df.dtypes.to_string(),
                "```",
                "",
                "- Head:",
                "",
                "```text",
                df.head().to_string(index=False),
                "```",
                "",
                "- Anomalies/notes:",
            ]
        )
        lines.extend(f"  - {note}" for note in anomalies_for(name, df, datasets))
        lines.append("")
    (REPORTS_DIR / "csv_ingestion_audit.md").write_text("\n".join(lines), encoding="utf-8")


def write_quality_summary(datasets: dict[str, pd.DataFrame]) -> None:
    fund_master = datasets["01_fund_master"]
    nav_history = datasets["02_nav_history"]
    performance = datasets["07_scheme_performance"]
    transactions = datasets["08_investor_transactions"]

    fund_codes = set(fund_master["amfi_code"])
    nav_codes = set(nav_history["amfi_code"])
    missing = sorted(fund_codes - nav_codes)
    extra = sorted(nav_codes - fund_codes)

    lines = [
        "# Data Quality Summary",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Fund Master Exploration",
        "",
        f"- Fund houses: {', '.join(sorted(fund_master['fund_house'].dropna().unique()))}",
        f"- Categories: {', '.join(sorted(fund_master['category'].dropna().unique()))}",
        f"- Sub-categories: {', '.join(sorted(fund_master['sub_category'].dropna().unique()))}",
        f"- Risk categories: {', '.join(sorted(fund_master['risk_category'].dropna().unique()))}",
        f"- Risk grades: {', '.join(sorted(performance['risk_grade'].dropna().unique()))}",
        "",
        "## AMFI Scheme Code Structure",
        "",
        "AMFI codes are numeric scheme identifiers. In this project they are stored as integers and used as the stable key between fund master, NAV history, performance, transactions, and portfolio holdings. Regular and Direct plans usually have distinct AMFI codes even when they belong to the same strategy family.",
        "",
        "## AMFI Code Validation",
        "",
        f"- `fund_master` distinct AMFI codes: {len(fund_codes)}",
        f"- `nav_history` distinct AMFI codes: {len(nav_codes)}",
        f"- Codes in `fund_master` missing from `nav_history`: {len(missing)}",
        f"- Codes in `nav_history` not present in `fund_master`: {len(extra)}",
        f"- Validation result: {'PASS - every fund_master code exists in nav_history.' if not missing else 'FAIL - missing codes: ' + ', '.join(map(str, missing))}",
        "",
        "## Cleaning Checks",
        "",
        f"- NAV rows with invalid dates: {pd.to_datetime(nav_history['date'], errors='coerce').isna().sum()}",
        f"- NAV rows with non-positive NAV: {(pd.to_numeric(nav_history['nav'], errors='coerce') <= 0).sum()}",
        f"- NAV duplicate `amfi_code` + `date` rows: {nav_history.duplicated(subset=['amfi_code', 'date']).sum()}",
        f"- Transaction rows with non-positive amount: {(pd.to_numeric(transactions['amount_inr'], errors='coerce') <= 0).sum()}",
        f"- Transaction type values: {', '.join(sorted(transactions['transaction_type'].dropna().unique()))}",
        f"- KYC status values: {', '.join(sorted(transactions['kyc_status'].dropna().unique()))}",
        f"- Performance expense ratios outside 0.1%-2.5%: {len(performance[~performance['expense_ratio_pct'].between(0.1, 2.5)])}",
        "",
        "The ETL pipeline parses dates, removes invalid NAV/transaction records, de-duplicates NAV by `amfi_code` + `date`, forward-fills daily NAV gaps, standardizes transaction types, validates positive amounts, coerces performance metrics to numeric values, and loads the cleaned outputs into SQLite.",
    ]
    (REPORTS_DIR / "data_quality_summary.md").write_text("\n".join(lines), encoding="utf-8")


def write_data_dictionary(datasets: dict[str, pd.DataFrame]) -> None:
    source_refs = {
        "01_fund_master": "Raw CSV: data/raw/01_fund_master.csv; SQLite: dim_fund",
        "02_nav_history": "Raw CSV: data/raw/02_nav_history.csv; SQLite: fact_nav",
        "03_aum_by_fund_house": "Raw CSV: data/raw/03_aum_by_fund_house.csv; SQLite: fact_aum",
        "04_monthly_sip_inflows": "Raw CSV: data/raw/04_monthly_sip_inflows.csv; SQLite: fact_sip_industry",
        "05_category_inflows": "Raw CSV: data/raw/05_category_inflows.csv; SQLite: fact_category_inflows",
        "06_industry_folio_count": "Raw CSV: data/raw/06_industry_folio_count.csv; SQLite: fact_folio_count",
        "07_scheme_performance": "Raw CSV: data/raw/07_scheme_performance.csv; SQLite: fact_performance",
        "08_investor_transactions": "Raw CSV: data/raw/08_investor_transactions.csv; SQLite: fact_transactions",
        "09_portfolio_holdings": "Raw CSV: data/raw/09_portfolio_holdings.csv; SQLite: fact_portfolio",
        "10_benchmark_indices": "Raw CSV: data/raw/10_benchmark_indices.csv; SQLite: fact_benchmark",
    }
    lines = ["# Data Dictionary", "", f"Generated: {datetime.now().isoformat(timespec='seconds')}", ""]
    for name, df in datasets.items():
        lines.extend([f"## {name}", "", f"Source reference: {source_refs.get(name, 'Raw CSV')}", "", "| Column | Pandas dtype | Business definition |", "| --- | --- | --- |"])
        for col, dtype in df.dtypes.items():
            definition = BUSINESS_DEFINITIONS.get(col, "Source-provided analytical field.")
            lines.append(f"| `{col}` | `{dtype}` | {definition} |")
        lines.append("")
    (REPORTS_DIR / "data_dictionary.md").write_text("\n".join(lines), encoding="utf-8")


def fetch_live_nav() -> None:
    latest_rows = []
    for code, label in SCHEMES.items():
        url = f"https://api.mfapi.in/mf/{code}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        payload = response.json()
        api_name = payload.get("meta", {}).get("scheme_name", label)
        records = pd.DataFrame(payload.get("data", []))
        if records.empty:
            raise ValueError(f"No NAV data returned for {code}")
        records["amfi_code"] = code
        records["requested_scheme"] = label
        records["api_scheme_name"] = api_name
        records["source_url"] = url
        records["fetched_at"] = datetime.now().isoformat(timespec="seconds")
        records["date"] = pd.to_datetime(records["date"], format="%d-%m-%Y", errors="coerce").dt.strftime("%Y-%m-%d")
        records["nav"] = pd.to_numeric(records["nav"], errors="coerce")
        records = records[["amfi_code", "requested_scheme", "api_scheme_name", "date", "nav", "source_url", "fetched_at"]]
        records.to_csv(RAW_DIR / f"mfapi_nav_{code}.csv", index=False)
        latest_rows.append(records.iloc[0].to_dict())
    pd.DataFrame(latest_rows).to_csv(RAW_DIR / "mfapi_latest_nav.csv", index=False)


def main() -> None:
    ensure_dirs()
    sync_raw_csvs()
    datasets = read_source_data()
    if len(datasets) != 10:
        raise ValueError(f"Expected 10 source CSVs in data/raw, found {len(datasets)}")
    write_ingestion_audit(datasets)
    write_quality_summary(datasets)
    write_data_dictionary(datasets)
    fetch_live_nav()


if __name__ == "__main__":
    main()

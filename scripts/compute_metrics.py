#!/usr/bin/env python3
"""
Bluestock Mutual Fund Analytics — Performance Metrics Computation (Day 4)
=========================================================================
Standalone script that computes all risk-adjusted performance metrics from
NAV history and saves results as CSV files to outputs/.

Metrics computed:
  - Daily & annualised returns
  - CAGR (1yr, 3yr, 5yr)
  - Sharpe Ratio  (Rf = 6.5% RBI repo rate proxy)
  - Sortino Ratio (downside deviation only)
  - Alpha & Beta  (OLS regression vs benchmark index)
  - Maximum Drawdown
  - Composite Fund Scorecard (0–100)

Usage:
    python scripts/compute_metrics.py

Outputs saved to outputs/:
    returns_computed.csv
    cagr_report.csv
    sharpe_values.csv
    sortino_values.csv
    alpha_beta.csv
    max_drawdown.csv
    fund_scorecard.csv
    benchmark_chart.png

Author: Bluestock Fintech Analytics Team
"""

from __future__ import annotations

import logging
import sys
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import stats

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH      = PROJECT_ROOT / "data" / "db" / "bluestock_mf.db"
OUTPUT_DIR   = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RISK_FREE_RATE_ANNUAL = 0.065   # 6.5% RBI repo rate proxy
TRADING_DAYS_PER_YEAR = 252
RF_DAILY = RISK_FREE_RATE_ANNUAL / TRADING_DAYS_PER_YEAR

# Benchmark mapping: fund category → index to use for Alpha/Beta regression
CATEGORY_BENCHMARK_MAP = {
    "Large Cap":      "NIFTY100",
    "Mid Cap":        "NIFTY_MIDCAP150",
    "Small Cap":      "BSE_SMALLCAP",
    "ELSS":           "NIFTY100",
    "Flexi Cap":      "NIFTY500",
    "Multi Cap":      "NIFTY500",
    "Large & Mid Cap":"NIFTY500",
    "Liquid":         "CRISIL_LIQUID",
    "Short Duration": "CRISIL_LIQUID",
    "Gilt":           "CRISIL_GILT",
}
DEFAULT_BENCHMARK = "NIFTY50"

# Scorecard weights (must sum to 1.0)
SCORE_WEIGHTS = {
    "cagr_3yr_rank":       0.30,
    "sharpe_rank":         0.25,
    "alpha_rank":          0.20,
    "expense_ratio_rank":  0.15,   # inverse (lower is better)
    "max_drawdown_rank":   0.10,   # inverse (smaller drawdown is better)
}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(PROJECT_ROOT / "pipeline.log", mode="a"),
    ],
)
log = logging.getLogger("compute_metrics")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_from_db() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load NAV, fund master, and benchmark data from SQLite."""
    log.info("Loading data from %s", DB_PATH)
    conn = sqlite3.connect(DB_PATH)

    nav = pd.read_sql(
        "SELECT amfi_code, date, nav, daily_return_pct FROM fact_nav ORDER BY amfi_code, date",
        conn,
        parse_dates=["date"],
    )
    funds = pd.read_sql(
        "SELECT amfi_code, scheme_name, fund_house, category, sub_category, expense_ratio_pct FROM dim_fund",
        conn,
    )
    bench = pd.read_sql(
        "SELECT date, index_name, close_value FROM fact_benchmark ORDER BY date",
        conn,
        parse_dates=["date"],
    )
    conn.close()
    log.info("  NAV rows: %d | Funds: %d | Benchmark rows: %d", len(nav), len(funds), len(bench))
    return nav, funds, bench


def compute_daily_returns(nav: pd.DataFrame) -> pd.DataFrame:
    """Compute daily return % for every fund and save returns_computed.csv."""
    log.info("Computing daily returns …")
    nav = nav.sort_values(["amfi_code", "date"]).copy()

    # Use existing daily_return_pct if present; recompute otherwise
    if "daily_return_pct" not in nav.columns or nav["daily_return_pct"].isnull().all():
        nav["daily_return_pct"] = (
            nav.groupby("amfi_code")["nav"]
            .pct_change() * 100
        )

    nav.dropna(subset=["daily_return_pct"], inplace=True)
    out_path = OUTPUT_DIR / "returns_computed.csv"
    nav.to_csv(out_path, index=False)
    log.info("  returns_computed.csv written (%d rows)", len(nav))
    return nav


def compute_cagr(nav: pd.DataFrame, funds: pd.DataFrame) -> pd.DataFrame:
    """Compute 1yr / 3yr / 5yr CAGR for every fund."""
    log.info("Computing CAGR …")
    end_date   = nav["date"].max()
    cutoffs    = {
        "1yr": end_date - pd.DateOffset(years=1),
        "3yr": end_date - pd.DateOffset(years=3),
        "5yr": end_date - pd.DateOffset(years=5),
    }

    records = []
    for amfi_code, grp in nav.groupby("amfi_code"):
        grp = grp.sort_values("date")
        nav_end = grp["nav"].iloc[-1]
        row: dict = {"amfi_code": amfi_code}
        for label, start_date in cutoffs.items():
            subset = grp[grp["date"] >= start_date]
            if len(subset) < 20:          # not enough data
                row[f"cagr_{label}_pct"] = np.nan
            else:
                nav_start = subset["nav"].iloc[0]
                n_days    = len(subset)
                cagr = (nav_end / nav_start) ** (TRADING_DAYS_PER_YEAR / n_days) - 1
                row[f"cagr_{label}_pct"] = round(cagr * 100, 4)
        records.append(row)

    cagr_df = pd.DataFrame(records).merge(
        funds[["amfi_code", "scheme_name", "sub_category", "fund_house"]], on="amfi_code", how="left"
    )
    out_path = OUTPUT_DIR / "cagr_report.csv"
    cagr_df.to_csv(out_path, index=False)
    log.info("  cagr_report.csv written (%d rows)", len(cagr_df))
    return cagr_df


def compute_sharpe(nav: pd.DataFrame, funds: pd.DataFrame) -> pd.DataFrame:
    """Compute annualised Sharpe Ratio for every fund."""
    log.info("Computing Sharpe Ratio …")
    records = []
    for amfi_code, grp in nav.groupby("amfi_code"):
        r = grp["daily_return_pct"].dropna() / 100
        if len(r) < 50:
            continue
        excess   = r - RF_DAILY
        sharpe   = (excess.mean() / r.std()) * np.sqrt(TRADING_DAYS_PER_YEAR)
        ann_ret  = ((1 + r).prod() ** (TRADING_DAYS_PER_YEAR / len(r)) - 1) * 100
        records.append({
            "amfi_code":      amfi_code,
            "sharpe_ratio":   round(sharpe, 4),
            "ann_return_pct": round(ann_ret, 4),
            "ann_volatility_pct": round(r.std() * np.sqrt(TRADING_DAYS_PER_YEAR) * 100, 4),
        })

    sharpe_df = pd.DataFrame(records).merge(
        funds[["amfi_code", "scheme_name", "sub_category"]], on="amfi_code", how="left"
    )
    sharpe_df.to_csv(OUTPUT_DIR / "sharpe_values.csv", index=False)
    log.info("  sharpe_values.csv written (%d funds)", len(sharpe_df))
    return sharpe_df


def compute_sortino(nav: pd.DataFrame, funds: pd.DataFrame) -> pd.DataFrame:
    """Compute Sortino Ratio (penalises only downside volatility)."""
    log.info("Computing Sortino Ratio …")
    records = []
    for amfi_code, grp in nav.groupby("amfi_code"):
        r = grp["daily_return_pct"].dropna() / 100
        if len(r) < 50:
            continue
        excess       = r - RF_DAILY
        downside     = r[r < RF_DAILY]
        down_std     = downside.std() if len(downside) > 1 else np.nan
        sortino      = (excess.mean() / down_std * np.sqrt(TRADING_DAYS_PER_YEAR)) if down_std else np.nan
        records.append({
            "amfi_code":         amfi_code,
            "sortino_ratio":     round(sortino, 4) if sortino else np.nan,
            "downside_std_pct":  round(down_std * 100, 4) if down_std else np.nan,
            "n_negative_days":   len(downside),
        })

    sortino_df = pd.DataFrame(records).merge(
        funds[["amfi_code", "scheme_name", "sub_category"]], on="amfi_code", how="left"
    )
    sortino_df.to_csv(OUTPUT_DIR / "sortino_values.csv", index=False)
    log.info("  sortino_values.csv written (%d funds)", len(sortino_df))
    return sortino_df


def compute_alpha_beta(nav: pd.DataFrame, funds: pd.DataFrame, bench: pd.DataFrame) -> pd.DataFrame:
    """Compute Alpha & Beta for every fund via OLS regression on Nifty 100."""
    log.info("Computing Alpha & Beta (OLS) …")

    # Build a daily return series for each benchmark index
    bench_ret = (
        bench
        .sort_values(["index_name", "date"])
        .assign(bench_ret=lambda d: d.groupby("index_name")["close_value"].pct_change())
        .dropna(subset=["bench_ret"])
    )

    records = []
    for amfi_code, grp in nav.groupby("amfi_code"):
        # Pick the right benchmark for this fund's category
        meta = funds[funds["amfi_code"] == amfi_code]
        if meta.empty:
            bench_idx = DEFAULT_BENCHMARK
        else:
            sub_cat = meta["sub_category"].iloc[0]
            bench_idx = CATEGORY_BENCHMARK_MAP.get(sub_cat, DEFAULT_BENCHMARK)

        idx_ret = bench_ret[bench_ret["index_name"] == bench_idx][["date", "bench_ret"]].copy()

        merged = grp[["date", "daily_return_pct"]].dropna().merge(idx_ret, on="date", how="inner")
        if len(merged) < 50:
            continue

        fund_r  = merged["daily_return_pct"].values / 100
        bench_r = merged["bench_ret"].values

        slope, intercept, r_value, p_value, std_err = stats.linregress(bench_r, fund_r)
        alpha_annual = intercept * TRADING_DAYS_PER_YEAR * 100   # annualised %
        records.append({
            "amfi_code":       amfi_code,
            "benchmark_used":  bench_idx,
            "alpha_pct":       round(alpha_annual, 4),
            "beta":            round(slope, 4),
            "r_squared":       round(r_value ** 2, 4),
            "p_value":         round(p_value, 6),
            "n_obs":           len(merged),
        })

    ab_df = pd.DataFrame(records).merge(
        funds[["amfi_code", "scheme_name", "sub_category"]], on="amfi_code", how="left"
    )
    ab_df.to_csv(OUTPUT_DIR / "alpha_beta.csv", index=False)
    log.info("  alpha_beta.csv written (%d funds)", len(ab_df))
    return ab_df


def compute_max_drawdown(nav: pd.DataFrame, funds: pd.DataFrame) -> pd.DataFrame:
    """Compute Maximum Drawdown (worst peak-to-trough decline) per fund."""
    log.info("Computing Maximum Drawdown …")
    records = []
    for amfi_code, grp in nav.groupby("amfi_code"):
        grp = grp.sort_values("date")
        prices = grp["nav"].values
        dates  = grp["date"].values

        running_max   = np.maximum.accumulate(prices)
        drawdown      = prices / running_max - 1.0
        max_dd_idx    = drawdown.argmin()
        max_dd        = drawdown[max_dd_idx]

        # Find the peak before the max drawdown trough
        peak_idx = np.argmax(prices[:max_dd_idx + 1]) if max_dd_idx > 0 else 0

        records.append({
            "amfi_code":        amfi_code,
            "max_drawdown_pct": round(max_dd * 100, 4),
            "peak_date":        str(dates[peak_idx])[:10],
            "trough_date":      str(dates[max_dd_idx])[:10],
            "worst_date":       str(dates[max_dd_idx])[:10],
        })

    dd_df = pd.DataFrame(records).merge(
        funds[["amfi_code", "scheme_name", "sub_category", "fund_house"]], on="amfi_code", how="left"
    )
    dd_df.to_csv(OUTPUT_DIR / "max_drawdown.csv", index=False)
    log.info("  max_drawdown.csv written (%d funds)", len(dd_df))
    return dd_df


def build_scorecard(
    cagr_df: pd.DataFrame,
    sharpe_df: pd.DataFrame,
    ab_df: pd.DataFrame,
    dd_df: pd.DataFrame,
    funds: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build a composite Fund Scorecard (0–100) using weighted percentile ranks.

    Score = 30% × 3yr CAGR rank
          + 25% × Sharpe rank
          + 20% × Alpha rank
          + 15% × Expense ratio rank (inverse — lower cost is better)
          + 10% × Max drawdown rank (inverse — smaller loss is better)
    """
    log.info("Building Fund Scorecard …")

    # Merge all metric tables on amfi_code
    sc = funds[["amfi_code", "scheme_name", "fund_house", "sub_category", "expense_ratio_pct"]].copy()
    sc = sc.merge(cagr_df[["amfi_code", "cagr_3yr_pct"]], on="amfi_code", how="left")
    sc = sc.merge(sharpe_df[["amfi_code", "sharpe_ratio"]], on="amfi_code", how="left")
    sc = sc.merge(ab_df[["amfi_code", "alpha_pct"]], on="amfi_code", how="left")
    sc = sc.merge(dd_df[["amfi_code", "max_drawdown_pct"]], on="amfi_code", how="left")

    n = len(sc)
    if n == 0:
        return sc

    def _pct_rank(series: pd.Series, ascending: bool = True) -> pd.Series:
        """Return 0–100 percentile rank (ascending=True → higher value → higher rank)."""
        return series.rank(ascending=ascending, pct=True) * 100

    sc["cagr_3yr_rank"]      = _pct_rank(sc["cagr_3yr_pct"],      ascending=True)
    sc["sharpe_rank"]        = _pct_rank(sc["sharpe_ratio"],       ascending=True)
    sc["alpha_rank"]         = _pct_rank(sc["alpha_pct"],          ascending=True)
    sc["expense_ratio_rank"] = _pct_rank(sc["expense_ratio_pct"],  ascending=False)  # lower cost → better
    sc["max_drawdown_rank"]  = _pct_rank(sc["max_drawdown_pct"],   ascending=False)  # less negative → better

    sc["composite_score"] = (
        sc["cagr_3yr_rank"]      * SCORE_WEIGHTS["cagr_3yr_rank"]      +
        sc["sharpe_rank"]        * SCORE_WEIGHTS["sharpe_rank"]         +
        sc["alpha_rank"]         * SCORE_WEIGHTS["alpha_rank"]          +
        sc["expense_ratio_rank"] * SCORE_WEIGHTS["expense_ratio_rank"]  +
        sc["max_drawdown_rank"]  * SCORE_WEIGHTS["max_drawdown_rank"]
    ).round(2)

    sc["rank"] = sc["composite_score"].rank(ascending=False).astype(int)
    sc = sc.sort_values("rank")

    sc.to_csv(OUTPUT_DIR / "fund_scorecard.csv", index=False)
    log.info("  fund_scorecard.csv written (%d funds)", len(sc))
    return sc


def plot_benchmark_comparison(
    nav: pd.DataFrame,
    sc: pd.DataFrame,
    bench: pd.DataFrame,
) -> None:
    """Plot top-5 funds vs Nifty 50 & Nifty 100, indexed to 100 at start."""
    log.info("Generating benchmark comparison chart …")

    top5_codes = sc.head(5)["amfi_code"].tolist()
    end_date   = nav["date"].max()
    start_date = end_date - pd.DateOffset(years=3)

    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor("#0f1117")
    ax.set_facecolor("#0f1117")

    COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6",
              "#06b6d4", "#ec4899"]

    # Plot fund NAVs indexed to 100
    for i, code in enumerate(top5_codes):
        grp = nav[(nav["amfi_code"] == code) & (nav["date"] >= start_date)].sort_values("date")
        if grp.empty:
            continue
        indexed = grp["nav"] / grp["nav"].iloc[0] * 100
        label   = sc[sc["amfi_code"] == code]["scheme_name"].values[0][:28]
        ax.plot(grp["date"], indexed, label=label, color=COLORS[i % len(COLORS)], linewidth=1.8)

    # Plot Nifty 50 and Nifty 100
    for idx_name, color, ls in [("NIFTY50", "#94a3b8", "--"), ("NIFTY100", "#64748b", ":")]:
        b = bench[(bench["index_name"] == idx_name) & (bench["date"] >= start_date)].sort_values("date")
        if not b.empty:
            indexed = b["close_value"] / b["close_value"].iloc[0] * 100
            ax.plot(b["date"], indexed, label=idx_name, color=color, linewidth=1.2, linestyle=ls)

    ax.set_title("Top-5 Funds vs Benchmark (Indexed to 100, 3-Year Window)",
                 color="white", fontsize=14, pad=12)
    ax.set_xlabel("Date", color="#94a3b8")
    ax.set_ylabel("Indexed NAV (Base = 100)", color="#94a3b8")
    ax.tick_params(colors="#94a3b8")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b'%y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))

    for spine in ax.spines.values():
        spine.set_edgecolor("#334155")

    ax.grid(axis="y", color="#1e293b", linewidth=0.6)
    ax.legend(loc="upper left", fontsize=8, framealpha=0.2,
              labelcolor="white", facecolor="#1e293b")

    plt.tight_layout()
    out_path = OUTPUT_DIR / "benchmark_chart.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    log.info("  benchmark_chart.png written → %s", out_path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    log.info("=" * 60)
    log.info("COMPUTE METRICS — Bluestock MF Analytics (Day 4)")
    log.info("=" * 60)

    nav, funds, bench = load_from_db()

    nav        = compute_daily_returns(nav)
    cagr_df    = compute_cagr(nav, funds)
    sharpe_df  = compute_sharpe(nav, funds)
    sortino_df = compute_sortino(nav, funds)
    ab_df      = compute_alpha_beta(nav, funds, bench)
    dd_df      = compute_max_drawdown(nav, funds)
    sc         = build_scorecard(cagr_df, sharpe_df, ab_df, dd_df, funds)
    plot_benchmark_comparison(nav, sc, bench)

    log.info("=" * 60)
    log.info("✅ All metrics computed. Outputs saved to outputs/")
    log.info("   Files: returns_computed.csv, cagr_report.csv,")
    log.info("          sharpe_values.csv, sortino_values.csv,")
    log.info("          alpha_beta.csv, max_drawdown.csv,")
    log.info("          fund_scorecard.csv, benchmark_chart.png")
    log.info("=" * 60)


if __name__ == "__main__":
    main()

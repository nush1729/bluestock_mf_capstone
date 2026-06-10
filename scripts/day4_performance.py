#!/usr/bin/env python3
"""
Bluestock Mutual Fund Analytics — Day 4: Fund Performance Analytics
====================================================================
Computes all required metrics and generates deliverables:
  outputs/returns_computed.csv
  outputs/cagr_report.csv
  outputs/sharpe_values.csv
  outputs/sortino_values.csv
  outputs/alpha_beta.csv
  outputs/max_drawdown.csv
  outputs/fund_scorecard.csv
  outputs/benchmark_chart.png

Usage:
    python scripts/day4_performance.py
"""

import logging
import sys
import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from scipy import stats

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH      = PROJECT_ROOT / "data" / "db" / "bluestock_mf.db"
OUTPUT_DIR   = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RISK_FREE_RATE = 0.065   # 6.5% annual
TRADING_DAYS   = 252

# Benchmark mapping: fund_master benchmark field -> index_name in fact_benchmark
BENCH_MAP = {
    "NIFTY 50 TRI":              "NIFTY50",
    "NIFTY 100 TRI":             "NIFTY100",
    "NIFTY 500 TRI":             "NIFTY500",
    "NIFTY Midcap 150 TRI":      "NIFTY_MIDCAP150",
    "NIFTY Midcap 50 TRI":       "NIFTY_MIDCAP150",
    "NIFTY Large Midcap 250 TRI":"NIFTY500",
    "BSE 250 SmallCap TRI":      "BSE_SMALLCAP",
    "CRISIL Liquid Fund AI Index":"CRISIL_LIQUID",
    "CRISIL Short Term Bond Index":"CRISIL_LIQUID",
    "CRISIL Dynamic Gilt Index":  "CRISIL_GILT",
}

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s | %(levelname)-8s | %(message)s",
                    handlers=[logging.StreamHandler(sys.stdout)])
log = logging.getLogger("Day4")

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
def load_data():
    conn = sqlite3.connect(DB_PATH)
    nav = pd.read_sql(
        "SELECT amfi_code, date, nav FROM fact_nav ORDER BY amfi_code, date", conn)
    nav["date"] = pd.to_datetime(nav["date"])
    nav["nav"]  = nav["nav"].astype(float)

    bench = pd.read_sql(
        "SELECT date, index_name, close_value FROM fact_benchmark ORDER BY index_name, date", conn)
    bench["date"]        = pd.to_datetime(bench["date"])
    bench["close_value"] = bench["close_value"].astype(float)

    funds = pd.read_sql(
        "SELECT amfi_code, scheme_name, sub_category, benchmark, expense_ratio_pct "
        "FROM dim_fund", conn)

    perf_src = pd.read_sql(
        "SELECT amfi_code, expense_ratio_pct FROM fact_performance", conn)

    conn.close()
    return nav, bench, funds, perf_src

# ---------------------------------------------------------------------------
# Task 1: Daily returns
# ---------------------------------------------------------------------------
def compute_daily_returns(nav: pd.DataFrame) -> pd.DataFrame:
    log.info("Task 1: Computing daily returns for all funds…")
    nav = nav.sort_values(["amfi_code", "date"])
    nav["daily_return"] = nav.groupby("amfi_code")["nav"].pct_change()

    # Annualised return per fund
    ann = (nav.groupby("amfi_code")["daily_return"]
             .apply(lambda r: ((1 + r.dropna()).prod() ** (TRADING_DAYS / max(len(r.dropna()), 1)) - 1) * 100)
             .reset_index()
             .rename(columns={"daily_return": "annualised_return_pct"}))

    out = nav[["amfi_code", "date", "nav", "daily_return"]].copy()
    out["daily_return_pct"] = out["daily_return"] * 100
    out = out.drop(columns=["daily_return"])
    out.to_csv(OUTPUT_DIR / "returns_computed.csv", index=False)
    log.info(f"  Saved returns_computed.csv ({len(out)} rows)")
    return out

# ---------------------------------------------------------------------------
# Task 2: CAGR
# ---------------------------------------------------------------------------
def compute_cagr(nav: pd.DataFrame, funds: pd.DataFrame) -> pd.DataFrame:
    log.info("Task 2: Computing 1yr / 3yr / 5yr CAGR…")
    records = []
    for amfi_code, grp in nav.groupby("amfi_code"):
        grp = grp.sort_values("date").reset_index(drop=True)
        latest_nav  = grp["nav"].iloc[-1]
        latest_date = grp["date"].iloc[-1]

        def cagr_for_years(n_years):
            target = latest_date - pd.DateOffset(years=n_years)
            sub = grp[grp["date"] <= target]
            if sub.empty:
                return np.nan
            start_nav = sub["nav"].iloc[-1]
            td = len(grp[grp["date"] > sub["date"].iloc[-1]])
            if td <= 0 or start_nav <= 0:
                return np.nan
            return ((latest_nav / start_nav) ** (TRADING_DAYS / td) - 1) * 100

        row = {"amfi_code": amfi_code}
        row["cagr_1yr_pct"] = cagr_for_years(1)
        row["cagr_3yr_pct"] = cagr_for_years(3)
        row["cagr_5yr_pct"] = cagr_for_years(5)
        records.append(row)

    df = pd.DataFrame(records).merge(
        funds[["amfi_code", "scheme_name", "sub_category"]], on="amfi_code", how="left")
    df = df[["amfi_code", "scheme_name", "sub_category",
             "cagr_1yr_pct", "cagr_3yr_pct", "cagr_5yr_pct"]]
    df.to_csv(OUTPUT_DIR / "cagr_report.csv", index=False)
    log.info(f"  Saved cagr_report.csv ({len(df)} rows)")
    return df

# ---------------------------------------------------------------------------
# Task 3: Sharpe
# ---------------------------------------------------------------------------
def compute_sharpe(nav: pd.DataFrame, funds: pd.DataFrame) -> pd.DataFrame:
    log.info("Task 3: Computing Sharpe Ratios…")
    daily_rf = RISK_FREE_RATE / TRADING_DAYS
    records = []
    for amfi_code, grp in nav.groupby("amfi_code"):
        r = grp.sort_values("date")["nav"].pct_change().dropna()
        if len(r) < 20:
            continue
        excess = r - daily_rf
        ann_excess = excess.mean() * TRADING_DAYS
        ann_std    = r.std() * np.sqrt(TRADING_DAYS)
        sharpe = ann_excess / ann_std if ann_std > 0 else np.nan
        records.append({"amfi_code": amfi_code, "sharpe_ratio": round(sharpe, 4),
                         "ann_return_pct": round(r.mean() * TRADING_DAYS * 100, 4),
                         "ann_volatility_pct": round(ann_std * 100, 4)})
    df = pd.DataFrame(records).merge(
        funds[["amfi_code", "scheme_name", "sub_category"]], on="amfi_code", how="left")
    df.to_csv(OUTPUT_DIR / "sharpe_values.csv", index=False)
    log.info(f"  Saved sharpe_values.csv ({len(df)} rows)")
    return df

# ---------------------------------------------------------------------------
# Task 4: Sortino
# ---------------------------------------------------------------------------
def compute_sortino(nav: pd.DataFrame, funds: pd.DataFrame) -> pd.DataFrame:
    log.info("Task 4: Computing Sortino Ratios…")
    daily_rf = RISK_FREE_RATE / TRADING_DAYS
    records = []
    for amfi_code, grp in nav.groupby("amfi_code"):
        r = grp.sort_values("date")["nav"].pct_change().dropna()
        if len(r) < 20:
            continue
        ann_return   = r.mean() * TRADING_DAYS
        downside     = r[r < 0]
        down_std     = downside.std() * np.sqrt(TRADING_DAYS) if len(downside) > 1 else np.nan
        sortino      = (ann_return - RISK_FREE_RATE) / down_std if down_std and down_std > 0 else np.nan
        records.append({"amfi_code": amfi_code,
                         "sortino_ratio": round(sortino, 4),
                         "ann_return_pct": round(ann_return * 100, 4),
                         "downside_volatility_pct": round(down_std * 100, 4) if down_std else np.nan})
    df = pd.DataFrame(records).merge(
        funds[["amfi_code", "scheme_name", "sub_category"]], on="amfi_code", how="left")
    df.to_csv(OUTPUT_DIR / "sortino_values.csv", index=False)
    log.info(f"  Saved sortino_values.csv ({len(df)} rows)")
    return df

# ---------------------------------------------------------------------------
# Task 5: Alpha & Beta
# ---------------------------------------------------------------------------
def compute_alpha_beta(nav: pd.DataFrame, bench: pd.DataFrame,
                       funds: pd.DataFrame) -> pd.DataFrame:
    log.info("Task 5: Computing Alpha & Beta (OLS vs benchmark)…")
    records = []
    for _, fund_row in funds.iterrows():
        amfi_code  = fund_row["amfi_code"]
        bench_name = BENCH_MAP.get(fund_row["benchmark"], "NIFTY100")

        f = nav[nav["amfi_code"] == amfi_code].sort_values("date").set_index("date")
        b = bench[bench["index_name"] == bench_name].sort_values("date").set_index("date")

        f_ret = f["nav"].pct_change().dropna()
        b_ret = b["close_value"].pct_change().dropna()

        aligned = pd.concat([f_ret.rename("fund"), b_ret.rename("bench")],
                             axis=1).dropna()
        if len(aligned) < 60:
            continue

        slope, intercept, r_val, p_val, se = stats.linregress(
            aligned["bench"], aligned["fund"])
        beta  = slope
        alpha = intercept * TRADING_DAYS * 100      # annualised alpha in %
        r_sq  = r_val ** 2

        # Tracking error
        diff = aligned["fund"] - aligned["bench"]
        tracking_error = diff.std() * np.sqrt(TRADING_DAYS) * 100

        records.append({
            "amfi_code": amfi_code,
            "scheme_name": fund_row["scheme_name"],
            "sub_category": fund_row["sub_category"],
            "benchmark_used": bench_name,
            "beta": round(beta, 4),
            "alpha_pct": round(alpha, 4),
            "r_squared": round(r_sq, 4),
            "tracking_error_pct": round(tracking_error, 4),
        })

    df = pd.DataFrame(records)
    df.to_csv(OUTPUT_DIR / "alpha_beta.csv", index=False)
    log.info(f"  Saved alpha_beta.csv ({len(df)} rows)")
    return df

# ---------------------------------------------------------------------------
# Task 6: Maximum Drawdown
# ---------------------------------------------------------------------------
def compute_max_drawdown(nav: pd.DataFrame, funds: pd.DataFrame) -> pd.DataFrame:
    log.info("Task 6: Computing Maximum Drawdowns…")
    records = []
    for amfi_code, grp in nav.groupby("amfi_code"):
        grp = grp.sort_values("date")
        running_max = grp["nav"].cummax()
        drawdown    = (grp["nav"] - running_max) / running_max
        max_dd      = drawdown.min()
        worst_date  = grp.loc[drawdown.idxmin(), "date"] if not drawdown.empty else pd.NaT
        records.append({"amfi_code": amfi_code,
                         "max_drawdown_pct": round(max_dd * 100, 4),
                         "worst_date": worst_date.date() if pd.notna(worst_date) else None})
    df = pd.DataFrame(records).merge(
        funds[["amfi_code", "scheme_name", "sub_category"]], on="amfi_code", how="left")
    df = df.sort_values("max_drawdown_pct")  # worst first
    df.to_csv(OUTPUT_DIR / "max_drawdown.csv", index=False)
    log.info(f"  Saved max_drawdown.csv ({len(df)} rows)")
    return df

# ---------------------------------------------------------------------------
# Task 7: Fund Scorecard
# ---------------------------------------------------------------------------
def compute_scorecard(cagr_df, sharpe_df, ab_df, dd_df, funds, perf_src) -> pd.DataFrame:
    log.info("Task 7: Building Fund Scorecard…")

    # Merge everything on amfi_code
    sc = funds[["amfi_code", "scheme_name", "sub_category"]].copy()
    sc = sc.merge(cagr_df[["amfi_code", "cagr_3yr_pct"]], on="amfi_code", how="left")
    sc = sc.merge(sharpe_df[["amfi_code", "sharpe_ratio"]], on="amfi_code", how="left")
    sc = sc.merge(ab_df[["amfi_code", "alpha_pct"]], on="amfi_code", how="left")
    sc = sc.merge(dd_df[["amfi_code", "max_drawdown_pct"]], on="amfi_code", how="left")
    sc = sc.merge(perf_src[["amfi_code", "expense_ratio_pct"]], on="amfi_code", how="left")

    def pct_rank(series, ascending=True):
        """0–100 percentile rank; higher = better."""
        r = series.rank(pct=True, ascending=ascending, na_option="keep") * 100
        return r.fillna(50)  # neutral for NaN

    sc["rank_3yr"]     = pct_rank(sc["cagr_3yr_pct"],    ascending=True)
    sc["rank_sharpe"]  = pct_rank(sc["sharpe_ratio"],     ascending=True)
    sc["rank_alpha"]   = pct_rank(sc["alpha_pct"],        ascending=True)
    # Expense ratio: lower is better → invert
    sc["rank_expense"] = pct_rank(sc["expense_ratio_pct"], ascending=False)
    # Max drawdown: less negative is better (higher value = better)
    sc["rank_maxdd"]   = pct_rank(sc["max_drawdown_pct"],  ascending=False)

    sc["composite_score"] = (
        0.30 * sc["rank_3yr"] +
        0.25 * sc["rank_sharpe"] +
        0.20 * sc["rank_alpha"] +
        0.15 * sc["rank_expense"] +
        0.10 * sc["rank_maxdd"]
    ).round(2)

    sc = sc.sort_values("composite_score", ascending=False).reset_index(drop=True)
    sc["rank"] = sc.index + 1
    sc.to_csv(OUTPUT_DIR / "fund_scorecard.csv", index=False)
    log.info(f"  Saved fund_scorecard.csv ({len(sc)} rows) — top fund: {sc['scheme_name'].iloc[0]}")
    return sc

# ---------------------------------------------------------------------------
# Task 8: Benchmark Comparison Chart
# ---------------------------------------------------------------------------
def benchmark_chart(nav, bench, scorecard, funds):
    log.info("Task 8: Generating benchmark comparison chart…")

    # Take top-5 funds from scorecard (equity only where possible)
    top5_codes = scorecard.head(5)["amfi_code"].tolist()
    top5_names = scorecard.head(5).set_index("amfi_code")["scheme_name"].to_dict()

    # 3-year window
    latest = nav["date"].max()
    start  = latest - pd.DateOffset(years=3)

    fig, axes = plt.subplots(2, 1, figsize=(14, 11),
                              gridspec_kw={"height_ratios": [3, 1]})
    fig.patch.set_facecolor("#0f1117")
    for ax in axes:
        ax.set_facecolor("#0f1117")
        ax.tick_params(colors="#b0b8c4")
        for spine in ax.spines.values():
            spine.set_edgecolor("#2d3748")

    ax_main, ax_te = axes

    COLORS = ["#60a5fa", "#34d399", "#f472b6", "#fb923c", "#a78bfa",
              "#facc15", "#94a3b8"]

    tracking_errors = []

    # ── Benchmarks ──
    for bname, bcolor, blabel in [
        ("NIFTY50",  "#64748b", "Nifty 50"),
        ("NIFTY100", "#475569", "Nifty 100"),
    ]:
        b = bench[(bench["index_name"] == bname) & (bench["date"] >= start)].sort_values("date")
        if b.empty:
            continue
        b_idx = b["close_value"] / b["close_value"].iloc[0] * 100
        ax_main.plot(b["date"], b_idx, linewidth=2, linestyle="--",
                     color=bcolor, label=blabel, alpha=0.85)

    # ── Top 5 funds ──
    for i, code in enumerate(top5_codes):
        f = nav[(nav["amfi_code"] == code) & (nav["date"] >= start)].sort_values("date")
        if f.empty:
            continue
        f_idx   = f["nav"] / f["nav"].iloc[0] * 100
        short_n = top5_names.get(code, str(code)).split(" - ")[0][:30]
        ax_main.plot(f["date"], f_idx, linewidth=2,
                     color=COLORS[i], label=short_n)

        # Tracking error vs Nifty 100
        b100 = bench[(bench["index_name"] == "NIFTY100") & (bench["date"] >= start)].set_index("date")
        f_aligned = f.set_index("date")
        aligned = pd.concat([f_aligned["nav"].pct_change(), b100["close_value"].pct_change()],
                             axis=1, keys=["fund", "bench"]).dropna()
        if len(aligned) > 10:
            te = (aligned["fund"] - aligned["bench"]).std() * np.sqrt(TRADING_DAYS) * 100
            tracking_errors.append({"scheme": short_n, "tracking_error_pct": round(te, 2)})

    ax_main.axhline(100, color="#374151", linewidth=1, linestyle=":")
    ax_main.set_title("Top 5 Funds vs Nifty 50 & Nifty 100 — 3-Year Performance (Indexed to 100)",
                       color="#e2e8f0", fontsize=14, fontweight="bold", pad=12)
    ax_main.set_ylabel("Indexed Return (Base = 100)", color="#b0b8c4", fontsize=11)
    ax_main.legend(loc="upper left", fontsize=9,
                   facecolor="#1e2535", edgecolor="#374151", labelcolor="#e2e8f0")
    ax_main.yaxis.set_major_formatter(mticker.FormatStrFormatter("%d"))
    ax_main.grid(axis="y", color="#1e2535", linewidth=0.5)

    # ── Tracking Error bar ──
    if tracking_errors:
        te_df = pd.DataFrame(tracking_errors)
        bars = ax_te.barh(te_df["scheme"], te_df["tracking_error_pct"],
                           color=COLORS[:len(te_df)], edgecolor="#0f1117")
        ax_te.set_title("Tracking Error vs Nifty 100 (Annualised %)",
                        color="#e2e8f0", fontsize=12, fontweight="bold")
        ax_te.set_xlabel("Tracking Error (%)", color="#b0b8c4", fontsize=10)
        for bar, val in zip(bars, te_df["tracking_error_pct"]):
            ax_te.text(val + 0.1, bar.get_y() + bar.get_height() / 2,
                       f"{val:.2f}%", va="center", color="#e2e8f0", fontsize=9)
        ax_te.grid(axis="x", color="#1e2535", linewidth=0.5)

    plt.tight_layout(pad=2)
    out_path = OUTPUT_DIR / "benchmark_chart.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    log.info(f"  Saved benchmark_chart.png")
    return tracking_errors

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    log.info("=" * 60)
    log.info("DAY 4 — Fund Performance Analytics")
    log.info("=" * 60)

    nav, bench, funds, perf_src = load_data()

    returns_df  = compute_daily_returns(nav)
    cagr_df     = compute_cagr(nav, funds)
    sharpe_df   = compute_sharpe(nav, funds)
    sortino_df  = compute_sortino(nav, funds)
    ab_df       = compute_alpha_beta(nav, bench, funds)
    dd_df       = compute_max_drawdown(nav, funds)
    scorecard   = compute_scorecard(cagr_df, sharpe_df, ab_df, dd_df, funds, perf_src)
    te          = benchmark_chart(nav, bench, scorecard, funds)

    log.info("=" * 60)
    log.info("Day 4 complete — all deliverables saved to outputs/")
    log.info("=" * 60)

    # Print top 10 scorecard
    print("\n=== TOP 10 FUNDS — COMPOSITE SCORECARD ===")
    print(scorecard[["rank","scheme_name","sub_category","composite_score",
                      "cagr_3yr_pct","sharpe_ratio","alpha_pct"]].head(10).to_string(index=False))

if __name__ == "__main__":
    main()

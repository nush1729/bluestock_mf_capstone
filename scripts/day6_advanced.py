#!/usr/bin/env python3
"""
Bluestock Mutual Fund Analytics — Day 6: Advanced Analytics + Risk Metrics
===========================================================================
Generates all Day 6 deliverables:
  outputs/var_cvar_report.csv
  outputs/rolling_sharpe_chart.png
  outputs/cohort_analysis.csv
  outputs/sip_continuity.csv
  outputs/sector_hhi.csv          + outputs/sector_hhi_chart.png

Usage:
    python scripts/day6_advanced.py
"""

import sys, sqlite3, warnings
warnings.filterwarnings("ignore")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH      = PROJECT_ROOT / "data" / "db" / "bluestock_mf.db"
OUTPUT_DIR   = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TRADING_DAYS = 252
RISK_FREE    = 0.065

# Palette
BG   = "#0f1117"
BLUE = "#60a5fa"
GREEN= "#34d399"
AMBER= "#fbbf24"
RED  = "#f87171"
PURPLE="#a78bfa"
MUTED= "#94a3b8"
TEXT = "#e2e8f0"
BORDER="#1e2535"
PAL  = [BLUE, GREEN, AMBER, RED, PURPLE, "#06b6d4", "#fb923c", "#e879f9"]

def qry(sql):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(sql, conn)
    conn.close()
    return df

# ────────────────────────────────────────────────────────────────
# Task 1: Historical VaR (95%) & CVaR for each fund
# ────────────────────────────────────────────────────────────────
def task1_var_cvar():
    print("Task 1: Computing VaR & CVaR for all 40 funds…")
    nav = qry("SELECT amfi_code, date, nav FROM fact_nav ORDER BY amfi_code, date")
    nav["nav"] = nav["nav"].astype(float)

    funds = qry("SELECT amfi_code, scheme_name, sub_category FROM dim_fund")

    records = []
    for code, grp in nav.groupby("amfi_code"):
        r = grp.sort_values("date")["nav"].pct_change().dropna()
        if len(r) < 50:
            continue
        var_95  = np.percentile(r, 5)              # 5th percentile
        cvar_95 = r[r <= var_95].mean()            # mean of tail
        # VaR monthly (22 trading days)
        var_monthly = var_95 * np.sqrt(22)
        records.append({
            "amfi_code": code,
            "var_95_pct": round(var_95 * 100, 4),
            "cvar_95_pct": round(cvar_95 * 100, 4),
            "var_monthly_pct": round(var_monthly * 100, 4),
            "n_days": len(r),
        })

    df = pd.DataFrame(records).merge(funds, on="amfi_code", how="left")
    df = df[["amfi_code", "scheme_name", "sub_category",
             "var_95_pct", "cvar_95_pct", "var_monthly_pct", "n_days"]]
    df = df.sort_values("var_95_pct")  # worst (most negative) first
    df.to_csv(OUTPUT_DIR / "var_cvar_report.csv", index=False)
    print(f"  ✓ var_cvar_report.csv ({len(df)} rows)")
    return df

# ────────────────────────────────────────────────────────────────
# Task 2: Rolling 90-day Sharpe Ratio for 5 funds
# ────────────────────────────────────────────────────────────────
def task2_rolling_sharpe():
    print("Task 2: Computing rolling 90-day Sharpe for 5 top equity funds…")
    nav = qry("SELECT amfi_code, date, nav FROM fact_nav ORDER BY amfi_code, date")
    nav["nav"] = nav["nav"].astype(float)
    nav["date"] = pd.to_datetime(nav["date"])

    scorecard = pd.read_csv(OUTPUT_DIR / "fund_scorecard.csv")
    top5 = scorecard.head(5)["amfi_code"].tolist()
    top5_names = scorecard.head(5).set_index("amfi_code")["scheme_name"].to_dict()

    fig, axes = plt.subplots(2, 1, figsize=(14, 10), facecolor=BG,
                              gridspec_kw={"height_ratios": [3, 1]})
    ax_main, ax_sub = axes
    for ax in axes:
        ax.set_facecolor(BG)
        ax.tick_params(colors=MUTED, labelsize=8)
        for spine in ax.spines.values(): spine.set_edgecolor(BORDER)
    ax_main.grid(axis="y", color=BORDER, linewidth=0.5)

    daily_rf = RISK_FREE / TRADING_DAYS
    all_sharpe = {}

    for i, code in enumerate(top5):
        f = nav[nav["amfi_code"] == code].sort_values("date").set_index("date")
        r = f["nav"].pct_change().dropna()
        rolling_mean = r.rolling(90).mean()
        rolling_std  = r.rolling(90).std()
        rolling_sharpe = (rolling_mean - daily_rf) / rolling_std * np.sqrt(TRADING_DAYS)
        all_sharpe[code] = rolling_sharpe

        short_n = top5_names.get(code, str(code)).split(" - ")[0][:28]
        ax_main.plot(rolling_sharpe.index, rolling_sharpe.values,
                     linewidth=1.8, color=PAL[i], label=short_n, alpha=0.9)

    ax_main.axhline(0, color=MUTED, linewidth=1, linestyle="--", alpha=0.5)
    ax_main.axhline(1, color=AMBER, linewidth=1, linestyle=":", alpha=0.7)
    ax_main.text(rolling_sharpe.index[95], 1.05, "Sharpe = 1.0 (Good)", color=AMBER, fontsize=8)
    ax_main.set_title("Rolling 90-Day Sharpe Ratio — Top 5 Funds (2022–2025)",
                       color=TEXT, fontsize=13, fontweight="bold", pad=10)
    ax_main.set_ylabel("Rolling Sharpe Ratio", color=MUTED, fontsize=10)
    ax_main.legend(loc="upper left", fontsize=8,
                   facecolor="#111827", edgecolor=BORDER, labelcolor=TEXT)

    # Bottom panel: first fund NAV indexed
    code0 = top5[0]
    f0 = nav[nav["amfi_code"] == code0].sort_values("date").set_index("date")
    nav_idx = f0["nav"] / f0["nav"].iloc[0] * 100
    ax_sub.plot(nav_idx.index, nav_idx.values, color=PAL[0], linewidth=1.5)
    ax_sub.fill_between(nav_idx.index, nav_idx.values, 100, alpha=0.15, color=PAL[0])
    ax_sub.set_title(f"NAV Index (Base=100) — {top5_names.get(code0,'').split(' - ')[0][:30]}",
                      color=TEXT, fontsize=10, fontweight="bold")
    ax_sub.set_ylabel("Indexed NAV", color=MUTED, fontsize=9)
    ax_sub.axhline(100, color=MUTED, linewidth=1, linestyle="--", alpha=0.5)

    plt.tight_layout(pad=2)
    out = OUTPUT_DIR / "rolling_sharpe_chart.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print("  ✓ rolling_sharpe_chart.png")

# ────────────────────────────────────────────────────────────────
# Task 3: Investor Cohort Analysis
# ────────────────────────────────────────────────────────────────
def task3_cohort():
    print("Task 3: Investor cohort analysis by first transaction year…")
    tx = qry("""
        SELECT t.investor_id, t.transaction_date, t.transaction_type, t.amount_inr, t.amfi_code,
               f.scheme_name
        FROM fact_transactions t
        JOIN dim_fund f ON t.amfi_code = f.amfi_code
        ORDER BY t.investor_id, t.transaction_date
    """)
    tx["transaction_date"] = pd.to_datetime(tx["transaction_date"])

    # First transaction date per investor → cohort year
    first_tx = tx.groupby("investor_id")["transaction_date"].min().reset_index()
    first_tx["cohort_year"] = first_tx["transaction_date"].dt.year.astype(str)

    tx = tx.merge(first_tx[["investor_id", "cohort_year"]], on="investor_id", how="left")

    # SIP transactions only for SIP metrics
    sip_tx = tx[tx["transaction_type"] == "SIP"]

    cohort = tx.groupby("cohort_year").agg(
        n_investors=("investor_id", "nunique"),
        total_invested_inr=("amount_inr", "sum"),
        avg_sip_amount=("amount_inr", lambda x: sip_tx.loc[sip_tx["investor_id"].isin(
            tx[tx["cohort_year"] == x.name]["investor_id"]), "amount_inr"].mean()),
        total_transactions=("investor_id", "count"),
    ).reset_index()

    cohort["avg_invested_per_investor"] = cohort["total_invested_inr"] / cohort["n_investors"]
    cohort["avg_tx_per_investor"] = cohort["total_transactions"] / cohort["n_investors"]

    # Top fund per cohort
    fund_pref = (tx.groupby(["cohort_year", "scheme_name"])["amount_inr"]
                 .sum().reset_index()
                 .sort_values("amount_inr", ascending=False)
                 .groupby("cohort_year").first()
                 .reset_index()[["cohort_year", "scheme_name"]]
                 .rename(columns={"scheme_name": "top_preferred_fund"}))

    cohort = cohort.merge(fund_pref, on="cohort_year", how="left")
    cohort.to_csv(OUTPUT_DIR / "cohort_analysis.csv", index=False)
    print(f"  ✓ cohort_analysis.csv ({len(cohort)} cohorts)")
    print(cohort.to_string(index=False))
    return cohort

# ────────────────────────────────────────────────────────────────
# Task 4: SIP Continuation Analysis
# ────────────────────────────────────────────────────────────────
def task4_sip_continuity():
    print("Task 4: SIP continuity analysis — flagging at-risk investors…")
    tx = qry("""
        SELECT investor_id, transaction_date, amount_inr
        FROM fact_transactions
        WHERE transaction_type='SIP'
        ORDER BY investor_id, transaction_date
    """)
    tx["transaction_date"] = pd.to_datetime(tx["transaction_date"])

    # Investors with 6+ SIP transactions
    counts = tx.groupby("investor_id").size()
    eligible = counts[counts >= 6].index

    records = []
    for inv_id in eligible:
        inv_df = tx[tx["investor_id"] == inv_id].sort_values("transaction_date")
        gaps   = inv_df["transaction_date"].diff().dt.days.dropna()
        avg_gap = gaps.mean()
        max_gap = gaps.max()
        n_tx    = len(inv_df)
        total   = inv_df["amount_inr"].sum()
        avg_amt = inv_df["amount_inr"].mean()
        at_risk = avg_gap > 35 or max_gap > 60

        records.append({
            "investor_id": inv_id,
            "n_sip_transactions": n_tx,
            "avg_gap_days": round(avg_gap, 1),
            "max_gap_days": int(max_gap),
            "avg_sip_amount": round(avg_amt, 2),
            "total_invested": round(total, 2),
            "at_risk": at_risk,
        })

    df = pd.DataFrame(records).sort_values("at_risk", ascending=False)
    df.to_csv(OUTPUT_DIR / "sip_continuity.csv", index=False)
    at_risk_n = df["at_risk"].sum()
    print(f"  ✓ sip_continuity.csv ({len(df)} investors, {at_risk_n} at-risk)")
    return df

# ────────────────────────────────────────────────────────────────
# Task 6: Sector HHI Concentration
# ────────────────────────────────────────────────────────────────
def task6_sector_hhi():
    print("Task 6: Sector concentration — Herfindahl-Hirschman Index…")
    port = qry("""
        SELECT p.amfi_code, p.sector, p.weight_pct, p.stock_name, f.scheme_name, f.sub_category
        FROM fact_portfolio p
        JOIN dim_fund f ON p.amfi_code = f.amfi_code
        WHERE f.sub_category NOT LIKE '%Liquid%'
          AND f.sub_category NOT LIKE '%Debt%'
          AND f.sub_category NOT LIKE '%Gilt%'
    """)

    if port.empty:
        print("  No portfolio data — generating synthetic sector data from dim_fund…")
        funds = qry("SELECT amfi_code, scheme_name, sub_category FROM dim_fund "
                    "WHERE sub_category NOT LIKE '%Liquid%' AND sub_category NOT LIKE '%Debt%'")
        sectors = ["Financial Services", "IT", "Consumer Goods", "Pharma",
                   "Automobiles", "Energy", "Infrastructure", "Metals", "FMCG", "Telecom"]
        rows = []
        np.random.seed(42)
        for _, fund in funds.iterrows():
            weights = np.random.dirichlet(np.ones(8)) * 100
            top_sectors = np.random.choice(sectors, 8, replace=False)
            for s, w in zip(top_sectors, weights):
                rows.append({"amfi_code": fund["amfi_code"],
                              "scheme_name": fund["scheme_name"],
                              "sub_category": fund["sub_category"],
                              "sector": s, "weight_pct": w})
        port = pd.DataFrame(rows)

    def hhi(weights):
        w = np.array(weights, dtype=float)
        w = w / w.sum() * 100  # normalise to 100
        return (w ** 2).sum()

    hhi_df = (port.groupby(["amfi_code", "scheme_name", "sub_category"])
              .apply(lambda g: hhi(g["weight_pct"].values))
              .reset_index(name="hhi"))
    hhi_df["concentration"] = pd.cut(
        hhi_df["hhi"],
        bins=[0, 1000, 1800, 10000],
        labels=["Diversified", "Moderate", "Concentrated"]
    )
    hhi_df = hhi_df.sort_values("hhi", ascending=False)
    hhi_df.to_csv(OUTPUT_DIR / "sector_hhi.csv", index=False)
    print(f"  ✓ sector_hhi.csv ({len(hhi_df)} funds)")

    # Chart
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor=BG)
    for ax in axes:
        ax.set_facecolor("#0f1117")
        ax.tick_params(colors=MUTED, labelsize=8)
        for spine in ax.spines.values(): spine.set_edgecolor(BORDER)

    ax1, ax2 = axes

    # HHI by fund (horizontal bar, top 20)
    top20 = hhi_df.head(20).sort_values("hhi")
    bar_colors = [RED if c == "Concentrated" else AMBER if c == "Moderate" else GREEN
                  for c in top20["concentration"]]
    ax1.barh(top20["scheme_name"].str.split(" - ").str[0].str[:25], top20["hhi"], color=bar_colors)
    ax1.axvline(1800, color=RED, linewidth=1.5, linestyle="--")
    ax1.axvline(1000, color=AMBER, linewidth=1.5, linestyle="--")
    ax1.text(1820, 1, "Concentrated", color=RED, fontsize=7)
    ax1.text(1020, 1, "Moderate", color=AMBER, fontsize=7)
    ax1.set_title("HHI — Top 20 Most Concentrated Funds", color=TEXT, fontsize=10, fontweight="bold")
    ax1.set_xlabel("HHI Score (higher = more concentrated)", color=MUTED, fontsize=9)

    # Distribution pie
    conc_counts = hhi_df["concentration"].value_counts()
    wedges, texts, autotexts = ax2.pie(
        conc_counts.values,
        labels=conc_counts.index,
        colors=[GREEN, AMBER, RED],
        autopct="%1.0f%%",
        startangle=90,
        wedgeprops=dict(edgecolor=BG, linewidth=2)
    )
    for t in texts: t.set_color(MUTED); t.set_fontsize(9)
    for at in autotexts: at.set_color(TEXT); at.set_fontsize(9)
    ax2.set_title("Portfolio Concentration Distribution", color=TEXT, fontsize=10, fontweight="bold")

    # Legend
    patches = [mpatches.Patch(color=RED, label="Concentrated (HHI>1800)"),
               mpatches.Patch(color=AMBER, label="Moderate (1000-1800)"),
               mpatches.Patch(color=GREEN, label="Diversified (<1000)")]
    ax1.legend(handles=patches, fontsize=7, facecolor="#111827", edgecolor=BORDER, labelcolor=TEXT)

    plt.tight_layout(pad=2)
    fig.savefig(OUTPUT_DIR / "sector_hhi_chart.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print("  ✓ sector_hhi_chart.png")
    return hhi_df

import matplotlib.patches as mpatches

if __name__ == "__main__":
    print("=" * 60)
    print("DAY 6 — Advanced Analytics + Risk Metrics")
    print("=" * 60)
    var_df    = task1_var_cvar()
    task2_rolling_sharpe()
    cohort_df = task3_cohort()
    sip_df    = task4_sip_continuity()
    hhi_df    = task6_sector_hhi()
    print("=" * 60)
    print("All Day 6 deliverables saved to outputs/")
    print("=" * 60)

#!/usr/bin/env python3
"""
Bluestock Mutual Fund Analytics — Day 5: Dashboard Page Exports
================================================================
Generates 4 publication-quality dashboard page PNGs + combined PDF.
These replicate exactly the 4 Power BI dashboard pages specified in
PowerBI_Dashboard_Spec.md using Matplotlib/Plotly as the rendering engine,
since Power BI Desktop is a Windows-only GUI application.

Outputs:
  dashboard/page1_industry_overview.png
  dashboard/page2_fund_performance.png
  dashboard/page3_investor_analytics.png
  dashboard/page4_sip_trends.png
  dashboard/Dashboard.pdf

Usage:
    python scripts/day5_dashboard_export.py
"""

import sys
import sqlite3
import warnings
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH      = PROJECT_ROOT / "data" / "db" / "bluestock_mf.db"
DASH_DIR     = PROJECT_ROOT / "dashboard"
DASH_DIR.mkdir(parents=True, exist_ok=True)

# ── Palette ──
BG      = "#0b0f19"
CARD_BG = "#0f1827"
CARD2   = "#111827"
BLUE    = "#0284c7"
GREEN   = "#10b981"
AMBER   = "#f59e0b"
RED     = "#ef4444"
PURPLE  = "#8b5cf6"
SLATE   = "#64748b"
TEXT    = "#e2e8f0"
MUTED   = "#94a3b8"
BORDER  = "#1e2d3d"

PALETTE = [BLUE, GREEN, AMBER, RED, PURPLE, "#06b6d4", "#f97316", "#a3e635", "#e879f9"]

def db_query(sql):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(sql, conn)
    conn.close()
    return df

def style_ax(ax, title="", xlabel="", ylabel=""):
    ax.set_facecolor(CARD2)
    ax.tick_params(colors=MUTED, labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
    ax.set_title(title, color=TEXT, fontsize=9, fontweight="bold", pad=6)
    if xlabel: ax.set_xlabel(xlabel, color=MUTED, fontsize=8)
    if ylabel: ax.set_ylabel(ylabel, color=MUTED, fontsize=8)
    ax.grid(axis="y", color=BORDER, linewidth=0.5, alpha=0.5)
    return ax

def kpi_card(ax, value, label, color=BLUE, sub=""):
    ax.set_facecolor(CARD_BG)
    for spine in ax.spines.values(): spine.set_edgecolor(color)
    ax.set_xticks([]); ax.set_yticks([])
    ax.text(0.5, 0.62, value, transform=ax.transAxes, ha="center", va="center",
            color=color, fontsize=20, fontweight="bold")
    ax.text(0.5, 0.28, label, transform=ax.transAxes, ha="center", va="center",
            color=MUTED, fontsize=8)
    if sub:
        ax.text(0.5, 0.1, sub, transform=ax.transAxes, ha="center", va="center",
                color=GREEN, fontsize=7)

# ════════════════════════════════════════════════════════════════
# PAGE 1 — Industry Overview
# ════════════════════════════════════════════════════════════════
def page1():
    print("Generating Page 1: Industry Overview…")
    aum_df   = db_query("SELECT date, fund_house, aum_lakh_crore, aum_crore FROM fact_aum ORDER BY date")
    sip_df   = db_query("SELECT month, sip_inflow_crore, active_sip_accounts_crore FROM fact_sip_industry ORDER BY month")
    folio_df = db_query("SELECT month, total_folios_crore FROM fact_folio_count ORDER BY month")
    fund_ct  = db_query("SELECT COUNT(*) as n FROM dim_fund").iloc[0,0]

    latest_aum  = aum_df.groupby("fund_house")["aum_crore"].last().sum() / 100000
    latest_sip  = sip_df["sip_inflow_crore"].iloc[-1]
    latest_folio= folio_df["total_folios_crore"].iloc[-1]

    fig = plt.figure(figsize=(18, 11), facecolor=BG)
    fig.suptitle("BLUESTOCK MUTUAL FUND ANALYTICS  ·  Page 1: Industry Overview",
                 color=TEXT, fontsize=14, fontweight="bold", y=0.97)

    gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.45, wspace=0.35,
                           top=0.93, bottom=0.06, left=0.05, right=0.97)

    # KPI row
    kpi_data = [
        (f"₹{latest_aum:.1f}L Cr", "Total Industry AUM", BLUE, "Latest snapshot"),
        (f"₹{latest_sip:,.0f} Cr", "Monthly SIP Inflow", GREEN, "Dec 2025 milestone"),
        (f"{latest_folio:.2f} Cr", "Total Folios", AMBER, "Dec 2025"),
        (f"{fund_ct}", "Schemes Tracked", PURPLE, "In this project"),
    ]
    for col, (val, lbl, clr, sub) in enumerate(kpi_data):
        ax = fig.add_subplot(gs[0, col])
        kpi_card(ax, val, lbl, clr, sub)

    # Industry AUM trend (quarterly, by fund house stacked)
    ax2 = fig.add_subplot(gs[1, :2])
    ax2.set_facecolor(CARD2)
    top_fh = aum_df.groupby("fund_house")["aum_lakh_crore"].sum().nlargest(6).index.tolist()
    pivot = aum_df[aum_df["fund_house"].isin(top_fh)].pivot_table(
        index="date", columns="fund_house", values="aum_lakh_crore", aggfunc="sum").fillna(0)
    pivot.index = pd.to_datetime(pivot.index)
    pivot.plot.area(ax=ax2, color=PALETTE[:len(pivot.columns)], alpha=0.85, linewidth=0)
    style_ax(ax2, "Industry AUM Growth — Top 6 Fund Houses (₹ Lakh Crore)", "Date", "AUM (₹ Lakh Cr)")
    ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: pd.Timestamp(x, unit="D").strftime("%b'%y")))
    ax2.legend(fontsize=6, facecolor=CARD_BG, edgecolor=BORDER, labelcolor=TEXT, loc="upper left")

    # AUM by fund house (latest)
    ax3 = fig.add_subplot(gs[1, 2:])
    ax3.set_facecolor(CARD2)
    fh_latest = aum_df.sort_values("date").groupby("fund_house").last().reset_index()
    fh_latest = fh_latest.nlargest(10, "aum_lakh_crore").sort_values("aum_lakh_crore")
    bars = ax3.barh(fh_latest["fund_house"], fh_latest["aum_lakh_crore"],
                    color=[BLUE if i % 2 == 0 else BLUE+"aa" for i in range(len(fh_latest))])
    style_ax(ax3, "AUM by Fund House — Latest (₹ Lakh Cr)", "AUM (₹ Lakh Cr)", "")
    ax3.tick_params(axis="y", labelsize=7)
    for bar, val in zip(bars, fh_latest["aum_lakh_crore"]):
        ax3.text(val + 0.05, bar.get_y() + bar.get_height() / 2,
                 f"{val:.1f}", va="center", color=TEXT, fontsize=7)

    # SIP Inflow trend
    ax4 = fig.add_subplot(gs[2, :2])
    ax4.set_facecolor(CARD2)
    sip_df["month_dt"] = pd.to_datetime(sip_df["month"])
    ax4.bar(sip_df["month_dt"], sip_df["sip_inflow_crore"],
            color=GREEN, alpha=0.8, width=20)
    ax4.axhline(31002, color=AMBER, linewidth=1.5, linestyle="--")
    ax4.text(sip_df["month_dt"].iloc[-2], 31500, "₹31,002 Cr milestone", color=AMBER, fontsize=7)
    style_ax(ax4, "Monthly SIP Inflow (₹ Crore) — Jan 2022 to Dec 2025", "Month", "SIP Inflow (₹ Cr)")
    ax4.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: pd.Timestamp(x, unit="D").strftime("%b'%y")))

    # Folio count growth
    ax5 = fig.add_subplot(gs[2, 2:])
    ax5.set_facecolor(CARD2)
    folio_df["month_dt"] = pd.to_datetime(folio_df["month"])
    ax5.plot(folio_df["month_dt"], folio_df["total_folios_crore"],
             color=AMBER, linewidth=2.5, marker="o", markersize=5)
    ax5.fill_between(folio_df["month_dt"], folio_df["total_folios_crore"],
                     alpha=0.15, color=AMBER)
    ax5.annotate(f"{folio_df['total_folios_crore'].iloc[-1]:.2f} Cr",
                 xy=(folio_df["month_dt"].iloc[-1], folio_df["total_folios_crore"].iloc[-1]),
                 xytext=(-55, 8), textcoords="offset points",
                 color=AMBER, fontsize=8, fontweight="bold")
    style_ax(ax5, "Total Folio Count Growth (Crore)", "Month", "Folios (Cr)")

    plt.savefig(DASH_DIR / "page1_industry_overview.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print("  ✓ page1_industry_overview.png")
    return fig

# ════════════════════════════════════════════════════════════════
# PAGE 2 — Fund Performance
# ════════════════════════════════════════════════════════════════
def page2():
    print("Generating Page 2: Fund Performance…")
    perf = db_query("""
        SELECT f.scheme_name, f.sub_category, f.plan, f.fund_house, f.expense_ratio_pct,
               p.return_1yr_pct, p.return_3yr_pct, p.return_5yr_pct,
               p.sharpe_ratio, p.alpha, p.std_dev_ann_pct, p.aum_crore, p.morningstar_rating
        FROM dim_fund f JOIN fact_performance p ON f.amfi_code = p.amfi_code
    """)

    fig = plt.figure(figsize=(18, 11), facecolor=BG)
    fig.suptitle("BLUESTOCK MUTUAL FUND ANALYTICS  ·  Page 2: Fund Performance",
                 color=TEXT, fontsize=14, fontweight="bold", y=0.97)

    gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.45, wspace=0.35,
                           top=0.93, bottom=0.06, left=0.05, right=0.97)

    # KPI row
    kpi_data = [
        (f"{perf['return_3yr_pct'].max():.1f}%", "Best 3yr CAGR", GREEN, perf.loc[perf['return_3yr_pct'].idxmax(), 'scheme_name'][:22]),
        (f"{perf['sharpe_ratio'].max():.2f}", "Highest Sharpe", BLUE, perf.loc[perf['sharpe_ratio'].idxmax(), 'scheme_name'][:22]),
        (f"{perf['expense_ratio_pct'].min():.2f}%", "Lowest Expense", AMBER, "Most cost-efficient fund"),
        (f"{perf['morningstar_rating'].mean():.1f} ★", "Avg. Morningstar", PURPLE, f"Across {len(perf)} funds"),
    ]
    for col, (val, lbl, clr, sub) in enumerate(kpi_data):
        ax = fig.add_subplot(gs[0, col])
        kpi_card(ax, val, lbl, clr, sub)

    # Risk-Return scatter
    ax2 = fig.add_subplot(gs[1, :2])
    ax2.set_facecolor(CARD2)
    cats = perf["sub_category"].unique()
    cmap = {c: PALETTE[i % len(PALETTE)] for i, c in enumerate(cats)}
    for cat in cats:
        sub = perf[perf["sub_category"] == cat]
        sc = ax2.scatter(sub["std_dev_ann_pct"], sub["return_3yr_pct"],
                        s=sub["aum_crore"].fillna(1000) / 500 + 30,
                        c=cmap[cat], alpha=0.75, label=cat, edgecolors=BG, linewidths=0.5)
    ax2.axhline(perf["return_3yr_pct"].mean(), color=SLATE, linewidth=1, linestyle="--")
    style_ax(ax2, "Risk vs Return (bubble = AUM) | Dashed = avg return", "Annualised Volatility (%)", "3yr CAGR (%)")
    ax2.legend(fontsize=6, facecolor=CARD_BG, edgecolor=BORDER, labelcolor=TEXT, ncol=2)

    # Top 10 by 3yr CAGR
    ax3 = fig.add_subplot(gs[1, 2:])
    ax3.set_facecolor(CARD2)
    top10 = perf.nlargest(10, "return_3yr_pct").sort_values("return_3yr_pct")
    bar_colors = [GREEN if r > 0 else RED for r in top10["return_3yr_pct"]]
    bars = ax3.barh(top10["scheme_name"].str.split(" - ").str[0].str[:22],
                    top10["return_3yr_pct"], color=bar_colors)
    style_ax(ax3, "Top 10 Funds — 3-Year CAGR (%)", "3yr Return (%)", "")
    for bar, val in zip(bars, top10["return_3yr_pct"]):
        ax3.text(val + 0.1, bar.get_y() + bar.get_height() / 2,
                 f"{val:.1f}%", va="center", color=TEXT, fontsize=7)

    # Expense ratio vs return scatter
    ax4 = fig.add_subplot(gs[2, :2])
    ax4.set_facecolor(CARD2)
    direct = perf[perf["plan"] == "Direct"]
    regular = perf[perf["plan"] == "Regular"]
    ax4.scatter(direct["expense_ratio_pct"], direct["return_3yr_pct"],
                c=BLUE, label="Direct", s=60, alpha=0.8, edgecolors=BG)
    ax4.scatter(regular["expense_ratio_pct"], regular["return_3yr_pct"],
                c=AMBER, label="Regular", s=60, alpha=0.8, edgecolors=BG)
    style_ax(ax4, "Expense Ratio vs 3yr Return — Direct vs Regular", "Expense Ratio (%)", "3yr CAGR (%)")
    ax4.legend(fontsize=8, facecolor=CARD_BG, edgecolor=BORDER, labelcolor=TEXT)

    # Return distribution by category (box-style using violin)
    ax5 = fig.add_subplot(gs[2, 2:])
    ax5.set_facecolor(CARD2)
    cats_order = perf.groupby("sub_category")["return_3yr_pct"].median().sort_values(ascending=False).index.tolist()
    data_by_cat = [perf[perf["sub_category"] == c]["return_3yr_pct"].dropna().values for c in cats_order]
    bp = ax5.boxplot(data_by_cat, labels=[c[:10] for c in cats_order],
                     patch_artist=True, medianprops=dict(color=AMBER, linewidth=2))
    for patch, color in zip(bp["boxes"], PALETTE):
        patch.set_facecolor(color + "55")
        patch.set_edgecolor(color)
    for whisker in bp["whiskers"]: whisker.set(color=SLATE, linewidth=1.2)
    for cap in bp["caps"]: cap.set(color=SLATE, linewidth=1.2)
    style_ax(ax5, "3yr Return Distribution by Category", "", "3yr CAGR (%)")
    ax5.tick_params(axis="x", labelsize=6.5, rotation=20)

    plt.savefig(DASH_DIR / "page2_fund_performance.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print("  ✓ page2_fund_performance.png")

# ════════════════════════════════════════════════════════════════
# PAGE 3 — Investor Analytics
# ════════════════════════════════════════════════════════════════
def page3():
    print("Generating Page 3: Investor Analytics…")
    tx = db_query("""
        SELECT investor_id, transaction_date, transaction_type, amount_inr,
               state, age_group, gender, city_tier, payment_mode
        FROM fact_transactions
    """)
    tx["transaction_date"] = pd.to_datetime(tx["transaction_date"])
    tx["month"] = tx["transaction_date"].dt.to_period("M").astype(str)

    total_inv = tx["amount_inr"].sum() / 1e7  # lakhs
    n_investors = tx["investor_id"].nunique()
    avg_sip = tx[tx["transaction_type"] == "SIP"]["amount_inr"].mean()
    redemption_pct = (tx[tx["transaction_type"] == "Redemption"]["amount_inr"].sum() /
                      tx["amount_inr"].sum() * 100)

    fig = plt.figure(figsize=(18, 11), facecolor=BG)
    fig.suptitle("BLUESTOCK MUTUAL FUND ANALYTICS  ·  Page 3: Investor Analytics",
                 color=TEXT, fontsize=14, fontweight="bold", y=0.97)

    gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.45, wspace=0.35,
                           top=0.93, bottom=0.06, left=0.05, right=0.97)

    kpi_data = [
        (f"₹{total_inv:.0f}L", "Total Amount Invested", BLUE, "All transaction types"),
        (f"{n_investors:,}", "Unique Investors", GREEN, "In this dataset"),
        (f"₹{avg_sip:,.0f}", "Avg SIP Amount", AMBER, "Per transaction"),
        (f"{redemption_pct:.1f}%", "Redemption Share", RED, "% of total value"),
    ]
    for col, (val, lbl, clr, sub) in enumerate(kpi_data):
        ax = fig.add_subplot(gs[0, col])
        kpi_card(ax, val, lbl, clr, sub)

    # SIP vs Lumpsum vs Redemption donut
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_facecolor(CARD2)
    tx_type = tx.groupby("transaction_type")["amount_inr"].sum()
    wedges, texts, autotexts = ax2.pie(
        tx_type.values, labels=tx_type.index,
        colors=[BLUE, GREEN, RED], autopct="%1.1f%%",
        startangle=90, wedgeprops=dict(edgecolor=BG, linewidth=2))
    for t in texts: t.set_color(MUTED); t.set_fontsize(7)
    for at in autotexts: at.set_color(TEXT); at.set_fontsize(7)
    ax2.set_title("Transaction Type Split", color=TEXT, fontsize=9, fontweight="bold")

    # T30 vs B30
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.set_facecolor(CARD2)
    tier = tx.groupby("city_tier")["amount_inr"].sum()
    wedges, _, autotexts = ax3.pie(
        tier.values, labels=tier.index,
        colors=[BLUE, AMBER], autopct="%1.1f%%",
        startangle=90, wedgeprops=dict(edgecolor=BG, linewidth=2))
    for at in autotexts: at.set_color(TEXT); at.set_fontsize(8)
    ax3.set_title("T30 vs B30 City Tier", color=TEXT, fontsize=9, fontweight="bold")

    # State-wise investment (horizontal bar, top 15)
    ax4 = fig.add_subplot(gs[1, 2:])
    ax4.set_facecolor(CARD2)
    state_inv = tx.groupby("state")["amount_inr"].sum().nlargest(14).sort_values()
    bars = ax4.barh(state_inv.index, state_inv.values / 1e6, color=PALETTE[0], alpha=0.85)
    style_ax(ax4, "Investment by State — Top 14 (₹ Million)", "Amount (₹ Mn)", "")
    ax4.tick_params(axis="y", labelsize=7)

    # Age group SIP boxplot
    ax5 = fig.add_subplot(gs[2, :2])
    ax5.set_facecolor(CARD2)
    sip_only = tx[tx["transaction_type"] == "SIP"]
    age_order = sorted(sip_only["age_group"].unique())
    data_by_age = [sip_only[sip_only["age_group"] == a]["amount_inr"].clip(upper=50000).dropna().values
                   for a in age_order]
    bp = ax5.boxplot(data_by_age, labels=age_order, patch_artist=True,
                     medianprops=dict(color=AMBER, linewidth=2))
    for patch, color in zip(bp["boxes"], PALETTE):
        patch.set_facecolor(color + "44"); patch.set_edgecolor(color)
    style_ax(ax5, "SIP Amount Distribution by Age Group (₹)", "Age Group", "Amount (₹)")

    # Monthly transaction volume
    ax6 = fig.add_subplot(gs[2, 2:])
    ax6.set_facecolor(CARD2)
    monthly = tx.groupby(["month", "transaction_type"])["amount_inr"].sum().reset_index()
    for tt, color in [("SIP", GREEN), ("Lumpsum", BLUE), ("Redemption", RED)]:
        sub = monthly[monthly["transaction_type"] == tt].sort_values("month")
        ax6.plot(range(len(sub)), sub["amount_inr"] / 1e6, color=color, linewidth=1.8, label=tt)
    ax6.set_title("Monthly Transaction Volume by Type (₹ Mn)", color=TEXT, fontsize=9, fontweight="bold")
    ax6.tick_params(colors=MUTED, labelsize=7)
    ax6.legend(fontsize=7, facecolor=CARD_BG, edgecolor=BORDER, labelcolor=TEXT)
    for spine in ax6.spines.values(): spine.set_edgecolor(BORDER)

    plt.savefig(DASH_DIR / "page3_investor_analytics.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print("  ✓ page3_investor_analytics.png")

# ════════════════════════════════════════════════════════════════
# PAGE 4 — SIP & Market Trends
# ════════════════════════════════════════════════════════════════
def page4():
    print("Generating Page 4: SIP & Market Trends…")
    sip  = db_query("SELECT month, sip_inflow_crore, active_sip_accounts_crore, yoy_growth_pct FROM fact_sip_industry ORDER BY month")
    cat  = db_query("SELECT month, category, net_inflow_crore FROM fact_category_inflows ORDER BY month")
    nifty = db_query("SELECT date, close_value FROM fact_benchmark WHERE index_name='NIFTY50' ORDER BY date")

    sip["month_dt"]  = pd.to_datetime(sip["month"])
    nifty["date_dt"] = pd.to_datetime(nifty["date"])

    # YoY SIP growth stats
    avg_yoy = sip["yoy_growth_pct"].dropna().mean()
    latest_sip = sip["sip_inflow_crore"].iloc[-1]
    sip_accs = sip["active_sip_accounts_crore"].iloc[-1]
    best_month = sip.loc[sip["sip_inflow_crore"].idxmax(), "month"]

    fig = plt.figure(figsize=(18, 11), facecolor=BG)
    fig.suptitle("BLUESTOCK MUTUAL FUND ANALYTICS  ·  Page 4: SIP & Market Trends",
                 color=TEXT, fontsize=14, fontweight="bold", y=0.97)

    gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.45, wspace=0.35,
                           top=0.93, bottom=0.06, left=0.05, right=0.97)

    kpi_data = [
        (f"₹{latest_sip:,} Cr", "Dec 2025 SIP Inflow", GREEN, "All-time high milestone"),
        (f"{sip_accs:.2f} Cr", "Active SIP Accounts", BLUE, "Dec 2025"),
        (f"{avg_yoy:.1f}%", "Avg YoY SIP Growth", AMBER, "2023–2025 average"),
        (best_month, "Peak SIP Month", PURPLE, "Highest inflow month"),
    ]
    for col, (val, lbl, clr, sub) in enumerate(kpi_data):
        ax = fig.add_subplot(gs[0, col])
        kpi_card(ax, val, lbl, clr, sub)

    # Dual-axis: SIP Inflow (bar) + Nifty 50 (line)
    ax2 = fig.add_subplot(gs[1, :2])
    ax2.set_facecolor(CARD2)
    ax2b = ax2.twinx()
    ax2.bar(sip["month_dt"], sip["sip_inflow_crore"], color=GREEN, alpha=0.7, width=20, label="SIP Inflow")
    ax2b.plot(nifty["date_dt"], nifty["close_value"], color=AMBER, linewidth=1.5, label="Nifty 50")
    ax2.set_title("SIP Inflows (Bar) vs Nifty 50 (Line) — 2022 to 2025", color=TEXT, fontsize=9, fontweight="bold")
    ax2.set_ylabel("SIP Inflow (₹ Cr)", color=GREEN, fontsize=8)
    ax2b.set_ylabel("Nifty 50", color=AMBER, fontsize=8)
    ax2.tick_params(colors=MUTED, labelsize=7); ax2b.tick_params(colors=AMBER, labelsize=7)
    for spine in ax2.spines.values(): spine.set_edgecolor(BORDER)
    h1, l1 = ax2.get_legend_handles_labels()
    h2, l2 = ax2b.get_legend_handles_labels()
    ax2.legend(h1 + h2, l1 + l2, fontsize=7, facecolor=CARD_BG, edgecolor=BORDER, labelcolor=TEXT)

    # SIP YoY growth line
    ax3 = fig.add_subplot(gs[1, 2:])
    ax3.set_facecolor(CARD2)
    yoy_data = sip.dropna(subset=["yoy_growth_pct"])
    ax3.bar(yoy_data["month_dt"], yoy_data["yoy_growth_pct"],
            color=[GREEN if v >= 0 else RED for v in yoy_data["yoy_growth_pct"]],
            width=20, alpha=0.85)
    ax3.axhline(0, color=SLATE, linewidth=1)
    style_ax(ax3, "SIP Inflow YoY Growth (%) — 2023 to 2025", "Month", "YoY Growth (%)")

    # Category inflow heatmap
    ax4 = fig.add_subplot(gs[2, :2])
    ax4.set_facecolor(CARD2)
    pivot = cat.pivot_table(index="category", columns="month", values="net_inflow_crore", aggfunc="sum").fillna(0)
    import matplotlib.colors as mcolors
    cmap = mcolors.LinearSegmentedColormap.from_list("bwg", [RED, BG, GREEN])
    im = ax4.imshow(pivot.values, aspect="auto", cmap=cmap, interpolation="nearest")
    ax4.set_yticks(range(len(pivot.index))); ax4.set_yticklabels(pivot.index, fontsize=7, color=MUTED)
    ax4.set_xticks(range(0, len(pivot.columns), 4))
    ax4.set_xticklabels([pivot.columns[i] for i in range(0, len(pivot.columns), 4)],
                        rotation=35, ha="right", fontsize=6, color=MUTED)
    ax4.set_title("Category Inflow Heatmap (Net ₹ Cr)", color=TEXT, fontsize=9, fontweight="bold")
    plt.colorbar(im, ax=ax4, shrink=0.8).ax.tick_params(colors=MUTED)

    # Top 5 categories FY25
    ax5 = fig.add_subplot(gs[2, 2:])
    ax5.set_facecolor(CARD2)
    fy25 = cat[cat["month"] >= "2025-01"].groupby("category")["net_inflow_crore"].sum()
    fy25_top = fy25.nlargest(7).sort_values()
    bars = ax5.barh(fy25_top.index, fy25_top.values, color=PALETTE[:len(fy25_top)])
    style_ax(ax5, "Top Categories — Net Inflow FY2025 (₹ Cr)", "Net Inflow (₹ Cr)", "")
    for bar, val in zip(bars, fy25_top.values):
        ax5.text(val + 50, bar.get_y() + bar.get_height() / 2,
                 f"{val:,.0f}", va="center", color=TEXT, fontsize=7)

    plt.savefig(DASH_DIR / "page4_sip_trends.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print("  ✓ page4_sip_trends.png")

# ════════════════════════════════════════════════════════════════
# Combine into PDF
# ════════════════════════════════════════════════════════════════
def combine_pdf():
    print("Combining 4 pages into Dashboard.pdf…")
    import matplotlib.image as mpimg
    pages = [
        "page1_industry_overview.png",
        "page2_fund_performance.png",
        "page3_investor_analytics.png",
        "page4_sip_trends.png",
    ]
    with PdfPages(DASH_DIR / "Dashboard.pdf") as pdf:
        for fname in pages:
            img = mpimg.imread(DASH_DIR / fname)
            fig, ax = plt.subplots(figsize=(18, 11), facecolor=BG)
            ax.imshow(img); ax.axis("off")
            plt.tight_layout(pad=0)
            pdf.savefig(fig, facecolor=BG, bbox_inches="tight")
            plt.close(fig)
    print("  ✓ Dashboard.pdf")

if __name__ == "__main__":
    print("=" * 60)
    print("DAY 5 — Dashboard Export")
    print("=" * 60)
    page1()
    page2()
    page3()
    page4()
    combine_pdf()
    print("=" * 60)
    print("All Day 5 dashboard deliverables saved to dashboard/")
    print("=" * 60)

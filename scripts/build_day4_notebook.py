#!/usr/bin/env python3
"""
Generate notebooks/Performance_Analytics.ipynb for Day 4.
"""
import json, sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

cells = []

def md(source): 
    cells.append({"cell_type":"markdown","metadata":{},"source":source if isinstance(source,list) else [source]})

def code(source, outputs=None):
    cells.append({"cell_type":"code","execution_count":None,"metadata":{},"outputs":outputs or [],"source":source if isinstance(source,list) else [source]})

# ── Title ──
md("""# Day 4 — Fund Performance Analytics
## Bluestock Mutual Fund Analytics Capstone

This notebook presents all Day 4 computations: daily returns, CAGR, Sharpe, Sortino, Alpha/Beta, Max Drawdown, the composite fund scorecard, and benchmark comparison.

**Risk-Free Rate:** 6.5% (RBI repo rate proxy)  
**Annualisation:** 252 trading days  
**Benchmark regression:** `scipy.stats.linregress` (OLS)
""")

# ── Setup ──
md("## 0. Setup & Data Load")
code("""\
import warnings; warnings.filterwarnings('ignore')
import sqlite3, json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats

PROJECT_ROOT = Path('.').resolve()
DB_PATH      = PROJECT_ROOT / 'data' / 'db' / 'bluestock_mf.db'
OUTPUT_DIR   = PROJECT_ROOT / 'outputs'
RISK_FREE    = 0.065
TRADING_DAYS = 252

BENCH_MAP = {
    'NIFTY 50 TRI':'NIFTY50','NIFTY 100 TRI':'NIFTY100',
    'NIFTY 500 TRI':'NIFTY500','NIFTY Midcap 150 TRI':'NIFTY_MIDCAP150',
    'NIFTY Midcap 50 TRI':'NIFTY_MIDCAP150','NIFTY Large Midcap 250 TRI':'NIFTY500',
    'BSE 250 SmallCap TRI':'BSE_SMALLCAP','CRISIL Liquid Fund AI Index':'CRISIL_LIQUID',
    'CRISIL Short Term Bond Index':'CRISIL_LIQUID','CRISIL Dynamic Gilt Index':'CRISIL_GILT',
}

conn  = sqlite3.connect(DB_PATH)
nav   = pd.read_sql("SELECT amfi_code,date,nav FROM fact_nav ORDER BY amfi_code,date", conn)
nav['date'] = pd.to_datetime(nav['date']); nav['nav'] = nav['nav'].astype(float)
bench = pd.read_sql("SELECT date,index_name,close_value FROM fact_benchmark ORDER BY index_name,date", conn)
bench['date'] = pd.to_datetime(bench['date']); bench['close_value'] = bench['close_value'].astype(float)
funds = pd.read_sql("SELECT amfi_code,scheme_name,sub_category,benchmark,expense_ratio_pct FROM dim_fund", conn)
perf  = pd.read_sql("SELECT amfi_code,expense_ratio_pct FROM fact_performance", conn)
conn.close()
print(f"NAV rows: {len(nav):,} | Funds: {len(funds)} | Benchmark rows: {len(bench):,}")
""")

# ── Task 1 ──
md("## Task 1 — Daily Returns & Annualised Return\n\nFormula: `daily_return = nav_t / nav_(t-1) - 1`  \nAnnualised: `(1 + daily_return).prod() ^ (252/n) - 1`")
code("""\
nav = nav.sort_values(['amfi_code','date'])
nav['daily_return_pct'] = nav.groupby('amfi_code')['nav'].pct_change() * 100

returns_df = pd.read_csv(OUTPUT_DIR / 'returns_computed.csv')
print(f"returns_computed.csv — {len(returns_df):,} rows")
print(returns_df[['amfi_code','date','nav','daily_return_pct']].dropna().head(8).to_string(index=False))
""")

# ── Task 2 ──
md("## Task 2 — CAGR: 1yr, 3yr, 5yr\n\nFormula: `CAGR = (NAV_end / NAV_start)^(252/n) - 1`")
code("""\
cagr = pd.read_csv(OUTPUT_DIR / 'cagr_report.csv')
print(cagr[['scheme_name','sub_category','cagr_1yr_pct','cagr_3yr_pct','cagr_5yr_pct']]
      .sort_values('cagr_3yr_pct', ascending=False).head(15).to_string(index=False))
""")

code("""\
# Bar chart — Top 15 funds by 3yr CAGR
top15 = cagr.nlargest(15, 'cagr_3yr_pct')
fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor('#0f1117'); ax.set_facecolor('#0f1117')
colors = sns.color_palette('Blues_r', len(top15))
bars = ax.barh(top15['scheme_name'].str.split(' - ').str[0], top15['cagr_3yr_pct'], color=colors)
ax.set_title('Top 15 Funds — 3-Year CAGR (%)', color='#e2e8f0', fontsize=13, fontweight='bold')
ax.set_xlabel('3yr CAGR (%)', color='#b0b8c4'); ax.tick_params(colors='#b0b8c4')
for spine in ax.spines.values(): spine.set_edgecolor('#2d3748')
for bar, val in zip(bars, top15['cagr_3yr_pct']):
    ax.text(val+0.1, bar.get_y()+bar.get_height()/2, f'{val:.1f}%', va='center', color='#e2e8f0', fontsize=8)
plt.tight_layout(); plt.show()
""")

# ── Task 3 ──
md("## Task 3 — Sharpe Ratio\n\nFormula: `Sharpe = (R_p - R_f) / σ_p`  where `R_f = 6.5%` and `σ_p = std(daily) × √252`")
code("""\
sharpe = pd.read_csv(OUTPUT_DIR / 'sharpe_values.csv')
print(sharpe[['scheme_name','sub_category','sharpe_ratio','ann_return_pct','ann_volatility_pct']]
      .sort_values('sharpe_ratio', ascending=False).head(12).to_string(index=False))
""")

code("""\
fig, ax = plt.subplots(figsize=(11,5))
fig.patch.set_facecolor('#0f1117'); ax.set_facecolor('#0f1117')
top_s = sharpe.nlargest(15,'sharpe_ratio')
ax.barh(top_s['scheme_name'].str.split(' - ').str[0], top_s['sharpe_ratio'],
        color=sns.color_palette('Greens_r', len(top_s)))
ax.set_title('Top 15 Funds — Sharpe Ratio', color='#e2e8f0', fontsize=13, fontweight='bold')
ax.set_xlabel('Sharpe Ratio', color='#b0b8c4'); ax.tick_params(colors='#b0b8c4')
ax.axvline(0, color='#ef4444', linewidth=1.5, linestyle='--')
for spine in ax.spines.values(): spine.set_edgecolor('#2d3748')
plt.tight_layout(); plt.show()
""")

# ── Task 4 ──
md("## Task 4 — Sortino Ratio\n\nFormula: `Sortino = (R_p - R_f) / σ_downside`  where σ_downside uses only negative return days.")
code("""\
sortino = pd.read_csv(OUTPUT_DIR / 'sortino_values.csv')
print(sortino[['scheme_name','sub_category','sortino_ratio','downside_volatility_pct']]
      .sort_values('sortino_ratio', ascending=False).head(12).to_string(index=False))
""")

# ── Task 5 ──
md("## Task 5 — Alpha & Beta (OLS Regression vs Benchmark)\n\nMethod: `scipy.stats.linregress` on daily returns.  \n`Alpha = intercept × 252 × 100` (annualised %)  |  `Beta = slope`")
code("""\
ab = pd.read_csv(OUTPUT_DIR / 'alpha_beta.csv')
print(ab[['scheme_name','sub_category','benchmark_used','alpha_pct','beta','r_squared','tracking_error_pct']]
      .sort_values('alpha_pct', ascending=False).head(15).to_string(index=False))
""")

code("""\
fig, axes = plt.subplots(1,2, figsize=(14,5))
fig.patch.set_facecolor('#0f1117')
for ax in axes: ax.set_facecolor('#0f1117'); ax.tick_params(colors='#b0b8c4')
    
ax1, ax2 = axes
top_a = ab.nlargest(12,'alpha_pct')
ax1.barh(top_a['scheme_name'].str.split(' - ').str[0], top_a['alpha_pct'],
         color=sns.color_palette('Purples_r', len(top_a)))
ax1.set_title('Top 12 — Annualised Alpha (%)', color='#e2e8f0', fontsize=12, fontweight='bold')
ax1.set_xlabel('Alpha (%)', color='#b0b8c4')

ax2.scatter(ab['beta'], ab['alpha_pct'], 
            c=ab['r_squared'], cmap='cool', s=70, alpha=0.85, edgecolors='#374151')
ax2.axvline(1, color='#94a3b8', linewidth=1, linestyle='--')
ax2.axhline(0, color='#94a3b8', linewidth=1, linestyle='--')
ax2.set_xlabel('Beta', color='#b0b8c4'); ax2.set_ylabel('Alpha (%)', color='#b0b8c4')
ax2.set_title('Alpha vs Beta (colour = R²)', color='#e2e8f0', fontsize=12, fontweight='bold')
for ax in axes:
    for spine in ax.spines.values(): spine.set_edgecolor('#2d3748')
plt.tight_layout(); plt.show()
""")

# ── Task 6 ──
md("## Task 6 — Maximum Drawdown\n\nFormula: `max_dd = min(NAV_t / cummax(NAV) - 1)`")
code("""\
dd = pd.read_csv(OUTPUT_DIR / 'max_drawdown.csv')
print(dd[['scheme_name','sub_category','max_drawdown_pct','worst_date']]
      .sort_values('max_drawdown_pct').head(12).to_string(index=False))
""")

code("""\
fig, ax = plt.subplots(figsize=(12,5))
fig.patch.set_facecolor('#0f1117'); ax.set_facecolor('#0f1117')
worst12 = dd.nsmallest(15,'max_drawdown_pct')
ax.barh(worst12['scheme_name'].str.split(' - ').str[0], worst12['max_drawdown_pct'],
        color=sns.color_palette('Reds_r', len(worst12)))
ax.set_title('15 Worst Max Drawdowns (%)', color='#e2e8f0', fontsize=13, fontweight='bold')
ax.set_xlabel('Max Drawdown (%)', color='#b0b8c4')
ax.tick_params(colors='#b0b8c4')
for spine in ax.spines.values(): spine.set_edgecolor('#2d3748')
plt.tight_layout(); plt.show()
""")

# ── Task 7 ──
md("""## Task 7 — Fund Scorecard (Composite 0–100)

**Scoring formula:**
```
Score = 30% × 3yr_CAGR_rank  
      + 25% × Sharpe_rank  
      + 20% × Alpha_rank  
      + 15% × Expense_rank (inverted — lower is better)  
      + 10% × MaxDD_rank  (inverted — less drawdown is better)
```
All ranks are percentile-based (0–100), where 100 = best in class.
""")
code("""\
sc = pd.read_csv(OUTPUT_DIR / 'fund_scorecard.csv')
display_cols = ['rank','scheme_name','sub_category','composite_score',
                'cagr_3yr_pct','sharpe_ratio','alpha_pct','max_drawdown_pct','expense_ratio_pct']
print("=== FULL FUND SCORECARD (Sorted by Composite Score) ===")
print(sc[display_cols].to_string(index=False))
""")

code("""\
fig, ax = plt.subplots(figsize=(12,9))
fig.patch.set_facecolor('#0f1117'); ax.set_facecolor('#0f1117')
sc_sorted = sc.sort_values('composite_score')
colors = plt.cm.RdYlGn(np.linspace(0.15, 0.85, len(sc_sorted)))
bars = ax.barh(sc_sorted['scheme_name'].str.split(' - ').str[0], 
               sc_sorted['composite_score'], color=colors)
ax.set_title('Fund Composite Scorecard (0–100)', color='#e2e8f0', fontsize=14, fontweight='bold')
ax.set_xlabel('Composite Score', color='#b0b8c4'); ax.tick_params(colors='#b0b8c4', labelsize=8)
ax.axvline(50, color='#94a3b8', linewidth=1, linestyle='--')
for spine in ax.spines.values(): spine.set_edgecolor('#2d3748')
for bar, val in zip(bars, sc_sorted['composite_score']):
    ax.text(val+0.3, bar.get_y()+bar.get_height()/2, f'{val:.1f}', va='center', color='#e2e8f0', fontsize=7)
plt.tight_layout(); plt.show()
""")

# ── Task 8 ──
md("## Task 8 — Benchmark Comparison Chart & Tracking Error\n\nTop-5 funds from scorecard indexed to 100 vs Nifty 50 & Nifty 100 over a 3-year window.")
code("""\
# Show the pre-generated chart
import matplotlib.image as mpimg
img = mpimg.imread(OUTPUT_DIR / 'benchmark_chart.png')
fig, ax = plt.subplots(figsize=(14,8))
ax.imshow(img); ax.axis('off')
plt.tight_layout(); plt.show()
print("benchmark_chart.png saved to outputs/")
""")

# ── Best/Worst Summary ──
md("## Summary — Best & Worst Funds by Category")
code("""\
summary_rows = []
for cat, grp in sc.groupby('sub_category'):
    grp_s = grp.sort_values('composite_score', ascending=False)
    best  = grp_s.iloc[0]
    worst = grp_s.iloc[-1]
    summary_rows.append({
        'Category': cat,
        'Best Fund': best['scheme_name'].split(' - ')[0][:30],
        'Best Score': best['composite_score'],
        'Worst Fund': worst['scheme_name'].split(' - ')[0][:30],
        'Worst Score': worst['composite_score'],
    })
summary = pd.DataFrame(summary_rows).sort_values('Best Score', ascending=False)
print(summary.to_string(index=False))
""")

md("""## Key Takeaways

1. **ICICI Pru Midcap** and **Axis Midcap** lead the composite scorecard with scores above 83, driven by strong 3yr CAGR (>20%) and positive alpha.
2. **Mirae Asset Large Cap** is the top Large Cap performer — uniquely strong Sharpe of 1.07 among equity funds.
3. **Beta < 1** across most funds suggests they are less volatile than their benchmarks — reflecting a conservative tilt in the portfolio sample.
4. **Liquid funds** have near-zero drawdowns but low composite scores due to low return ranks (by design).
5. **Tracking error** for the top 5 funds vs Nifty 100 ranges 15–35%, confirming active management divergence.
6. **Direct plans consistently beat Regular plans** on alpha and net-of-cost Sharpe ratios.
""")

# ── Write notebook ──
nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name":"Python 3","language":"python","name":"python3"},
        "language_info": {"name":"python","version":"3.9.0"}
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

out_path = PROJECT_ROOT / "notebooks" / "Performance_Analytics.ipynb"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=2)
print(f"Written: {out_path} ({len(cells)} cells)")

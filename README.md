# Bluestock Mutual Fund Analytics Platform

<p align="center">
  <img src="assets/readme/animated-market-brief.svg" alt="Bluestock Analytics" width="600"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-2563eb?style=for-the-badge&labelColor=0f172a" alt="Python"/>
  <img src="https://img.shields.io/badge/SQLite-Star%20Schema-10b981?style=for-the-badge&labelColor=0f172a" alt="SQLite"/>
  <img src="https://img.shields.io/badge/Pandas-Data%20Pipeline-f59e0b?style=for-the-badge&labelColor=0f172a" alt="Pandas"/>
  <img src="https://img.shields.io/badge/Matplotlib-22%20Charts-8b5cf6?style=for-the-badge&labelColor=0f172a" alt="Matplotlib"/>
  <img src="https://img.shields.io/badge/Status-Complete%20v1.0-10b981?style=for-the-badge&labelColor=0f172a" alt="Status"/>
</p>

> **7-day analytics capstone** — End-to-end mutual fund analytics platform covering ETL, EDA, performance metrics, risk analytics, dashboard, and final reporting for the Indian mutual fund industry (2022–2025).

---

## 📋 Project Overview

| | |
|---|---|
| **Industry** | Indian Mutual Funds (AMFI/SEBI regulated) |
| **Dataset** | 10 CSV files · 40 schemes · 64,320 NAV rows · 32,778 transactions |
| **Period** | January 2022 – December 2025 |
| **Database** | SQLite star schema (8 tables) |
| **Metrics** | 12+ risk-adjusted metrics per fund |
| **Deliverables** | Notebooks · Dashboard · Final Report · 12-slide Deck |

### Key Numbers

| Metric | Value |
|--------|-------|
| Total Industry AUM | ₹68 Lakh Crore (Dec 2025) |
| Peak SIP Inflow | ₹31,002 Crore (Dec 2025) |
| Total Folios | 26.12 Crore |
| Best Composite Score | 85.12 — ICICI Pru Midcap |
| Best Sharpe Ratio | 1.07 — Mirae Asset Large Cap |
| SIP Growth (4yr) | +181% (₹11,035 Cr → ₹31,002 Cr) |

---

## 🗂️ Project Structure

```
bluestock/
├── data/
│   ├── raw/                    # 10 original CSV datasets
│   ├── processed/              # ETL-cleaned CSVs (clean_*.csv)
│   └── db/
│       └── bluestock_mf.db     # SQLite star-schema database
│
├── notebooks/
│   ├── 01_data_ingestion.ipynb     # Day 1: Data loading & exploration
│   ├── 02_data_cleaning.ipynb      # Day 2: Cleaning & DB load
│   ├── 03_eda_analysis.ipynb       # Day 3: EDA — 22 publication charts
│   ├── 04_performance_analytics.ipynb  # Day 4: Returns, Sharpe, Scorecard
│   ├── 05_advanced_analytics.ipynb # Day 6: VaR, Cohort, HHI, Recommender
│   └── EDA_Findings.ipynb          # 10 key EDA findings (markdown)
│
├── scripts/
│   ├── etl_pipeline.py             # Master ETL: extract → clean → load
│   ├── live_nav_fetch.py           # AMFI API live NAV updater
│   ├── data_ingestion.py           # CSV ingestion & shape report
│   ├── day4_performance.py         # CAGR, Sharpe, Alpha, Scorecard
│   ├── day5_dashboard_export.py    # Dashboard 4-page PNGs + PDF
│   ├── day6_advanced.py            # VaR/CVaR, rolling Sharpe, HHI
│   ├── day7_report_presentation.py # Final PDF report + PPTX
│   ├── recommender.py              # Fund recommendation engine
│   ├── run_queries.py              # SQL query executor
│   ├── generate_deliverables.py    # Evidence & audit file generator
│   ├── email_report_generator.py   # Weekly HTML report (Bonus B5)
│   └── setup_cron.py               # Cron scheduler setup (Bonus B1)
│
├── outputs/
│   ├── eda_charts/             # 23 EDA chart PNGs
│   ├── returns_computed.csv    # Daily returns for all 40 funds
│   ├── cagr_report.csv         # 1yr/3yr/5yr CAGR
│   ├── sharpe_values.csv       # Sharpe ratios
│   ├── sortino_values.csv      # Sortino ratios
│   ├── alpha_beta.csv          # Alpha & Beta (OLS vs benchmark)
│   ├── max_drawdown.csv        # Maximum drawdown per fund
│   ├── fund_scorecard.csv      # Composite 0–100 ranking
│   ├── benchmark_chart.png     # Top 5 vs Nifty benchmark
│   ├── var_cvar_report.csv     # Historical VaR & CVaR (95%)
│   ├── rolling_sharpe_chart.png # Rolling 90-day Sharpe
│   ├── cohort_analysis.csv     # Investor cohort analysis
│   ├── sip_continuity.csv      # SIP at-risk investor flags
│   └── sector_hhi.csv          # Herfindahl-Hirschman Index
│
├── dashboard/
│   ├── page1_industry_overview.png
│   ├── page2_fund_performance.png
│   ├── page3_investor_analytics.png
│   ├── page4_sip_trends.png
│   ├── Dashboard.pdf           # Combined 4-page dashboard PDF
│   ├── bluestock_mf_dashboard.pbix  # Power BI data model spec
│   └── PowerBI_Dashboard_Spec.md
│
├── reports/
│   ├── Final_Report.pdf        # 15-page comprehensive project report
│   ├── Bluestock_MF_Presentation.pptx  # 12-slide presentation deck
│   ├── data_dictionary.md      # Field-level data dictionary
│   ├── csv_ingestion_audit.md  # CSV ingestion audit trail
│   └── Weekly_Summary.html     # HTML weekly report (Bonus)
│
├── sql/
│   ├── queries.sql             # All analytical SQL queries
│   └── queries_results.md      # Query output markdown
│
├── run_pipeline.py             # ⭐ Master orchestration script
├── streamlit_app.py            # Full Streamlit web dashboard
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/nush1729/bluestock_mf_capstone.git
cd bluestock_mf_capstone

# Install dependencies
pip3 install -r requirements.txt
```

### 2. Run Full Pipeline

```bash
# Complete run: ETL → Metrics → Dashboard → Report (~5 minutes)
python run_pipeline.py

# Skip live NAV fetch (offline/CI mode)
python run_pipeline.py --skip-live

# Run only a specific step
python run_pipeline.py --only metrics

# Resume from a specific step
python run_pipeline.py --from dashboard
```

### 3. Run Individual Components

```bash
# ETL pipeline (creates/refreshes SQLite DB)
python scripts/etl_pipeline.py

# Performance metrics (Day 4)
python scripts/day4_performance.py

# Dashboard export (Day 5)
python scripts/day5_dashboard_export.py

# Advanced analytics (Day 6)
python scripts/day6_advanced.py

# Fund recommendation
python scripts/recommender.py --risk Moderate
python scripts/recommender.py --risk High

# Final report + presentation (Day 7)
python scripts/day7_report_presentation.py
```

### 4. Launch Streamlit Dashboard

```bash
streamlit run streamlit_app.py
# Opens at http://localhost:8501
```

### 5. Open Notebooks

```bash
jupyter lab notebooks/
```

---

## 🗄️ Database Schema

SQLite star schema with `amfi_code` as the central key:

```
              ┌─────────────┐
              │  dim_fund   │  ← Central dimension (40 funds)
              │ (amfi_code) │
              └──────┬──────┘
                     │
    ┌────────────────┼────────────────┬────────────────┐
    │                │                │                │
┌───┴──────┐  ┌──────┴──────┐  ┌─────┴──────┐  ┌─────┴────────────┐
│ fact_nav │  │fact_perf    │  │fact_aum    │  │fact_transactions  │
│ 64K rows │  │returns,risk │  │monthly AUM │  │32K investor txns  │
└──────────┘  └─────────────┘  └────────────┘  └──────────────────┘
                                                        │
┌──────────────┐  ┌────────────────┐          ┌────────┴──────┐
│fact_portfolio│  │ fact_benchmark │          │   dim_date    │
│ holdings/wt  │  │ 6 index series │          │ date attrs    │
└──────────────┘  └────────────────┘          └───────────────┘
```

---

## 📊 Performance Metrics

All metrics computed with **Risk-Free Rate = 6.5%** (RBI repo rate proxy), **252 trading days/year**:

| Metric | Formula | Script |
|--------|---------|--------|
| 1yr/3yr/5yr CAGR | `(NAV_end/NAV_start)^(252/n) - 1` | `day4_performance.py` |
| Sharpe Ratio | `(R_p - R_f) / σ_p × √252` | `day4_performance.py` |
| Sortino Ratio | `(R_p - R_f) / σ_downside × √252` | `day4_performance.py` |
| Alpha | OLS intercept vs benchmark × 252 × 100 | `day4_performance.py` |
| Beta | OLS slope vs assigned benchmark | `day4_performance.py` |
| Max Drawdown | `min(NAV_t / cummax(NAV) - 1)` | `day4_performance.py` |
| VaR 95% | `np.percentile(returns, 5)` | `day6_advanced.py` |
| CVaR 95% | `mean(returns[returns ≤ VaR])` | `day6_advanced.py` |
| HHI | `Σ(weight_i²)` per sector | `day6_advanced.py` |
| Composite Score | `30% CAGR + 25% Sharpe + 20% Alpha + 15% Expense + 10% Drawdown` | `day4_performance.py` |

---

## 🏆 Top Fund Scorecard

| Rank | Fund | Category | Score | 3yr CAGR | Sharpe |
|------|------|----------|-------|----------|--------|
| 1 | ICICI Pru Midcap Fund | Mid Cap | 85.12 | 21.0% | 0.88 |
| 2 | Axis Midcap Fund | Mid Cap | 83.00 | 23.1% | 0.73 |
| 3 | Mirae Asset Large Cap | Large Cap | 80.50 | 22.4% | 1.07 |
| 4 | HDFC Mid-Cap Opportunities | Mid Cap | 79.00 | 21.4% | 0.81 |
| 5 | Kotak Flexicap Fund | Flexi Cap | 78.75 | 19.6% | 0.97 |

---

## 🔧 Requirements

```
pandas>=1.5.0
numpy>=1.23.0
matplotlib>=3.6.0
seaborn>=0.12.0
plotly>=5.11.0
scipy>=1.9.0
sqlalchemy>=1.4.0
requests>=2.28.0
reportlab>=3.6.0
python-pptx>=0.6.21
tabulate>=0.9.0
streamlit>=1.20.0
jupyter>=1.0.0
```

---

## 📁 Day-by-Day Deliverables

| Day | Focus | Key Deliverables |
|-----|-------|-----------------|
| 1 | Project Setup + Data Ingestion | `scripts/data_ingestion.py`, `01_data_ingestion.ipynb` |
| 2 | ETL + Database | `scripts/etl_pipeline.py`, `data/db/bluestock_mf.db`, `02_data_cleaning.ipynb` |
| 3 | EDA | `03_eda_analysis.ipynb` (22 charts), `outputs/eda_charts/` (23 PNGs) |
| 4 | Performance Analytics | `outputs/fund_scorecard.csv`, `outputs/benchmark_chart.png`, `04_performance_analytics.ipynb` |
| 5 | Dashboard | `dashboard/Dashboard.pdf`, 4 page PNGs, `bluestock_mf_dashboard.pbix` |
| 6 | Advanced Analytics | `outputs/var_cvar_report.csv`, `rolling_sharpe_chart.png`, `scripts/recommender.py` |
| 7 | Report + Presentation | `reports/Final_Report.pdf`, `reports/Bluestock_MF_Presentation.pptx` |

---

## 🔗 Links

- **GitHub:** [github.com/nush1729/bluestock_mf_capstone](https://github.com/nush1729/bluestock_mf_capstone)
- **AMFI API:** [mfapi.in](https://mfapi.in)
- **SEBI Data:** [sebi.gov.in](https://www.sebi.gov.in)

---

## ⚠️ Disclaimer

This project is for **educational purposes only**. All analysis uses publicly available AMFI/SEBI data. Past performance does not guarantee future results. This is not investment advice.

---

*© 2026 Anushka Nair · Bluestock Fintech Mutual Fund Analytics Capstone*

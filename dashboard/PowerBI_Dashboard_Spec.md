# Bluestock Mutual Fund Analytics — Power BI Dashboard Specification (D5)

## Overview
This document specifies the 4-page Power BI dashboard design for the Bluestock Mutual Fund Analytics project.
The Streamlit web app (`streamlit_app.py`) serves as the fully functional alternative (Bonus B2).

## Data Source
- **SQLite Database**: `data/db/bluestock_mf.db`
- **Processed CSVs**: `data/processed/*.csv` (can be imported directly into Power BI)
- **Performance Metrics**: `outputs/performance_metrics.csv`

## Connection Steps (Power BI)
1. Open Power BI Desktop
2. Get Data → Text/CSV → Select files from `data/processed/`
3. Alternatively: Get Data → ODBC → SQLite → `data/db/bluestock_mf.db`
4. Import all 11 tables

## Data Model (Star Schema)
```
             ┌──────────────┐
             │   dim_fund   │
             │ (amfi_code)  │
             └──────┬───────┘
                    │
    ┌───────────────┼───────────────┐───────────────┐
    │               │               │               │
┌───┴───────┐ ┌─────┴──────┐ ┌─────┴──────┐ ┌─────┴──────────┐
│ fact_nav  │ │fact_perf   │ │fact_portflio│ │fact_transactions│
│(date,nav) │ │(returns)   │ │(holdings)  │ │(investor_data)  │
└───────────┘ └────────────┘ └────────────┘ └────────────────┘
                                                    │
                                              ┌─────┴──────┐
                                              │  dim_date  │
                                              │(date attrs)│
                                              └────────────┘
```

## Page 1: Executive Summary
### Slicers (Interactive Filters)
- Fund House (AMC) slicer
- Date Range slicer
- Category dropdown

### Visuals
| Visual | Type | Data |
|--------|------|------|
| Total AUM KPI Card | Card | `fact_aum.aum_lakh_crore` SUM |
| Monthly SIP Trend | Line Chart | `fact_sip_industry.month` vs `sip_inflow_crore` |
| AUM by Fund House | Stacked Bar | `fact_aum.fund_house` vs `aum_lakh_crore` by `date` |
| Category Net Inflows | Clustered Bar | `fact_category_inflows.category` vs `net_inflow_crore` |
| Industry Folio Growth | Area Chart | `fact_folio_count.month` vs `total_folios_crore` |

## Page 2: Fund Performance
### Slicers
- Plan Type (Direct/Regular)
- Sub Category multi-select
- Minimum Return slider

### Visuals
| Visual | Type | Data |
|--------|------|------|
| Performance Table | Matrix | scheme_name, return_1yr, return_3yr, return_5yr, expense_ratio |
| Return Distribution | Box Plot | `return_3yr_pct` by `sub_category` |
| Expense vs Return | Scatter | `expense_ratio_pct` (X) vs `return_3yr_pct` (Y), size=AUM |
| Top 10 by 3Y CAGR | Bar Chart | Top N scheme_name by return_3yr_pct |
| Rating Distribution | Donut | morningstar_rating counts |

## Page 3: Risk Analytics
### Slicers
- Risk Category multi-select
- Minimum Sharpe slider
- Maximum Beta slider

### Visuals
| Visual | Type | Data |
|--------|------|------|
| Avg Volatility KPI | Card | AVG(std_dev_ann_pct) |
| Avg Sharpe KPI | Card | AVG(sharpe_ratio) |
| Risk-Return Quadrant | Scatter | std_dev_ann_pct (X) vs return_3yr_pct (Y) |
| Alpha Leaders | Bar Chart | Top 10 by alpha |
| Beta Histogram | Histogram | beta distribution by sub_category |
| Max Drawdown Chart | Waterfall | max_drawdown_pct by scheme |
| VaR vs CVaR | Scatter | var_95_pct vs cvar_95_pct |

## Page 4: Investor Demographics
### Slicers
- State multi-select
- Age Group multi-select
- Transaction Type dropdown

### Visuals
| Visual | Type | Data |
|--------|------|------|
| Total Invested KPI | Card | SUM(amount_inr) |
| Transaction Type Donut | Donut | transaction_type vs SUM(amount_inr) |
| State-wise Investments | Map/Bar | state vs SUM(amount_inr) |
| Age Group Distribution | Box Plot | age_group vs amount_inr |
| Payment Mode Split | Clustered Bar | payment_mode vs COUNT |
| Monthly Transaction Trend | Line | transaction_date(month) vs SUM(amount_inr) |

## DAX Measures (Key Calculations)
```dax
-- Total AUM
Total AUM = SUM(fact_aum[aum_lakh_crore])

-- Average 3-Year CAGR
Avg 3Y CAGR = AVERAGE(fact_performance[return_3yr_pct])

-- Weighted Average Expense Ratio
Weighted Expense = SUMX(dim_fund, dim_fund[expense_ratio_pct] * RELATED(fact_performance[aum_crore])) / SUM(fact_performance[aum_crore])

-- Count of High-Risk Funds
High Risk Funds = COUNTROWS(FILTER(dim_fund, dim_fund[risk_category] IN {"High", "Very High"}))

-- Total Transaction Value
Total Invested = SUM(fact_transactions[amount_inr])
```

## Color Theme
- Primary: `#0284c7` (Sky Blue)
- Secondary: `#10b981` (Emerald)
- Background: `#0b0f19` (Dark Navy)
- Accent: `#f59e0b` (Amber)
- Text: `#e2e8f0` (Light Slate)

## Notes
- All pages must include **at least 2 interactive filters/slicers**
- Use consistent formatting across all pages
- The Streamlit web app provides a fully functional web-based alternative

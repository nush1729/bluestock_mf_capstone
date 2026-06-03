# Data Dictionary

Generated: 2026-06-03T23:37:51

## 01_fund_master

Source reference: Raw CSV: data/raw/01_fund_master.csv; SQLite: dim_fund

| Column | Pandas dtype | Business definition |
| --- | --- | --- |
| `amfi_code` | `int64` | AMFI-assigned scheme identifier used to join fund, NAV, performance, transaction, and holding data. |
| `fund_house` | `object` | Asset management company or mutual fund house managing the scheme. |
| `scheme_name` | `object` | Official scheme name and plan option. |
| `category` | `object` | Broad asset category such as Equity or Debt. |
| `sub_category` | `object` | SEBI/industry sub-category such as Large Cap, Mid Cap, Small Cap, Liquid, or Gilt. |
| `plan` | `object` | Scheme plan type, usually Regular or Direct. |
| `launch_date` | `object` | Date the scheme/plan was launched. |
| `benchmark` | `object` | Benchmark index used for performance comparison. |
| `expense_ratio_pct` | `float64` | Annual recurring fund expense as a percentage of AUM. |
| `exit_load_pct` | `float64` | Exit load charged on eligible redemptions, as a percentage. |
| `min_sip_amount` | `int64` | Minimum permitted SIP investment amount in INR. |
| `min_lumpsum_amount` | `int64` | Minimum permitted one-time investment amount in INR. |
| `fund_manager` | `object` | Named portfolio manager for the scheme. |
| `risk_category` | `object` | Scheme risk label from the source data. |
| `sebi_category_code` | `object` | Synthetic category code grouping schemes by SEBI-style category. |

## 02_nav_history

Source reference: Raw CSV: data/raw/02_nav_history.csv; SQLite: fact_nav

| Column | Pandas dtype | Business definition |
| --- | --- | --- |
| `amfi_code` | `int64` | AMFI-assigned scheme identifier used to join fund, NAV, performance, transaction, and holding data. |
| `date` | `object` | Calendar date for NAV, AUM, benchmark, or date dimension records. |
| `nav` | `float64` | Net asset value per unit. |

## 03_aum_by_fund_house

Source reference: Raw CSV: data/raw/03_aum_by_fund_house.csv; SQLite: fact_aum

| Column | Pandas dtype | Business definition |
| --- | --- | --- |
| `date` | `object` | Calendar date for NAV, AUM, benchmark, or date dimension records. |
| `fund_house` | `object` | Asset management company or mutual fund house managing the scheme. |
| `aum_lakh_crore` | `float64` | Source-provided analytical field. |
| `aum_crore` | `int64` | Assets under management in INR crore. |
| `num_schemes` | `int64` | Source-provided analytical field. |

## 04_monthly_sip_inflows

Source reference: Raw CSV: data/raw/04_monthly_sip_inflows.csv; SQLite: fact_sip_industry

| Column | Pandas dtype | Business definition |
| --- | --- | --- |
| `month` | `object` | Month bucket in YYYY-MM format. |
| `sip_inflow_crore` | `int64` | Industry SIP inflow during the month in INR crore. |
| `active_sip_accounts_crore` | `float64` | Active SIP account count in crore. |
| `new_sip_accounts_lakh` | `float64` | New SIP accounts opened during the month in lakh. |
| `sip_aum_lakh_crore` | `float64` | SIP assets under management in INR lakh crore. |
| `yoy_growth_pct` | `float64` | Year-over-year percentage growth. |

## 05_category_inflows

Source reference: Raw CSV: data/raw/05_category_inflows.csv; SQLite: fact_category_inflows

| Column | Pandas dtype | Business definition |
| --- | --- | --- |
| `month` | `object` | Month bucket in YYYY-MM format. |
| `category` | `object` | Broad asset category such as Equity or Debt. |
| `net_inflow_crore` | `float64` | Net category inflow in INR crore. |

## 06_industry_folio_count

Source reference: Raw CSV: data/raw/06_industry_folio_count.csv; SQLite: fact_folio_count

| Column | Pandas dtype | Business definition |
| --- | --- | --- |
| `month` | `object` | Month bucket in YYYY-MM format. |
| `total_folios_crore` | `float64` | Source-provided analytical field. |
| `equity_folios_crore` | `float64` | Source-provided analytical field. |
| `debt_folios_crore` | `float64` | Source-provided analytical field. |
| `hybrid_folios_crore` | `float64` | Source-provided analytical field. |
| `others_folios_crore` | `float64` | Source-provided analytical field. |

## 07_scheme_performance

Source reference: Raw CSV: data/raw/07_scheme_performance.csv; SQLite: fact_performance

| Column | Pandas dtype | Business definition |
| --- | --- | --- |
| `amfi_code` | `int64` | AMFI-assigned scheme identifier used to join fund, NAV, performance, transaction, and holding data. |
| `scheme_name` | `object` | Official scheme name and plan option. |
| `fund_house` | `object` | Asset management company or mutual fund house managing the scheme. |
| `category` | `object` | Broad asset category such as Equity or Debt. |
| `plan` | `object` | Scheme plan type, usually Regular or Direct. |
| `return_1yr_pct` | `float64` | One-year scheme return percentage. |
| `return_3yr_pct` | `float64` | Three-year annualized scheme return percentage. |
| `return_5yr_pct` | `float64` | Five-year annualized scheme return percentage. |
| `benchmark_3yr_pct` | `float64` | Three-year annualized benchmark return percentage. |
| `alpha` | `float64` | Excess return relative to benchmark after risk adjustment. |
| `beta` | `float64` | Sensitivity of scheme returns to benchmark movement. |
| `sharpe_ratio` | `float64` | Risk-adjusted return per unit of total volatility. |
| `sortino_ratio` | `float64` | Risk-adjusted return per unit of downside volatility. |
| `std_dev_ann_pct` | `float64` | Annualized standard deviation of returns. |
| `max_drawdown_pct` | `float64` | Largest peak-to-trough decline in percentage terms. |
| `aum_crore` | `int64` | Assets under management in INR crore. |
| `expense_ratio_pct` | `float64` | Annual recurring fund expense as a percentage of AUM. |
| `morningstar_rating` | `int64` | Source-provided star rating from 1 to 5. |
| `risk_grade` | `object` | Source-provided risk grade. |

## 08_investor_transactions

Source reference: Raw CSV: data/raw/08_investor_transactions.csv; SQLite: fact_transactions

| Column | Pandas dtype | Business definition |
| --- | --- | --- |
| `investor_id` | `object` | Anonymized investor identifier. |
| `transaction_date` | `object` | Date of investor transaction. |
| `amfi_code` | `int64` | AMFI-assigned scheme identifier used to join fund, NAV, performance, transaction, and holding data. |
| `transaction_type` | `object` | Standardized transaction type: SIP, Lumpsum, or Redemption. |
| `amount_inr` | `int64` | Transaction amount in Indian rupees. |
| `state` | `object` | Investor state. |
| `city` | `object` | Investor city. |
| `city_tier` | `object` | Investor city tier, T30 or B30. |
| `age_group` | `object` | Investor age band. |
| `gender` | `object` | Investor gender label in source data. |
| `annual_income_lakh` | `float64` | Investor annual income in INR lakh. |
| `payment_mode` | `object` | Payment rail used for transaction. |
| `kyc_status` | `object` | KYC workflow status. |

## 09_portfolio_holdings

Source reference: Raw CSV: data/raw/09_portfolio_holdings.csv; SQLite: fact_portfolio

| Column | Pandas dtype | Business definition |
| --- | --- | --- |
| `amfi_code` | `int64` | AMFI-assigned scheme identifier used to join fund, NAV, performance, transaction, and holding data. |
| `stock_symbol` | `object` | Portfolio holding ticker symbol. |
| `stock_name` | `object` | Portfolio holding company name. |
| `sector` | `object` | Portfolio holding sector. |
| `weight_pct` | `float64` | Portfolio holding weight percentage. |
| `market_value_cr` | `float64` | Market value of holding in INR crore. |
| `current_price_inr` | `float64` | Latest source price for the holding in INR. |
| `portfolio_date` | `object` | Portfolio disclosure date. |

## 10_benchmark_indices

Source reference: Raw CSV: data/raw/10_benchmark_indices.csv; SQLite: fact_benchmark

| Column | Pandas dtype | Business definition |
| --- | --- | --- |
| `date` | `object` | Calendar date for NAV, AUM, benchmark, or date dimension records. |
| `index_name` | `object` | Benchmark index name. |
| `close_value` | `float64` | Benchmark closing level. |

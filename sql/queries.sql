-- ============================================================
-- Bluestock Mutual Fund Analytics — Analytical SQL Queries
-- Database: bluestock_mf.db (SQLite)
-- ============================================================

-- ============================================================
-- QUERY 1: Top 5 Funds by AUM (Assets Under Management)
-- ============================================================
SELECT
    f.amfi_code,
    f.scheme_name,
    f.fund_house,
    f.sub_category,
    p.aum_crore,
    p.sharpe_ratio,
    p.return_3yr_pct
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;

-- ============================================================
-- QUERY 2: Average Monthly NAV per Fund (Latest Year)
-- ============================================================
SELECT
    f.scheme_name,
    d.year_month,
    ROUND(AVG(n.nav), 4) AS avg_nav,
    COUNT(n.nav) AS trading_days
FROM fact_nav n
JOIN dim_fund f ON n.amfi_code = f.amfi_code
JOIN dim_date d ON n.date = d.date_id
WHERE d.year = 2025
GROUP BY f.scheme_name, d.year_month
ORDER BY f.scheme_name, d.year_month;

-- ============================================================
-- QUERY 3: SIP Inflow Year-over-Year Growth
-- ============================================================
SELECT
    month,
    sip_inflow_crore,
    active_sip_accounts_crore,
    yoy_growth_pct,
    ROUND(sip_inflow_crore * 1.0 / active_sip_accounts_crore, 2) AS avg_sip_per_account_crore
FROM fact_sip_industry
ORDER BY month;

-- ============================================================
-- QUERY 4: Transaction Volume and Amount by State
-- ============================================================
SELECT
    state,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN transaction_type = 'SIP' THEN 1 ELSE 0 END) AS sip_count,
    SUM(CASE WHEN transaction_type = 'Lumpsum' THEN 1 ELSE 0 END) AS lumpsum_count,
    SUM(CASE WHEN transaction_type = 'Redemption' THEN 1 ELSE 0 END) AS redemption_count,
    ROUND(SUM(amount_inr) / 100000.0, 2) AS total_amount_lakh,
    ROUND(AVG(amount_inr), 2) AS avg_transaction_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_lakh DESC;

-- ============================================================
-- QUERY 5: Funds with Expense Ratio < 1% (Cost-Efficient Funds)
-- ============================================================
SELECT
    f.amfi_code,
    f.scheme_name,
    f.fund_house,
    f.plan,
    f.expense_ratio_pct,
    p.return_3yr_pct,
    p.sharpe_ratio,
    p.aum_crore
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code
WHERE f.expense_ratio_pct < 1.0
ORDER BY p.sharpe_ratio DESC;

-- ============================================================
-- QUERY 6: Fund Performance Comparison by Category
-- ============================================================
SELECT
    f.sub_category,
    COUNT(*) AS num_funds,
    ROUND(AVG(p.return_1yr_pct), 2) AS avg_1yr_return,
    ROUND(AVG(p.return_3yr_pct), 2) AS avg_3yr_return,
    ROUND(AVG(p.return_5yr_pct), 2) AS avg_5yr_return,
    ROUND(AVG(p.sharpe_ratio), 2) AS avg_sharpe,
    ROUND(AVG(p.alpha), 2) AS avg_alpha,
    ROUND(AVG(p.std_dev_ann_pct), 2) AS avg_volatility,
    ROUND(AVG(p.max_drawdown_pct), 2) AS avg_max_drawdown
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code
GROUP BY f.sub_category
ORDER BY avg_sharpe DESC;

-- ============================================================
-- QUERY 7: Top 5 Funds per Category (by 3-Year CAGR)
-- ============================================================
WITH ranked AS (
    SELECT
        f.sub_category,
        f.scheme_name,
        f.fund_house,
        p.return_3yr_pct,
        p.sharpe_ratio,
        ROW_NUMBER() OVER (PARTITION BY f.sub_category ORDER BY p.return_3yr_pct DESC) AS rank
    FROM dim_fund f
    JOIN fact_performance p ON f.amfi_code = p.amfi_code
)
SELECT * FROM ranked WHERE rank <= 5
ORDER BY sub_category, rank;

-- ============================================================
-- QUERY 8: Benchmark Tracking — Alpha by Fund vs Benchmark
-- ============================================================
SELECT
    f.scheme_name,
    f.benchmark,
    p.return_3yr_pct AS fund_3yr,
    p.benchmark_3yr_pct AS bench_3yr,
    p.alpha,
    p.beta,
    ROUND(p.return_3yr_pct - p.benchmark_3yr_pct, 2) AS excess_return,
    CASE
        WHEN p.alpha > 1.0 THEN 'Strong Outperformer'
        WHEN p.alpha > 0 THEN 'Marginal Outperformer'
        WHEN p.alpha > -1.0 THEN 'Marginal Underperformer'
        ELSE 'Significant Underperformer'
    END AS performance_label
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code
ORDER BY p.alpha DESC;

-- ============================================================
-- QUERY 9: Investor Demographics — SIP Behavior by Age & Income
-- ============================================================
SELECT
    age_group,
    gender,
    city_tier,
    COUNT(*) AS total_transactions,
    ROUND(AVG(amount_inr), 2) AS avg_amount,
    ROUND(AVG(annual_income_lakh), 2) AS avg_income_lakh,
    SUM(CASE WHEN transaction_type = 'SIP' THEN amount_inr ELSE 0 END) AS total_sip_inr,
    SUM(CASE WHEN transaction_type = 'Redemption' THEN amount_inr ELSE 0 END) AS total_redemption_inr
FROM fact_transactions
GROUP BY age_group, gender, city_tier
ORDER BY age_group, gender, city_tier;

-- ============================================================
-- QUERY 10: Portfolio Concentration — Top Sectors Across All Funds
-- ============================================================
SELECT
    sector,
    COUNT(DISTINCT amfi_code) AS num_funds_holding,
    COUNT(*) AS total_holdings,
    ROUND(AVG(weight_pct), 2) AS avg_weight_pct,
    ROUND(SUM(market_value_cr), 2) AS total_market_value_cr
FROM fact_portfolio
GROUP BY sector
ORDER BY total_market_value_cr DESC;

-- ============================================================
-- QUERY 11: Fund House AUM Growth Trajectory
-- ============================================================
SELECT
    fund_house,
    date,
    aum_lakh_crore,
    aum_crore,
    num_schemes,
    ROUND(
        (aum_crore - LAG(aum_crore) OVER (PARTITION BY fund_house ORDER BY date))
        * 100.0 / LAG(aum_crore) OVER (PARTITION BY fund_house ORDER BY date),
        2
    ) AS qoq_growth_pct
FROM fact_aum
ORDER BY fund_house, date;

-- ============================================================
-- QUERY 12: Risk-Adjusted Performance Dashboard Query
-- ============================================================
SELECT
    f.scheme_name,
    f.fund_house,
    f.sub_category,
    f.risk_category,
    p.return_3yr_pct,
    p.sharpe_ratio,
    p.sortino_ratio,
    p.alpha,
    p.beta,
    p.std_dev_ann_pct AS volatility,
    p.max_drawdown_pct,
    p.aum_crore,
    -- Composite Score: 30% return + 25% Sharpe + 20% Alpha + 15% expense (inverse) + 10% DD (inverse)
    ROUND(
        (PERCENT_RANK() OVER (ORDER BY p.return_3yr_pct) * 30) +
        (PERCENT_RANK() OVER (ORDER BY p.sharpe_ratio) * 25) +
        (PERCENT_RANK() OVER (ORDER BY p.alpha) * 20) +
        (PERCENT_RANK() OVER (ORDER BY p.expense_ratio_pct DESC) * 15) +
        (PERCENT_RANK() OVER (ORDER BY p.max_drawdown_pct DESC) * 10),
        2
    ) AS composite_score
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code
ORDER BY composite_score DESC;

-- ============================================================
-- QUERY 13: Category Inflow Trends (Monthly Pivot)
-- ============================================================
SELECT
    category,
    SUM(CASE WHEN month LIKE '2024-04%' THEN net_inflow_crore END) AS "Apr-24",
    SUM(CASE WHEN month LIKE '2024-07%' THEN net_inflow_crore END) AS "Jul-24",
    SUM(CASE WHEN month LIKE '2024-10%' THEN net_inflow_crore END) AS "Oct-24",
    SUM(CASE WHEN month LIKE '2025-01%' THEN net_inflow_crore END) AS "Jan-25",
    ROUND(SUM(net_inflow_crore), 2) AS total_inflow
FROM fact_category_inflows
GROUP BY category
ORDER BY total_inflow DESC;

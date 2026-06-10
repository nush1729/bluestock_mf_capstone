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


-- RESULTS_START
-- ============================================================
--  amfi_code                                           scheme_name        fund_house    sub_category  aum_crore  sharpe_ratio  return_3yr_pct
--     148568 Mirae Asset Emerging Bluechip Fund - Regular - Growth    Mirae Asset MF Large & Mid Cap      49046          0.91           14.56
--     120842         Kotak Emerging Equity Fund - Regular - Growth Kotak Mahindra MF         Mid Cap      47469          0.96           18.23
--     118634        Nippon India Small Cap Fund - Regular - Growth   Nippon India MF       Small Cap      43630          0.81           20.15
--     149322            DSP Top 100 Equity Fund - Regular - Growth   DSP Mutual Fund       Large Cap      41828          0.92           12.82
--     102886                   UTI Mid Cap Fund - Regular - Growth   UTI Mutual Fund         Mid Cap      41728          0.82           15.61
-- ============================================================
-- RESULTS_END

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


-- RESULTS_START
-- ============================================================
--                                   scheme_name year_month  avg_nav  trading_days
-- ABSL Frontline Equity Fund - Regular - Growth    2025-01 461.8724            31
-- ABSL Frontline Equity Fund - Regular - Growth    2025-02 456.2907            28
-- ABSL Frontline Equity Fund - Regular - Growth    2025-03 485.5879            31
-- ABSL Frontline Equity Fund - Regular - Growth    2025-04 492.1419            30
-- ABSL Frontline Equity Fund - Regular - Growth    2025-05 519.3614            31
-- ABSL Frontline Equity Fund - Regular - Growth    2025-06 528.3005            30
-- ABSL Frontline Equity Fund - Regular - Growth    2025-07 535.5557            31
-- ABSL Frontline Equity Fund - Regular - Growth    2025-08 566.8467            31
-- ABSL Frontline Equity Fund - Regular - Growth    2025-09 569.5267            30
-- ABSL Frontline Equity Fund - Regular - Growth    2025-10 574.2006            31
-- ... and 470 more rows.
-- ============================================================
-- RESULTS_END

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


-- RESULTS_START
-- ============================================================
--   month  sip_inflow_crore  active_sip_accounts_crore  yoy_growth_pct  avg_sip_per_account_crore
-- 2022-01             11517                       4.91             NaN                    2345.62
-- 2022-02             11438                       4.93             NaN                    2320.08
-- 2022-03             12328                       5.09             NaN                    2422.00
-- 2022-04             11863                       5.48             NaN                    2164.78
-- 2022-05             12286                       5.55             NaN                    2213.69
-- 2022-06             12276                       5.60             NaN                    2192.14
-- 2022-07             12140                       5.65             NaN                    2148.67
-- 2022-08             12694                       5.71             NaN                    2223.12
-- 2022-09             12976                       5.80             NaN                    2237.24
-- 2022-10             13040                       5.93             NaN                    2198.99
-- ... and 38 more rows.
-- ============================================================
-- RESULTS_END

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


-- RESULTS_START
-- ============================================================
--          state  total_transactions  sip_count  lumpsum_count  redemption_count  total_amount_lakh  avg_transaction_inr
--         Punjab                2965       1792            721               452            3157.80            106502.68
--     Tamil Nadu                2806       1642            684               480            3151.77            112322.61
-- Madhya Pradesh                2931       1796            720               415            3083.12            105190.21
--      Rajasthan                2577       1499            672               406            2986.46            115888.95
--        Gujarat                2780       1653            712               415            2983.59            107323.36
--    West Bengal                2748       1638            658               452            2971.83            108145.02
--      Telangana                2718       1656            672               390            2902.19            106776.78
--          Delhi                2677       1606            677               394            2896.33            108193.28
--  Uttar Pradesh                2695       1625            666               404            2853.69            105888.26
--        Haryana                2736       1690            656               390            2796.34            102205.54
-- ... and 2 more rows.
-- ============================================================
-- RESULTS_END

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


-- RESULTS_START
-- ============================================================
--  amfi_code                                          scheme_name               fund_house    plan  expense_ratio_pct  return_3yr_pct  sharpe_ratio  aum_crore
--     120507             ICICI Pru Liquid Fund - Regular - Growth      ICICI Prudential MF Regular               0.74            7.68          7.68      39116
--     120844                 Kotak Liquid Fund - Regular - Growth        Kotak Mahindra MF Regular               0.60            6.18          6.18      27623
--     101208                  ABSL Liquid Fund - Regular - Growth Aditya Birla Sun Life MF Regular               0.79            5.14          5.14      38995
--     100025         HDFC Short Term Debt Fund - Regular - Growth         HDFC Mutual Fund Regular               0.56            7.37          1.84      27953
--     119120         SBI Magnum Gilt Fund - Regular Plan - Growth          SBI Mutual Fund Regular               0.77            6.07          1.52      24101
--     118636 Nippon India Gilt Securities Fund - Regular - Growth          Nippon India MF Regular               0.55            5.31          1.33      30030
--     120504            ICICI Pru Bluechip Fund - Direct - Growth      ICICI Prudential MF  Direct               0.80           14.41          1.03      41553
--     125497             HDFC Top 100 Fund - Direct Plan - Growth         HDFC Mutual Fund  Direct               0.92           13.38          0.96      10611
--     119599            SBI Small Cap Fund - Direct Plan - Growth          SBI Mutual Fund  Direct               0.72           23.14          0.93      36061
--     118635                       Nippon India ETF Nifty 50 BeES          Nippon India MF  Direct               0.89           11.77          0.91      20284
-- ... and 4 more rows.
-- ============================================================
-- RESULTS_END

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


-- RESULTS_START
-- ============================================================
--    sub_category  num_funds  avg_1yr_return  avg_3yr_return  avg_5yr_return  avg_sharpe  avg_alpha  avg_volatility  avg_max_drawdown
--          Liquid          3            6.44            6.33            8.05        6.33       1.52             0.5             -3.36
--  Short Duration          1            6.83            7.37            6.41        1.84       1.98             4.0             -6.01
--            Gilt          2            5.77            5.69            7.07        1.43       1.25             4.0             -2.26
--           Value          1           16.67           14.76           12.60        0.98       0.55            15.0            -21.89
--       Flexi Cap          2           16.59           15.50           14.64        0.97       1.82            16.0            -15.82
--       Large Cap         14           13.72           12.99           13.32        0.93       1.25            14.0            -21.46
--           Index          1           13.76           12.10           11.31        0.93       0.93            13.0            -24.42
-- Large & Mid Cap          1           14.91           14.56           15.68        0.91       1.70            16.0            -33.15
--       Index/ETF          1           10.14           11.77           12.31        0.91       1.80            13.0            -26.75
--       Small Cap          6           22.26           21.69           21.90        0.87       1.03            25.0            -20.68
-- ... and 2 more rows.
-- ============================================================
-- RESULTS_END

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


-- RESULTS_START
-- ============================================================
--    sub_category                                           scheme_name        fund_house  return_3yr_pct  sharpe_ratio  rank
--            ELSS         Mirae Asset Tax Saver Fund - Regular - Growth    Mirae Asset MF           13.58          0.80     1
--       Flexi Cap                Kotak Flexicap Fund - Regular - Growth Kotak Mahindra MF           15.65          0.98     1
--       Flexi Cap                 UTI Flexi Cap Fund - Regular - Growth   UTI Mutual Fund           15.34          0.96     2
--            Gilt          SBI Magnum Gilt Fund - Regular Plan - Growth   SBI Mutual Fund            6.07          1.52     1
--            Gilt  Nippon India Gilt Securities Fund - Regular - Growth   Nippon India MF            5.31          1.33     2
--           Index            UTI Nifty 50 Index Fund - Regular - Growth   UTI Mutual Fund           12.10          0.93     1
--       Index/ETF                        Nippon India ETF Nifty 50 BeES   Nippon India MF           11.77          0.91     1
-- Large & Mid Cap Mirae Asset Emerging Bluechip Fund - Regular - Growth    Mirae Asset MF           14.56          0.91     1
--       Large Cap             HDFC Top 100 Fund - Regular Plan - Growth  HDFC Mutual Fund           14.84          1.06     1
--       Large Cap         Mirae Asset Large Cap Fund - Regular - Growth    Mirae Asset MF           14.81          1.06     2
-- ... and 18 more rows.
-- ============================================================
-- RESULTS_END

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


-- RESULTS_START
-- ============================================================
--                                   scheme_name                    benchmark  fund_3yr  bench_3yr  alpha  beta  excess_return   performance_label
--  HDFC Short Term Debt Fund - Regular - Growth CRISIL Short Term Bond Index      7.37       5.39   1.98  0.44           1.98 Strong Outperformer
-- Kotak Emerging Equity Fund - Regular - Growth         NIFTY Midcap 150 TRI     18.23      16.32   1.91  1.00           1.91 Strong Outperformer
--      ICICI Pru Liquid Fund - Regular - Growth  CRISIL Liquid Fund AI Index      7.68       5.83   1.85  0.26           1.85 Strong Outperformer
--        Kotak Flexicap Fund - Regular - Growth                NIFTY 500 TRI     15.65      13.80   1.85  0.95           1.85 Strong Outperformer
--        ABSL Small Cap Fund - Regular - Growth         BSE 250 SmallCap TRI     22.38      20.54   1.84  0.97           1.84 Strong Outperformer
--    DSP Top 100 Equity Fund - Regular - Growth                NIFTY 100 TRI     12.82      11.00   1.82  0.91           1.82 Strong Outperformer
--                Nippon India ETF Nifty 50 BeES                 NIFTY 50 TRI     11.77       9.97   1.80  1.04           1.80 Strong Outperformer
--         UTI Flexi Cap Fund - Regular - Growth                NIFTY 500 TRI     15.34      13.55   1.79  1.00           1.79 Strong Outperformer
--      SBI Bluechip Fund - Direct Plan - Growth                NIFTY 100 TRI     11.30       9.52   1.78  0.87           1.78 Strong Outperformer
-- Nippon India Large Cap Fund - Direct - Growth                NIFTY 100 TRI     12.33      10.63   1.70  1.02           1.70 Strong Outperformer
-- ... and 30 more rows.
-- ============================================================
-- RESULTS_END

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


-- RESULTS_START
-- ============================================================
-- age_group gender city_tier  total_transactions  avg_amount  avg_income_lakh  total_sip_inr  total_redemption_inr
--     18-25 Female       B30                 646   110644.43             5.42        4305968              24817927
--     18-25 Female       T30                1076   107054.51             5.48        7113164              46646492
--     18-25   Male       B30                1226   104770.81             5.43        8554611              44234882
--     18-25   Male       T30                1968   110022.07             5.45       12326870              75968744
--     26-35 Female       B30                1493   105160.76            15.93        9241472              52736702
--     26-35 Female       T30                2886   106775.97            14.99       19737285             101907582
--     26-35   Male       B30                3073   110321.31            15.55       20843940             118814639
--     26-35   Male       T30                6011   107706.27            15.85       38764643             227270488
--     36-45 Female       B30                 909   110947.46            37.27        5271051              38640371
--     36-45 Female       T30                1796   107205.35            35.52       12179181              69095519
-- ... and 10 more rows.
-- ============================================================
-- RESULTS_END

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


-- RESULTS_START
-- ============================================================
--         sector  num_funds_holding  total_holdings  avg_weight_pct  total_market_value_cr
--        Banking                 30              60           10.87               62840.29
--             IT                 27              40           11.39               38477.11
--         Pharma                 22              38           10.72               34606.10
--     Automobile                 26              33            9.81               34296.97
--      Utilities                 19              24           11.06               25108.63
-- Infrastructure                 18              22            8.73               22433.39
--           FMCG                 19              21           10.91               21151.15
--        Telecom                 15              15            9.71               16051.45
--         Energy                 13              13            9.07               15286.54
--    Diversified                 14              14           12.09               13897.79
-- ... and 4 more rows.
-- ============================================================
-- RESULTS_END

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


-- RESULTS_START
-- ============================================================
--               fund_house       date  aum_lakh_crore  aum_crore  num_schemes  qoq_growth_pct
-- Aditya Birla Sun Life MF 2022-03-31            2.78     278000          199             NaN
-- Aditya Birla Sun Life MF 2022-09-30            2.85     285000          199            2.52
-- Aditya Birla Sun Life MF 2023-03-31            2.75     275000          199           -3.51
-- Aditya Birla Sun Life MF 2023-09-30            3.08     308000          199           12.00
-- Aditya Birla Sun Life MF 2024-03-31            3.40     340000          199           10.39
-- Aditya Birla Sun Life MF 2024-09-30            3.62     362000          199            6.47
-- Aditya Birla Sun Life MF 2024-12-31            3.84     384000          199            6.08
-- Aditya Birla Sun Life MF 2025-03-31            3.85     385000          199            0.26
-- Aditya Birla Sun Life MF 2025-12-31            4.60     460000          199           19.48
--         Axis Mutual Fund 2022-03-31            2.50     250000           95             NaN
-- ... and 80 more rows.
-- ============================================================
-- RESULTS_END

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


-- RESULTS_START
-- ============================================================
--                                   scheme_name               fund_house   sub_category   risk_category  return_3yr_pct  sharpe_ratio  sortino_ratio  alpha  beta  volatility  max_drawdown_pct  aum_crore  composite_score
--     SBI Small Cap Fund - Direct Plan - Growth          SBI Mutual Fund      Small Cap       Very High           23.14          0.93           1.67   1.13  1.04        25.0            -24.78      36061            71.28
--        Kotak Flexicap Fund - Regular - Growth        Kotak Mahindra MF      Flexi Cap Moderately High           15.65          0.98           1.57   1.85  0.95        16.0            -19.50      35012            69.87
-- Kotak Emerging Equity Fund - Regular - Growth        Kotak Mahindra MF        Mid Cap            High           18.23          0.96           1.27   1.91  1.00        19.0            -21.92      47469            69.10
--        ABSL Small Cap Fund - Regular - Growth Aditya Birla Sun Life MF      Small Cap       Very High           22.38          0.90           1.47   1.84  0.97        25.0            -23.61      41613            66.92
--    SBI Small Cap Fund - Regular Plan - Growth          SBI Mutual Fund      Small Cap       Very High           23.39          0.94           1.35   1.23  0.89        25.0            -13.35      19259            63.46
-- Mirae Asset Large Cap Fund - Regular - Growth           Mirae Asset MF      Large Cap        Moderate           14.81          1.06           1.66   1.62  0.96        14.0            -17.07      11361            62.69
--  HDFC Short Term Debt Fund - Regular - Growth         HDFC Mutual Fund Short Duration             Low            7.37          1.84           2.79   1.98  0.44         4.0             -6.01      27953            62.05
--      ICICI Pru Liquid Fund - Regular - Growth      ICICI Prudential MF         Liquid             Low            7.68          7.68          10.37   1.85  0.26         0.5             -2.62      39116            60.51
--      ICICI Pru Midcap Fund - Regular - Growth      ICICI Prudential MF        Mid Cap            High           18.08          0.95           1.45   0.89  1.00        19.0            -21.84        979            59.74
--     ICICI Pru Bluechip Fund - Direct - Growth      ICICI Prudential MF      Large Cap        Moderate           14.41          1.03           1.27   0.88  1.03        14.0            -26.59      41553            58.59
-- ... and 30 more rows.
-- ============================================================
-- RESULTS_END

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


-- RESULTS_START
-- ============================================================
--          category  Apr-24  Jul-24  Oct-24  Jan-25  total_inflow
--            Liquid 37537.0 34643.0 39091.0 33892.0      451275.0
-- Sectoral/Thematic  8052.0  9896.0  7680.0  7893.0      103829.0
--         Flexi Cap  4947.0  4869.0  6004.0  5603.0       63989.0
--   Large & Mid Cap  4214.0  5023.0  4581.0  4816.0       57752.0
--    Short Duration  4400.0  4170.0  4675.0  4752.0       55530.0
--           Mid Cap  3897.0  4548.0  4106.0  4316.0       55312.0
--         Small Cap  3533.0  3582.0  4444.0  4554.0       46596.0
--            Hybrid  2955.0  3291.0  3314.0  2967.0       38868.0
--         Large Cap  2413.0  2574.0  2255.0  2025.0       25633.0
--      Value/Contra  1328.0  1582.0  1595.0  1339.0       16980.0
-- ... and 2 more rows.
-- ============================================================
-- RESULTS_END


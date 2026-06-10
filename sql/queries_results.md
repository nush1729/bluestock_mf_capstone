# Bluestock Mutual Fund Analytics — SQL Query Results

Generated: 2026-06-10 23:43:13
Database source: `data/db/bluestock_mf.db`

This file contains the output of all the analytical queries written in `sql/queries.sql`.

## Top 5 Funds by AUM (Assets Under Management)

### Query
```sql
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
```

### Result
|   amfi_code | scheme_name                                           | fund_house        | sub_category    |   aum_crore |   sharpe_ratio |   return_3yr_pct |
|------------:|:------------------------------------------------------|:------------------|:----------------|------------:|---------------:|-----------------:|
|      148568 | Mirae Asset Emerging Bluechip Fund - Regular - Growth | Mirae Asset MF    | Large & Mid Cap |       49046 |           0.91 |            14.56 |
|      120842 | Kotak Emerging Equity Fund - Regular - Growth         | Kotak Mahindra MF | Mid Cap         |       47469 |           0.96 |            18.23 |
|      118634 | Nippon India Small Cap Fund - Regular - Growth        | Nippon India MF   | Small Cap       |       43630 |           0.81 |            20.15 |
|      149322 | DSP Top 100 Equity Fund - Regular - Growth            | DSP Mutual Fund   | Large Cap       |       41828 |           0.92 |            12.82 |
|      102886 | UTI Mid Cap Fund - Regular - Growth                   | UTI Mutual Fund   | Mid Cap         |       41728 |           0.82 |            15.61 |

## Average Monthly NAV per Fund (Latest Year)

### Query
```sql
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
```

### Result
| scheme_name                                           | year_month   |   avg_nav |   trading_days |
|:------------------------------------------------------|:-------------|----------:|---------------:|
| ABSL Frontline Equity Fund - Regular - Growth         | 2025-01      |  461.872  |             31 |
| ABSL Frontline Equity Fund - Regular - Growth         | 2025-02      |  456.291  |             28 |
| ABSL Frontline Equity Fund - Regular - Growth         | 2025-03      |  485.588  |             31 |
| ABSL Frontline Equity Fund - Regular - Growth         | 2025-04      |  492.142  |             30 |
| ABSL Frontline Equity Fund - Regular - Growth         | 2025-05      |  519.361  |             31 |
| ABSL Frontline Equity Fund - Regular - Growth         | 2025-06      |  528.301  |             30 |
| ABSL Frontline Equity Fund - Regular - Growth         | 2025-07      |  535.556  |             31 |
| ABSL Frontline Equity Fund - Regular - Growth         | 2025-08      |  566.847  |             31 |
| ABSL Frontline Equity Fund - Regular - Growth         | 2025-09      |  569.527  |             30 |
| ABSL Frontline Equity Fund - Regular - Growth         | 2025-10      |  574.201  |             31 |
| ABSL Frontline Equity Fund - Regular - Growth         | 2025-11      |  573.997  |             30 |
| ABSL Frontline Equity Fund - Regular - Growth         | 2025-12      |  561.645  |             31 |
| ABSL Liquid Fund - Regular - Growth                   | 2025-01      |  375.49   |             31 |
| ABSL Liquid Fund - Regular - Growth                   | 2025-02      |  377.144  |             28 |
| ABSL Liquid Fund - Regular - Growth                   | 2025-03      |  378.777  |             31 |
| ABSL Liquid Fund - Regular - Growth                   | 2025-04      |  379.863  |             30 |
| ABSL Liquid Fund - Regular - Growth                   | 2025-05      |  381.656  |             31 |
| ABSL Liquid Fund - Regular - Growth                   | 2025-06      |  383.764  |             30 |
| ABSL Liquid Fund - Regular - Growth                   | 2025-07      |  385.55   |             31 |
| ABSL Liquid Fund - Regular - Growth                   | 2025-08      |  387.604  |             31 |
| ABSL Liquid Fund - Regular - Growth                   | 2025-09      |  389.732  |             30 |
| ABSL Liquid Fund - Regular - Growth                   | 2025-10      |  391.935  |             31 |
| ABSL Liquid Fund - Regular - Growth                   | 2025-11      |  394.757  |             30 |
| ABSL Liquid Fund - Regular - Growth                   | 2025-12      |  397.544  |             31 |
| ABSL Small Cap Fund - Regular - Growth                | 2025-01      |   72.031  |             31 |
| ABSL Small Cap Fund - Regular - Growth                | 2025-02      |   77.0485 |             28 |
| ABSL Small Cap Fund - Regular - Growth                | 2025-03      |   74.4197 |             31 |
| ABSL Small Cap Fund - Regular - Growth                | 2025-04      |   71.5333 |             30 |
| ABSL Small Cap Fund - Regular - Growth                | 2025-05      |   73.5543 |             31 |
| ABSL Small Cap Fund - Regular - Growth                | 2025-06      |   71.0492 |             30 |
| ABSL Small Cap Fund - Regular - Growth                | 2025-07      |   65.2818 |             31 |
| ABSL Small Cap Fund - Regular - Growth                | 2025-08      |   64.3806 |             31 |
| ABSL Small Cap Fund - Regular - Growth                | 2025-09      |   61.9497 |             30 |
| ABSL Small Cap Fund - Regular - Growth                | 2025-10      |   60.4472 |             31 |
| ABSL Small Cap Fund - Regular - Growth                | 2025-11      |   64.5792 |             30 |
| ABSL Small Cap Fund - Regular - Growth                | 2025-12      |   65.487  |             31 |
| Axis Bluechip Fund - Direct - Growth                  | 2025-01      |   45.4268 |             31 |
| Axis Bluechip Fund - Direct - Growth                  | 2025-02      |   45.8292 |             28 |
| Axis Bluechip Fund - Direct - Growth                  | 2025-03      |   49.767  |             31 |
| Axis Bluechip Fund - Direct - Growth                  | 2025-04      |   48.2386 |             30 |
| Axis Bluechip Fund - Direct - Growth                  | 2025-05      |   47.9401 |             31 |
| Axis Bluechip Fund - Direct - Growth                  | 2025-06      |   49.8289 |             30 |
| Axis Bluechip Fund - Direct - Growth                  | 2025-07      |   51.0903 |             31 |
| Axis Bluechip Fund - Direct - Growth                  | 2025-08      |   53.6958 |             31 |
| Axis Bluechip Fund - Direct - Growth                  | 2025-09      |   53.1544 |             30 |
| Axis Bluechip Fund - Direct - Growth                  | 2025-10      |   52.9139 |             31 |
| Axis Bluechip Fund - Direct - Growth                  | 2025-11      |   56.1586 |             30 |
| Axis Bluechip Fund - Direct - Growth                  | 2025-12      |   57.7009 |             31 |
| Axis Bluechip Fund - Regular - Growth                 | 2025-01      |   48.9126 |             31 |
| Axis Bluechip Fund - Regular - Growth                 | 2025-02      |   48.3892 |             28 |
| Axis Bluechip Fund - Regular - Growth                 | 2025-03      |   48.3251 |             31 |
| Axis Bluechip Fund - Regular - Growth                 | 2025-04      |   47.6311 |             30 |
| Axis Bluechip Fund - Regular - Growth                 | 2025-05      |   50.0844 |             31 |
| Axis Bluechip Fund - Regular - Growth                 | 2025-06      |   49.798  |             30 |
| Axis Bluechip Fund - Regular - Growth                 | 2025-07      |   51.397  |             31 |
| Axis Bluechip Fund - Regular - Growth                 | 2025-08      |   52.1869 |             31 |
| Axis Bluechip Fund - Regular - Growth                 | 2025-09      |   50.0357 |             30 |
| Axis Bluechip Fund - Regular - Growth                 | 2025-10      |   51.5654 |             31 |
| Axis Bluechip Fund - Regular - Growth                 | 2025-11      |   51.9512 |             30 |
| Axis Bluechip Fund - Regular - Growth                 | 2025-12      |   53.3357 |             31 |
| Axis Midcap Fund - Regular - Growth                   | 2025-01      |  154.669  |             31 |
| Axis Midcap Fund - Regular - Growth                   | 2025-02      |  170.021  |             28 |
| Axis Midcap Fund - Regular - Growth                   | 2025-03      |  165.033  |             31 |
| Axis Midcap Fund - Regular - Growth                   | 2025-04      |  157.91   |             30 |
| Axis Midcap Fund - Regular - Growth                   | 2025-05      |  163.902  |             31 |
| Axis Midcap Fund - Regular - Growth                   | 2025-06      |  162.549  |             30 |
| Axis Midcap Fund - Regular - Growth                   | 2025-07      |  164.772  |             31 |
| Axis Midcap Fund - Regular - Growth                   | 2025-08      |  164.828  |             31 |
| Axis Midcap Fund - Regular - Growth                   | 2025-09      |  170.955  |             30 |
| Axis Midcap Fund - Regular - Growth                   | 2025-10      |  187.579  |             31 |
| Axis Midcap Fund - Regular - Growth                   | 2025-11      |  198.822  |             30 |
| Axis Midcap Fund - Regular - Growth                   | 2025-12      |  201.654  |             31 |
| Axis Small Cap Fund - Regular - Growth                | 2025-01      |   78.8971 |             31 |
| Axis Small Cap Fund - Regular - Growth                | 2025-02      |   79.4336 |             28 |
| Axis Small Cap Fund - Regular - Growth                | 2025-03      |   90.4368 |             31 |
| Axis Small Cap Fund - Regular - Growth                | 2025-04      |   94.2404 |             30 |
| Axis Small Cap Fund - Regular - Growth                | 2025-05      |  102.83   |             31 |
| Axis Small Cap Fund - Regular - Growth                | 2025-06      |   97.2784 |             30 |
| Axis Small Cap Fund - Regular - Growth                | 2025-07      |   86.7794 |             31 |
| Axis Small Cap Fund - Regular - Growth                | 2025-08      |   84.9968 |             31 |
| Axis Small Cap Fund - Regular - Growth                | 2025-09      |   73.6795 |             30 |
| Axis Small Cap Fund - Regular - Growth                | 2025-10      |   72.4156 |             31 |
| Axis Small Cap Fund - Regular - Growth                | 2025-11      |   73.0901 |             30 |
| Axis Small Cap Fund - Regular - Growth                | 2025-12      |   68.908  |             31 |
| DSP Midcap Fund - Regular - Growth                    | 2025-01      |  218.309  |             31 |
| DSP Midcap Fund - Regular - Growth                    | 2025-02      |  211.296  |             28 |
| DSP Midcap Fund - Regular - Growth                    | 2025-03      |  204.558  |             31 |
| DSP Midcap Fund - Regular - Growth                    | 2025-04      |  195.135  |             30 |
| DSP Midcap Fund - Regular - Growth                    | 2025-05      |  198.316  |             31 |
| DSP Midcap Fund - Regular - Growth                    | 2025-06      |  203.476  |             30 |
| DSP Midcap Fund - Regular - Growth                    | 2025-07      |  213.537  |             31 |
| DSP Midcap Fund - Regular - Growth                    | 2025-08      |  219.253  |             31 |
| DSP Midcap Fund - Regular - Growth                    | 2025-09      |  222.875  |             30 |
| DSP Midcap Fund - Regular - Growth                    | 2025-10      |  228.189  |             31 |
| DSP Midcap Fund - Regular - Growth                    | 2025-11      |  241.256  |             30 |
| DSP Midcap Fund - Regular - Growth                    | 2025-12      |  225.167  |             31 |
| DSP Small Cap Fund - Regular - Growth                 | 2025-01      |  133.744  |             31 |
| DSP Small Cap Fund - Regular - Growth                 | 2025-02      |  143.668  |             28 |
| DSP Small Cap Fund - Regular - Growth                 | 2025-03      |  151.41   |             31 |
| DSP Small Cap Fund - Regular - Growth                 | 2025-04      |  164.149  |             30 |
| DSP Small Cap Fund - Regular - Growth                 | 2025-05      |  169.298  |             31 |
| DSP Small Cap Fund - Regular - Growth                 | 2025-06      |  174.296  |             30 |
| DSP Small Cap Fund - Regular - Growth                 | 2025-07      |  170.993  |             31 |
| DSP Small Cap Fund - Regular - Growth                 | 2025-08      |  179.654  |             31 |
| DSP Small Cap Fund - Regular - Growth                 | 2025-09      |  198.637  |             30 |
| DSP Small Cap Fund - Regular - Growth                 | 2025-10      |  216.82   |             31 |
| DSP Small Cap Fund - Regular - Growth                 | 2025-11      |  247.119  |             30 |
| DSP Small Cap Fund - Regular - Growth                 | 2025-12      |  253.557  |             31 |
| DSP Top 100 Equity Fund - Regular - Growth            | 2025-01      |  474.267  |             31 |
| DSP Top 100 Equity Fund - Regular - Growth            | 2025-02      |  493.508  |             28 |
| DSP Top 100 Equity Fund - Regular - Growth            | 2025-03      |  494.43   |             31 |
| DSP Top 100 Equity Fund - Regular - Growth            | 2025-04      |  519.014  |             30 |
| DSP Top 100 Equity Fund - Regular - Growth            | 2025-05      |  512.259  |             31 |
| DSP Top 100 Equity Fund - Regular - Growth            | 2025-06      |  509.52   |             30 |
| DSP Top 100 Equity Fund - Regular - Growth            | 2025-07      |  513.597  |             31 |
| DSP Top 100 Equity Fund - Regular - Growth            | 2025-08      |  524.875  |             31 |
| DSP Top 100 Equity Fund - Regular - Growth            | 2025-09      |  542.69   |             30 |
| DSP Top 100 Equity Fund - Regular - Growth            | 2025-10      |  556.721  |             31 |
| DSP Top 100 Equity Fund - Regular - Growth            | 2025-11      |  588.76   |             30 |
| DSP Top 100 Equity Fund - Regular - Growth            | 2025-12      |  616.82   |             31 |
| HDFC Mid-Cap Opportunities Fund - Direct - Growth     | 2025-01      |  151.229  |             31 |
| HDFC Mid-Cap Opportunities Fund - Direct - Growth     | 2025-02      |  153.55   |             28 |
| HDFC Mid-Cap Opportunities Fund - Direct - Growth     | 2025-03      |  164.795  |             31 |
| HDFC Mid-Cap Opportunities Fund - Direct - Growth     | 2025-04      |  162.666  |             30 |
| HDFC Mid-Cap Opportunities Fund - Direct - Growth     | 2025-05      |  162.534  |             31 |
| HDFC Mid-Cap Opportunities Fund - Direct - Growth     | 2025-06      |  159.686  |             30 |
| HDFC Mid-Cap Opportunities Fund - Direct - Growth     | 2025-07      |  160.171  |             31 |
| HDFC Mid-Cap Opportunities Fund - Direct - Growth     | 2025-08      |  143.961  |             31 |
| HDFC Mid-Cap Opportunities Fund - Direct - Growth     | 2025-09      |  137.401  |             30 |
| HDFC Mid-Cap Opportunities Fund - Direct - Growth     | 2025-10      |  148.598  |             31 |
| HDFC Mid-Cap Opportunities Fund - Direct - Growth     | 2025-11      |  160.223  |             30 |
| HDFC Mid-Cap Opportunities Fund - Direct - Growth     | 2025-12      |  157.155  |             31 |
| HDFC Mid-Cap Opportunities Fund - Regular - Growth    | 2025-01      |  248.944  |             31 |
| HDFC Mid-Cap Opportunities Fund - Regular - Growth    | 2025-02      |  233.567  |             28 |
| HDFC Mid-Cap Opportunities Fund - Regular - Growth    | 2025-03      |  224.408  |             31 |
| HDFC Mid-Cap Opportunities Fund - Regular - Growth    | 2025-04      |  223.691  |             30 |
| HDFC Mid-Cap Opportunities Fund - Regular - Growth    | 2025-05      |  221.297  |             31 |
| HDFC Mid-Cap Opportunities Fund - Regular - Growth    | 2025-06      |  229.381  |             30 |
| HDFC Mid-Cap Opportunities Fund - Regular - Growth    | 2025-07      |  236.137  |             31 |
| HDFC Mid-Cap Opportunities Fund - Regular - Growth    | 2025-08      |  258.116  |             31 |
| HDFC Mid-Cap Opportunities Fund - Regular - Growth    | 2025-09      |  259.702  |             30 |
| HDFC Mid-Cap Opportunities Fund - Regular - Growth    | 2025-10      |  264.497  |             31 |
| HDFC Mid-Cap Opportunities Fund - Regular - Growth    | 2025-11      |  259.754  |             30 |
| HDFC Mid-Cap Opportunities Fund - Regular - Growth    | 2025-12      |  273.873  |             31 |
| HDFC Short Term Debt Fund - Regular - Growth          | 2025-01      |   29.6977 |             31 |
| HDFC Short Term Debt Fund - Regular - Growth          | 2025-02      |   29.829  |             28 |
| HDFC Short Term Debt Fund - Regular - Growth          | 2025-03      |   30.0277 |             31 |
| HDFC Short Term Debt Fund - Regular - Growth          | 2025-04      |   30.2213 |             30 |
| HDFC Short Term Debt Fund - Regular - Growth          | 2025-05      |   30.7195 |             31 |
| HDFC Short Term Debt Fund - Regular - Growth          | 2025-06      |   31.0285 |             30 |
| HDFC Short Term Debt Fund - Regular - Growth          | 2025-07      |   31.3451 |             31 |
| HDFC Short Term Debt Fund - Regular - Growth          | 2025-08      |   31.7492 |             31 |
| HDFC Short Term Debt Fund - Regular - Growth          | 2025-09      |   31.2081 |             30 |
| HDFC Short Term Debt Fund - Regular - Growth          | 2025-10      |   31.6493 |             31 |
| HDFC Short Term Debt Fund - Regular - Growth          | 2025-11      |   32.3849 |             30 |
| HDFC Short Term Debt Fund - Regular - Growth          | 2025-12      |   32.4208 |             31 |
| HDFC Top 100 Fund - Direct Plan - Growth              | 2025-01      |  762.08   |             31 |
| HDFC Top 100 Fund - Direct Plan - Growth              | 2025-02      |  784.346  |             28 |
| HDFC Top 100 Fund - Direct Plan - Growth              | 2025-03      |  801.721  |             31 |
| HDFC Top 100 Fund - Direct Plan - Growth              | 2025-04      |  854.539  |             30 |
| HDFC Top 100 Fund - Direct Plan - Growth              | 2025-05      |  916.995  |             31 |
| HDFC Top 100 Fund - Direct Plan - Growth              | 2025-06      |  920.396  |             30 |
| HDFC Top 100 Fund - Direct Plan - Growth              | 2025-07      |  923.948  |             31 |
| HDFC Top 100 Fund - Direct Plan - Growth              | 2025-08      |  950.872  |             31 |
| HDFC Top 100 Fund - Direct Plan - Growth              | 2025-09      |  947.799  |             30 |
| HDFC Top 100 Fund - Direct Plan - Growth              | 2025-10      |  995.337  |             31 |
| HDFC Top 100 Fund - Direct Plan - Growth              | 2025-11      |  968.556  |             30 |
| HDFC Top 100 Fund - Direct Plan - Growth              | 2025-12      | 1007.94   |             31 |
| HDFC Top 100 Fund - Regular Plan - Growth             | 2025-01      |  589.529  |             31 |
| HDFC Top 100 Fund - Regular Plan - Growth             | 2025-02      |  601.053  |             28 |
| HDFC Top 100 Fund - Regular Plan - Growth             | 2025-03      |  619.422  |             31 |
| HDFC Top 100 Fund - Regular Plan - Growth             | 2025-04      |  611.928  |             30 |
| HDFC Top 100 Fund - Regular Plan - Growth             | 2025-05      |  614.53   |             31 |
| HDFC Top 100 Fund - Regular Plan - Growth             | 2025-06      |  602.966  |             30 |
| HDFC Top 100 Fund - Regular Plan - Growth             | 2025-07      |  602.346  |             31 |
| HDFC Top 100 Fund - Regular Plan - Growth             | 2025-08      |  589.971  |             31 |
| HDFC Top 100 Fund - Regular Plan - Growth             | 2025-09      |  594.822  |             30 |
| HDFC Top 100 Fund - Regular Plan - Growth             | 2025-10      |  617.653  |             31 |
| HDFC Top 100 Fund - Regular Plan - Growth             | 2025-11      |  601.675  |             30 |
| HDFC Top 100 Fund - Regular Plan - Growth             | 2025-12      |  618.352  |             31 |
| ICICI Pru Bluechip Fund - Direct - Growth             | 2025-01      |  112.743  |             31 |
| ICICI Pru Bluechip Fund - Direct - Growth             | 2025-02      |  115.97   |             28 |
| ICICI Pru Bluechip Fund - Direct - Growth             | 2025-03      |  118.034  |             31 |
| ICICI Pru Bluechip Fund - Direct - Growth             | 2025-04      |  123.465  |             30 |
| ICICI Pru Bluechip Fund - Direct - Growth             | 2025-05      |  128.75   |             31 |
| ICICI Pru Bluechip Fund - Direct - Growth             | 2025-06      |  134.283  |             30 |
| ICICI Pru Bluechip Fund - Direct - Growth             | 2025-07      |  128.023  |             31 |
| ICICI Pru Bluechip Fund - Direct - Growth             | 2025-08      |  125.412  |             31 |
| ICICI Pru Bluechip Fund - Direct - Growth             | 2025-09      |  131.921  |             30 |
| ICICI Pru Bluechip Fund - Direct - Growth             | 2025-10      |  129.801  |             31 |
| ICICI Pru Bluechip Fund - Direct - Growth             | 2025-11      |  133.393  |             30 |
| ICICI Pru Bluechip Fund - Direct - Growth             | 2025-12      |  150.551  |             31 |
| ICICI Pru Bluechip Fund - Regular - Growth            | 2025-01      |  105.969  |             31 |
| ICICI Pru Bluechip Fund - Regular - Growth            | 2025-02      |  112.781  |             28 |
| ICICI Pru Bluechip Fund - Regular - Growth            | 2025-03      |  111.776  |             31 |
| ICICI Pru Bluechip Fund - Regular - Growth            | 2025-04      |  108.528  |             30 |
| ICICI Pru Bluechip Fund - Regular - Growth            | 2025-05      |  110.297  |             31 |
| ICICI Pru Bluechip Fund - Regular - Growth            | 2025-06      |  112.287  |             30 |
| ICICI Pru Bluechip Fund - Regular - Growth            | 2025-07      |  112.07   |             31 |
| ICICI Pru Bluechip Fund - Regular - Growth            | 2025-08      |  110.806  |             31 |
| ICICI Pru Bluechip Fund - Regular - Growth            | 2025-09      |  110.995  |             30 |
| ICICI Pru Bluechip Fund - Regular - Growth            | 2025-10      |  113.668  |             31 |
| ICICI Pru Bluechip Fund - Regular - Growth            | 2025-11      |  112.51   |             30 |
| ICICI Pru Bluechip Fund - Regular - Growth            | 2025-12      |  113.802  |             31 |
| ICICI Pru Liquid Fund - Regular - Growth              | 2025-01      |  352.486  |             31 |
| ICICI Pru Liquid Fund - Regular - Growth              | 2025-02      |  355.094  |             28 |
| ICICI Pru Liquid Fund - Regular - Growth              | 2025-03      |  357.27   |             31 |
| ICICI Pru Liquid Fund - Regular - Growth              | 2025-04      |  359.47   |             30 |
| ICICI Pru Liquid Fund - Regular - Growth              | 2025-05      |  361.04   |             31 |
| ICICI Pru Liquid Fund - Regular - Growth              | 2025-06      |  363.177  |             30 |
| ICICI Pru Liquid Fund - Regular - Growth              | 2025-07      |  365.474  |             31 |
| ICICI Pru Liquid Fund - Regular - Growth              | 2025-08      |  367.378  |             31 |
| ICICI Pru Liquid Fund - Regular - Growth              | 2025-09      |  369.567  |             30 |
| ICICI Pru Liquid Fund - Regular - Growth              | 2025-10      |  371.728  |             31 |
| ICICI Pru Liquid Fund - Regular - Growth              | 2025-11      |  373.227  |             30 |
| ICICI Pru Liquid Fund - Regular - Growth              | 2025-12      |  374.853  |             31 |
| ICICI Pru Midcap Fund - Regular - Growth              | 2025-01      |  290.823  |             31 |
| ICICI Pru Midcap Fund - Regular - Growth              | 2025-02      |  310.723  |             28 |
| ICICI Pru Midcap Fund - Regular - Growth              | 2025-03      |  338.845  |             31 |
| ICICI Pru Midcap Fund - Regular - Growth              | 2025-04      |  344.048  |             30 |
| ICICI Pru Midcap Fund - Regular - Growth              | 2025-05      |  356.919  |             31 |
| ICICI Pru Midcap Fund - Regular - Growth              | 2025-06      |  363.999  |             30 |
| ICICI Pru Midcap Fund - Regular - Growth              | 2025-07      |  375.708  |             31 |
| ICICI Pru Midcap Fund - Regular - Growth              | 2025-08      |  376.387  |             31 |
| ICICI Pru Midcap Fund - Regular - Growth              | 2025-09      |  375.608  |             30 |
| ICICI Pru Midcap Fund - Regular - Growth              | 2025-10      |  385.203  |             31 |
| ICICI Pru Midcap Fund - Regular - Growth              | 2025-11      |  374.03   |             30 |
| ICICI Pru Midcap Fund - Regular - Growth              | 2025-12      |  390.779  |             31 |
| ICICI Pru Value Discovery Fund - Regular - Growth     | 2025-01      |  260.768  |             31 |
| ICICI Pru Value Discovery Fund - Regular - Growth     | 2025-02      |  276.506  |             28 |
| ICICI Pru Value Discovery Fund - Regular - Growth     | 2025-03      |  275.355  |             31 |
| ICICI Pru Value Discovery Fund - Regular - Growth     | 2025-04      |  265.282  |             30 |
| ICICI Pru Value Discovery Fund - Regular - Growth     | 2025-05      |  275.228  |             31 |
| ICICI Pru Value Discovery Fund - Regular - Growth     | 2025-06      |  302.731  |             30 |
| ICICI Pru Value Discovery Fund - Regular - Growth     | 2025-07      |  317.612  |             31 |
| ICICI Pru Value Discovery Fund - Regular - Growth     | 2025-08      |  328.511  |             31 |
| ICICI Pru Value Discovery Fund - Regular - Growth     | 2025-09      |  330.911  |             30 |
| ICICI Pru Value Discovery Fund - Regular - Growth     | 2025-10      |  330.096  |             31 |
| ICICI Pru Value Discovery Fund - Regular - Growth     | 2025-11      |  346.439  |             30 |
| ICICI Pru Value Discovery Fund - Regular - Growth     | 2025-12      |  362.831  |             31 |
| Kotak Bluechip Fund - Regular - Growth                | 2025-01      |  387.236  |             31 |
| Kotak Bluechip Fund - Regular - Growth                | 2025-02      |  369.655  |             28 |
| Kotak Bluechip Fund - Regular - Growth                | 2025-03      |  390.202  |             31 |
| Kotak Bluechip Fund - Regular - Growth                | 2025-04      |  401.654  |             30 |
| Kotak Bluechip Fund - Regular - Growth                | 2025-05      |  414.35   |             31 |
| Kotak Bluechip Fund - Regular - Growth                | 2025-06      |  406.358  |             30 |
| Kotak Bluechip Fund - Regular - Growth                | 2025-07      |  385.55   |             31 |
| Kotak Bluechip Fund - Regular - Growth                | 2025-08      |  372.077  |             31 |
| Kotak Bluechip Fund - Regular - Growth                | 2025-09      |  374.275  |             30 |
| Kotak Bluechip Fund - Regular - Growth                | 2025-10      |  390.47   |             31 |
| Kotak Bluechip Fund - Regular - Growth                | 2025-11      |  420.689  |             30 |
| Kotak Bluechip Fund - Regular - Growth                | 2025-12      |  434.841  |             31 |
| Kotak Emerging Equity Fund - Regular - Growth         | 2025-01      |   70.4526 |             31 |
| Kotak Emerging Equity Fund - Regular - Growth         | 2025-02      |   68.4635 |             28 |
| Kotak Emerging Equity Fund - Regular - Growth         | 2025-03      |   71.4438 |             31 |
| Kotak Emerging Equity Fund - Regular - Growth         | 2025-04      |   74.4591 |             30 |
| Kotak Emerging Equity Fund - Regular - Growth         | 2025-05      |   70.7721 |             31 |
| Kotak Emerging Equity Fund - Regular - Growth         | 2025-06      |   69.0463 |             30 |
| Kotak Emerging Equity Fund - Regular - Growth         | 2025-07      |   69.6323 |             31 |
| Kotak Emerging Equity Fund - Regular - Growth         | 2025-08      |   73.1967 |             31 |
| Kotak Emerging Equity Fund - Regular - Growth         | 2025-09      |   72.9715 |             30 |
| Kotak Emerging Equity Fund - Regular - Growth         | 2025-10      |   79.345  |             31 |
| Kotak Emerging Equity Fund - Regular - Growth         | 2025-11      |   77.5761 |             30 |
| Kotak Emerging Equity Fund - Regular - Growth         | 2025-12      |   73.6773 |             31 |
| Kotak Flexicap Fund - Regular - Growth                | 2025-01      |  130.957  |             31 |
| Kotak Flexicap Fund - Regular - Growth                | 2025-02      |  134.796  |             28 |
| Kotak Flexicap Fund - Regular - Growth                | 2025-03      |  128.114  |             31 |
| Kotak Flexicap Fund - Regular - Growth                | 2025-04      |  125.28   |             30 |
| Kotak Flexicap Fund - Regular - Growth                | 2025-05      |  127.466  |             31 |
| Kotak Flexicap Fund - Regular - Growth                | 2025-06      |  126.678  |             30 |
| Kotak Flexicap Fund - Regular - Growth                | 2025-07      |  127.256  |             31 |
| Kotak Flexicap Fund - Regular - Growth                | 2025-08      |  132.627  |             31 |
| Kotak Flexicap Fund - Regular - Growth                | 2025-09      |  131.836  |             30 |
| Kotak Flexicap Fund - Regular - Growth                | 2025-10      |  136.44   |             31 |
| Kotak Flexicap Fund - Regular - Growth                | 2025-11      |  148.377  |             30 |
| Kotak Flexicap Fund - Regular - Growth                | 2025-12      |  164.102  |             31 |
| Kotak Liquid Fund - Regular - Growth                  | 2025-01      | 3888.73   |             31 |
| Kotak Liquid Fund - Regular - Growth                  | 2025-02      | 3902.6    |             28 |
| Kotak Liquid Fund - Regular - Growth                  | 2025-03      | 3927.82   |             31 |
| Kotak Liquid Fund - Regular - Growth                  | 2025-04      | 3950.11   |             30 |
| Kotak Liquid Fund - Regular - Growth                  | 2025-05      | 3972.89   |             31 |
| Kotak Liquid Fund - Regular - Growth                  | 2025-06      | 3994.87   |             30 |
| Kotak Liquid Fund - Regular - Growth                  | 2025-07      | 4014.62   |             31 |
| Kotak Liquid Fund - Regular - Growth                  | 2025-08      | 4034.9    |             31 |
| Kotak Liquid Fund - Regular - Growth                  | 2025-09      | 4052      |             30 |
| Kotak Liquid Fund - Regular - Growth                  | 2025-10      | 4076.7    |             31 |
| Kotak Liquid Fund - Regular - Growth                  | 2025-11      | 4108      |             30 |
| Kotak Liquid Fund - Regular - Growth                  | 2025-12      | 4134.53   |             31 |
| Mirae Asset Emerging Bluechip Fund - Regular - Growth | 2025-01      |  166.976  |             31 |
| Mirae Asset Emerging Bluechip Fund - Regular - Growth | 2025-02      |  168.236  |             28 |
| Mirae Asset Emerging Bluechip Fund - Regular - Growth | 2025-03      |  177.137  |             31 |
| Mirae Asset Emerging Bluechip Fund - Regular - Growth | 2025-04      |  182.251  |             30 |
| Mirae Asset Emerging Bluechip Fund - Regular - Growth | 2025-05      |  181.832  |             31 |
| Mirae Asset Emerging Bluechip Fund - Regular - Growth | 2025-06      |  189.169  |             30 |
| Mirae Asset Emerging Bluechip Fund - Regular - Growth | 2025-07      |  190.931  |             31 |
| Mirae Asset Emerging Bluechip Fund - Regular - Growth | 2025-08      |  182.138  |             31 |
| Mirae Asset Emerging Bluechip Fund - Regular - Growth | 2025-09      |  176.611  |             30 |
| Mirae Asset Emerging Bluechip Fund - Regular - Growth | 2025-10      |  181.752  |             31 |
| Mirae Asset Emerging Bluechip Fund - Regular - Growth | 2025-11      |  186.639  |             30 |
| Mirae Asset Emerging Bluechip Fund - Regular - Growth | 2025-12      |  184.666  |             31 |
| Mirae Asset Large Cap Fund - Regular - Growth         | 2025-01      |  169.233  |             31 |
| Mirae Asset Large Cap Fund - Regular - Growth         | 2025-02      |  164.255  |             28 |
| Mirae Asset Large Cap Fund - Regular - Growth         | 2025-03      |  169.907  |             31 |
| Mirae Asset Large Cap Fund - Regular - Growth         | 2025-04      |  180.976  |             30 |
| Mirae Asset Large Cap Fund - Regular - Growth         | 2025-05      |  189.743  |             31 |
| Mirae Asset Large Cap Fund - Regular - Growth         | 2025-06      |  200.46   |             30 |
| Mirae Asset Large Cap Fund - Regular - Growth         | 2025-07      |  208.647  |             31 |
| Mirae Asset Large Cap Fund - Regular - Growth         | 2025-08      |  209.686  |             31 |
| Mirae Asset Large Cap Fund - Regular - Growth         | 2025-09      |  219.016  |             30 |
| Mirae Asset Large Cap Fund - Regular - Growth         | 2025-10      |  222.615  |             31 |
| Mirae Asset Large Cap Fund - Regular - Growth         | 2025-11      |  223.094  |             30 |
| Mirae Asset Large Cap Fund - Regular - Growth         | 2025-12      |  231.611  |             31 |
| Mirae Asset Tax Saver Fund - Regular - Growth         | 2025-01      |   58.0102 |             31 |
| Mirae Asset Tax Saver Fund - Regular - Growth         | 2025-02      |   62.06   |             28 |
| Mirae Asset Tax Saver Fund - Regular - Growth         | 2025-03      |   65.8887 |             31 |
| Mirae Asset Tax Saver Fund - Regular - Growth         | 2025-04      |   70.1372 |             30 |
| Mirae Asset Tax Saver Fund - Regular - Growth         | 2025-05      |   69.3566 |             31 |
| Mirae Asset Tax Saver Fund - Regular - Growth         | 2025-06      |   67.7899 |             30 |
| Mirae Asset Tax Saver Fund - Regular - Growth         | 2025-07      |   70.5445 |             31 |
| Mirae Asset Tax Saver Fund - Regular - Growth         | 2025-08      |   69.5717 |             31 |
| Mirae Asset Tax Saver Fund - Regular - Growth         | 2025-09      |   69.8867 |             30 |
| Mirae Asset Tax Saver Fund - Regular - Growth         | 2025-10      |   68.8981 |             31 |
| Mirae Asset Tax Saver Fund - Regular - Growth         | 2025-11      |   74.6011 |             30 |
| Mirae Asset Tax Saver Fund - Regular - Growth         | 2025-12      |   75.0795 |             31 |
| Nippon India ETF Nifty 50 BeES                        | 2025-01      |  249.679  |             31 |
| Nippon India ETF Nifty 50 BeES                        | 2025-02      |  258.82   |             28 |
| Nippon India ETF Nifty 50 BeES                        | 2025-03      |  262.298  |             31 |
| Nippon India ETF Nifty 50 BeES                        | 2025-04      |  263.804  |             30 |
| Nippon India ETF Nifty 50 BeES                        | 2025-05      |  259.059  |             31 |
| Nippon India ETF Nifty 50 BeES                        | 2025-06      |  265.612  |             30 |
| Nippon India ETF Nifty 50 BeES                        | 2025-07      |  282.754  |             31 |
| Nippon India ETF Nifty 50 BeES                        | 2025-08      |  293.39   |             31 |
| Nippon India ETF Nifty 50 BeES                        | 2025-09      |  293.24   |             30 |
| Nippon India ETF Nifty 50 BeES                        | 2025-10      |  291.941  |             31 |
| Nippon India ETF Nifty 50 BeES                        | 2025-11      |  303.792  |             30 |
| Nippon India ETF Nifty 50 BeES                        | 2025-12      |  314.418  |             31 |
| Nippon India Gilt Securities Fund - Regular - Growth  | 2025-01      |   34.5162 |             31 |
| Nippon India Gilt Securities Fund - Regular - Growth  | 2025-02      |   34.1098 |             28 |
| Nippon India Gilt Securities Fund - Regular - Growth  | 2025-03      |   33.4917 |             31 |
| Nippon India Gilt Securities Fund - Regular - Growth  | 2025-04      |   33.9203 |             30 |
| Nippon India Gilt Securities Fund - Regular - Growth  | 2025-05      |   34.1568 |             31 |
| Nippon India Gilt Securities Fund - Regular - Growth  | 2025-06      |   34.2219 |             30 |
| Nippon India Gilt Securities Fund - Regular - Growth  | 2025-07      |   34.1182 |             31 |
| Nippon India Gilt Securities Fund - Regular - Growth  | 2025-08      |   34.7824 |             31 |
| Nippon India Gilt Securities Fund - Regular - Growth  | 2025-09      |   35.0621 |             30 |
| Nippon India Gilt Securities Fund - Regular - Growth  | 2025-10      |   35.1597 |             31 |
| Nippon India Gilt Securities Fund - Regular - Growth  | 2025-11      |   35.8555 |             30 |
| Nippon India Gilt Securities Fund - Regular - Growth  | 2025-12      |   36.5452 |             31 |
| Nippon India Large Cap Fund - Direct - Growth         | 2025-01      |   62.2575 |             31 |
| Nippon India Large Cap Fund - Direct - Growth         | 2025-02      |   65.994  |             28 |
| Nippon India Large Cap Fund - Direct - Growth         | 2025-03      |   68.0345 |             31 |
| Nippon India Large Cap Fund - Direct - Growth         | 2025-04      |   70.175  |             30 |
| Nippon India Large Cap Fund - Direct - Growth         | 2025-05      |   70.6346 |             31 |
| Nippon India Large Cap Fund - Direct - Growth         | 2025-06      |   72.5956 |             30 |
| Nippon India Large Cap Fund - Direct - Growth         | 2025-07      |   75.264  |             31 |
| Nippon India Large Cap Fund - Direct - Growth         | 2025-08      |   77.5039 |             31 |
| Nippon India Large Cap Fund - Direct - Growth         | 2025-09      |   78.0391 |             30 |
| Nippon India Large Cap Fund - Direct - Growth         | 2025-10      |   82.8465 |             31 |
| Nippon India Large Cap Fund - Direct - Growth         | 2025-11      |   81.5502 |             30 |
| Nippon India Large Cap Fund - Direct - Growth         | 2025-12      |   79.3529 |             31 |
| Nippon India Large Cap Fund - Regular - Growth        | 2025-01      |   77.3875 |             31 |
| Nippon India Large Cap Fund - Regular - Growth        | 2025-02      |   78.7748 |             28 |
| Nippon India Large Cap Fund - Regular - Growth        | 2025-03      |   79.0729 |             31 |
| Nippon India Large Cap Fund - Regular - Growth        | 2025-04      |   79.2676 |             30 |
| Nippon India Large Cap Fund - Regular - Growth        | 2025-05      |   81.4768 |             31 |
| Nippon India Large Cap Fund - Regular - Growth        | 2025-06      |   89.3215 |             30 |
| Nippon India Large Cap Fund - Regular - Growth        | 2025-07      |   90.7414 |             31 |
| Nippon India Large Cap Fund - Regular - Growth        | 2025-08      |   94.5986 |             31 |
| Nippon India Large Cap Fund - Regular - Growth        | 2025-09      |   94.7015 |             30 |
| Nippon India Large Cap Fund - Regular - Growth        | 2025-10      |   97.4038 |             31 |
| Nippon India Large Cap Fund - Regular - Growth        | 2025-11      |   97.4104 |             30 |
| Nippon India Large Cap Fund - Regular - Growth        | 2025-12      |   96.0467 |             31 |
| Nippon India Small Cap Fund - Regular - Growth        | 2025-01      |  109.489  |             31 |
| Nippon India Small Cap Fund - Regular - Growth        | 2025-02      |  116.07   |             28 |
| Nippon India Small Cap Fund - Regular - Growth        | 2025-03      |  116.463  |             31 |
| Nippon India Small Cap Fund - Regular - Growth        | 2025-04      |  122.172  |             30 |
| Nippon India Small Cap Fund - Regular - Growth        | 2025-05      |  120.068  |             31 |
| Nippon India Small Cap Fund - Regular - Growth        | 2025-06      |  112.536  |             30 |
| Nippon India Small Cap Fund - Regular - Growth        | 2025-07      |  103.907  |             31 |
| Nippon India Small Cap Fund - Regular - Growth        | 2025-08      |  101.73   |             31 |
| Nippon India Small Cap Fund - Regular - Growth        | 2025-09      |  104.286  |             30 |
| Nippon India Small Cap Fund - Regular - Growth        | 2025-10      |  105.655  |             31 |
| Nippon India Small Cap Fund - Regular - Growth        | 2025-11      |  110.535  |             30 |
| Nippon India Small Cap Fund - Regular - Growth        | 2025-12      |  110.645  |             31 |
| SBI Bluechip Fund - Direct Plan - Growth              | 2025-01      |  119.558  |             31 |
| SBI Bluechip Fund - Direct Plan - Growth              | 2025-02      |  124.284  |             28 |
| SBI Bluechip Fund - Direct Plan - Growth              | 2025-03      |  128.234  |             31 |
| SBI Bluechip Fund - Direct Plan - Growth              | 2025-04      |  129.4    |             30 |
| SBI Bluechip Fund - Direct Plan - Growth              | 2025-05      |  125.385  |             31 |
| SBI Bluechip Fund - Direct Plan - Growth              | 2025-06      |  126.463  |             30 |
| SBI Bluechip Fund - Direct Plan - Growth              | 2025-07      |  128.309  |             31 |
| SBI Bluechip Fund - Direct Plan - Growth              | 2025-08      |  126.371  |             31 |
| SBI Bluechip Fund - Direct Plan - Growth              | 2025-09      |  125.776  |             30 |
| SBI Bluechip Fund - Direct Plan - Growth              | 2025-10      |  129.048  |             31 |
| SBI Bluechip Fund - Direct Plan - Growth              | 2025-11      |  128.294  |             30 |
| SBI Bluechip Fund - Direct Plan - Growth              | 2025-12      |  130.75   |             31 |
| SBI Bluechip Fund - Regular Plan - Growth             | 2025-01      |   76.904  |             31 |
| SBI Bluechip Fund - Regular Plan - Growth             | 2025-02      |   78.6389 |             28 |
| SBI Bluechip Fund - Regular Plan - Growth             | 2025-03      |   81.9144 |             31 |
| SBI Bluechip Fund - Regular Plan - Growth             | 2025-04      |   84.2085 |             30 |
| SBI Bluechip Fund - Regular Plan - Growth             | 2025-05      |   88.8723 |             31 |
| SBI Bluechip Fund - Regular Plan - Growth             | 2025-06      |   99.6928 |             30 |
| SBI Bluechip Fund - Regular Plan - Growth             | 2025-07      |  106.254  |             31 |
| SBI Bluechip Fund - Regular Plan - Growth             | 2025-08      |  105.156  |             31 |
| SBI Bluechip Fund - Regular Plan - Growth             | 2025-09      |  110.615  |             30 |
| SBI Bluechip Fund - Regular Plan - Growth             | 2025-10      |  107.068  |             31 |
| SBI Bluechip Fund - Regular Plan - Growth             | 2025-11      |  113.51   |             30 |
| SBI Bluechip Fund - Regular Plan - Growth             | 2025-12      |  121.243  |             31 |
| SBI Magnum Gilt Fund - Regular Plan - Growth          | 2025-01      |   51.0947 |             31 |
| SBI Magnum Gilt Fund - Regular Plan - Growth          | 2025-02      |   50.733  |             28 |
| SBI Magnum Gilt Fund - Regular Plan - Growth          | 2025-03      |   50.4472 |             31 |
| SBI Magnum Gilt Fund - Regular Plan - Growth          | 2025-04      |   50.5416 |             30 |
| SBI Magnum Gilt Fund - Regular Plan - Growth          | 2025-05      |   51.0823 |             31 |
| SBI Magnum Gilt Fund - Regular Plan - Growth          | 2025-06      |   51.4754 |             30 |
| SBI Magnum Gilt Fund - Regular Plan - Growth          | 2025-07      |   51.3266 |             31 |
| SBI Magnum Gilt Fund - Regular Plan - Growth          | 2025-08      |   52.179  |             31 |
| SBI Magnum Gilt Fund - Regular Plan - Growth          | 2025-09      |   52.8083 |             30 |
| SBI Magnum Gilt Fund - Regular Plan - Growth          | 2025-10      |   52.994  |             31 |
| SBI Magnum Gilt Fund - Regular Plan - Growth          | 2025-11      |   53.4804 |             30 |
| SBI Magnum Gilt Fund - Regular Plan - Growth          | 2025-12      |   53.7532 |             31 |
| SBI Small Cap Fund - Direct Plan - Growth             | 2025-01      |  103.375  |             31 |
| SBI Small Cap Fund - Direct Plan - Growth             | 2025-02      |  108.661  |             28 |
| SBI Small Cap Fund - Direct Plan - Growth             | 2025-03      |  102.956  |             31 |
| SBI Small Cap Fund - Direct Plan - Growth             | 2025-04      |   94.6978 |             30 |
| SBI Small Cap Fund - Direct Plan - Growth             | 2025-05      |   94.4866 |             31 |
| SBI Small Cap Fund - Direct Plan - Growth             | 2025-06      |   93.0492 |             30 |
| SBI Small Cap Fund - Direct Plan - Growth             | 2025-07      |   92.8845 |             31 |
| SBI Small Cap Fund - Direct Plan - Growth             | 2025-08      |   91.1984 |             31 |
| SBI Small Cap Fund - Direct Plan - Growth             | 2025-09      |   90.677  |             30 |
| SBI Small Cap Fund - Direct Plan - Growth             | 2025-10      |   81.8853 |             31 |
| SBI Small Cap Fund - Direct Plan - Growth             | 2025-11      |   83.961  |             30 |
| SBI Small Cap Fund - Direct Plan - Growth             | 2025-12      |   93.4877 |             31 |
| SBI Small Cap Fund - Regular Plan - Growth            | 2025-01      |  198.591  |             31 |
| SBI Small Cap Fund - Regular Plan - Growth            | 2025-02      |  204.218  |             28 |
| SBI Small Cap Fund - Regular Plan - Growth            | 2025-03      |  204.002  |             31 |
| SBI Small Cap Fund - Regular Plan - Growth            | 2025-04      |  186.005  |             30 |
| SBI Small Cap Fund - Regular Plan - Growth            | 2025-05      |  167.247  |             31 |
| SBI Small Cap Fund - Regular Plan - Growth            | 2025-06      |  173.253  |             30 |
| SBI Small Cap Fund - Regular Plan - Growth            | 2025-07      |  189.354  |             31 |
| SBI Small Cap Fund - Regular Plan - Growth            | 2025-08      |  196.711  |             31 |
| SBI Small Cap Fund - Regular Plan - Growth            | 2025-09      |  215.968  |             30 |
| SBI Small Cap Fund - Regular Plan - Growth            | 2025-10      |  224.512  |             31 |
| SBI Small Cap Fund - Regular Plan - Growth            | 2025-11      |  231.27   |             30 |
| SBI Small Cap Fund - Regular Plan - Growth            | 2025-12      |  249.321  |             31 |
| UTI Flexi Cap Fund - Regular - Growth                 | 2025-01      |  288.522  |             31 |
| UTI Flexi Cap Fund - Regular - Growth                 | 2025-02      |  295.407  |             28 |
| UTI Flexi Cap Fund - Regular - Growth                 | 2025-03      |  306.763  |             31 |
| UTI Flexi Cap Fund - Regular - Growth                 | 2025-04      |  311.696  |             30 |
| UTI Flexi Cap Fund - Regular - Growth                 | 2025-05      |  329.159  |             31 |
| UTI Flexi Cap Fund - Regular - Growth                 | 2025-06      |  344.043  |             30 |
| UTI Flexi Cap Fund - Regular - Growth                 | 2025-07      |  358.062  |             31 |
| UTI Flexi Cap Fund - Regular - Growth                 | 2025-08      |  389.769  |             31 |
| UTI Flexi Cap Fund - Regular - Growth                 | 2025-09      |  409.072  |             30 |
| UTI Flexi Cap Fund - Regular - Growth                 | 2025-10      |  400.872  |             31 |
| UTI Flexi Cap Fund - Regular - Growth                 | 2025-11      |  399.469  |             30 |
| UTI Flexi Cap Fund - Regular - Growth                 | 2025-12      |  392.587  |             31 |
| UTI Mid Cap Fund - Regular - Growth                   | 2025-01      |  164.512  |             31 |
| UTI Mid Cap Fund - Regular - Growth                   | 2025-02      |  156.89   |             28 |
| UTI Mid Cap Fund - Regular - Growth                   | 2025-03      |  150.38   |             31 |
| UTI Mid Cap Fund - Regular - Growth                   | 2025-04      |  157.86   |             30 |
| UTI Mid Cap Fund - Regular - Growth                   | 2025-05      |  154.29   |             31 |
| UTI Mid Cap Fund - Regular - Growth                   | 2025-06      |  149.195  |             30 |
| UTI Mid Cap Fund - Regular - Growth                   | 2025-07      |  157.578  |             31 |
| UTI Mid Cap Fund - Regular - Growth                   | 2025-08      |  148.373  |             31 |
| UTI Mid Cap Fund - Regular - Growth                   | 2025-09      |  149.819  |             30 |
| UTI Mid Cap Fund - Regular - Growth                   | 2025-10      |  143.925  |             31 |
| UTI Mid Cap Fund - Regular - Growth                   | 2025-11      |  126.631  |             30 |
| UTI Mid Cap Fund - Regular - Growth                   | 2025-12      |  135.793  |             31 |
| UTI Nifty 50 Index Fund - Regular - Growth            | 2025-01      |  141.211  |             31 |
| UTI Nifty 50 Index Fund - Regular - Growth            | 2025-02      |  141.451  |             28 |
| UTI Nifty 50 Index Fund - Regular - Growth            | 2025-03      |  146.342  |             31 |
| UTI Nifty 50 Index Fund - Regular - Growth            | 2025-04      |  153.841  |             30 |
| UTI Nifty 50 Index Fund - Regular - Growth            | 2025-05      |  155.526  |             31 |
| UTI Nifty 50 Index Fund - Regular - Growth            | 2025-06      |  159.026  |             30 |
| UTI Nifty 50 Index Fund - Regular - Growth            | 2025-07      |  159.212  |             31 |
| UTI Nifty 50 Index Fund - Regular - Growth            | 2025-08      |  158.03   |             31 |
| UTI Nifty 50 Index Fund - Regular - Growth            | 2025-09      |  164.845  |             30 |
| UTI Nifty 50 Index Fund - Regular - Growth            | 2025-10      |  163.27   |             31 |
| UTI Nifty 50 Index Fund - Regular - Growth            | 2025-11      |  169.429  |             30 |
| UTI Nifty 50 Index Fund - Regular - Growth            | 2025-12      |  173.917  |             31 |

## SIP Inflow Year-over-Year Growth

### Query
```sql
SELECT
    month,
    sip_inflow_crore,
    active_sip_accounts_crore,
    yoy_growth_pct,
    ROUND(sip_inflow_crore * 1.0 / active_sip_accounts_crore, 2) AS avg_sip_per_account_crore
FROM fact_sip_industry
ORDER BY month;
```

### Result
| month   |   sip_inflow_crore |   active_sip_accounts_crore |   yoy_growth_pct |   avg_sip_per_account_crore |
|:--------|-------------------:|----------------------------:|-----------------:|----------------------------:|
| 2022-01 |              11517 |                        4.91 |           nan    |                     2345.62 |
| 2022-02 |              11438 |                        4.93 |           nan    |                     2320.08 |
| 2022-03 |              12328 |                        5.09 |           nan    |                     2422    |
| 2022-04 |              11863 |                        5.48 |           nan    |                     2164.78 |
| 2022-05 |              12286 |                        5.55 |           nan    |                     2213.69 |
| 2022-06 |              12276 |                        5.6  |           nan    |                     2192.14 |
| 2022-07 |              12140 |                        5.65 |           nan    |                     2148.67 |
| 2022-08 |              12694 |                        5.71 |           nan    |                     2223.12 |
| 2022-09 |              12976 |                        5.8  |           nan    |                     2237.24 |
| 2022-10 |              13040 |                        5.93 |           nan    |                     2198.99 |
| 2022-11 |              13306 |                        6    |           nan    |                     2217.67 |
| 2022-12 |              13573 |                        6.05 |           nan    |                     2243.47 |
| 2023-01 |              13856 |                        6.13 |            20.31 |                     2260.36 |
| 2023-02 |              13687 |                        6.19 |            19.66 |                     2211.15 |
| 2023-03 |              14276 |                        6.32 |            15.8  |                     2258.86 |
| 2023-04 |              14749 |                        6.41 |            24.33 |                     2300.94 |
| 2023-05 |              14749 |                        6.5  |            20.05 |                     2269.08 |
| 2023-06 |              14734 |                        6.55 |            20.02 |                     2249.47 |
| 2023-07 |              15245 |                        6.65 |            25.58 |                     2292.48 |
| 2023-08 |              15814 |                        6.73 |            24.58 |                     2349.78 |
| 2023-09 |              16042 |                        6.82 |            23.63 |                     2352.2  |
| 2023-10 |              16928 |                        6.91 |            29.82 |                     2449.78 |
| 2023-11 |              17073 |                        7    |            28.31 |                     2439    |
| 2023-12 |              17610 |                        7.1  |            29.74 |                     2480.28 |
| 2024-01 |              18838 |                        7.2  |            35.96 |                     2616.39 |
| 2024-02 |              19187 |                        7.3  |            40.18 |                     2628.36 |
| 2024-03 |              20371 |                        7.4  |            42.69 |                     2752.84 |
| 2024-04 |              20371 |                        7.6  |            38.12 |                     2680.39 |
| 2024-05 |              21262 |                        7.78 |            44.16 |                     2732.9  |
| 2024-06 |              21262 |                        7.9  |            44.31 |                     2691.39 |
| 2024-07 |              23332 |                        8    |            53.05 |                     2916.5  |
| 2024-08 |              23547 |                        8.11 |            48.9  |                     2903.45 |
| 2024-09 |              24509 |                        8.22 |            52.78 |                     2981.63 |
| 2024-10 |              25323 |                        8.3  |            49.59 |                     3050.96 |
| 2024-11 |              25320 |                        8.4  |            48.3  |                     3014.29 |
| 2024-12 |              26459 |                        8.5  |            50.25 |                     3112.82 |
| 2025-01 |              26400 |                        8.22 |            40.14 |                     3211.68 |
| 2025-02 |              25999 |                        8.3  |            35.5  |                     3132.41 |
| 2025-03 |              25926 |                        8.11 |            27.27 |                     3196.79 |
| 2025-04 |              26632 |                        8.38 |            30.73 |                     3178.04 |
| 2025-05 |              26688 |                        8.5  |            25.52 |                     3139.76 |
| 2025-06 |              27274 |                        8.62 |            28.28 |                     3164.04 |
| 2025-07 |              28464 |                        8.75 |            22    |                     3253.03 |
| 2025-08 |              28265 |                        8.85 |            20.04 |                     3193.79 |
| 2025-09 |              29361 |                        9    |            19.8  |                     3262.33 |
| 2025-10 |              29529 |                        9.1  |            16.61 |                     3244.95 |
| 2025-11 |              30200 |                        9.2  |            19.27 |                     3282.61 |
| 2025-12 |              31002 |                        9.35 |            17.17 |                     3315.72 |

## Transaction Volume and Amount by State

### Query
```sql
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
```

### Result
| state          |   total_transactions |   sip_count |   lumpsum_count |   redemption_count |   total_amount_lakh |   avg_transaction_inr |
|:---------------|---------------------:|------------:|----------------:|-------------------:|--------------------:|----------------------:|
| Punjab         |                 2965 |        1792 |             721 |                452 |             3157.8  |                106503 |
| Tamil Nadu     |                 2806 |        1642 |             684 |                480 |             3151.77 |                112323 |
| Madhya Pradesh |                 2931 |        1796 |             720 |                415 |             3083.12 |                105190 |
| Rajasthan      |                 2577 |        1499 |             672 |                406 |             2986.46 |                115889 |
| Gujarat        |                 2780 |        1653 |             712 |                415 |             2983.59 |                107323 |
| West Bengal    |                 2748 |        1638 |             658 |                452 |             2971.83 |                108145 |
| Telangana      |                 2718 |        1656 |             672 |                390 |             2902.19 |                106777 |
| Delhi          |                 2677 |        1606 |             677 |                394 |             2896.33 |                108193 |
| Uttar Pradesh  |                 2695 |        1625 |             666 |                404 |             2853.69 |                105888 |
| Haryana        |                 2736 |        1690 |             656 |                390 |             2796.34 |                102206 |
| Karnataka      |                 2621 |        1620 |             605 |                396 |             2737.54 |                104446 |
| Maharashtra    |                 2524 |        1499 |             652 |                373 |             2695.13 |                106780 |

## Funds with Expense Ratio < 1% (Cost-Efficient Funds)

### Query
```sql
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
```

### Result
|   amfi_code | scheme_name                                          | fund_house               | plan    |   expense_ratio_pct |   return_3yr_pct |   sharpe_ratio |   aum_crore |
|------------:|:-----------------------------------------------------|:-------------------------|:--------|--------------------:|-----------------:|---------------:|------------:|
|      120507 | ICICI Pru Liquid Fund - Regular - Growth             | ICICI Prudential MF      | Regular |                0.74 |             7.68 |           7.68 |       39116 |
|      120844 | Kotak Liquid Fund - Regular - Growth                 | Kotak Mahindra MF        | Regular |                0.6  |             6.18 |           6.18 |       27623 |
|      101208 | ABSL Liquid Fund - Regular - Growth                  | Aditya Birla Sun Life MF | Regular |                0.79 |             5.14 |           5.14 |       38995 |
|      100025 | HDFC Short Term Debt Fund - Regular - Growth         | HDFC Mutual Fund         | Regular |                0.56 |             7.37 |           1.84 |       27953 |
|      119120 | SBI Magnum Gilt Fund - Regular Plan - Growth         | SBI Mutual Fund          | Regular |                0.77 |             6.07 |           1.52 |       24101 |
|      118636 | Nippon India Gilt Securities Fund - Regular - Growth | Nippon India MF          | Regular |                0.55 |             5.31 |           1.33 |       30030 |
|      120504 | ICICI Pru Bluechip Fund - Direct - Growth            | ICICI Prudential MF      | Direct  |                0.8  |            14.41 |           1.03 |       41553 |
|      125497 | HDFC Top 100 Fund - Direct Plan - Growth             | HDFC Mutual Fund         | Direct  |                0.92 |            13.38 |           0.96 |       10611 |
|      119599 | SBI Small Cap Fund - Direct Plan - Growth            | SBI Mutual Fund          | Direct  |                0.72 |            23.14 |           0.93 |       36061 |
|      118635 | Nippon India ETF Nifty 50 BeES                       | Nippon India MF          | Direct  |                0.89 |            11.77 |           0.91 |       20284 |
|      118633 | Nippon India Large Cap Fund - Direct - Growth        | Nippon India MF          | Direct  |                0.72 |            12.33 |           0.88 |       39475 |
|      119093 | Axis Bluechip Fund - Direct - Growth                 | Axis Mutual Fund         | Direct  |                0.75 |            12.14 |           0.87 |       15866 |
|      119552 | SBI Bluechip Fund - Direct Plan - Growth             | SBI Mutual Fund          | Direct  |                0.66 |            11.3  |           0.81 |        1231 |
|      125498 | HDFC Mid-Cap Opportunities Fund - Direct - Growth    | HDFC Mutual Fund         | Direct  |                0.78 |            15.29 |           0.8  |       18792 |

## Fund Performance Comparison by Category

### Query
```sql
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
```

### Result
| sub_category    |   num_funds |   avg_1yr_return |   avg_3yr_return |   avg_5yr_return |   avg_sharpe |   avg_alpha |   avg_volatility |   avg_max_drawdown |
|:----------------|------------:|-----------------:|-----------------:|-----------------:|-------------:|------------:|-----------------:|-------------------:|
| Liquid          |           3 |             6.44 |             6.33 |             8.05 |         6.33 |        1.52 |              0.5 |              -3.36 |
| Short Duration  |           1 |             6.83 |             7.37 |             6.41 |         1.84 |        1.98 |              4   |              -6.01 |
| Gilt            |           2 |             5.77 |             5.69 |             7.07 |         1.43 |        1.25 |              4   |              -2.26 |
| Value           |           1 |            16.67 |            14.76 |            12.6  |         0.98 |        0.55 |             15   |             -21.89 |
| Flexi Cap       |           2 |            16.59 |            15.5  |            14.64 |         0.97 |        1.82 |             16   |             -15.82 |
| Large Cap       |          14 |            13.72 |            12.99 |            13.32 |         0.93 |        1.25 |             14   |             -21.46 |
| Index           |           1 |            13.76 |            12.1  |            11.31 |         0.93 |        0.93 |             13   |             -24.42 |
| Large & Mid Cap |           1 |            14.91 |            14.56 |            15.68 |         0.91 |        1.7  |             16   |             -33.15 |
| Index/ETF       |           1 |            10.14 |            11.77 |            12.31 |         0.91 |        1.8  |             13   |             -26.75 |
| Small Cap       |           6 |            22.26 |            21.69 |            21.9  |         0.87 |        1.03 |             25   |             -20.68 |
| Mid Cap         |           7 |            15.98 |            16.59 |            17.52 |         0.87 |        1.17 |             19   |             -23.21 |
| ELSS            |           1 |            11.16 |            13.58 |            14.26 |         0.8  |        0.54 |             17   |             -22.62 |

## Top 5 Funds per Category (by 3-Year CAGR)

### Query
```sql
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
```

### Result
| sub_category    | scheme_name                                           | fund_house               |   return_3yr_pct |   sharpe_ratio |   rank |
|:----------------|:------------------------------------------------------|:-------------------------|-----------------:|---------------:|-------:|
| ELSS            | Mirae Asset Tax Saver Fund - Regular - Growth         | Mirae Asset MF           |            13.58 |           0.8  |      1 |
| Flexi Cap       | Kotak Flexicap Fund - Regular - Growth                | Kotak Mahindra MF        |            15.65 |           0.98 |      1 |
| Flexi Cap       | UTI Flexi Cap Fund - Regular - Growth                 | UTI Mutual Fund          |            15.34 |           0.96 |      2 |
| Gilt            | SBI Magnum Gilt Fund - Regular Plan - Growth          | SBI Mutual Fund          |             6.07 |           1.52 |      1 |
| Gilt            | Nippon India Gilt Securities Fund - Regular - Growth  | Nippon India MF          |             5.31 |           1.33 |      2 |
| Index           | UTI Nifty 50 Index Fund - Regular - Growth            | UTI Mutual Fund          |            12.1  |           0.93 |      1 |
| Index/ETF       | Nippon India ETF Nifty 50 BeES                        | Nippon India MF          |            11.77 |           0.91 |      1 |
| Large & Mid Cap | Mirae Asset Emerging Bluechip Fund - Regular - Growth | Mirae Asset MF           |            14.56 |           0.91 |      1 |
| Large Cap       | HDFC Top 100 Fund - Regular Plan - Growth             | HDFC Mutual Fund         |            14.84 |           1.06 |      1 |
| Large Cap       | Mirae Asset Large Cap Fund - Regular - Growth         | Mirae Asset MF           |            14.81 |           1.06 |      2 |
| Large Cap       | ICICI Pru Bluechip Fund - Direct - Growth             | ICICI Prudential MF      |            14.41 |           1.03 |      3 |
| Large Cap       | Nippon India Large Cap Fund - Regular - Growth        | Nippon India MF          |            14    |           1    |      4 |
| Large Cap       | ABSL Frontline Equity Fund - Regular - Growth         | Aditya Birla Sun Life MF |            13.78 |           0.98 |      5 |
| Liquid          | ICICI Pru Liquid Fund - Regular - Growth              | ICICI Prudential MF      |             7.68 |           7.68 |      1 |
| Liquid          | Kotak Liquid Fund - Regular - Growth                  | Kotak Mahindra MF        |             6.18 |           6.18 |      2 |
| Liquid          | ABSL Liquid Fund - Regular - Growth                   | Aditya Birla Sun Life MF |             5.14 |           5.14 |      3 |
| Mid Cap         | Kotak Emerging Equity Fund - Regular - Growth         | Kotak Mahindra MF        |            18.23 |           0.96 |      1 |
| Mid Cap         | ICICI Pru Midcap Fund - Regular - Growth              | ICICI Prudential MF      |            18.08 |           0.95 |      2 |
| Mid Cap         | DSP Midcap Fund - Regular - Growth                    | DSP Mutual Fund          |            17.16 |           0.9  |      3 |
| Mid Cap         | HDFC Mid-Cap Opportunities Fund - Regular - Growth    | HDFC Mutual Fund         |            16.58 |           0.87 |      4 |
| Mid Cap         | UTI Mid Cap Fund - Regular - Growth                   | UTI Mutual Fund          |            15.61 |           0.82 |      5 |
| Short Duration  | HDFC Short Term Debt Fund - Regular - Growth          | HDFC Mutual Fund         |             7.37 |           1.84 |      1 |
| Small Cap       | SBI Small Cap Fund - Regular Plan - Growth            | SBI Mutual Fund          |            23.39 |           0.94 |      1 |
| Small Cap       | SBI Small Cap Fund - Direct Plan - Growth             | SBI Mutual Fund          |            23.14 |           0.93 |      2 |
| Small Cap       | ABSL Small Cap Fund - Regular - Growth                | Aditya Birla Sun Life MF |            22.38 |           0.9  |      3 |
| Small Cap       | Axis Small Cap Fund - Regular - Growth                | Axis Mutual Fund         |            20.98 |           0.84 |      4 |
| Small Cap       | Nippon India Small Cap Fund - Regular - Growth        | Nippon India MF          |            20.15 |           0.81 |      5 |
| Value           | ICICI Pru Value Discovery Fund - Regular - Growth     | ICICI Prudential MF      |            14.76 |           0.98 |      1 |

## Benchmark Tracking — Alpha by Fund vs Benchmark

### Query
```sql
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
```

### Result
| scheme_name                                           | benchmark                    |   fund_3yr |   bench_3yr |   alpha |   beta |   excess_return | performance_label     |
|:------------------------------------------------------|:-----------------------------|-----------:|------------:|--------:|-------:|----------------:|:----------------------|
| HDFC Short Term Debt Fund - Regular - Growth          | CRISIL Short Term Bond Index |       7.37 |        5.39 |    1.98 |   0.44 |            1.98 | Strong Outperformer   |
| Kotak Emerging Equity Fund - Regular - Growth         | NIFTY Midcap 150 TRI         |      18.23 |       16.32 |    1.91 |   1    |            1.91 | Strong Outperformer   |
| ICICI Pru Liquid Fund - Regular - Growth              | CRISIL Liquid Fund AI Index  |       7.68 |        5.83 |    1.85 |   0.26 |            1.85 | Strong Outperformer   |
| Kotak Flexicap Fund - Regular - Growth                | NIFTY 500 TRI                |      15.65 |       13.8  |    1.85 |   0.95 |            1.85 | Strong Outperformer   |
| ABSL Small Cap Fund - Regular - Growth                | BSE 250 SmallCap TRI         |      22.38 |       20.54 |    1.84 |   0.97 |            1.84 | Strong Outperformer   |
| DSP Top 100 Equity Fund - Regular - Growth            | NIFTY 100 TRI                |      12.82 |       11    |    1.82 |   0.91 |            1.82 | Strong Outperformer   |
| Nippon India ETF Nifty 50 BeES                        | NIFTY 50 TRI                 |      11.77 |        9.97 |    1.8  |   1.04 |            1.8  | Strong Outperformer   |
| UTI Flexi Cap Fund - Regular - Growth                 | NIFTY 500 TRI                |      15.34 |       13.55 |    1.79 |   1    |            1.79 | Strong Outperformer   |
| SBI Bluechip Fund - Direct Plan - Growth              | NIFTY 100 TRI                |      11.3  |        9.52 |    1.78 |   0.87 |            1.78 | Strong Outperformer   |
| Nippon India Large Cap Fund - Direct - Growth         | NIFTY 100 TRI                |      12.33 |       10.63 |    1.7  |   1.02 |            1.7  | Strong Outperformer   |
| Mirae Asset Emerging Bluechip Fund - Regular - Growth | NIFTY Large Midcap 250 TRI   |      14.56 |       12.86 |    1.7  |   0.99 |            1.7  | Strong Outperformer   |
| Mirae Asset Large Cap Fund - Regular - Growth         | NIFTY 100 TRI                |      14.81 |       13.19 |    1.62 |   0.96 |            1.62 | Strong Outperformer   |
| SBI Magnum Gilt Fund - Regular Plan - Growth          | CRISIL Dynamic Gilt Index    |       6.07 |        4.47 |    1.6  |   0.22 |            1.6  | Strong Outperformer   |
| Kotak Liquid Fund - Regular - Growth                  | CRISIL Liquid Fund AI Index  |       6.18 |        4.66 |    1.52 |   0.47 |            1.52 | Strong Outperformer   |
| Axis Bluechip Fund - Direct - Growth                  | NIFTY 100 TRI                |      12.14 |       10.71 |    1.43 |   0.87 |            1.43 | Strong Outperformer   |
| Axis Midcap Fund - Regular - Growth                   | NIFTY Midcap 50 TRI          |      15.18 |       13.76 |    1.42 |   1    |            1.42 | Strong Outperformer   |
| Axis Bluechip Fund - Regular - Growth                 | NIFTY 100 TRI                |      11.84 |       10.43 |    1.41 |   0.91 |            1.41 | Strong Outperformer   |
| ABSL Frontline Equity Fund - Regular - Growth         | NIFTY 100 TRI                |      13.78 |       12.44 |    1.34 |   1.03 |            1.34 | Strong Outperformer   |
| Kotak Bluechip Fund - Regular - Growth                | NIFTY 100 TRI                |      12.25 |       10.98 |    1.27 |   0.93 |            1.27 | Strong Outperformer   |
| SBI Small Cap Fund - Regular Plan - Growth            | BSE 250 SmallCap TRI         |      23.39 |       22.16 |    1.23 |   0.89 |            1.23 | Strong Outperformer   |
| ABSL Liquid Fund - Regular - Growth                   | CRISIL Liquid Fund AI Index  |       5.14 |        3.96 |    1.18 |   0.43 |            1.18 | Strong Outperformer   |
| SBI Small Cap Fund - Direct Plan - Growth             | BSE 250 SmallCap TRI         |      23.14 |       22.01 |    1.13 |   1.04 |            1.13 | Strong Outperformer   |
| HDFC Top 100 Fund - Direct Plan - Growth              | NIFTY 100 TRI                |      13.38 |       12.25 |    1.13 |   0.97 |            1.13 | Strong Outperformer   |
| UTI Mid Cap Fund - Regular - Growth                   | NIFTY Midcap 150 TRI         |      15.61 |       14.49 |    1.12 |   0.92 |            1.12 | Strong Outperformer   |
| DSP Midcap Fund - Regular - Growth                    | NIFTY Midcap 150 TRI         |      17.16 |       16.14 |    1.02 |   0.98 |            1.02 | Strong Outperformer   |
| HDFC Mid-Cap Opportunities Fund - Regular - Growth    | NIFTY Midcap 150 TRI         |      16.58 |       15.63 |    0.95 |   0.91 |            0.95 | Marginal Outperformer |
| UTI Nifty 50 Index Fund - Regular - Growth            | NIFTY 50 TRI                 |      12.1  |       11.17 |    0.93 |   0.9  |            0.93 | Marginal Outperformer |
| HDFC Mid-Cap Opportunities Fund - Direct - Growth     | NIFTY Midcap 150 TRI         |      15.29 |       14.39 |    0.9  |   1.04 |            0.9  | Marginal Outperformer |
| Nippon India Gilt Securities Fund - Regular - Growth  | CRISIL Dynamic Gilt Index    |       5.31 |        4.42 |    0.89 |   0.37 |            0.89 | Marginal Outperformer |
| ICICI Pru Midcap Fund - Regular - Growth              | NIFTY Midcap 150 TRI         |      18.08 |       17.19 |    0.89 |   1    |            0.89 | Marginal Outperformer |
| ICICI Pru Bluechip Fund - Direct - Growth             | NIFTY 100 TRI                |      14.41 |       13.53 |    0.88 |   1.03 |            0.88 | Marginal Outperformer |
| SBI Bluechip Fund - Regular Plan - Growth             | NIFTY 100 TRI                |      12.36 |       11.49 |    0.87 |   0.89 |            0.87 | Marginal Outperformer |
| Nippon India Large Cap Fund - Regular - Growth        | NIFTY 100 TRI                |      14    |       13.14 |    0.86 |   0.88 |            0.86 | Marginal Outperformer |
| Nippon India Small Cap Fund - Regular - Growth        | BSE 250 SmallCap TRI         |      20.15 |       19.35 |    0.8  |   1.03 |            0.8  | Marginal Outperformer |
| HDFC Top 100 Fund - Regular Plan - Growth             | NIFTY 100 TRI                |      14.84 |       14.06 |    0.78 |   0.97 |            0.78 | Marginal Outperformer |
| DSP Small Cap Fund - Regular - Growth                 | BSE 250 SmallCap TRI         |      20.08 |       19.39 |    0.69 |   0.98 |            0.69 | Marginal Outperformer |
| ICICI Pru Bluechip Fund - Regular - Growth            | NIFTY 100 TRI                |      11.54 |       10.88 |    0.66 |   0.96 |            0.66 | Marginal Outperformer |
| ICICI Pru Value Discovery Fund - Regular - Growth     | NIFTY 500 TRI                |      14.76 |       14.21 |    0.55 |   0.92 |            0.55 | Marginal Outperformer |
| Mirae Asset Tax Saver Fund - Regular - Growth         | NIFTY 500 TRI                |      13.58 |       13.04 |    0.54 |   0.98 |            0.54 | Marginal Outperformer |
| Axis Small Cap Fund - Regular - Growth                | BSE 250 SmallCap TRI         |      20.98 |       20.47 |    0.51 |   1    |            0.51 | Marginal Outperformer |

## Investor Demographics — SIP Behavior by Age & Income

### Query
```sql
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
```

### Result
| age_group   | gender   | city_tier   |   total_transactions |   avg_amount |   avg_income_lakh |   total_sip_inr |   total_redemption_inr |
|:------------|:---------|:------------|---------------------:|-------------:|------------------:|----------------:|-----------------------:|
| 18-25       | Female   | B30         |                  646 |       110644 |              5.42 |         4305968 |               24817927 |
| 18-25       | Female   | T30         |                 1076 |       107055 |              5.48 |         7113164 |               46646492 |
| 18-25       | Male     | B30         |                 1226 |       104771 |              5.43 |         8554611 |               44234882 |
| 18-25       | Male     | T30         |                 1968 |       110022 |              5.45 |        12326870 |               75968744 |
| 26-35       | Female   | B30         |                 1493 |       105161 |             15.93 |         9241472 |               52736702 |
| 26-35       | Female   | T30         |                 2886 |       106776 |             14.99 |        19737285 |              101907582 |
| 26-35       | Male     | B30         |                 3073 |       110321 |             15.55 |        20843940 |              118814639 |
| 26-35       | Male     | T30         |                 6011 |       107706 |             15.85 |        38764643 |              227270488 |
| 36-45       | Female   | B30         |                  909 |       110947 |             37.27 |         5271051 |               38640371 |
| 36-45       | Female   | T30         |                 1796 |       107205 |             35.52 |        12179181 |               69095519 |
| 36-45       | Male     | B30         |                 1679 |       113533 |             36.03 |        11095944 |               69964093 |
| 36-45       | Male     | T30         |                 3762 |       103039 |             35.77 |        25077071 |              141425926 |
| 46-55       | Female   | B30         |                  402 |       112324 |             54.58 |         2237045 |               16581266 |
| 46-55       | Female   | T30         |                  868 |       109632 |             57.34 |         6012431 |               34743982 |
| 46-55       | Male     | B30         |                  777 |       105336 |             56.65 |         4636568 |               26810282 |
| 46-55       | Male     | T30         |                 1732 |       105800 |             59.36 |        12728512 |               63189967 |
| 56+         | Female   | B30         |                  317 |       101752 |             45.88 |         1836367 |               12802054 |
| 56+         | Female   | T30         |                  576 |       101661 |             45.47 |         3829838 |               21120613 |
| 56+         | Male     | B30         |                  537 |       103630 |             45.9  |         4281904 |               19105251 |
| 56+         | Male     | T30         |                 1044 |       109986 |             42.74 |         7159626 |               38648711 |

## Portfolio Concentration — Top Sectors Across All Funds

### Query
```sql
SELECT
    sector,
    COUNT(DISTINCT amfi_code) AS num_funds_holding,
    COUNT(*) AS total_holdings,
    ROUND(AVG(weight_pct), 2) AS avg_weight_pct,
    ROUND(SUM(market_value_cr), 2) AS total_market_value_cr
FROM fact_portfolio
GROUP BY sector
ORDER BY total_market_value_cr DESC;
```

### Result
| sector         |   num_funds_holding |   total_holdings |   avg_weight_pct |   total_market_value_cr |
|:---------------|--------------------:|-----------------:|-----------------:|------------------------:|
| Banking        |                  30 |               60 |            10.87 |                62840.3  |
| IT             |                  27 |               40 |            11.39 |                38477.1  |
| Pharma         |                  22 |               38 |            10.72 |                34606.1  |
| Automobile     |                  26 |               33 |             9.81 |                34297    |
| Utilities      |                  19 |               24 |            11.06 |                25108.6  |
| Infrastructure |                  18 |               22 |             8.73 |                22433.4  |
| FMCG           |                  19 |               21 |            10.91 |                21151.2  |
| Telecom        |                  15 |               15 |             9.71 |                16051.5  |
| Energy         |                  13 |               13 |             9.07 |                15286.5  |
| Diversified    |                  14 |               14 |            12.09 |                13897.8  |
| Cement         |                  12 |               12 |             8.75 |                11612    |
| Paints         |                  10 |               10 |             8.99 |                10612.1  |
| Consumer Goods |                   9 |                9 |            14.18 |                 9859.7  |
| NBFC           |                  11 |               11 |            10.83 |                 8615.46 |

## Fund House AUM Growth Trajectory

### Query
```sql
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
```

### Result
| fund_house               | date       |   aum_lakh_crore |   aum_crore |   num_schemes |   qoq_growth_pct |
|:-------------------------|:-----------|-----------------:|------------:|--------------:|-----------------:|
| Aditya Birla Sun Life MF | 2022-03-31 |             2.78 |      278000 |           199 |           nan    |
| Aditya Birla Sun Life MF | 2022-09-30 |             2.85 |      285000 |           199 |             2.52 |
| Aditya Birla Sun Life MF | 2023-03-31 |             2.75 |      275000 |           199 |            -3.51 |
| Aditya Birla Sun Life MF | 2023-09-30 |             3.08 |      308000 |           199 |            12    |
| Aditya Birla Sun Life MF | 2024-03-31 |             3.4  |      340000 |           199 |            10.39 |
| Aditya Birla Sun Life MF | 2024-09-30 |             3.62 |      362000 |           199 |             6.47 |
| Aditya Birla Sun Life MF | 2024-12-31 |             3.84 |      384000 |           199 |             6.08 |
| Aditya Birla Sun Life MF | 2025-03-31 |             3.85 |      385000 |           199 |             0.26 |
| Aditya Birla Sun Life MF | 2025-12-31 |             4.6  |      460000 |           199 |            19.48 |
| Axis Mutual Fund         | 2022-03-31 |             2.5  |      250000 |            95 |           nan    |
| Axis Mutual Fund         | 2022-09-30 |             2.4  |      240000 |            95 |            -4    |
| Axis Mutual Fund         | 2023-03-31 |             2.41 |      241000 |            95 |             0.42 |
| Axis Mutual Fund         | 2023-09-30 |             2.6  |      260000 |            95 |             7.88 |
| Axis Mutual Fund         | 2024-03-31 |             2.8  |      280000 |            95 |             7.69 |
| Axis Mutual Fund         | 2024-09-30 |             2.9  |      290000 |            95 |             3.57 |
| Axis Mutual Fund         | 2024-12-31 |             3    |      300000 |            95 |             3.45 |
| Axis Mutual Fund         | 2025-03-31 |             3.1  |      310000 |            95 |             3.33 |
| Axis Mutual Fund         | 2025-12-31 |             3.5  |      350000 |            95 |            12.9  |
| DSP Mutual Fund          | 2022-03-31 |             1.1  |      110000 |            88 |           nan    |
| DSP Mutual Fund          | 2022-09-30 |             1.12 |      112000 |            88 |             1.82 |
| DSP Mutual Fund          | 2023-03-31 |             1.15 |      115000 |            88 |             2.68 |
| DSP Mutual Fund          | 2023-09-30 |             1.32 |      132000 |            88 |            14.78 |
| DSP Mutual Fund          | 2024-03-31 |             1.55 |      155000 |            88 |            17.42 |
| DSP Mutual Fund          | 2024-09-30 |             1.72 |      172000 |            88 |            10.97 |
| DSP Mutual Fund          | 2024-12-31 |             1.88 |      188000 |            88 |             9.3  |
| DSP Mutual Fund          | 2025-03-31 |             1.95 |      195000 |            88 |             3.72 |
| DSP Mutual Fund          | 2025-12-31 |             2.3  |      230000 |            88 |            17.95 |
| HDFC Mutual Fund         | 2022-03-31 |             4.35 |      435000 |           195 |           nan    |
| HDFC Mutual Fund         | 2022-09-30 |             4.45 |      445000 |           195 |             2.3  |
| HDFC Mutual Fund         | 2023-03-31 |             4.5  |      450000 |           195 |             1.12 |
| HDFC Mutual Fund         | 2023-09-30 |             5.35 |      535000 |           195 |            18.89 |
| HDFC Mutual Fund         | 2024-03-31 |             6.45 |      645000 |           195 |            20.56 |
| HDFC Mutual Fund         | 2024-09-30 |             7.1  |      710000 |           195 |            10.08 |
| HDFC Mutual Fund         | 2024-12-31 |             7.87 |      787000 |           195 |            10.85 |
| HDFC Mutual Fund         | 2025-03-31 |             7.95 |      795000 |           195 |             1.02 |
| HDFC Mutual Fund         | 2025-12-31 |             9.3  |      930000 |           195 |            16.98 |
| ICICI Prudential MF      | 2022-03-31 |             4.65 |      465000 |           216 |           nan    |
| ICICI Prudential MF      | 2022-09-30 |             4.88 |      488000 |           216 |             4.95 |
| ICICI Prudential MF      | 2023-03-31 |             5    |      500000 |           216 |             2.46 |
| ICICI Prudential MF      | 2023-09-30 |             5.9  |      590000 |           216 |            18    |
| ICICI Prudential MF      | 2024-03-31 |             6.8  |      680000 |           216 |            15.25 |
| ICICI Prudential MF      | 2024-09-30 |             7.42 |      742000 |           216 |             9.12 |
| ICICI Prudential MF      | 2024-12-31 |             8.74 |      874000 |           216 |            17.79 |
| ICICI Prudential MF      | 2025-03-31 |             8.8  |      880000 |           216 |             0.69 |
| ICICI Prudential MF      | 2025-12-31 |            10.74 |     1074000 |           216 |            22.05 |
| Kotak Mahindra MF        | 2022-03-31 |             2.7  |      270000 |           168 |           nan    |
| Kotak Mahindra MF        | 2022-09-30 |             2.72 |      272000 |           168 |             0.74 |
| Kotak Mahindra MF        | 2023-03-31 |             2.89 |      289000 |           168 |             6.25 |
| Kotak Mahindra MF        | 2023-09-30 |             3.25 |      325000 |           168 |            12.46 |
| Kotak Mahindra MF        | 2024-03-31 |             3.8  |      380000 |           168 |            16.92 |
| Kotak Mahindra MF        | 2024-09-30 |             4.05 |      405000 |           168 |             6.58 |
| Kotak Mahindra MF        | 2024-12-31 |             4.89 |      489000 |           168 |            20.74 |
| Kotak Mahindra MF        | 2025-03-31 |             4.92 |      492000 |           168 |             0.61 |
| Kotak Mahindra MF        | 2025-12-31 |             5.8  |      580000 |           168 |            17.89 |
| Mirae Asset MF           | 2022-03-31 |             1.05 |      105000 |            56 |           nan    |
| Mirae Asset MF           | 2022-09-30 |             1.08 |      108000 |            56 |             2.86 |
| Mirae Asset MF           | 2023-03-31 |             1.16 |      116000 |            56 |             7.41 |
| Mirae Asset MF           | 2023-09-30 |             1.42 |      142000 |            56 |            22.41 |
| Mirae Asset MF           | 2024-03-31 |             1.75 |      175000 |            56 |            23.24 |
| Mirae Asset MF           | 2024-09-30 |             1.9  |      190000 |            56 |             8.57 |
| Mirae Asset MF           | 2024-12-31 |             2.1  |      210000 |            56 |            10.53 |
| Mirae Asset MF           | 2025-03-31 |             2.25 |      225000 |            56 |             7.14 |
| Mirae Asset MF           | 2025-12-31 |             2.9  |      290000 |            56 |            28.89 |
| Nippon India MF          | 2022-03-31 |             2.7  |      270000 |           177 |           nan    |
| Nippon India MF          | 2022-09-30 |             2.78 |      278000 |           177 |             2.96 |
| Nippon India MF          | 2023-03-31 |             2.93 |      293000 |           177 |             5.4  |
| Nippon India MF          | 2023-09-30 |             3.4  |      340000 |           177 |            16.04 |
| Nippon India MF          | 2024-03-31 |             4.3  |      430000 |           177 |            26.47 |
| Nippon India MF          | 2024-09-30 |             4.68 |      468000 |           177 |             8.84 |
| Nippon India MF          | 2024-12-31 |             5.7  |      570000 |           177 |            21.79 |
| Nippon India MF          | 2025-03-31 |             5.6  |      560000 |           177 |            -1.75 |
| Nippon India MF          | 2025-12-31 |             7    |      700000 |           177 |            25    |
| SBI Mutual Fund          | 2022-03-31 |             6.05 |      605000 |           186 |           nan    |
| SBI Mutual Fund          | 2022-09-30 |             6.3  |      630000 |           186 |             4.13 |
| SBI Mutual Fund          | 2023-03-31 |             7.17 |      717000 |           186 |            13.81 |
| SBI Mutual Fund          | 2023-09-30 |             8.45 |      845000 |           186 |            17.85 |
| SBI Mutual Fund          | 2024-03-31 |            10    |     1000000 |           186 |            18.34 |
| SBI Mutual Fund          | 2024-09-30 |            10.8  |     1080000 |           186 |             8    |
| SBI Mutual Fund          | 2024-12-31 |            11.14 |     1114000 |           186 |             3.15 |
| SBI Mutual Fund          | 2025-03-31 |            12.5  |     1250000 |           186 |            12.21 |
| SBI Mutual Fund          | 2025-12-31 |            12.5  |     1250000 |           186 |             0    |
| UTI Mutual Fund          | 2022-03-31 |             2.3  |      230000 |           142 |           nan    |
| UTI Mutual Fund          | 2022-09-30 |             2.32 |      232000 |           142 |             0.87 |
| UTI Mutual Fund          | 2023-03-31 |             2.39 |      239000 |           142 |             3.02 |
| UTI Mutual Fund          | 2023-09-30 |             2.65 |      265000 |           142 |            10.88 |
| UTI Mutual Fund          | 2024-03-31 |             2.9  |      290000 |           142 |             9.43 |
| UTI Mutual Fund          | 2024-09-30 |             3.08 |      308000 |           142 |             6.21 |
| UTI Mutual Fund          | 2024-12-31 |             3.52 |      352000 |           142 |            14.29 |
| UTI Mutual Fund          | 2025-03-31 |             3.55 |      355000 |           142 |             0.85 |
| UTI Mutual Fund          | 2025-12-31 |             4.1  |      410000 |           142 |            15.49 |

## Risk-Adjusted Performance Dashboard Query

### Query
```sql
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
```

### Result
| scheme_name                                           | fund_house               | sub_category    | risk_category   |   return_3yr_pct |   sharpe_ratio |   sortino_ratio |   alpha |   beta |   volatility |   max_drawdown_pct |   aum_crore |   composite_score |
|:------------------------------------------------------|:-------------------------|:----------------|:----------------|-----------------:|---------------:|----------------:|--------:|-------:|-------------:|-------------------:|------------:|------------------:|
| SBI Small Cap Fund - Direct Plan - Growth             | SBI Mutual Fund          | Small Cap       | Very High       |            23.14 |           0.93 |            1.67 |    1.13 |   1.04 |         25   |             -24.78 |       36061 |             71.28 |
| Kotak Flexicap Fund - Regular - Growth                | Kotak Mahindra MF        | Flexi Cap       | Moderately High |            15.65 |           0.98 |            1.57 |    1.85 |   0.95 |         16   |             -19.5  |       35012 |             69.87 |
| Kotak Emerging Equity Fund - Regular - Growth         | Kotak Mahindra MF        | Mid Cap         | High            |            18.23 |           0.96 |            1.27 |    1.91 |   1    |         19   |             -21.92 |       47469 |             69.1  |
| ABSL Small Cap Fund - Regular - Growth                | Aditya Birla Sun Life MF | Small Cap       | Very High       |            22.38 |           0.9  |            1.47 |    1.84 |   0.97 |         25   |             -23.61 |       41613 |             66.92 |
| SBI Small Cap Fund - Regular Plan - Growth            | SBI Mutual Fund          | Small Cap       | Very High       |            23.39 |           0.94 |            1.35 |    1.23 |   0.89 |         25   |             -13.35 |       19259 |             63.46 |
| Mirae Asset Large Cap Fund - Regular - Growth         | Mirae Asset MF           | Large Cap       | Moderate        |            14.81 |           1.06 |            1.66 |    1.62 |   0.96 |         14   |             -17.07 |       11361 |             62.69 |
| HDFC Short Term Debt Fund - Regular - Growth          | HDFC Mutual Fund         | Short Duration  | Low             |             7.37 |           1.84 |            2.79 |    1.98 |   0.44 |          4   |              -6.01 |       27953 |             62.05 |
| ICICI Pru Liquid Fund - Regular - Growth              | ICICI Prudential MF      | Liquid          | Low             |             7.68 |           7.68 |           10.37 |    1.85 |   0.26 |          0.5 |              -2.62 |       39116 |             60.51 |
| ICICI Pru Midcap Fund - Regular - Growth              | ICICI Prudential MF      | Mid Cap         | High            |            18.08 |           0.95 |            1.45 |    0.89 |   1    |         19   |             -21.84 |         979 |             59.74 |
| ICICI Pru Bluechip Fund - Direct - Growth             | ICICI Prudential MF      | Large Cap       | Moderate        |            14.41 |           1.03 |            1.27 |    0.88 |   1.03 |         14   |             -26.59 |       41553 |             58.59 |
| Mirae Asset Emerging Bluechip Fund - Regular - Growth | Mirae Asset MF           | Large & Mid Cap | Moderately High |            14.56 |           0.91 |            1.55 |    1.7  |   0.99 |         16   |             -33.15 |       49046 |             56.67 |
| HDFC Top 100 Fund - Direct Plan - Growth              | HDFC Mutual Fund         | Large Cap       | Moderate        |            13.38 |           0.96 |            1.45 |    1.13 |   0.97 |         14   |             -33.5  |       10611 |             56.41 |
| Kotak Liquid Fund - Regular - Growth                  | Kotak Mahindra MF        | Liquid          | Low             |             6.18 |           6.18 |            9.7  |    1.52 |   0.47 |          0.5 |              -3.81 |       27623 |             55.26 |
| UTI Flexi Cap Fund - Regular - Growth                 | UTI Mutual Fund          | Flexi Cap       | Moderately High |            15.34 |           0.96 |            1.37 |    1.79 |   1    |         16   |             -12.14 |       17912 |             54.1  |
| Nippon India ETF Nifty 50 BeES                        | Nippon India MF          | Index/ETF       | Moderate        |            11.77 |           0.91 |            1.24 |    1.8  |   1.04 |         13   |             -26.75 |       20284 |             52.56 |
| Nippon India Large Cap Fund - Direct - Growth         | Nippon India MF          | Large Cap       | Moderate        |            12.33 |           0.88 |            1.48 |    1.7  |   1.02 |         14   |             -18.14 |       39475 |             50.9  |
| DSP Midcap Fund - Regular - Growth                    | DSP Mutual Fund          | Mid Cap         | High            |            17.16 |           0.9  |            1.5  |    1.02 |   0.98 |         19   |             -26.99 |       37835 |             50.38 |
| SBI Magnum Gilt Fund - Regular Plan - Growth          | SBI Mutual Fund          | Gilt            | Low             |             6.07 |           1.52 |            2.11 |    1.6  |   0.22 |          4   |              -2.3  |       24101 |             50    |
| DSP Top 100 Equity Fund - Regular - Growth            | DSP Mutual Fund          | Large Cap       | Moderate        |            12.82 |           0.92 |            1.63 |    1.82 |   0.91 |         14   |             -21.7  |       41828 |             49.74 |
| Axis Midcap Fund - Regular - Growth                   | Axis Mutual Fund         | Mid Cap         | High            |            15.18 |           0.8  |            1.18 |    1.42 |   1    |         19   |             -32.38 |       28996 |             49.49 |
| ICICI Pru Value Discovery Fund - Regular - Growth     | ICICI Prudential MF      | Value           | Moderately High |            14.76 |           0.98 |            1.5  |    0.55 |   0.92 |         15   |             -21.89 |        2571 |             49.23 |
| HDFC Top 100 Fund - Regular Plan - Growth             | HDFC Mutual Fund         | Large Cap       | Moderate        |            14.84 |           1.06 |            1.7  |    0.78 |   0.97 |         14   |             -17.41 |        6434 |             48.72 |
| HDFC Mid-Cap Opportunities Fund - Regular - Growth    | HDFC Mutual Fund         | Mid Cap         | High            |            16.58 |           0.87 |            1.44 |    0.95 |   0.91 |         19   |             -13.67 |       23185 |             47.44 |
| HDFC Mid-Cap Opportunities Fund - Direct - Growth     | HDFC Mutual Fund         | Mid Cap         | High            |            15.29 |           0.8  |            1.38 |    0.9  |   1.04 |         19   |             -32.22 |       18792 |             46.92 |
| ABSL Frontline Equity Fund - Regular - Growth         | Aditya Birla Sun Life MF | Large Cap       | Moderate        |            13.78 |           0.98 |            1.25 |    1.34 |   1.03 |         14   |             -15.07 |       23500 |             46.41 |
| Nippon India Large Cap Fund - Regular - Growth        | Nippon India MF          | Large Cap       | Moderate        |            14    |           1    |            1.68 |    0.86 |   0.88 |         14   |             -16.07 |       20909 |             46.28 |
| Nippon India Small Cap Fund - Regular - Growth        | Nippon India MF          | Small Cap       | Very High       |            20.15 |           0.81 |            1.14 |    0.8  |   1.03 |         25   |             -30.87 |       43630 |             45.77 |
| ABSL Liquid Fund - Regular - Growth                   | Aditya Birla Sun Life MF | Liquid          | Low             |             5.14 |           5.14 |            8.76 |    1.18 |   0.43 |          0.5 |              -3.66 |       38995 |             45.38 |
| SBI Bluechip Fund - Direct Plan - Growth              | SBI Mutual Fund          | Large Cap       | Moderate        |            11.3  |           0.81 |            1.29 |    1.78 |   0.87 |         14   |             -24.43 |        1231 |             44.1  |
| Axis Bluechip Fund - Direct - Growth                  | Axis Mutual Fund         | Large Cap       | Moderate        |            12.14 |           0.87 |            1.54 |    1.43 |   0.87 |         14   |             -17.4  |       15866 |             43.85 |
| Axis Small Cap Fund - Regular - Growth                | Axis Mutual Fund         | Small Cap       | Very High       |            20.98 |           0.84 |            1.4  |    0.51 |   1    |         25   |             -14.45 |       21545 |             43.85 |
| Nippon India Gilt Securities Fund - Regular - Growth  | Nippon India MF          | Gilt            | Low             |             5.31 |           1.33 |            2.38 |    0.89 |   0.37 |          4   |              -2.23 |       30030 |             42.69 |
| UTI Mid Cap Fund - Regular - Growth                   | UTI Mutual Fund          | Mid Cap         | High            |            15.61 |           0.82 |            1.21 |    1.12 |   0.92 |         19   |             -13.43 |       41728 |             41.41 |
| DSP Small Cap Fund - Regular - Growth                 | DSP Mutual Fund          | Small Cap       | Very High       |            20.08 |           0.8  |            1.23 |    0.69 |   0.98 |         25   |             -17.01 |       35124 |             36.54 |
| UTI Nifty 50 Index Fund - Regular - Growth            | UTI Mutual Fund          | Index           | Moderate        |            12.1  |           0.93 |            1.29 |    0.93 |   0.9  |         13   |             -24.42 |        7350 |             36.41 |
| Axis Bluechip Fund - Regular - Growth                 | Axis Mutual Fund         | Large Cap       | Moderate        |            11.84 |           0.85 |            1.25 |    1.41 |   0.91 |         14   |             -27.54 |       25803 |             33.21 |
| Kotak Bluechip Fund - Regular - Growth                | Kotak Mahindra MF        | Large Cap       | Moderate        |            12.25 |           0.87 |            1.34 |    1.27 |   0.93 |         14   |             -17.86 |       35585 |             32.69 |
| SBI Bluechip Fund - Regular Plan - Growth             | SBI Mutual Fund          | Large Cap       | Moderate        |            12.36 |           0.88 |            1.29 |    0.87 |   0.89 |         14   |             -21.7  |       14288 |             31.79 |
| ICICI Pru Bluechip Fund - Regular - Growth            | ICICI Prudential MF      | Large Cap       | Moderate        |            11.54 |           0.82 |            1.12 |    0.66 |   0.96 |         14   |             -25.91 |       36022 |             26.15 |
| Mirae Asset Tax Saver Fund - Regular - Growth         | Mirae Asset MF           | ELSS            | High            |            13.58 |           0.8  |            1.03 |    0.54 |   0.98 |         17   |             -22.62 |        2989 |             21.15 |

## Category Inflow Trends (Monthly Pivot)

### Query
```sql
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
```

### Result
| category          |   Apr-24 |   Jul-24 |   Oct-24 |   Jan-25 |   total_inflow |
|:------------------|---------:|---------:|---------:|---------:|---------------:|
| Liquid            |    37537 |    34643 |    39091 |    33892 |         451275 |
| Sectoral/Thematic |     8052 |     9896 |     7680 |     7893 |         103829 |
| Flexi Cap         |     4947 |     4869 |     6004 |     5603 |          63989 |
| Large & Mid Cap   |     4214 |     5023 |     4581 |     4816 |          57752 |
| Short Duration    |     4400 |     4170 |     4675 |     4752 |          55530 |
| Mid Cap           |     3897 |     4548 |     4106 |     4316 |          55312 |
| Small Cap         |     3533 |     3582 |     4444 |     4554 |          46596 |
| Hybrid            |     2955 |     3291 |     3314 |     2967 |          38868 |
| Large Cap         |     2413 |     2574 |     2255 |     2025 |          25633 |
| Value/Contra      |     1328 |     1582 |     1595 |     1339 |          16980 |
| Gilt              |      784 |      959 |      898 |      744 |          10395 |
| ELSS              |      466 |      471 |      537 |      516 |           6080 |

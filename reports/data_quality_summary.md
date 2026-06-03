# Data Quality Summary

Generated: 2026-06-03T23:37:51

## Fund Master Exploration

- Fund houses: Aditya Birla Sun Life MF, Axis Mutual Fund, DSP Mutual Fund, HDFC Mutual Fund, ICICI Prudential MF, Kotak Mahindra MF, Mirae Asset MF, Nippon India MF, SBI Mutual Fund, UTI Mutual Fund
- Categories: Debt, Equity
- Sub-categories: ELSS, Flexi Cap, Gilt, Index, Index/ETF, Large & Mid Cap, Large Cap, Liquid, Mid Cap, Short Duration, Small Cap, Value
- Risk categories: High, Low, Moderate, Moderately High, Very High
- Risk grades: High, Low, Moderate, Moderately High, Very High

## AMFI Scheme Code Structure

AMFI codes are numeric scheme identifiers. In this project they are stored as integers and used as the stable key between fund master, NAV history, performance, transactions, and portfolio holdings. Regular and Direct plans usually have distinct AMFI codes even when they belong to the same strategy family.

## AMFI Code Validation

- `fund_master` distinct AMFI codes: 40
- `nav_history` distinct AMFI codes: 40
- Codes in `fund_master` missing from `nav_history`: 0
- Codes in `nav_history` not present in `fund_master`: 0
- Validation result: PASS - every fund_master code exists in nav_history.

## Cleaning Checks

- NAV rows with invalid dates: 0
- NAV rows with non-positive NAV: 0
- NAV duplicate `amfi_code` + `date` rows: 0
- Transaction rows with non-positive amount: 0
- Transaction type values: Lumpsum, Redemption, SIP
- KYC status values: Pending, Verified
- Performance expense ratios outside 0.1%-2.5%: 0

The ETL pipeline parses dates, removes invalid NAV/transaction records, de-duplicates NAV by `amfi_code` + `date`, forward-fills daily NAV gaps, standardizes transaction types, validates positive amounts, coerces performance metrics to numeric values, and loads the cleaned outputs into SQLite.
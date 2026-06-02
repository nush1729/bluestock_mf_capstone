-- ============================================================
-- Bluestock Mutual Fund Analytics — SQLite Star Schema
-- Generated for: bluestock_mf.db
-- ============================================================

-- ============================================================
-- DIMENSION TABLES
-- ============================================================

-- Dimension: Fund Master (central dimension)
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code        INTEGER PRIMARY KEY,
    fund_house       TEXT NOT NULL,
    scheme_name      TEXT NOT NULL,
    category         TEXT NOT NULL,       -- Equity / Debt
    sub_category     TEXT NOT NULL,       -- Large Cap, Mid Cap, Small Cap, etc.
    plan             TEXT NOT NULL,       -- Regular / Direct
    launch_date      DATE,
    benchmark        TEXT,
    expense_ratio_pct REAL,
    exit_load_pct    REAL,
    min_sip_amount   INTEGER,
    min_lumpsum_amount INTEGER,
    fund_manager     TEXT,
    risk_category    TEXT,                -- Low / Moderate / High / Very High
    sebi_category_code TEXT
);

-- Dimension: Date (generated date dimension)
CREATE TABLE IF NOT EXISTS dim_date (
    date_id          TEXT PRIMARY KEY,     -- YYYY-MM-DD
    date             DATE NOT NULL,
    year             INTEGER NOT NULL,
    month            INTEGER NOT NULL,
    quarter          INTEGER NOT NULL,
    day_of_week      INTEGER NOT NULL,     -- 0=Monday, 6=Sunday
    day_name         TEXT NOT NULL,
    month_name       TEXT NOT NULL,
    is_weekday       INTEGER NOT NULL,     -- 1=weekday, 0=weekend
    year_month       TEXT NOT NULL          -- YYYY-MM
);

CREATE INDEX IF NOT EXISTS idx_dim_date_year ON dim_date(year);
CREATE INDEX IF NOT EXISTS idx_dim_date_year_month ON dim_date(year_month);

-- ============================================================
-- FACT TABLES
-- ============================================================

-- Fact: Daily NAV History
CREATE TABLE IF NOT EXISTS fact_nav (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code        INTEGER NOT NULL,
    date             TEXT NOT NULL,
    nav              REAL NOT NULL,
    daily_return_pct REAL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    UNIQUE(amfi_code, date)
);

CREATE INDEX IF NOT EXISTS idx_fact_nav_amfi ON fact_nav(amfi_code);
CREATE INDEX IF NOT EXISTS idx_fact_nav_date ON fact_nav(date);
CREATE INDEX IF NOT EXISTS idx_fact_nav_amfi_date ON fact_nav(amfi_code, date);

-- Fact: Investor Transactions
CREATE TABLE IF NOT EXISTS fact_transactions (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id        TEXT NOT NULL,
    transaction_date   TEXT NOT NULL,
    amfi_code          INTEGER NOT NULL,
    transaction_type   TEXT NOT NULL,       -- SIP / Lumpsum / Redemption
    amount_inr         INTEGER NOT NULL,
    state              TEXT,
    city               TEXT,
    city_tier          TEXT,                -- T30 / B30
    age_group          TEXT,
    gender             TEXT,
    annual_income_lakh REAL,
    payment_mode       TEXT,
    kyc_status         TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE INDEX IF NOT EXISTS idx_fact_tx_amfi ON fact_transactions(amfi_code);
CREATE INDEX IF NOT EXISTS idx_fact_tx_investor ON fact_transactions(investor_id);
CREATE INDEX IF NOT EXISTS idx_fact_tx_date ON fact_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_fact_tx_type ON fact_transactions(transaction_type);

-- Fact: Scheme Performance Metrics
CREATE TABLE IF NOT EXISTS fact_performance (
    amfi_code          INTEGER PRIMARY KEY,
    scheme_name        TEXT NOT NULL,
    fund_house         TEXT NOT NULL,
    category           TEXT,
    plan               TEXT,
    return_1yr_pct     REAL,
    return_3yr_pct     REAL,
    return_5yr_pct     REAL,
    benchmark_3yr_pct  REAL,
    alpha              REAL,
    beta               REAL,
    sharpe_ratio       REAL,
    sortino_ratio      REAL,
    std_dev_ann_pct    REAL,
    max_drawdown_pct   REAL,
    aum_crore          INTEGER,
    expense_ratio_pct  REAL,
    morningstar_rating INTEGER,
    risk_grade         TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- Fact: Portfolio Holdings
CREATE TABLE IF NOT EXISTS fact_portfolio (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code         INTEGER NOT NULL,
    stock_symbol      TEXT NOT NULL,
    stock_name        TEXT NOT NULL,
    sector            TEXT,
    weight_pct        REAL,
    market_value_cr   REAL,
    current_price_inr REAL,
    portfolio_date    TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE INDEX IF NOT EXISTS idx_fact_portfolio_amfi ON fact_portfolio(amfi_code);
CREATE INDEX IF NOT EXISTS idx_fact_portfolio_sector ON fact_portfolio(sector);

-- Fact: AUM by Fund House (Quarterly)
CREATE TABLE IF NOT EXISTS fact_aum (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT NOT NULL,
    fund_house      TEXT NOT NULL,
    aum_lakh_crore  REAL,
    aum_crore       INTEGER,
    num_schemes     INTEGER,
    UNIQUE(date, fund_house)
);

CREATE INDEX IF NOT EXISTS idx_fact_aum_fh ON fact_aum(fund_house);
CREATE INDEX IF NOT EXISTS idx_fact_aum_date ON fact_aum(date);

-- Fact: Monthly SIP Inflows (Industry Level)
CREATE TABLE IF NOT EXISTS fact_sip_industry (
    month                     TEXT PRIMARY KEY,
    sip_inflow_crore          INTEGER,
    active_sip_accounts_crore REAL,
    new_sip_accounts_lakh     REAL,
    sip_aum_lakh_crore        REAL,
    yoy_growth_pct            REAL
);

-- Fact: Category-wise Inflows
CREATE TABLE IF NOT EXISTS fact_category_inflows (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    month            TEXT NOT NULL,
    category         TEXT NOT NULL,
    net_inflow_crore REAL,
    UNIQUE(month, category)
);

CREATE INDEX IF NOT EXISTS idx_fact_cat_month ON fact_category_inflows(month);
CREATE INDEX IF NOT EXISTS idx_fact_cat_category ON fact_category_inflows(category);

-- Fact: Industry Folio Count
CREATE TABLE IF NOT EXISTS fact_folio_count (
    month                TEXT PRIMARY KEY,
    total_folios_crore   REAL,
    equity_folios_crore  REAL,
    debt_folios_crore    REAL,
    hybrid_folios_crore  REAL,
    others_folios_crore  REAL
);

-- Fact: Benchmark Indices
CREATE TABLE IF NOT EXISTS fact_benchmark (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date        TEXT NOT NULL,
    index_name  TEXT NOT NULL,
    close_value REAL NOT NULL,
    UNIQUE(date, index_name)
);

CREATE INDEX IF NOT EXISTS idx_fact_bench_date ON fact_benchmark(date);
CREATE INDEX IF NOT EXISTS idx_fact_bench_name ON fact_benchmark(index_name);

-- ============================================================
-- VIEWS (for common analytical queries)
-- ============================================================

-- View: Fund with latest NAV
CREATE VIEW IF NOT EXISTS vw_fund_latest_nav AS
SELECT
    f.amfi_code,
    f.scheme_name,
    f.fund_house,
    f.category,
    f.sub_category,
    f.risk_category,
    n.nav AS latest_nav,
    n.date AS nav_date
FROM dim_fund f
JOIN fact_nav n ON f.amfi_code = n.amfi_code
WHERE n.date = (SELECT MAX(date) FROM fact_nav WHERE amfi_code = f.amfi_code);

-- View: Fund performance with metadata
CREATE VIEW IF NOT EXISTS vw_fund_performance_full AS
SELECT
    f.amfi_code,
    f.scheme_name,
    f.fund_house,
    f.category,
    f.sub_category,
    f.plan,
    f.risk_category,
    f.expense_ratio_pct AS fund_expense_ratio,
    p.return_1yr_pct,
    p.return_3yr_pct,
    p.return_5yr_pct,
    p.alpha,
    p.beta,
    p.sharpe_ratio,
    p.sortino_ratio,
    p.std_dev_ann_pct,
    p.max_drawdown_pct,
    p.aum_crore,
    p.morningstar_rating,
    p.risk_grade
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code;

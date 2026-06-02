#!/usr/bin/env python3
"""
Bluestock Mutual Fund Analytics — Performance & Risk Metrics
============================================================
Calculates risk and return metrics from NAV history and benchmarks.
Outputs metrics to `outputs/performance_metrics.csv`

Usage:
    python scripts/compute_metrics.py
"""

import logging
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import sqlite3
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "db" / "bluestock_mf.db"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RISK_FREE_RATE = 0.065  # 6.5% as per requirements (RBI repo rate proxy)
TRADING_DAYS = 252

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
logger = logging.getLogger("MetricsEngine")

# ---------------------------------------------------------------------------
# Core Calculation Engine
# ---------------------------------------------------------------------------
def compute_metrics():
    logger.info("Starting Performance & Risk Metrics computation...")
    
    if not DB_PATH.exists():
        logger.error(f"Database not found at {DB_PATH}. Run ETL pipeline first.")
        sys.exit(1)
        
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Load Data
    logger.info("Loading NAV and Benchmark data from database...")
    nav_df = pd.read_sql("SELECT amfi_code, date, nav, daily_return_pct FROM fact_nav ORDER BY amfi_code, date", conn)
    nav_df['date'] = pd.to_datetime(nav_df['date'])
    
    bench_df = pd.read_sql("SELECT date, index_name, close_value FROM fact_benchmark ORDER BY index_name, date", conn)
    bench_df['date'] = pd.to_datetime(bench_df['date'])
    bench_df['daily_return_pct'] = bench_df.groupby('index_name')['close_value'].pct_change() * 100
    
    fund_master = pd.read_sql("SELECT amfi_code, scheme_name, sub_category, benchmark, risk_category FROM dim_fund", conn)
    
    # Benchmark mapping as defined in ETL
    benchmark_map = {
        "NIFTY 50 TRI": "NIFTY50",
        "NIFTY 100 TRI": "NIFTY100",
        "NIFTY 500 TRI": "NIFTY500",
        "NIFTY Midcap 150 TRI": "NIFTY_MIDCAP150",
        "NIFTY Midcap 50 TRI": "NIFTY_MIDCAP150",
        "NIFTY Large Midcap 250 TRI": "NIFTY500",
        "BSE 250 SmallCap TRI": "BSE_SMALLCAP",
        "CRISIL Liquid Fund AI Index": "CRISIL_LIQUID",
        "CRISIL Short Term Bond Index": "CRISIL_LIQUID",
        "CRISIL Dynamic Gilt Index": "CRISIL_GILT",
    }
    
    results = []
    
    logger.info("Computing metrics for all funds...")
    for idx, fund in fund_master.iterrows():
        amfi_code = fund['amfi_code']
        bench_name = benchmark_map.get(fund['benchmark'], "NIFTY50")
        
        fund_nav = nav_df[nav_df['amfi_code'] == amfi_code].set_index('date')
        if fund_nav.empty:
            continue
            
        b_idx = bench_df[bench_df['index_name'] == bench_name].set_index('date')
        
        # Align dates
        aligned = pd.merge(fund_nav[['nav', 'daily_return_pct']], 
                           b_idx[['close_value', 'daily_return_pct']], 
                           left_index=True, right_index=True, suffixes=('_fund', '_bench'))
        aligned = aligned.dropna()
        
        if len(aligned) < 252:
            logger.warning(f"Fund {amfi_code} has less than 1 year of data. Skipping some metrics.")
            
        latest_date = aligned.index.max()
        
        # Dates for returns
        date_1yr = latest_date - pd.DateOffset(years=1)
        date_3yr = latest_date - pd.DateOffset(years=3)
        date_5yr = latest_date - pd.DateOffset(years=5)
        
        def get_nav_at_date(d):
            # Find closest date on or before
            subset = aligned[aligned.index <= d]
            if len(subset) == 0: return None
            return subset.iloc[-1]
            
        curr_row = get_nav_at_date(latest_date)
        row_1y = get_nav_at_date(date_1yr)
        row_3y = get_nav_at_date(date_3yr)
        row_5y = get_nav_at_date(date_5yr)
        
        # --- RETURN METRICS ---
        metrics = {
            'amfi_code': amfi_code,
            'scheme_name': fund['scheme_name'],
            'category': fund['sub_category'],
            'benchmark': fund['benchmark']
        }
        
        # 1-Year Absolute Return
        if row_1y is not None:
            metrics['return_1yr_pct'] = (curr_row['nav'] / row_1y['nav'] - 1) * 100
        else:
            metrics['return_1yr_pct'] = np.nan
            
        # 3-Year CAGR
        if row_3y is not None:
            trading_days_3y = len(aligned[aligned.index > row_3y.name])
            if trading_days_3y > 0:
                metrics['return_3yr_pct'] = ((curr_row['nav'] / row_3y['nav']) ** (TRADING_DAYS / trading_days_3y) - 1) * 100
                metrics['benchmark_3yr_pct'] = ((curr_row['close_value'] / row_3y['close_value']) ** (TRADING_DAYS / trading_days_3y) - 1) * 100
        else:
            metrics['return_3yr_pct'] = np.nan
            metrics['benchmark_3yr_pct'] = np.nan
            
        # 5-Year CAGR (we may not have 5y data, handled safely)
        if row_5y is not None and row_5y.name < date_3yr:
            trading_days_5y = len(aligned[aligned.index > row_5y.name])
            if trading_days_5y > 0:
                metrics['return_5yr_pct'] = ((curr_row['nav'] / row_5y['nav']) ** (TRADING_DAYS / trading_days_5y) - 1) * 100
        else:
            metrics['return_5yr_pct'] = np.nan
            
        # --- RISK METRICS ---
        # Convert daily return % to decimal for risk calcs
        r_fund = aligned['daily_return_pct_fund'] / 100
        r_bench = aligned['daily_return_pct_bench'] / 100
        
        # Volatility (Annualized Standard Deviation)
        volatility = r_fund.std() * np.sqrt(TRADING_DAYS)
        metrics['std_dev_ann_pct'] = volatility * 100
        
        # Sharpe Ratio: (Annual Return - Risk Free Rate) / Annual Volatility
        # We'll use the mean daily return annualized for the Sharpe return component
        ann_return = r_fund.mean() * TRADING_DAYS
        if volatility > 0:
            metrics['sharpe_ratio'] = (ann_return - RISK_FREE_RATE) / volatility
        else:
            metrics['sharpe_ratio'] = np.nan
            
        # Sortino Ratio
        downside_returns = r_fund[r_fund < 0]
        downside_volatility = downside_returns.std() * np.sqrt(TRADING_DAYS)
        if downside_volatility > 0:
            metrics['sortino_ratio'] = (ann_return - RISK_FREE_RATE) / downside_volatility
        else:
            metrics['sortino_ratio'] = np.nan
            
        # Alpha and Beta (using scipy.stats.linregress)
        # OLS regression: R_fund = Alpha + Beta * R_bench
        try:
            slope, intercept, r_value, p_value, std_err = stats.linregress(r_bench, r_fund)
            metrics['beta'] = slope
            metrics['alpha'] = intercept * TRADING_DAYS * 100  # Annualized Alpha in %
            metrics['r_squared'] = r_value ** 2
        except Exception:
            metrics['beta'] = np.nan
            metrics['alpha'] = np.nan
            metrics['r_squared'] = np.nan
            
        # Maximum Drawdown
        running_max = aligned['nav'].cummax()
        drawdown = (aligned['nav'] - running_max) / running_max
        metrics['max_drawdown_pct'] = drawdown.min() * 100
        
        # Value at Risk (VaR) 95% Historical
        metrics['var_95_pct'] = np.percentile(r_fund, 5) * 100
        
        # Conditional Value at Risk (CVaR) 95%
        cvar_returns = r_fund[r_fund <= np.percentile(r_fund, 5)]
        metrics['cvar_95_pct'] = cvar_returns.mean() * 100 if len(cvar_returns) > 0 else np.nan
        
        results.append(metrics)
        
    # Combine results
    metrics_df = pd.DataFrame(results)
    
    # Save to CSV
    output_path = OUTPUT_DIR / "performance_metrics.csv"
    metrics_df.to_csv(output_path, index=False)
    logger.info(f"Successfully computed metrics for {len(metrics_df)} funds.")
    logger.info(f"Saved to {output_path}")
    
    conn.close()

if __name__ == "__main__":
    compute_metrics()

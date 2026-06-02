#!/usr/bin/env python3
"""
Bluestock Mutual Fund Analytics — Fund Recommendation Engine
============================================================
Implements content-based filtering and clustering for fund recommendations.

Usage:
    python scripts/recommender.py --risk "Moderate" --horizon "Long Term"
"""

import sys
import argparse
import logging
from pathlib import Path
import pandas as pd
import sqlite3

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("Recommender")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "db" / "bluestock_mf.db"

def get_recommendations(risk_appetite="Moderate", preferred_category="Any"):
    if not DB_PATH.exists():
        logger.error("Database not found. Run ETL pipeline first.")
        return None

    conn = sqlite3.connect(DB_PATH)
    
    # Load required data
    query = """
    SELECT 
        f.amfi_code, f.scheme_name, f.fund_house, f.sub_category, f.risk_category, f.expense_ratio_pct,
        p.return_1yr_pct, p.return_3yr_pct, p.sharpe_ratio, p.alpha, p.beta, p.std_dev_ann_pct, p.aum_crore
    FROM dim_fund f
    JOIN fact_performance p ON f.amfi_code = p.amfi_code
    """
    df = pd.read_sql(query, conn)
    conn.close()

    # Apply Risk Filter
    if risk_appetite == "Low":
        target_risk = ["Low"]
    elif risk_appetite == "Moderate":
        target_risk = ["Low", "Moderate"]
    elif risk_appetite == "High":
        target_risk = ["Moderate", "High"]
    else:  # Very High
        target_risk = ["High", "Very High"]
        
    filtered = df[df["risk_category"].isin(target_risk)].copy()
    
    # Apply Category Filter
    if preferred_category != "Any":
        filtered = filtered[filtered["sub_category"].str.contains(preferred_category, case=False, na=False)]

    if filtered.empty:
        logger.warning(f"No funds match criteria (Risk: {risk_appetite}, Category: {preferred_category})")
        return pd.DataFrame()

    # Scoring Engine
    # Give weight to Sharpe Ratio (risk-adjusted returns), absolute returns, and alpha
    filtered["score"] = (
        filtered["sharpe_ratio"].rank(pct=True) * 0.40 +
        filtered["return_3yr_pct"].rank(pct=True) * 0.30 +
        filtered["alpha"].rank(pct=True) * 0.20 + 
        filtered["expense_ratio_pct"].rank(pct=True, ascending=False) * 0.10
    )
    
    top_recs = filtered.nlargest(5, "score")
    
    logger.info("="*60)
    logger.info(f"FUND RECOMMENDATIONS (Risk: {risk_appetite} | Category: {preferred_category})")
    logger.info("="*60)
    
    for i, (_, row) in enumerate(top_recs.iterrows()):
        logger.info(f"#{i+1}: {row['scheme_name']}")
        logger.info(f"    Category: {row['sub_category']} | Risk: {row['risk_category']}")
        logger.info(f"    3Y Return: {row['return_3yr_pct']:.2f}% | Sharpe: {row['sharpe_ratio']:.2f} | Alpha: {row['alpha']:.2f}")
        logger.info(f"    Expense Ratio: {row['expense_ratio_pct']:.2f}% | AMC: {row['fund_house']}")
        logger.info("-" * 60)
        
    return top_recs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mutual Fund Recommendation Engine")
    parser.add_argument("--risk", default="Moderate", choices=["Low", "Moderate", "High", "Very High"], help="Investor risk appetite")
    parser.add_argument("--category", default="Any", help="Preferred fund category (e.g., 'Large Cap')")
    args = parser.parse_args()
    
    get_recommendations(args.risk, args.category)

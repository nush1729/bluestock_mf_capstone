#!/usr/bin/env python3
"""
Bluestock Mutual Fund Analytics — Fund Recommendation Engine (Day 6, Task 5)
=============================================================================
Input:  Investor risk appetite (Low / Moderate / High)
Output: Top 3 funds by Sharpe ratio within matching risk_grade + composite score

Usage:
    python scripts/recommender.py --risk Low
    python scripts/recommender.py --risk Moderate
    python scripts/recommender.py --risk High
"""

import sys
import argparse
import logging
from pathlib import Path
import pandas as pd
import sqlite3

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("Recommender")

PROJECT_ROOT  = Path(__file__).resolve().parent.parent
DB_PATH       = PROJECT_ROOT / "data" / "db" / "bluestock_mf.db"
SCORECARD_CSV = PROJECT_ROOT / "outputs" / "fund_scorecard.csv"
SHARPE_CSV    = PROJECT_ROOT / "outputs" / "sharpe_values.csv"

# Risk appetite → allowed risk grades in dim_fund
RISK_MAP = {
    "Low":       ["Low", "Moderately Low"],
    "Moderate":  ["Moderate", "Moderately Low"],
    "High":      ["Moderate", "Moderately High", "High", "Very High"],
}

# Category hints per risk level (for subtitle)
CAT_HINT = {
    "Low":      "Liquid / Short Duration / Gilt",
    "Moderate": "Large Cap / Flexi Cap / ELSS",
    "High":     "Mid Cap / Small Cap / Thematic",
}


def get_recommendations(risk_appetite: str = "Moderate") -> pd.DataFrame:
    if risk_appetite not in RISK_MAP:
        log.error(f"Invalid risk. Choose from: {list(RISK_MAP.keys())}")
        return pd.DataFrame()

    if not DB_PATH.exists():
        log.error("Database not found. Run `python scripts/etl_pipeline.py` first.")
        return pd.DataFrame()

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("""
        SELECT f.amfi_code, f.scheme_name, f.fund_house, f.sub_category,
               f.risk_category, f.expense_ratio_pct, f.plan,
               p.return_1yr_pct, p.return_3yr_pct, p.sharpe_ratio,
               p.alpha, p.beta, p.std_dev_ann_pct, p.max_drawdown_pct, p.aum_crore
        FROM dim_fund f
        JOIN fact_performance p ON f.amfi_code = p.amfi_code
    """, conn)
    conn.close()

    # Filter by risk grade
    allowed = RISK_MAP[risk_appetite]
    filtered = df[df["risk_category"].isin(allowed)].copy()

    if filtered.empty:
        log.warning(f"No funds found for risk appetite: {risk_appetite}")
        return pd.DataFrame()

    # Score: weighted by Sharpe (primary Day 6 criterion), then return and alpha
    filtered = filtered.dropna(subset=["sharpe_ratio"])
    filtered["rec_score"] = (
        filtered["sharpe_ratio"].rank(pct=True) * 0.50 +
        filtered["return_3yr_pct"].fillna(0).rank(pct=True) * 0.30 +
        filtered["alpha"].fillna(0).rank(pct=True) * 0.20
    )

    # Top 3
    top3 = filtered.nlargest(3, "rec_score").reset_index(drop=True)

    # ── Print recommendation table ──
    log.info("=" * 65)
    log.info(f" BLUESTOCK FUND RECOMMENDATION ENGINE")
    log.info(f" Investor Risk Profile : {risk_appetite}")
    log.info(f" Suggested Categories  : {CAT_HINT.get(risk_appetite, 'Any')}")
    log.info("=" * 65)
    log.info(f"{'Rank':<5} {'Fund Name':<35} {'Cat':<12} {'Sharpe':>7} {'3yr%':>7} {'Exp%':>5}")
    log.info("-" * 65)
    for i, row in top3.iterrows():
        short = row["scheme_name"].split(" - ")[0][:33]
        cat   = row["sub_category"][:11]
        log.info(f"  #{i+1}  {short:<35} {cat:<12} {row['sharpe_ratio']:>7.2f} "
                 f"{row['return_3yr_pct']:>7.1f}% {row['expense_ratio_pct']:>5.2f}%")
    log.info("-" * 65)

    for i, row in top3.iterrows():
        log.info(f"\n{'='*3} Rank #{i+1}: {row['scheme_name']}")
        log.info(f"   Fund House     : {row['fund_house']}")
        log.info(f"   Category       : {row['sub_category']}  | Plan: {row['plan']}")
        log.info(f"   Risk Grade     : {row['risk_category']}")
        log.info(f"   Sharpe Ratio   : {row['sharpe_ratio']:.4f}")
        log.info(f"   3yr CAGR       : {row['return_3yr_pct']:.2f}%")
        log.info(f"   1yr Return     : {row['return_1yr_pct']:.2f}%")
        log.info(f"   Alpha          : {row['alpha']:.2f}")
        log.info(f"   Expense Ratio  : {row['expense_ratio_pct']:.2f}%")
        log.info(f"   Max Drawdown   : {row['max_drawdown_pct']:.2f}%")
        log.info(f"   AUM (₹ Cr)    : {row['aum_crore']:,.0f}")

    log.info("=" * 65)
    return top3[["scheme_name", "sub_category", "risk_category", "sharpe_ratio",
                 "return_3yr_pct", "alpha", "expense_ratio_pct", "max_drawdown_pct"]]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Bluestock Mutual Fund Recommendation Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  python scripts/recommender.py --risk Low
  python scripts/recommender.py --risk Moderate
  python scripts/recommender.py --risk High
        """
    )
    parser.add_argument("--risk", default="Moderate",
                        choices=["Low", "Moderate", "High"],
                        help="Investor risk appetite (default: Moderate)")
    args = parser.parse_args()
    result = get_recommendations(args.risk)

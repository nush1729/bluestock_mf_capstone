#!/usr/bin/env python3
"""
Bluestock Mutual Fund Analytics — Master Pipeline Runner
=========================================================
Runs the complete end-to-end analytics pipeline in the correct order:

  Step 1: ETL — Extract, Clean, Load all 10 datasets → SQLite
  Step 2: Live NAV Fetch — Update NAV for 5 selected schemes via AMFI API
  Step 3: Day 4 — Compute performance metrics (CAGR, Sharpe, Alpha, Scorecard)
  Step 4: Day 5 — Generate dashboard page PNGs and Dashboard.pdf
  Step 5: Day 6 — Advanced analytics (VaR, Rolling Sharpe, Cohort, HHI)
  Step 6: Day 7 — Build Final_Report.pdf and Bluestock_MF_Presentation.pptx

Usage:
    python run_pipeline.py                  # full run
    python run_pipeline.py --skip-live      # skip live NAV fetch (offline mode)
    python run_pipeline.py --only etl       # run only a specific step
    python run_pipeline.py --from metrics   # resume from a specific step
"""

import sys
import time
import argparse
import subprocess
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(PROJECT_ROOT / "pipeline.log", mode="w"),
    ]
)
log = logging.getLogger("Pipeline")

STEPS = {
    "etl": {
        "label": "ETL Pipeline (Extract → Clean → Load)",
        "script": "scripts/etl_pipeline.py",
        "expected_outputs": ["data/db/bluestock_mf.db", "data/processed/clean_nav.csv"],
    },
    "live": {
        "label": "Live NAV Fetch (AMFI API)",
        "script": "scripts/live_nav_fetch.py",
        "expected_outputs": [],  # appends to existing
    },
    "metrics": {
        "label": "Day 4: Performance Metrics & Scorecard",
        "script": "scripts/day4_performance.py",
        "expected_outputs": [
            "outputs/returns_computed.csv",
            "outputs/cagr_report.csv",
            "outputs/sharpe_values.csv",
            "outputs/sortino_values.csv",
            "outputs/alpha_beta.csv",
            "outputs/max_drawdown.csv",
            "outputs/fund_scorecard.csv",
            "outputs/benchmark_chart.png",
        ],
    },
    "dashboard": {
        "label": "Day 5: Dashboard Export (4 PNGs + PDF)",
        "script": "scripts/day5_dashboard_export.py",
        "expected_outputs": [
            "dashboard/page1_industry_overview.png",
            "dashboard/page2_fund_performance.png",
            "dashboard/page3_investor_analytics.png",
            "dashboard/page4_sip_trends.png",
            "dashboard/Dashboard.pdf",
        ],
    },
    "advanced": {
        "label": "Day 6: Advanced Analytics (VaR, Cohort, HHI)",
        "script": "scripts/day6_advanced.py",
        "expected_outputs": [
            "outputs/var_cvar_report.csv",
            "outputs/rolling_sharpe_chart.png",
            "outputs/cohort_analysis.csv",
            "outputs/sip_continuity.csv",
            "outputs/sector_hhi.csv",
        ],
    },
    "report": {
        "label": "Day 7: Final Report PDF + 12-Slide Presentation",
        "script": "scripts/day7_report_presentation.py",
        "expected_outputs": [
            "reports/Final_Report.pdf",
            "reports/Bluestock_MF_Presentation.pptx",
        ],
    },
}

STEP_ORDER = ["etl", "live", "metrics", "dashboard", "advanced", "report"]


def run_step(step_key: str, skip_live: bool = False) -> bool:
    """Run a single pipeline step. Returns True on success."""
    step = STEPS[step_key]
    if step_key == "live" and skip_live:
        log.info(f"  [SKIP] {step['label']} (--skip-live)")
        return True

    script = PROJECT_ROOT / step["script"]
    if not script.exists():
        log.warning(f"  [WARN] Script not found: {script} — skipping")
        return True

    log.info(f"  ▶ Running: {step['label']}")
    t0 = time.time()
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=False,
        cwd=str(PROJECT_ROOT),
    )
    elapsed = time.time() - t0

    if result.returncode != 0:
        log.error(f"  ✗ FAILED in {elapsed:.1f}s — returncode={result.returncode}")
        return False

    # Verify expected outputs exist
    missing = [o for o in step["expected_outputs"] if not (PROJECT_ROOT / o).exists()]
    if missing:
        log.warning(f"  ⚠ Step completed but missing outputs: {missing}")
    else:
        log.info(f"  ✓ Completed in {elapsed:.1f}s")

    return True


def check_prerequisites():
    """Check that required packages and data are available."""
    missing_pkgs = []
    try: import pandas
    except ImportError: missing_pkgs.append("pandas")
    try: import matplotlib
    except ImportError: missing_pkgs.append("matplotlib")
    try: import seaborn
    except ImportError: missing_pkgs.append("seaborn")
    try: import scipy
    except ImportError: missing_pkgs.append("scipy")
    try: import reportlab
    except ImportError: missing_pkgs.append("reportlab")
    try: import pptx
    except ImportError: missing_pkgs.append("python-pptx")

    if missing_pkgs:
        log.error(f"Missing packages: {missing_pkgs}")
        log.error("Run: pip3 install -r requirements.txt")
        return False

    raw_dir = PROJECT_ROOT / "data" / "raw"
    if not raw_dir.exists() or not list(raw_dir.glob("*.csv")):
        log.error("data/raw/ is empty — please add the 10 CSV datasets first")
        return False

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Bluestock MF Analytics — Master Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--skip-live", action="store_true",
                        help="Skip live NAV fetch (use for offline/CI runs)")
    parser.add_argument("--only", choices=list(STEPS.keys()),
                        help="Run only a single step")
    parser.add_argument("--from", dest="from_step", choices=list(STEPS.keys()),
                        help="Resume from a specific step (skips earlier steps)")
    args = parser.parse_args()

    log.info("=" * 65)
    log.info("  BLUESTOCK MUTUAL FUND ANALYTICS — MASTER PIPELINE")
    log.info("=" * 65)

    if not check_prerequisites():
        sys.exit(1)

    # Determine which steps to run
    if args.only:
        steps_to_run = [args.only]
    elif args.from_step:
        idx = STEP_ORDER.index(args.from_step)
        steps_to_run = STEP_ORDER[idx:]
    else:
        steps_to_run = STEP_ORDER

    log.info(f"  Steps: {' → '.join(steps_to_run)}")
    log.info("")

    t_total = time.time()
    results = {}
    for step_key in steps_to_run:
        success = run_step(step_key, skip_live=args.skip_live)
        results[step_key] = success
        if not success and step_key == "etl":
            log.error("ETL failed — cannot continue. Aborting pipeline.")
            sys.exit(1)

    # Summary
    elapsed_total = time.time() - t_total
    log.info("")
    log.info("=" * 65)
    log.info("  PIPELINE COMPLETE")
    log.info(f"  Total time: {elapsed_total:.1f}s")
    log.info("")
    log.info("  Step results:")
    for k, v in results.items():
        status = "✓" if v else "✗"
        log.info(f"    {status} {STEPS[k]['label']}")
    log.info("")
    log.info("  Key outputs:")
    log.info("    data/db/bluestock_mf.db          — SQLite database")
    log.info("    outputs/fund_scorecard.csv        — Composite fund ranking")
    log.info("    dashboard/Dashboard.pdf           — 4-page dashboard PDF")
    log.info("    reports/Final_Report.pdf          — 15-page project report")
    log.info("    reports/Bluestock_MF_Presentation.pptx — 12-slide deck")
    log.info("=" * 65)


if __name__ == "__main__":
    main()

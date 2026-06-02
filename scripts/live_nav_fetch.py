#!/usr/bin/env python3
"""
Bluestock Mutual Fund Analytics — Live NAV Fetcher (Bonus B1)
============================================================
Fetches latest NAV for all tracked funds from mfapi.in
Designed to run on a cron schedule (e.g. weekdays at 8 PM).

Usage:
    python scripts/live_nav_fetch.py
"""

import sys
import logging
from pathlib import Path
import sqlite3
import requests
from datetime import datetime

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path(__file__).parent.parent / "live_nav_fetch.log", mode="a")
    ]
)
logger = logging.getLogger("LiveNAV")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "db" / "bluestock_mf.db"

def fetch_nav():
    logger.info("Starting live NAV fetch...")
    
    if not DB_PATH.exists():
        logger.error(f"Database not found at {DB_PATH}")
        sys.exit(1)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all active amfi_codes
    cursor.execute("SELECT amfi_code, scheme_name FROM dim_fund")
    funds = cursor.fetchall()
    logger.info(f"Fetching NAV for {len(funds)} funds...")
    
    updates = 0
    errors = 0
    
    for amfi_code, scheme_name in funds:
        try:
            # Call mfapi.in
            url = f"https://api.mfapi.in/mf/{amfi_code}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("data") and len(data["data"]) > 0:
                    latest = data["data"][0]
                    # Format: dd-mm-yyyy -> yyyy-mm-dd
                    date_obj = datetime.strptime(latest["date"], "%d-%m-%Y")
                    formatted_date = date_obj.strftime("%Y-%m-%d")
                    nav = float(latest["nav"])
                    
                    # Check if exists
                    cursor.execute("SELECT 1 FROM fact_nav WHERE amfi_code = ? AND date = ?", (amfi_code, formatted_date))
                    if not cursor.fetchone():
                        cursor.execute(
                            "INSERT INTO fact_nav (amfi_code, date, nav) VALUES (?, ?, ?)",
                            (amfi_code, formatted_date, nav)
                        )
                        updates += 1
                        logger.info(f"Updated {amfi_code} ({scheme_name[:20]}...) -> Date: {formatted_date}, NAV: {nav}")
            else:
                logger.error(f"API Error for {amfi_code}: Status {response.status_code}")
                errors += 1
                
        except Exception as e:
            logger.error(f"Error fetching {amfi_code}: {e}")
            errors += 1
            
    conn.commit()
    conn.close()
    
    logger.info(f"Live NAV fetch complete. {updates} new records inserted. {errors} errors.")

if __name__ == "__main__":
    fetch_nav()

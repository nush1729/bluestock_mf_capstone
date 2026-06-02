#!/usr/bin/env python3
"""
Bluestock Mutual Fund Analytics — Daily Cron Scheduler Setup (Bonus B1)
========================================================================
Registers the daily NAV fetcher cron job to run every weekday (Mon-Fri) at 8:00 PM (20:00).

Usage:
    python scripts/setup_cron.py
"""

import sys
import os
import subprocess
from pathlib import Path

def setup_cron():
    print("="*60)
    print("BLUESTOCK ANALYTICS — AUTO-SCHEDULER SETUP")
    print("="*60)
    
    script_path = Path(__file__).resolve().parent / "live_nav_fetch.py"
    log_path = Path(__file__).resolve().parent.parent / "live_nav_fetch.log"
    python_bin = sys.executable
    
    # Standard Crontab entry: 8 PM (20:00) on weekdays (Mon-Fri = 1-5)
    cron_command = f"0 20 * * 1-5 {python_bin} {script_path} >> {log_path} 2>&1"
    
    print(f"Target script: {script_path}")
    print(f"Target log: {log_path}")
    print(f"Proposed crontab entry:")
    print(f"  {cron_command}")
    print("-"*60)
    
    try:
        # Get existing crontab
        try:
            current_cron = subprocess.check_output("crontab -l", shell=True, stderr=subprocess.DEVNULL).decode("utf-8")
        except subprocess.CalledProcessError:
            current_cron = ""
            
        # Check if already registered
        if str(script_path) in current_cron:
            print("INFO: Auto-scheduler already registered in system crontab.")
            print("="*60)
            return
            
        # Append new entry
        new_cron = current_cron.rstrip() + "\n" + cron_command + "\n"
        
        # Write back to crontab
        process = subprocess.Popen("crontab -", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(input=new_cron.encode("utf-8"))
        
        if process.returncode == 0:
            print("✅ SUCCESS: Auto-scheduler cron job registered successfully!")
            print("The live NAV fetcher will now automatically run every weekday at 8:00 PM.")
        else:
            print(f"❌ ERROR: Failed to update crontab. Reason: {stderr.decode('utf-8').strip()}")
            print("You can manually register the cron job using: crontab -e")
            
    except Exception as e:
        print(f"❌ ERROR: An unexpected error occurred: {e}")
        
    print("="*60)

if __name__ == "__main__":
    setup_cron()

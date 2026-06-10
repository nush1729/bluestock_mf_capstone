#!/usr/bin/env python3
"""
Wrapper for scripts/live_nav_fetch.py
"""
import os
import sys
from pathlib import Path

# Add scripts directory to path and run live_nav_fetch
scripts_dir = Path(__file__).resolve().parent / "scripts"
sys.path.insert(0, str(scripts_dir))

import live_nav_fetch

if __name__ == "__main__":
    live_nav_fetch.fetch_nav()

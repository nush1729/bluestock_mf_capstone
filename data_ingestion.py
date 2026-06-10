#!/usr/bin/env python3
"""
Wrapper for scripts/data_ingestion.py
"""
import os
import sys
from pathlib import Path

# Add scripts directory to path and run data_ingestion
scripts_dir = Path(__file__).resolve().parent / "scripts"
sys.path.insert(0, str(scripts_dir))

import data_ingestion

if __name__ == "__main__":
    data_ingestion.ingest_and_profile()

#!/usr/bin/env python3
"""
Bluestock Mutual Fund Analytics — Query Runner & Result Embedder
==============================================================
Reads SQL queries from sql/queries.sql, runs them against data/db/bluestock_mf.db,
and writes the results in a formatted markdown file sql/queries_results.md.
Also updates sql/queries.sql to include query results in comment sections.

Usage:
    python scripts/run_queries.py
"""

import os
import re
import sqlite3
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "db" / "bluestock_mf.db"
SQL_FILE = PROJECT_ROOT / "sql" / "queries.sql"
RESULTS_FILE = PROJECT_ROOT / "sql" / "queries_results.md"

def run_queries():
    print("=" * 70)
    print("BLUESTOCK MUTUAL FUND ANALYTICS — SQL QUERY RUNNER")
    print("=" * 70)
    
    if not DB_PATH.exists():
        print(f"Error: Database {DB_PATH} does not exist. Please run ETL pipeline first.")
        return

    if not SQL_FILE.exists():
        print(f"Error: Queries file {SQL_FILE} does not exist.")
        return

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    
    # Read queries.sql
    content = SQL_FILE.read_text(encoding="utf-8")
    
    # We want to split the queries by headers like:
    # -- ============================================================
    # -- QUERY X: ...
    # -- ============================================================
    
    # Let's find each query chunk. A simple way is to find segments starting with -- QUERY X or -- ====================================
    query_blocks = re.split(r"(-- =+[\r\n]+-- QUERY \d+:[^\r\n]*[\r\n]+-- =+)", content)
    
    if len(query_blocks) <= 1:
        # Fallback split if standard header not matched exactly
        query_blocks = re.split(r"(?i)(SELECT\s+)", content)
        print("Warning: Could not parse queries by standard header blocks. running standard execution.")
        conn.close()
        return

    markdown_lines = [
        "# Bluestock Mutual Fund Analytics — SQL Query Results",
        "",
        f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Database source: `data/db/bluestock_mf.db`",
        "",
        "This file contains the output of all the analytical queries written in `sql/queries.sql`.",
        ""
    ]
    
    # Reassemble blocks
    # Header block is usually query_blocks[0]
    # Then for i in range(1, len, 2), query_blocks[i] is the query separator/header, and query_blocks[i+1] is the SQL query text.
    
    updated_sql_blocks = [query_blocks[0]]
    
    for i in range(1, len(query_blocks), 2):
        header = query_blocks[i]
        query_text = query_blocks[i+1]
        
        # Extract query name/title
        title_match = re.search(r"-- QUERY \d+: ([^\r\n]+)", header)
        title = title_match.group(1) if title_match else f"Query {i//2 + 1}"
        
        # Clean SQL code to run: remove comments and strip
        # Keep only lines that don't start with --
        sql_lines = []
        for line in query_text.splitlines():
            clean_line = line.strip()
            # Stop if we hit a results comment from a previous run
            if clean_line.startswith("-- RESULTS_START") or clean_line.startswith("-- RESULTS_END") or (clean_line.startswith("--") and "RESULTS:" in clean_line):
                break
            if clean_line and not clean_line.startswith("--"):
                sql_lines.append(line)
        
        sql_to_run = "\n".join(sql_lines).strip()
        # Remove trailing semicolon for execute
        if sql_to_run.endswith(";"):
            sql_to_run = sql_to_run[:-1]
            
        print(f"Executing: {title}...")
        
        markdown_lines.extend([
            f"## {title}",
            "",
            "### Query",
            "```sql",
            sql_to_run + ";",
            "```",
            "",
            "### Result"
        ])
        
        # Run query and format output
        try:
            df = pd.read_sql_query(sql_to_run, conn)
            
            if df.empty:
                result_str = "No rows returned."
                markdown_lines.extend([result_str, ""])
            else:
                result_str = df.to_markdown(index=False)
                markdown_lines.extend([result_str, ""])
                
            # Add to SQL file comments as well
            # First, strip off any prior result comments from the query text
            cleaned_query_text = []
            for line in query_text.splitlines():
                if "-- RESULTS_START" in line:
                    break
                cleaned_query_text.append(line)
            
            # Format dataframe for SQL comment
            commented_results = ["\n", "-- RESULTS_START", "-- ============================================================"]
            if df.empty:
                commented_results.append("-- No rows returned.")
            else:
                # Limit rows to print in SQL file to top 10
                df_slice = df.head(10)
                formatted_df = df_slice.to_string(index=False)
                for line in formatted_df.splitlines():
                    commented_results.append(f"-- {line}")
                if len(df) > 10:
                    commented_results.append(f"-- ... and {len(df) - 10} more rows.")
            commented_results.extend(["-- ============================================================", "-- RESULTS_END"])
            
            new_query_text = "\n".join(cleaned_query_text).rstrip() + "\n" + "\n".join(commented_results) + "\n\n"
            updated_sql_blocks.extend([header, new_query_text])
            
        except Exception as e:
            print(f"Error running query '{title}': {e}")
            markdown_lines.extend([f"Error running query: {e}", ""])
            updated_sql_blocks.extend([header, query_text])
            
    conn.close()
    
    # Save results markdown file
    RESULTS_FILE.write_text("\n".join(markdown_lines), encoding="utf-8")
    print(f"Saved formatted markdown results to: {RESULTS_FILE}")
    
    # Save updated queries.sql with embedded comments
    updated_sql_content = "".join(updated_sql_blocks)
    SQL_FILE.write_text(updated_sql_content, encoding="utf-8")
    print(f"Updated SQL queries file with embedded results: {SQL_FILE}")

if __name__ == "__main__":
    run_queries()

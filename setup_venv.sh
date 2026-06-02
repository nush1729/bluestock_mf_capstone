#!/bin/bash
# ===========================================================================
# Bluestock Mutual Fund Analytics — Virtual Environment & Platform Setup Script
# ===========================================================================

# Exit immediately if a command exits with a non-zero status
set -e

# Define colors for beautiful logging output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}       BLUESTOCK MUTUAL FUND ANALYTICS PLATFORM SETUP       ${NC}"
echo -e "${BLUE}============================================================${NC}"

# 1. Create Virtual Environment
echo -e "\n${YELLOW}[STEP 1/5] Creating Python Virtual Environment (venv)...${NC}"
python3 -m venv venv
echo -e "${GREEN}✓ Virtual environment 'venv' created successfully.${NC}"

# 2. Activate Virtual Environment
echo -e "\n${YELLOW}[STEP 2/5] Activating Virtual Environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated.${NC}"

# 3. Upgrade pip and install requirements
echo -e "\n${YELLOW}[STEP 3/5] Installing Dependencies from requirements.txt...${NC}"
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓ Dependencies installed successfully.${NC}"

# 4. Run the Data Pipeline & Metrics Computations
echo -e "\n${YELLOW}[STEP 4/5] Executing ETL Pipeline & Metrics Computations...${NC}"
echo -e "${BLUE}  Running ETL Ingestion...${NC}"
python scripts/etl_pipeline.py

echo -e "${BLUE}  Running Metrics Computation Engine...${NC}"
python scripts/compute_metrics.py

echo -e "${BLUE}  Generating Weekly Email Summary Report...${NC}"
python scripts/email_report_generator.py

echo -e "${BLUE}  Generating Final PDF Report & PowerPoint Slides...${NC}"
python scripts/generate_report_slides.py

echo -e "${BLUE}  Configuring Auto-Scheduler Cron Job (Weekday at 8:00 PM)...${NC}"
python scripts/setup_cron.py

echo -e "${GREEN}✓ Data warehouse, performance metrics, reports, and cron job populated successfully.${NC}"

# 5. Launch the Dashboard
echo -e "\n${YELLOW}[STEP 5/5] Launching Streamlit Analytical Dashboard...${NC}"
echo -e "${GREEN}  Streamlit dashboard is starting up. Visit http://localhost:8501 in your browser!${NC}"
echo -e "${BLUE}============================================================${NC}"
streamlit run streamlit_app.py

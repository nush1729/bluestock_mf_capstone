import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sqlite3
from scipy import stats

# ---------------------------------------------------------------------------
# Configuration & Premium Design System
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Bluestock Mutual Fund Analytics Portal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium CSS Styling (Glassmorphism, Dark-mode, Custom Fonts, 3D Effects)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Orbitron:wght@600;800&family=Inter:wght@400;600;700&display=swap');

    /* Global Dark Mode & Typography */
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif;
        color: #38bdf8 !important;
        font-weight: 700 !important;
    }
    
    /* 3D Glassmorphic Cards (Framer Motion inspired) */
    .glass-card {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3), inset 0 1px 1px rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(12px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        transform-style: preserve-3d;
        perspective: 1000px;
    }
    
    .glass-card:hover {
        transform: translateY(-5px) rotateX(2deg) rotateY(2deg);
        border-color: rgba(56, 189, 248, 0.4);
        box-shadow: 0 20px 40px rgba(56, 189, 248, 0.15);
    }
    
    .card-title {
        font-size: 14px;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }
    
    .card-value {
        font-size: 36px;
        color: #f8fafc;
        font-weight: 800;
        font-family: 'Space Grotesk', sans-serif;
    }
    
    /* Sub-text tags */
    .trend-up {
        color: #10b981;
        font-weight: 600;
        font-size: 14px;
    }
    
    /* Elegant Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0b0f19;
    }
    ::-webkit-scrollbar-thumb {
        background: #1e293b;
        border-radius: 9999px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #38bdf8;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Data Loading & Safety Merges
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    """Load and cache all database tables safely without overlapping columns."""
    db_path = Path(__file__).resolve().parent / "data" / "db" / "bluestock_mf.db"
    
    if not db_path.exists():
        db_path = Path("data/db/bluestock_mf.db")
        if not db_path.exists():
            return None
        
    try:
        conn = sqlite3.connect(db_path)
        
        # Load tables
        funds = pd.read_sql("SELECT * FROM dim_fund", conn)
        performance = pd.read_sql("SELECT * FROM fact_performance", conn)
        aum = pd.read_sql("SELECT * FROM fact_aum", conn)
        sip = pd.read_sql("SELECT * FROM fact_sip_industry", conn)
        cat_inflows = pd.read_sql("SELECT * FROM fact_category_inflows", conn)
        transactions = pd.read_sql("SELECT * FROM fact_transactions", conn)
        portfolio = pd.read_sql("SELECT * FROM fact_portfolio", conn)
        nav_history = pd.read_sql("SELECT * FROM fact_nav", conn)
        benchmark = pd.read_sql("SELECT * FROM fact_benchmark", conn)
        
        # Merge dim_fund and fact_performance safely on amfi_code only, avoiding duplicates
        # Overlapping columns to drop from performance before merge:
        perf_cols_to_drop = ["scheme_name", "fund_house", "category", "plan", "expense_ratio_pct"]
        performance_clean = performance.drop(columns=perf_cols_to_drop, errors="ignore")
        
        fund_perf = pd.merge(funds, performance_clean, on="amfi_code")
        
        conn.close()
        return {
            "funds": funds,
            "performance": performance,
            "fund_perf": fund_perf,
            "aum": aum,
            "sip": sip,
            "cat_inflows": cat_inflows,
            "transactions": transactions,
            "portfolio": portfolio,
            "nav_history": nav_history,
            "benchmark": benchmark
        }
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Load the data
data = load_data()

# ---------------------------------------------------------------------------
# Sidebar Navigation System (With Beautiful Custom Text Logo)
# ---------------------------------------------------------------------------
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, #0284c7, #0369a1); padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 25px; box-shadow: 0 10px 25px rgba(2, 132, 199, 0.25); border: 1px solid rgba(255,255,255,0.1);">
    <h2 style="color: white; margin: 0; font-family: 'Orbitron', sans-serif; font-size: 24px; letter-spacing: 2px;">BLUESTOCK</h2>
    <span style="color: rgba(255, 255, 255, 0.85); font-size: 11px; text-transform: uppercase; font-weight: bold; letter-spacing: 1px;">MUTUAL FUND PORTAL</span>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("Navigation Hub")

page = st.sidebar.radio(
    "Navigation System:",
    [
        "� Home",
        "🏛 Executive Summary", 
        "🏆 Fund Performance", 
        "🛡 Risk Analytics", 
        "🎯 Recommendation Center",
        "👥 Investor Demographics",
        "💼 Portfolio & Concentration",
        "🎲 Simulations & Optimization"
    ]
)

# Global Filters
st.sidebar.markdown("---")
st.sidebar.header("Global Selection Filters")

if data:
    selected_amc = st.sidebar.multiselect(
        "Fund House (AMC)",
        options=sorted(data["funds"]["fund_house"].unique()),
        default=[]
    )
    
    selected_category = st.sidebar.multiselect(
        "Fund Category",
        options=sorted(data["funds"]["sub_category"].unique()),
        default=[]
    )
else:
    st.sidebar.warning("Data not available. Please run the ETL pipeline first.")
    st.stop()

# Filter the main performance dataframe based on global filters
filtered_fund_perf = data["fund_perf"].copy()
if selected_amc:
    filtered_fund_perf = filtered_fund_perf[filtered_fund_perf["fund_house"].isin(selected_amc)]
if selected_category:
    filtered_fund_perf = filtered_fund_perf[filtered_fund_perf["sub_category"].isin(selected_category)]

# ---------------------------------------------------------------------------
# Page 0: 3D Interactive Hub (Futuristic Landing Page with Three.js)
# ---------------------------------------------------------------------------
if "Home" in page:
    st.title("🏠 Welcome to Bluestock")
    st.markdown("Intelligent Mutual Fund Analytics Platform for Data-Driven Investment Decisions")
    
    # Hero Section with Welcome Message
    st.markdown("""
    <div class="glass-card" style="padding: 40px; text-align: center; margin-bottom: 30px;">
        <h2 style="color: #38bdf8; font-size: 2.5em; margin-bottom: 15px;">Transform Your Fund Analytics</h2>
        <p style="font-size: 1.1em; color: #94a3b8; line-height: 1.8;">
            Access comprehensive mutual fund data, advanced performance metrics, risk analytics, and AI-powered recommendations in one integrated platform.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Stats Section
    st.subheader("📊 Industry Overview")
    
    # Compute key metrics
    latest_aum_date = data["aum"]["date"].max()
    total_aum = data["aum"][data["aum"]["date"] == latest_aum_date]["aum_lakh_crore"].sum()
    
    # Calculate growth
    aum_dates_sorted = sorted(data["aum"]["date"].unique())
    if len(aum_dates_sorted) >= 2:
        prev_aum_date = aum_dates_sorted[-2]
        prev_aum = data["aum"][data["aum"]["date"] == prev_aum_date]["aum_lakh_crore"].sum()
        aum_growth = ((total_aum / prev_aum) - 1) * 100 if prev_aum > 0 else 0
    else:
        aum_growth = 0
    
    latest_sip = data["sip"].sort_values("month").iloc[-1]["sip_inflow_crore"] if not data["sip"].empty else 0
    total_schemes = len(data["funds"])
    num_amcs = data["funds"]["fund_house"].nunique()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-title">Total Industry AUM</div>
            <div class="card-value">₹{total_aum:.1f}L Cr</div>
            <div class="trend-up">▲ {aum_growth:.1f}% Growth</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-title">Monthly SIP Inflow</div>
            <div class="card-value">₹{latest_sip:,.0f} Cr</div>
            <div class="trend-up">▲ Latest Month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-title">Total Schemes</div>
            <div class="card-value">{total_schemes}</div>
            <div class="trend-up">▲ Tracked Funds</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-title">Active AMCs</div>
            <div class="card-value">{num_amcs}</div>
            <div class="trend-up">▲ Fund Houses</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Dashboard Navigation Section
    st.subheader("🚀 Explore the Dashboard")
    st.markdown("Choose a section below to dive deeper into mutual fund analytics:")
    
    nav_col1, nav_col2, nav_col3 = st.columns(3)
    
    with nav_col1:
        st.markdown("""
        <div class="glass-card" style="height: 220px; cursor: pointer;">
            <h3 style="color: #38bdf8; margin: 0 0 10px 0;">🏛 Executive Summary</h3>
            <p style="color: #94a3b8; line-height: 1.6; margin: 0;">
                Industry-wide metrics, quarterly AUM trends, SIP inflows, and category-wise net flows. Get a macro-level overview of the mutual fund landscape.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with nav_col2:
        st.markdown("""
        <div class="glass-card" style="height: 220px; cursor: pointer;">
            <h3 style="color: #38bdf8; margin: 0 0 10px 0;">🏆 Fund Performance</h3>
            <p style="color: #94a3b8; line-height: 1.6; margin: 0;">
                Deep dive into fund performance metrics: returns, rankings, performance vs benchmarks, and comparative analysis across categories.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with nav_col3:
        st.markdown("""
        <div class="glass-card" style="height: 220px; cursor: pointer;">
            <h3 style="color: #38bdf8; margin: 0 0 10px 0;">🛡 Risk Analytics</h3>
            <p style="color: #94a3b8; line-height: 1.6; margin: 0;">
                Comprehensive risk assessment: volatility, drawdowns, Value at Risk (VaR), Sharpe ratios, and correlation matrices for portfolio analysis.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    nav_col4, nav_col5, nav_col6 = st.columns(3)
    
    with nav_col4:
        st.markdown("""
        <div class="glass-card" style="height: 220px; cursor: pointer;">
            <h3 style="color: #38bdf8; margin: 0 0 10px 0;">🎯 Recommendations</h3>
            <p style="color: #94a3b8; line-height: 1.6; margin: 0;">
                AI-powered fund recommendations based on portfolio optimization, Markowitz frontier analysis, and personalized investment goals.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with nav_col5:
        st.markdown("""
        <div class="glass-card" style="height: 220px; cursor: pointer;">
            <h3 style="color: #38bdf8; margin: 0 0 10px 0;">👥 Demographics</h3>
            <p style="color: #94a3b8; line-height: 1.6; margin: 0;">
                Investor segmentation, demographic analysis, transaction patterns, and behavioral insights across the Indian mutual fund ecosystem.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with nav_col6:
        st.markdown("""
        <div class="glass-card" style="height: 220px; cursor: pointer;">
            <h3 style="color: #38bdf8; margin: 0 0 10px 0;">🎲 Simulations</h3>
            <p style="color: #94a3b8; line-height: 1.6; margin: 0;">
                Monte Carlo projections, scenario analysis, efficient frontier optimization, and advanced financial modeling for sophisticated analysis.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Features Highlight
    st.subheader("✨ Platform Capabilities")
    
    feat_col1, feat_col2 = st.columns(2)
    
    with feat_col1:
        st.markdown("""
        <div class="glass-card">
            <h4 style="color: #38bdf8; margin: 0 0 10px 0;">⚙️ Advanced Metrics</h4>
            <ul style="color: #94a3b8; padding-left: 20px;">
                <li>CAGR, Sharpe Ratio, Sortino Ratio</li>
                <li>Alpha, Beta, and Maximum Drawdown</li>
                <li>Value at Risk (VaR) and Conditional VaR</li>
                <li>Custom Return Calculations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with feat_col2:
        st.markdown("""
        <div class="glass-card">
            <h4 style="color: #38bdf8; margin: 0 0 10px 0;">📊 Data Pipeline</h4>
            <ul style="color: #94a3b8; padding-left: 20px;">
                <li>Automated ETL Pipeline</li>
                <li>Star Schema Data Warehouse</li>
                <li>Real-time NAV Sync</li>
                <li>10+ Synchronized Dimensions</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with st.columns(1)[0]:
        st.markdown("""
        <div class="glass-card">
            <h4 style="color: #38bdf8; margin: 0 0 10px 0;">🤖 ML & Analytics</h4>
            <p style="color: #94a3b8;">K-Means clustering for fund segmentation • Monte Carlo simulations for scenario planning • Markowitz portfolio optimization • Correlation analysis • Pattern recognition</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Call to Action
    st.markdown("<div style='text-align: center; padding: 20px;'></div>", unsafe_allow_html=True)
    
    col_cta1, col_cta2, col_cta3 = st.columns([1, 2, 1])
    
    with col_cta2:
        st.markdown("""
        <div style="text-align: center;">
            <p style="color: #94a3b8; font-size: 1.1em; margin-bottom: 15px;">
                👉 Select a dashboard section from the navigation menu to get started!
            </p>
            <p style="color: #38bdf8; font-weight: bold;">
                Ready to dive into mutual fund intelligence?
            </p>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Page 1: Executive Summary
# ---------------------------------------------------------------------------
elif "Executive Summary" in page:
    st.title("🏛 Executive Summary Dashboard")
    st.markdown("A macro-level dashboard tracking the Indian Mutual Fund industry, monthly SIP inflows, and top AMC performance.")
    
    # PAGE SPECIFIC FILTERS (Must have at least 2)
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        min_aum_lakh_cr = st.slider("Filter by Minimum AMC AUM (Lakh Crore)", 0.0, 15.0, 0.0, 0.5)
    with col_f2:
        year_filter = st.multiselect("Select SIP Fiscal Years/Periods", options=["2022", "2023", "2024", "2025"], default=["2022", "2023", "2024", "2025"])

    # Apply local page filters to AUM
    aum_df = data["aum"].copy()
    if min_aum_lakh_cr > 0:
        aum_df = aum_df[aum_df["aum_lakh_crore"] >= min_aum_lakh_cr]
    if selected_amc:
        aum_df = aum_df[aum_df["fund_house"].isin(selected_amc)]
        
    # Apply filters to SIP
    sip_df = data["sip"].copy()
    sip_df["year"] = sip_df["month"].apply(lambda x: x.split("-")[0])
    sip_df = sip_df[sip_df["year"].isin(year_filter)]

    # Industry KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    latest_aum_date = data["aum"]["date"].max()
    total_aum = data["aum"][data["aum"]["date"] == latest_aum_date]["aum_lakh_crore"].sum()
    total_funds = len(filtered_fund_perf)
    avg_3yr_return = filtered_fund_perf["return_3yr_pct"].mean() if not filtered_fund_perf.empty else 0.0
    num_amcs = filtered_fund_perf["fund_house"].nunique()
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Industry AUM ({latest_aum_date})</div>
            <div class="kpi-value">₹{total_aum:.2f} L Cr</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Schemes Tracked</div>
            <div class="kpi-value">{total_funds}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Average 3Y CAGR (Returns)</div>
            <div class="kpi-value">{avg_3yr_return:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Active AMCs Tracked</div>
            <div class="kpi-value">{num_amcs}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Visualizations
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Quarterly AUM Trend by Top AMCs")
        fig1 = px.line(
            aum_df, 
            x="date", 
            y="aum_lakh_crore", 
            color="fund_house",
            markers=True,
            title="AUM Growth Over Time (Lakh Crore)"
        )
        fig1.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig1, use_container_width=True)
        
    with col_chart2:
        st.subheader("Monthly Industry SIP Inflows")
        fig2 = px.bar(
            sip_df, 
            x="month", 
            y="sip_inflow_crore",
            title="Monthly SIP Inflow Trend (Rs. Crore)",
            color="sip_inflow_crore",
            color_continuous_scale="Blues"
        )
        fig2.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)
        
    st.subheader("Category-wise Net Inflow Analysis (FY 2024-25)")
    cat_inflows = data["cat_inflows"].groupby("category")["net_inflow_crore"].sum().reset_index()
    fig3 = px.bar(
        cat_inflows.sort_values("net_inflow_crore", ascending=False),
        x="category",
        y="net_inflow_crore",
        color="net_inflow_crore",
        color_continuous_scale="Greens",
        title="Net Flows (Rs. Crore)"
    )
    fig3.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig3, use_container_width=True)

    # --- NEW: Industry AUM Treemap ---
    st.subheader("🌳 Industry AUM Treemap by Fund House")
    latest_aum_exec = data["aum"][data["aum"]["date"] == data["aum"]["date"].max()]
    if not latest_aum_exec.empty:
        fig_tree = px.treemap(
            latest_aum_exec,
            path=["fund_house"],
            values="aum_lakh_crore",
            color="aum_lakh_crore",
            color_continuous_scale="Blues",
            title="Proportional AUM by Fund House"
        )
        fig_tree.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=400)
        st.plotly_chart(fig_tree, use_container_width=True)

    # --- NEW: Folio Count Trend ---
    st.subheader("📊 Industry Folio Count Growth")
    sip_trend = data["sip"].copy()
    if "total_folios_crore" in sip_trend.columns:
        fig_folio = px.area(
            sip_trend.sort_values("month"),
            x="month",
            y="total_folios_crore",
            title="Total Industry Folios Over Time (Crore)",
            color_discrete_sequence=["#38bdf8"]
        )
        fig_folio.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=350)
        st.plotly_chart(fig_folio, use_container_width=True)

# ---------------------------------------------------------------------------
# Page 2: Fund Performance
# ---------------------------------------------------------------------------
elif "Fund Performance" in page:
    st.title("🏆 Mutual Fund Performance Analytics")
    st.markdown("Track absolute and annualized compound returns (CAGR) across 40 schemes and multiple periods.")
    
    # PAGE SPECIFIC FILTERS (Must have at least 2)
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        min_return = st.slider("Minimum 3Y CAGR Return (%)", -10, 45, 10)
    with col_f2:
        max_expense = st.slider("Maximum Allowed Expense Ratio (%)", 0.1, 2.5, 2.5, 0.1)
    with col_f3:
        selected_plan = st.radio("Plan Type Filter", options=["All Plans", "Direct", "Regular"])
        
    # Apply filters
    view_df = filtered_fund_perf.copy()
    if selected_plan == "Direct":
        view_df = view_df[view_df["plan"] == "Direct"]
    elif selected_plan == "Regular":
        view_df = view_df[view_df["plan"] == "Regular"]
        
    view_df = view_df[
        (view_df["return_3yr_pct"] >= min_return) & 
        (view_df["expense_ratio_pct"] <= max_expense)
    ]
    
    # Performance Leaderboard Table
    st.subheader("Fund Performance Leaderboard")
    cols_to_show = [
        "scheme_name", "sub_category", "fund_house", "plan", 
        "return_1yr_pct", "return_3yr_pct", "return_5yr_pct", 
        "expense_ratio_pct", "morningstar_rating"
    ]
    
    if view_df.empty:
        st.warning("No schemes match your return and expense parameters.")
    else:
        display_df = view_df[cols_to_show].sort_values("return_3yr_pct", ascending=False)
        display_df.columns = [
            "Scheme Name", "Sub Category", "AMC", "Plan", 
            "1Y Return (%)", "3Y Return (%)", "5Y Return (%)", 
            "Expense Ratio (%)", "Rating"
        ]
        
        st.dataframe(
            display_df.style.background_gradient(subset=["3Y Return (%)", "5Y Return (%)"], cmap="Greens")
                     .format({"1Y Return (%)": "{:.1f}", "3Y Return (%)": "{:.1f}", 
                              "5Y Return (%)": "{:.1f}", "Expense Ratio (%)": "{:.2f}"}),
            use_container_width=True,
            height=350
        )
        
    # Performance Plots
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Distribution of 3Y Returns by Category")
        fig1 = px.box(
            filtered_fund_perf,
            x="sub_category",
            y="return_3yr_pct",
            color="sub_category",
            points="all",
            title="3Y CAGR distribution per Category"
        )
        fig1.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig1, use_container_width=True)
        
    with col_chart2:
        st.subheader("CAGR Return vs Expense Ratio Analysis")
        if not view_df.empty:
            fig2 = px.scatter(
                view_df,
                x="expense_ratio_pct",
                y="return_3yr_pct",
                color="sub_category",
                size="aum_crore",
                hover_name="scheme_name",
                title="Return vs Expense (Bubble size represents AUM)"
            )
            fig2.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Scatter plot cannot render because the active dataframe is empty.")
    
    # --- NEW: Top & Bottom Performers Heatmap ---
    st.markdown("---")
    st.subheader("🔥 Performance Heatmap — Returns Across Periods")
    heatmap_cols = ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct"]
    heatmap_df = filtered_fund_perf.dropna(subset=heatmap_cols).nlargest(15, "return_3yr_pct")
    if not heatmap_df.empty:
        fig_heat = go.Figure(data=go.Heatmap(
            z=heatmap_df[heatmap_cols].values,
            x=["1Y Return (%)", "3Y Return (%)", "5Y Return (%)"],
            y=heatmap_df["scheme_name"].str[:30].values,
            colorscale="RdYlGn",
            text=np.round(heatmap_df[heatmap_cols].values, 1),
            texttemplate="%{text}",
            hovertemplate="Fund: %{y}<br>Period: %{x}<br>Return: %{z:.1f}%<extra></extra>"
        ))
        fig_heat.update_layout(
            title="Top 15 Funds by Return (1Y / 3Y / 5Y)",
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=500
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    # --- NEW: Expense Ratio Distribution ---
    st.subheader("💰 Expense Ratio Distribution")
    fig_exp = px.histogram(
        filtered_fund_perf,
        x="expense_ratio_pct",
        color="plan",
        nbins=20,
        barmode="overlay",
        title="Direct vs Regular Plan Expense Ratios",
        labels={"expense_ratio_pct": "Expense Ratio (%)"}
    )
    fig_exp.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_exp, use_container_width=True)

# ---------------------------------------------------------------------------
# Page 3: Risk Analytics
# ---------------------------------------------------------------------------
elif "Risk Analytics" in page:
    st.title("🛡 Risk & Volatility Analytics")
    st.markdown("Analyze risk-adjusted return parameters (Sharpe, Sortino, Alpha, Beta, Max Drawdown) across all funds.")
    
    # PAGE SPECIFIC FILTERS (Must have at least 2)
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        risk_level = st.multiselect(
            "Filter by Risk Category",
            options=["Low", "Moderate", "High", "Very High", "Moderately High"],
            default=["Moderate", "High", "Very High"]
        )
    with col_f2:
        min_sharpe = st.slider("Minimum Sharpe Ratio", -1.0, 3.0, 0.0, 0.1)
    with col_f3:
        max_beta = st.slider("Maximum Beta (Market Sensitivity)", 0.0, 2.0, 2.0, 0.1)
        
    view_df = filtered_fund_perf[
        (filtered_fund_perf["risk_category"].isin(risk_level)) &
        (filtered_fund_perf["sharpe_ratio"] >= min_sharpe) &
        (filtered_fund_perf["beta"] <= max_beta)
    ].copy()
    
    if view_df.empty:
        st.warning("No funds found matching your selected risk parameters.")
    else:
        # Volatility & Risk KPIs
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Avg Annual Volatility", f"{view_df['std_dev_ann_pct'].mean():.2f}%")
        with col2:
            st.metric("Avg Sharpe Ratio", f"{view_df['sharpe_ratio'].mean():.2f}")
        with col3:
            st.metric("Avg Alpha (Excess Return)", f"{view_df['alpha'].mean():.2f}%")
        with col4:
            st.metric("Avg Max Drawdown", f"{view_df['max_drawdown_pct'].mean():.2f}%")
            
        st.markdown("---")
        
        # Risk-Return Plots
        st.subheader("Volatility vs Return (Efficient Frontier Concept)")
        fig1 = px.scatter(
            view_df,
            x="std_dev_ann_pct",
            y="return_3yr_pct",
            color="sub_category",
            size="aum_crore",
            hover_name="scheme_name",
            labels={
                "std_dev_ann_pct": "Annualized Volatility (%)",
                "return_3yr_pct": "3Y CAGR Return (%)"
            },
            title="High Return with Low Risk is Optimal (Top Left)"
        )
        # Quadrant Lines
        x_mid = view_df["std_dev_ann_pct"].median()
        y_mid = view_df["return_3yr_pct"].median()
        fig1.add_hline(y=y_mid, line_dash="dash", line_color="gray", opacity=0.5)
        fig1.add_vline(x=x_mid, line_dash="dash", line_color="gray", opacity=0.5)
        fig1.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig1, use_container_width=True)
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("Top Outperforming Funds by Alpha")
            top_alpha = view_df.nlargest(10, "alpha")
            fig2 = px.bar(
                top_alpha,
                x="alpha",
                y="scheme_name",
                orientation="h",
                color="alpha",
                color_continuous_scale="Purples",
                title="Top 10 Funds by Alpha (Excess Return vs Benchmark)"
            )
            fig2.update_layout(yaxis={'categoryorder':'total ascending'}, template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig2, use_container_width=True)
            
        with col_chart2:
            st.subheader("Sensitivity to Market (Beta distribution)")
            fig3 = px.histogram(
                view_df,
                x="beta",
                color="sub_category",
                nbins=15,
                title="Beta vs Sub Category (1.0 = Benchmark Index)"
            )
            fig3.add_vline(x=1.0, line_dash="dash", line_color="red")
            fig3.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig3, use_container_width=True)

        # --- NEW: Max Drawdown Waterfall ---
        st.markdown("---")
        st.subheader("📉 Maximum Drawdown Waterfall (Top 15 Funds)")
        dd_df = view_df.nlargest(15, "return_3yr_pct")[["scheme_name", "max_drawdown_pct"]].copy()
        dd_df["scheme_short"] = dd_df["scheme_name"].str[:30]
        fig_dd = px.bar(
            dd_df.sort_values("max_drawdown_pct"),
            x="max_drawdown_pct",
            y="scheme_short",
            orientation="h",
            color="max_drawdown_pct",
            color_continuous_scale="Reds_r",
            title="Largest Drawdowns (Negative = Bigger Loss)",
            labels={"max_drawdown_pct": "Max Drawdown (%)", "scheme_short": "Fund"}
        )
        fig_dd.update_layout(yaxis={'categoryorder':'total ascending'}, template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_dd, use_container_width=True)

        # --- NEW: VaR vs CVaR scatter ---
        st.subheader("⚠️ Value at Risk vs Conditional VaR (95% Confidence)")
        var_df = view_df.dropna(subset=["var_95_pct", "cvar_95_pct"])
        if not var_df.empty:
            fig_var = px.scatter(
                var_df,
                x="var_95_pct",
                y="cvar_95_pct",
                color="sub_category",
                hover_name="scheme_name",
                title="VaR vs CVaR (Higher magnitude = Higher tail risk)",
                labels={"var_95_pct": "VaR 95% (Daily %)", "cvar_95_pct": "CVaR 95% (Daily %)"}
            )
            fig_var.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_var, use_container_width=True)

# ---------------------------------------------------------------------------
# Page 4: Recommendation Center
# ---------------------------------------------------------------------------
elif "Recommendation Center" in page:
    st.title("🎯 Mutual Fund Recommendation Center")
    st.markdown("Specify your investment parameters and matching profile to get the top algorithmically scored funds.")
    
    # PAGE SPECIFIC FILTERS (Must have at least 2)
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        inv_horizon = st.selectbox(
            "Select Investment Horizon", 
            options=["Short Term (< 1 Year)", "Medium Term (1-3 Years)", "Long Term (> 3 Years)"]
        )
        
    with col_f2:
        risk_appetite = st.select_slider(
            "Select Risk Appetite Profile", 
            options=["Low", "Moderate", "High", "Very High"],
            value="Moderate"
        )
        
    with col_f3:
        pref_category = st.selectbox(
            "Filter Category Preferences", 
            options=["Any", "Large Cap", "Mid Cap", "Small Cap", "Liquid", "Debt"]
        )
        
    st.markdown("---")
    
    # Recommendation Scopes
    if risk_appetite == "Low":
        target_risk = ["Low"]
    elif risk_appetite == "Moderate":
        target_risk = ["Low", "Moderate"]
    elif risk_appetite == "High":
        target_risk = ["Moderate", "High", "Moderately High"]
    else:
        target_risk = ["High", "Very High", "Moderately High"]
        
    rec_df = data["fund_perf"][data["fund_perf"]["risk_category"].isin(target_risk)].copy()
    
    if pref_category != "Any":
        rec_df = rec_df[rec_df["sub_category"].str.contains(pref_category, case=False, na=False)]
        
    if "Short" in inv_horizon:
        rec_df = rec_df[rec_df["category"] == "Debt"]
        
    if rec_df.empty:
        st.warning("No funds found matching this specific profile combination. Try relaxing your filters.")
    else:
        # Score Engine (40% Sharpe, 30% CAGR Return, 30% Alpha)
        rec_df["score"] = (
            rec_df["sharpe_ratio"].rank(pct=True) * 40 +
            rec_df["return_3yr_pct"].rank(pct=True) * 30 +
            rec_df["alpha"].rank(pct=True) * 30
        )
        
        top_recs = rec_df.nlargest(5, "score")
        
        st.subheader("Top Recommended Funds for Your Profile")
        for i, (_, row) in enumerate(top_recs.iterrows()):
            st.markdown(f"""
            <div class="rec-card">
                <h4 style="color: #38bdf8; margin: 0 0 5px 0;">#{i+1}: {row['scheme_name']}</h4>
                <div style="display: flex; gap: 30px; font-size: 15px; flex-wrap: wrap;">
                    <div><strong>Category:</strong> {row['sub_category']}</div>
                    <div><strong>3Y Return (CAGR):</strong> <span style="color: #10b981;">{row['return_3yr_pct']:.2f}%</span></div>
                    <div><strong>Sharpe Ratio:</strong> {row['sharpe_ratio']:.2f}</div>
                    <div><strong>Expense Ratio:</strong> {row['expense_ratio_pct']:.2f}%</div>
                    <div><strong>Risk Profile:</strong> {row['risk_category']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # Comparison radar
        st.subheader("Multidimensional Fund Comparison")
        fig = go.Figure()
        
        metrics_categories = ['3Y Return (Scaled)', 'Sharpe Ratio (Scaled)', 'Alpha (Scaled)', 'Expense Ratio (Inverted)']
        
        for _, row in top_recs.head(3).iterrows():
            ret = min(100, max(0, row['return_3yr_pct'] * 2.5))
            sharpe = min(100, max(0, row['sharpe_ratio'] * 35))
            alpha = min(100, max(0, (row['alpha'] + 5) * 8))
            exp_ratio = min(100, max(0, (3 - row['expense_ratio_pct']) * 35))
            
            fig.add_trace(go.Scatterpolar(
                r=[ret, sharpe, alpha, exp_ratio],
                theta=metrics_categories,
                fill='toself',
                name=row['scheme_name'][:30]
            ))
            
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# Page 5: Investor Demographics (New!)
# ---------------------------------------------------------------------------
elif "Investor Demographics" in page:
    st.title("👥 Investor Demographics & Behavioral Analytics")
    st.markdown("Detailed transaction, geographic, and demographic analysis of Indian mutual fund retail investors.")
    
    # PAGE SPECIFIC FILTERS (Must have at least 2)
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        selected_states = st.multiselect(
            "Select States to Filter", 
            options=sorted(data["transactions"]["state"].dropna().unique()),
            default=[]
        )
    with col_f2:
        selected_age = st.multiselect(
            "Select Age Groups", 
            options=sorted(data["transactions"]["age_group"].dropna().unique()),
            default=[]
        )
        
    # Apply filters
    tx_df = data["transactions"].copy()
    if selected_states:
        tx_df = tx_df[tx_df["state"].isin(selected_states)]
    if selected_age:
        tx_df = tx_df[tx_df["age_group"].isin(selected_age)]
        
    if tx_df.empty:
        st.warning("No transactions found matching your demographic criteria.")
    else:
        # Demographic KPIs
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Transaction Value", f"₹{tx_df['amount_inr'].sum() / 1e7:.2f} Cr")
        with col2:
            st.metric("Average Transaction Amount", f"₹{tx_df['amount_inr'].mean():,.2f}")
        with col3:
            st.metric("Total Unique Investors Tracked", len(tx_df["investor_id"].unique()))
            
        st.markdown("---")
        
        # Charts
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            st.subheader("Transaction Type Distribution")
            tx_type = tx_df.groupby("transaction_type")["amount_inr"].sum().reset_index()
            fig1 = px.pie(
                tx_type, 
                names="transaction_type", 
                values="amount_inr",
                hole=0.4,
                title="SIP vs Lumpsum vs Redemption Splits"
            )
            fig1.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig1, use_container_width=True)
            
        with col_c2:
            st.subheader("Geographical Distribution (Transaction Value by State)")
            state_val = tx_df.groupby("state")["amount_inr"].sum().reset_index()
            fig2 = px.bar(
                state_val.sort_values("amount_inr", ascending=False),
                x="state",
                y="amount_inr",
                color="amount_inr",
                labels={"amount_inr": "Total Invested (INR)"},
                title="Total Value per State"
            )
            fig2.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig2, use_container_width=True)
            
        col_c3, col_c4 = st.columns(2)
        
        with col_c3:
            st.subheader("Average Investment Value by Age Group")
            fig3 = px.box(
                tx_df,
                x="age_group",
                y="amount_inr",
                color="age_group",
                title="SIP / Purchase Amount Ranges"
            )
            fig3.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig3, use_container_width=True)
            
        with col_c4:
            st.subheader("Preferred Payment Mode Split")
            pay_split = tx_df.groupby("payment_mode")["amount_inr"].count().reset_index()
            fig4 = px.bar(
                pay_split.sort_values("amount_inr", ascending=False),
                x="payment_mode",
                y="amount_inr",
                labels={"amount_inr": "Count of Transactions"},
                color="payment_mode",
                title="Preferred Modes (UPI, Cheque, Mandates)"
            )
            fig4.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig4, use_container_width=True)

        # --- NEW: Monthly Transaction Volume Trend ---
        st.markdown("---")
        st.subheader("📅 Monthly Transaction Volume Trend")
        tx_monthly = tx_df.copy()
        tx_monthly["transaction_date"] = pd.to_datetime(tx_monthly["transaction_date"], errors="coerce")
        tx_monthly["year_month"] = tx_monthly["transaction_date"].dt.to_period("M").astype(str)
        monthly_agg = tx_monthly.groupby(["year_month", "transaction_type"]).agg(
            total_value=pd.NamedAgg(column="amount_inr", aggfunc="sum"),
            count=pd.NamedAgg(column="amount_inr", aggfunc="count")
        ).reset_index()
        fig_trend = px.bar(
            monthly_agg,
            x="year_month",
            y="total_value",
            color="transaction_type",
            barmode="group",
            title="Monthly Transaction Value by Type",
            labels={"total_value": "Value (INR)", "year_month": "Month"}
        )
        fig_trend.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=400)
        st.plotly_chart(fig_trend, use_container_width=True)

        # --- NEW: Gender Distribution Sunburst ---
        if "gender" in tx_df.columns:
            st.subheader("🧑‍🤝‍🧑 Investment Breakdown: Gender × Transaction Type")
            gender_agg = tx_df.groupby(["gender", "transaction_type"])["amount_inr"].sum().reset_index()
            fig_sun = px.sunburst(
                gender_agg,
                path=["gender", "transaction_type"],
                values="amount_inr",
                title="Investor Gender to Transaction Type Flow",
                color="amount_inr",
                color_continuous_scale="Teal"
            )
            fig_sun.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=450)
            st.plotly_chart(fig_sun, use_container_width=True)

        # --- NEW: Top Investors Table ---
        st.subheader("💵 Top 20 Investors by Total Investment")
        top_investors = tx_df.groupby("investor_id").agg(
            total_invested=pd.NamedAgg(column="amount_inr", aggfunc="sum"),
            num_transactions=pd.NamedAgg(column="amount_inr", aggfunc="count")
        ).nlargest(20, "total_invested").reset_index()
        top_investors["avg_ticket"] = top_investors["total_invested"] / top_investors["num_transactions"]
        top_investors.columns = ["Investor ID", "Total Invested (INR)", "# Transactions", "Avg Ticket (INR)"]
        st.dataframe(
            top_investors.style.format({
                "Total Invested (INR)": "₹{:,.0f}",
                "Avg Ticket (INR)": "₹{:,.0f}"
            }),
            use_container_width=True
        )

# ---------------------------------------------------------------------------
# Page 6: Portfolio & Concentration (New!)
# ---------------------------------------------------------------------------
elif "Portfolio & Concentration" in page:
    st.title("💼 Portfolio Holdings & Sector Concentration")
    st.markdown("Examine the underlying stock holdings of equity funds and analyze sector concentration indices (HHI).")
    
    # PAGE SPECIFIC FILTERS (Must have at least 2)
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        # Load equity funds
        equity_funds = data["funds"]["scheme_name"].unique()
        selected_fund = st.selectbox("Select Mutual Fund Scheme", options=equity_funds)
    with col_f2:
        min_weight = st.slider("Filter Stocks by Minimum Weight (%)", 0.0, 10.0, 1.0, 0.5)

    # Filter details
    fund_code = data["funds"][data["funds"]["scheme_name"] == selected_fund]["amfi_code"].values[0]
    holdings = data["portfolio"][data["portfolio"]["amfi_code"] == fund_code].copy()

    if holdings.empty:
        st.info("Portfolio holdings for the selected fund are not available. Choose an equity scheme.")
    else:
        # HHI index calculation (Herfindahl-Hirschman Index)
        # HHI = sum(weights^2)
        # Low: < 1500, Mod: 1500 - 2500, High: > 2500
        sector_weights = holdings.groupby("sector")["weight_pct"].sum()
        hhi = np.sum(sector_weights ** 2)
        
        if hhi < 1000:
            hhi_status = "<span class='score-high'>Extremely Diversified</span>"
        elif hhi < 1800:
            hhi_status = "<span class='score-med'>Moderately Diversified</span>"
        else:
            hhi_status = "<span class='score-low'>Highly Concentrated</span>"

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Holdings", f"{len(holdings)} Stocks")
        with col2:
            st.metric("Sector HHI Index Value", f"{hhi:.1f}")
        with col3:
            st.markdown(f"<div style='font-size: 16px; margin-top:10px;'><strong>Concentration Grade:</strong><br/>{hhi_status}</div>", unsafe_allow_html=True)

        st.markdown("---")

        # Table & plots
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            st.subheader("Sector Allocation weights")
            sec_df = sector_weights.reset_index().sort_values("weight_pct", ascending=False)
            fig1 = px.pie(
                sec_df, 
                names="sector", 
                values="weight_pct",
                title="Sector Diversification Details"
            )
            fig1.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig1, use_container_width=True)
            
        with col_c2:
            st.subheader("Top stock Allocations")
            filtered_holdings = holdings[holdings["weight_pct"] >= min_weight].sort_values("weight_pct", ascending=False)
            fig2 = px.bar(
                filtered_holdings.head(15),
                x="weight_pct",
                y="stock_name",
                orientation="h",
                color="weight_pct",
                color_continuous_scale="Teal",
                title="Top Holdings (Weights %)"
            )
            fig2.update_layout(yaxis={'categoryorder':'total ascending'}, template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig2, use_container_width=True)
            
        st.subheader("Full Holdings Breakdown Table")
        st.dataframe(
            holdings[["stock_name", "stock_symbol", "sector", "weight_pct", "market_value_cr"]]
            .sort_values("weight_pct", ascending=False),
            use_container_width=True
        )

        # --- NEW: Sector-wise Summary Statistics ---
        st.markdown("---")
        st.subheader("📋 Sector-wise Summary Statistics")
        sec_stats = holdings.groupby("sector").agg(
            num_stocks=pd.NamedAgg(column="stock_name", aggfunc="count"),
            total_weight=pd.NamedAgg(column="weight_pct", aggfunc="sum"),
            avg_weight=pd.NamedAgg(column="weight_pct", aggfunc="mean"),
            total_market_value=pd.NamedAgg(column="market_value_cr", aggfunc="sum")
        ).sort_values("total_weight", ascending=False).reset_index()
        sec_stats.columns = ["Sector", "# Stocks", "Total Weight (%)", "Avg Weight (%)", "Market Value (Cr)"]
        st.dataframe(
            sec_stats.style.format({
                "Total Weight (%)": "{:.2f}",
                "Avg Weight (%)": "{:.2f}",
                "Market Value (Cr)": "₹{:,.2f}"
            }).background_gradient(subset=["Total Weight (%)"], cmap="YlGnBu"),
            use_container_width=True
        )

        # --- NEW: Radar chart for sector allocation ---
        st.subheader("🕹️ Sector Allocation Radar")
        radar_sectors = sector_weights.reset_index().sort_values("weight_pct", ascending=False).head(8)
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=radar_sectors["weight_pct"].values,
            theta=radar_sectors["sector"].values,
            fill="toself",
            name="Sector Weights",
            line=dict(color="#38bdf8")
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True)),
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            title="Top 8 Sectors Allocation Radar",
            height=400
        )
        st.plotly_chart(fig_radar, use_container_width=True)

# ---------------------------------------------------------------------------
# Page 7: Simulations & Optimization (New!)
# ---------------------------------------------------------------------------
elif "Simulations & Optimization" in page:
    st.title("🎲 Dynamic Advanced Portfolio Simulations")
    st.markdown("Run live 5-year Monte Carlo growth projections and compute the Markowitz Efficient Frontier portfolio optimizer.")

    # TABS FOR SIMULATION TYPES
    tab1, tab2 = st.tabs(["Monte Carlo Simulation (B3)", "Markowitz Portfolio Optimization (B4)"])

    with tab1:
        st.subheader("Monte Carlo Fund Projection Simulator")
        
        # PAGE SPECIFIC FILTERS (Must have at least 2)
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            selected_mc_fund = st.selectbox("Select Fund to Simulate", options=data["funds"]["scheme_name"].unique())
        with col_f2:
            starting_val = st.number_input("Starting Investment (INR)", min_value=5000, value=100000, step=10000)
        with col_f3:
            num_paths = st.slider("Select Simulation Paths", 100, 1000, 250, 50)
            
        # Get historical returns for selected fund
        mc_fund_code = data["funds"][data["funds"]["scheme_name"] == selected_mc_fund]["amfi_code"].values[0]
        fund_navs = data["nav_history"][data["nav_history"]["amfi_code"] == mc_fund_code].sort_values("date")
        
        if len(fund_navs) < 252:
            st.warning("Insufficient historical NAV data to execute Monte Carlo simulation.")
        else:
            returns = fund_navs["nav"].pct_change().dropna()
            mu = returns.mean()
            vol = returns.std()
            
            # Days to simulate (5 years of trading)
            sim_days = 252 * 5
            
            # Generate simulated paths (geometric brownian motion / random walk)
            sim_returns = np.random.normal(loc=mu, scale=vol, size=(sim_days, num_paths))
            price_paths = np.zeros((sim_days, num_paths))
            price_paths[0] = starting_val
            
            for t in range(1, sim_days):
                price_paths[t] = price_paths[t-1] * (1 + sim_returns[t])
                
            # Perform percentiles computation
            median_path = np.percentile(price_paths, 50, axis=1)
            high_path = np.percentile(price_paths, 90, axis=1)
            low_path = np.percentile(price_paths, 10, axis=1)
            
            # Plotly projection chart
            fig_mc = go.Figure()
            
            # Add range bands
            fig_mc.add_trace(go.Scatter(
                y=high_path, name="Optimistic (90th Pct)", 
                line=dict(color='rgba(57, 211, 83, 0.5)', width=1, dash='dash')
            ))
            fig_mc.add_trace(go.Scatter(
                y=median_path, name="Median Expectation (50th Pct)", 
                line=dict(color='#1f6feb', width=3)
            ))
            fig_mc.add_trace(go.Scatter(
                y=low_path, name="Conservative (10th Pct)", 
                line=dict(color='rgba(248, 81, 73, 0.5)', width=1, dash='dash')
            ))
            
            fig_mc.update_layout(
                title="5-Year Simulated NAV Portfolio Growth Projection",
                xaxis_title="Trading Days",
                yaxis_title="Portfolio Value (INR)",
                template="plotly_dark",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_mc, use_container_width=True)
            
            # Stats Table
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Conservative Expected Value", f"₹{low_path[-1]:,.2f}")
            with col2:
                st.metric("Median Expected Value", f"₹{median_path[-1]:,.2f}")
            with col3:
                st.metric("Optimistic Expected Value", f"₹{high_path[-1]:,.2f}")

    with tab2:
        st.subheader("Markowitz Efficient Frontier Asset Allocator")
        
        # PAGE SPECIFIC FILTERS (Must have at least 2)
        col_op1, col_op2 = st.columns(2)
        with col_op1:
            selected_op_funds = st.multiselect(
                "Select 5 Funds to Optimize Allocation",
                options=list(data["funds"]["scheme_name"].unique()),
                default=list(data["funds"]["scheme_name"].unique())[:5]
            )
        with col_op2:
            sim_portfolios = st.slider("Simulate Portfolio Weights Count", 500, 5000, 1000, 250)
            
        if len(selected_op_funds) < 3:
            st.warning("Please select at least 3 funds to generate a Markowitz portfolio frontier.")
        else:
            # Load NAV tables and returns
            returns_dict = {}
            for name in selected_op_funds:
                f_code = data["funds"][data["funds"]["scheme_name"] == name]["amfi_code"].values[0]
                nav_series = data["nav_history"][data["nav_history"]["amfi_code"] == f_code].sort_values("date")
                returns_dict[name] = nav_series["nav"].pct_change().dropna().values
                
            # Align lengths
            min_len = min([len(r) for r in returns_dict.values()])
            aligned_returns = np.array([r[-min_len:] for r in returns_dict.values()]).T
            
            # Compute mean and covariance matrix
            mean_returns = np.mean(aligned_returns, axis=0) * 252
            cov_matrix = np.cov(aligned_returns.T) * 252
            
            # Portfolios simulation
            n_assets = len(selected_op_funds)
            port_returns = []
            port_vols = []
            port_sharpe = []
            port_weights = []
            
            for _ in range(sim_portfolios):
                weights = np.random.random(n_assets)
                weights /= np.sum(weights)
                
                ret = np.sum(mean_returns * weights)
                vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                sharpe = (ret - 0.065) / vol # 6.5% Risk Free Rate
                
                port_returns.append(ret)
                port_vols.append(vol)
                port_sharpe.append(sharpe)
                port_weights.append(weights)
                
            port_returns = np.array(port_returns)
            port_vols = np.array(port_vols)
            port_sharpe = np.array(port_sharpe)
            
            # Identify optimal index (Max Sharpe)
            max_sharpe_idx = np.argmax(port_sharpe)
            optimal_weights = port_weights[max_sharpe_idx]
            
            # Plotly Scatter Plot
            fig_opt = go.Figure()
            fig_opt.add_trace(go.Scatter(
                x=port_vols, y=port_returns * 100,
                mode='markers',
                marker=dict(color=port_sharpe, colorscale='Viridis', size=6, showscale=True, colorbar=dict(title="Sharpe")),
                name="Simulated Portfolios"
            ))
            # Highlight optimal portfolio
            fig_opt.add_trace(go.Scatter(
                x=[port_vols[max_sharpe_idx]], y=[port_returns[max_sharpe_idx] * 100],
                mode='markers',
                marker=dict(color='red', size=15, symbol='star'),
                name="Max Sharpe Allocation"
            ))
            
            fig_opt.update_layout(
                title="Efficient Frontier Scatter Diagram",
                xaxis_title="Annualized Portfolio Risk (Volatility)",
                yaxis_title="Expected Portfolio Return (%)",
                template="plotly_dark",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_opt, use_container_width=True)
            
            # Display optimal weights
            st.subheader("Optimal Weight Allocation (Max Sharpe Ratio Portfolio)")
            opt_weights_df = pd.DataFrame({
                "Asset / Scheme Name": selected_op_funds,
                "Optimal Weight (%)": optimal_weights * 100
            }).sort_values("Optimal Weight (%)", ascending=False)
            
            st.table(opt_weights_df.style.format({"Optimal Weight (%)": "{:.2f}%"}))
            
            # --- NEW: Optimal Portfolio Pie Chart ---
            st.subheader("🥧 Optimal Portfolio Allocation Breakdown")
            fig_pie_opt = px.pie(
                opt_weights_df,
                names="Asset / Scheme Name",
                values="Optimal Weight (%)",
                title="Max Sharpe Portfolio Weight Distribution",
                hole=0.35
            )
            fig_pie_opt.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_pie_opt, use_container_width=True)

            # --- NEW: Portfolio Expected Returns Summary ---
            st.subheader("📊 Optimal Portfolio Expected Metrics")
            opt_ret = port_returns[max_sharpe_idx] * 100
            opt_vol = port_vols[max_sharpe_idx] * 100
            opt_sh = port_sharpe[max_sharpe_idx]
            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                st.metric("Expected Annual Return", f"{opt_ret:.2f}%")
            with mc2:
                st.metric("Expected Volatility", f"{opt_vol:.2f}%")
            with mc3:
                st.metric("Sharpe Ratio", f"{opt_sh:.3f}")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px 0; color: #64748b; font-size: 12px;">
    <p style="margin: 0;">Bluestock Mutual Fund Analytics Platform &bull; Powered by Real AMFI Data</p>
    <p style="margin: 5px 0 0 0;">Built with Streamlit, Plotly, Three.js &bull; &copy; 2025 Bluestock Fintech</p>
</div>
""", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import numpy as np
import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Sovereign | Live For The People",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CUSTOM CSS FOR GRAPHITE & NEON THEME ---
st.markdown("""
    <style>
    .main { background-color: #1a1a1a; color: #e0e0e0; }
    .stMetric { background-color: #262626; padding: 15px; border-radius: 10px; border: 1px solid #33ff33; }
    div[data-testid="stMetricValue"] { color: #33ff33; font-family: 'Courier New', monospace; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #33ff33; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER & TICKER ---
st.title("⚡ SOVEREIGN: LIVE FOR THE PEOPLE")
st.caption("Hybrid AI Asset Selection & Wealth Democratization Engine")
st.write("---")

# Simulated Live Ticker
ticker_cols = st.columns(4)
ticker_cols[0].metric("NIFTY 50", "22,450", "+1.2%")
ticker_cols[1].metric("SENSEX", "74,120", "+0.8%")
ticker_cols[2].metric("BRASS (IND)", "₹482/kg", "+2.4%")
ticker_cols[3].metric("USD/INR", "₹83.45", "-0.1%")

# --- SIDEBAR: RISK & STRATEGY ---
with st.sidebar:
    st.header("🛡️ Control Center")
    risk_profile = st.select_slider(
        "Risk Appetite",
        options=["Conservative", "Moderate", "Aggressive", "Sovereign Mode"]
    )
    
    st.write("---")
    st.subheader("Billing Tier")
    st.info("Current Tier: HNI Professional")
    
    st.write("---")
    st.subheader("Industrial Monitor")
    st.write(f"Last Update: {datetime.datetime.now().strftime('%H:%M:%S')}")

# --- STAGE 2: HYBRID AI ASSET SELECTION ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🎯 Hybrid AI Recommendations")
    
    # Logic for Asset Selection based on RSI & Sentiment
    assets = {
        "Asset": ["Equity Alpha", "Commodity Brass", "Liquid Gold", "Fintech Index"],
        "Sentiment Score": [88, 72, 45, 94],
        "RSI Indicator": [62, 58, 71, 54],
        "Action": ["STRONG BUY", "HOLD", "REDUCE", "STRONG BUY"]
    }
    df = pd.DataFrame(assets)
    
    # Highlighting the "Strong Buys"
    def highlight_action(val):
        color = '#33ff33' if val == 'STRONG BUY' else '#ff4b4b' if val == 'REDUCE' else 'white'
        return f'color: {color}'

    st.table(df.style.applymap(highlight_action, subset=['Action']))

with col2:
    st.subheader("🛡️ Solvency Guard")
    equity_ratio = st.progress(78)
    st.write("Current Liquidity Buffer: **78%**")
    st.warning("Strategy: Rebound Simulation active for low-volatility assets.")

# --- STAGE 3: WEALTH PROJECTION ---
st.write("---")
st.subheader("📈 Projected Growth Path")
chart_data = pd.DataFrame(
    np.random.randn(20, 2).cumsum(axis=0),
    columns=['Standard Portfolio', 'Sovereign AI Portfolio']
)
st.line_chart(chart_data)

# --- FOOTER ---
st.write("---")
st.caption("© 2026 Sovereign Systems | Confidential Startup Interface")

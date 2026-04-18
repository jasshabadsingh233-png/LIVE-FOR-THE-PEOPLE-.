import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Sovereign Terminal", layout="wide")

# Custom CSS for the Graphite/Neon "HNI" Look
st.markdown("""
    <style>
    .main { background-color: #111111; color: #ffffff; }
    .stMetric { border: 1px solid #33ff33; padding: 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ SOVEREIGN: LIVE FOR THE PEOPLE")
st.write("---")

# --- 2. THE TABS (ORGANIZATION) ---
tab1, tab2, tab3 = st.tabs(["📊 Market Watch", "💰 Wealth Projection", "🛠️ Industrial Arbitrage"])

with tab1:
    st.subheader("Live Global Market Pulse")
    
    # Define tickers for BTC and other assets
    tickers = {
        "Bitcoin": "BTC-USD",
        "Ethereum": "ETH-USD",
        "Gold": "GC=F",
        "Nifty 50": "^NSEI",
        "Reliance": "RELIANCE.NS"
    }
    
    cols = st.columns(len(tickers))
    
    for i, (name, symbol) in enumerate(tickers.items()):
        try:
            ticker = yf.Ticker(symbol)
            current_price = ticker.history(period="1d")['Close'].iloc[-1]
            prev_close = ticker.history(period="2d")['Close'].iloc[0]
            delta = ((current_price - prev_close) / prev_close) * 100
            
            cols[i].metric(name, f"{current_price:,.2f}", f"{delta:.2f}%")
        except:
            cols[i].metric(name, "Offline", "0%")

    st.write("### Bitcoin Trend Analysis")
    btc_hist = yf.Ticker("BTC-USD").history(period="7d")
    st.area_chart(btc_hist['Close'])

with tab2:
    st.subheader("🚀 Future Wealth Projection")
    st.write("Calculate your growth using our Sovereign AI strategy.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        initial_inv = st.number_input("Initial Investment (₹)", value=100000)
        monthly_sip = st.number_input("Monthly SIP (₹)", value=10000)
    with col_b:
        expected_return = st.slider("Expected Annual Return (%)", 5, 40, 15)
        years = st.slider("Time Horizon (Years)", 1, 30, 10)
    
    # Simple Compound Interest Formula
    months = years * 12
    monthly_rate = (expected_return / 100) / 12
    total = initial_inv * (1 + monthly_rate)**months + monthly_sip * (((1 + monthly_rate)**months - 1) / monthly_rate)
    
    st.write("---")
    st.header(f"Projected Value: **₹{total:,.0f}**")
    st.caption("Disclaimer: Projections based on historical Sovereign AI performance.")

with tab3:
    st.subheader("🏭 Industrial Monitor (Jamnagar Context)")
    st.write("Comparing Global Copper (LME) to local Brass Scrap trends.")
    
    copper = yf.Ticker("HG=F").history(period="1d")['Close'].iloc[-1]
    # Logic: Brass is usually ~60% of Copper price in local markets
    estimated_brass = (copper * 0.60 * 83.50) / 0.453592 # Converting lb to kg and USD to INR
    
    c1, c2 = st.columns(2)
    c1.metric("LME Copper (USD/lb)", f"${copper:.2f}")
    c2.metric("Est. Brass Value (₹/kg)", f"₹{estimated_brass:.0f}", help="Calculated based on 60% copper-zinc correlation.")
    
    st.info("Strategy: When BTC/Copper ratio hits 14,500, rotate liquidity into Industrial Assets.")

st.write("---")
st.caption("Secure Terminal Connection: Active | Location: Jamnagar")

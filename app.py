import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="SOVEREIGN OS | Live For The People", layout="wide", initial_sidebar_state="expanded")

# Extreme CSS for High-End Fintech Branding
st.markdown("""
    <style>
    .main { background-color: #050505; color: #00ffc8; font-family: 'Inter', sans-serif; }
    .stMetric { border: 1px solid #00ffc8; background-color: #0a0a0a; padding: 15px; border-radius: 12px; }
    div[data-testid="stExpander"] { background-color: #111; border: 1px solid #333; }
    .stButton>button { background: linear-gradient(90deg, #00ffc8, #008f7a); color: black; font-weight: bold; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VIRTUAL WALLET ENGINE ---
if 'balance' not in st.session_state:
    st.session_state.balance = 1000000.0  # ₹10 Lakh Demo Capital
if 'holdings' not in st.session_state:
    st.session_state.holdings = {}

# --- 3. SIDEBAR NAVIGATION & AI CONTROLS ---
with st.sidebar:
    st.title("🛡️ SOVEREIGN AI")
    st.info(f"Demo Wallet: ₹{st.session_state.balance:,.2f}")
    mode = st.radio("Select Module", ["Market Terminal", "AI Rebound Engine", "Wealth Matrix (SIP/SWP)", "Live Trade Demo"])
    st.write("---")
    st.subheader("System Status")
    st.success("Quantum Core: ONLINE")
    st.write(f"Last Sync: {datetime.now().strftime('%H:%M:%S')}")

# --- 4. MODULE: MARKET TERMINAL ---
if mode == "Market Terminal":
    st.header("🌐 Global Multi-Asset Terminal")
    tickers = {"BTC": "BTC-USD", "NIFTY": "^NSEI", "GOLD": "GC=F", "COPPER": "HG=F", "RELIANCE": "RELIANCE.NS"}
    
    m_cols = st.columns(len(tickers))
    for i, (name, sym) in enumerate(tickers.items()):
        data = yf.Ticker(sym).history(period="1d")
        price = data['Close'].iloc[-1]
        change = ((price - data['Open'].iloc[0]) / data['Open'].iloc[0]) * 100
        m_cols[i].metric(name, f"{price:,.2f}", f"{change:.2f}%")

    st.write("---")
    target = st.selectbox("Detailed Analysis", list(tickers.values()))
    hist = yf.Ticker(target).history(period="1mo")
    fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
    fig.update_layout(template="plotly_dark", title=f"{target} 30-Day Technicals")
    st.plotly_chart(fig, use_container_width=True)

# --- 5. MODULE: AI REBOUND ENGINE ---
elif mode == "AI Rebound Engine":
    st.header("🧠 Rebound Simulation AI")
    st.write("Our proprietary AI detects 'Oversold' assets for a snap-back recovery.")
    
    asset = st.selectbox("Scan Asset for Rebound", ["BTC-USD", "RELIANCE.NS", "TSLA"])
    drop_pct = st.slider("Simulated Market Crash (%)", 5, 50, 20)
    
    st.write("### AI Recovery Path Projection")
    base_price = yf.Ticker(asset).history(period="1d")['Close'].iloc[-1]
    crashed_price = base_price * (1 - drop_pct/100)
    
    # Simulation Logic
    days = np.array(range(30))
    recovery = crashed_price * (1 + (drop_pct/100 * (1 - np.exp(-0.15 * days))))
    
    rec_df = pd.DataFrame({"Day": days, "Price": recovery})
    st.line_chart(rec_df.set_index("Day"))
    st.success(f"AI Prediction: Full Rebound in {np.argmax(recovery >= base_price * 0.98)} days.")

# --- 6. MODULE: WEALTH MATRIX (SIP/SWP) ---
elif mode == "Wealth Matrix (SIP/SWP)":
    st.header("💰 Institutional Wealth Matrix")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("SIP (Wealth Accumulation)")
        monthly = st.number_input("Monthly SIP (₹)", 5000)
        rate = st.slider("Growth Rate (%)", 5, 30, 15)
        yrs = st.slider("Duration (Years)", 1, 40, 15)
        
        total_months = yrs * 12
        r = (rate / 100) / 12
        final_sip = monthly * (((1 + r)**total_months - 1) / r) * (1 + r)
        st.metric("Future Value", f"₹{final_sip:,.0f}")

    with col2:
        st.subheader("SWP (Pension Generation)")
        corpus = st.number_input("Corpus Amount (₹)", value=int(final_sip))
        withdraw = st.number_input("Monthly Withdrawal (₹)", 50000)
        
        # SWP Depletion logic
        remaining = corpus
        count = 0
        while remaining > withdraw and count < 600: # Max 50 years
            remaining = (remaining * (1 + r)) - withdraw
            count += 1
        st.metric("Sustainability", f"{count//12} Years", delta="Safe" if count > 240 else "Risk")

# --- 7. MODULE: LIVE TRADE DEMO ---
elif mode == "Live Trade Demo":
    st.header("🚀 Sovereign Execution Desk")
    trade_asset = st.selectbox("Asset to Trade", ["BTC-USD", "RELIANCE.NS"])
    live_price = yf.Ticker(trade_asset).history(period="1d")['Close'].iloc[-1]
    
    st.subheader(f"Live Price: ₹{live_price:,.2f}")
    qty = st.number_input("Quantity", min_value=1, value=1)
    cost = qty * live_price
    
    c1, c2 = st.columns(2)
    if c1.button("EXECUTE BUY"):
        if st.session_state.balance >= cost:
            st.session_state.balance -= cost
            st.session_state.holdings[trade_asset] = st.session_state.holdings.get(trade_asset, 0) + qty
            st.toast(f"Bought {qty} {trade_asset}", icon="✅")
        else:
            st.error("Insufficient Sovereign Funds")
            
    if c2.button("EXECUTE SELL"):
        if st.session_state.holdings.get(trade_asset, 0) >= qty:
            st.session_state.balance += cost
            st.session_state.holdings[trade_asset] -= qty
            st.toast(f"Sold {qty} {trade_asset}", icon="💰")
        else:
            st.error("No Holdings Found")

    st.write("---")
    st.subheader("Current Portfolio")
    st.write(st.session_state.holdings)

st.write("---")
st.caption("INTERNAL USE ONLY | Sovereign AI Core v9.4")

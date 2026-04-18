import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- 1. SYSTEM CONFIG & STYLING ---
st.set_page_config(page_title="SOVEREIGN ULTIMATE", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: #e0e0e0; }
    div[data-testid="stMetricValue"] { color: #00ffc8; font-family: 'Courier New', monospace; }
    .stTable { border: 1px solid #333; }
    .stButton>button { width: 100%; background: linear-gradient(90deg, #00ffc8, #008f7a); color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VIRTUAL CAPITAL ENGINE ---
if 'balance' not in st.session_state:
    st.session_state.balance = 1000000.0 

# --- 3. HEADER & LIVE TICKERS ---
st.title("⚡ SOVEREIGN ULTIMATE : LIVE FOR THE PEOPLE")
st.caption("Integrated AI Rebound & Trade Execution Terminal")

tickers = {"BTC": "BTC-USD", "NIFTY": "^NSEI", "GOLD": "GC=F", "RELIANCE": "RELIANCE.NS"}
t_cols = st.columns(len(tickers))

for i, (name, sym) in enumerate(tickers.items()):
    t_data = yf.Ticker(sym).history(period="1d")
    t_price = t_data['Close'].iloc[-1]
    t_change = ((t_price - t_data['Open'].iloc[0]) / t_data['Open'].iloc[0]) * 100
    t_cols[i].metric(name, f"{t_price:,.2f}", f"{t_change:.2f}%")

st.write("---")

# --- 4. THE CORE AI MODULES (TABS) ---
tab1, tab2 = st.tabs(["🧠 AI REBOUND & DISTRIBUTION", "🚀 LIVE TRADE EXECUTION"])

with tab1:
    st.subheader("AI Asset Rotation Strategy")
    
    # Logic: Scan for Drawdowns
    scan_results = []
    for name, symbol in tickers.items():
        data = yf.Ticker(symbol).history(period="30d")
        curr = data['Close'].iloc[-1]
        peak = data['High'].max()
        dd = ((peak - curr) / peak) * 100
        scan_results.append({"Asset": name, "Symbol": symbol, "Price": curr, "Drawdown": dd})
    
    df = pd.DataFrame(scan_results)
    total_dd = df["Drawdown"].sum()
    df["AI Weight %"] = (df["Drawdown"] / total_dd) * 100
    df["Recommended (₹)"] = (df["AI Weight %"] / 100) * st.session_state.balance

    c1, c2 = st.columns([2, 1])
    with c1:
        st.table(df.style.format({"Price": "{:,.2f}", "Drawdown": "{:.2f}%", "AI Weight %": "{:.1f}%", "Recommended (₹)": "₹{:,.0f}"}))
    with c2:
        fig = px.pie(df, values='AI Weight %', names='Asset', hole=.4, color_discrete_sequence=px.colors.sequential.Greens_r)
        fig.update_layout(template="plotly_dark", showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Execution Desk")
    col_l, col_r = st.columns([1, 2])
    
    with col_l:
        trade_target = st.selectbox("Select Asset", list(tickers.keys()))
        sym_target = tickers[trade_target]
        live_p = df[df['Asset'] == trade_target]['Price'].values[0]
        
        st.metric("Live Price", f"₹{live_p:,.2f}")
        qty = st.number_input("Quantity", min_value=0.01, value=1.0)
        total_cost = qty * live_p
        
        if st.button("CONFIRM TRADE"):
            if st.session_state.balance >= total_cost:
                st.session_state.balance -= total_cost
                st.success(f"Trade Successful: {qty} {trade_target}")
                st.balloons()
            else:
                st.error("Insufficient Capital")
        
        st.write(f"**Available Wallet:** ₹{st.session_state.balance:,.2f}")

    with col_r:
        # Technical Candlestick Chart
        h_data = yf.Ticker(sym_target).history(period="1mo")
        fig_chart = go.Figure(data=[go.Candlestick(x=h_data.index, open=h_data['Open'], high=h_data['High'], low=h_data['Low'], close=h_data['Close'])])
        fig_chart.update_layout(template="plotly_dark", title=f"{trade_target} Momentum (30D)", margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig_chart, use_container_width=True)

st.write("---")
st.caption("Sovereign Ultimate v11.0 | Integrated Fintech Logic | Jamnagar Hub")

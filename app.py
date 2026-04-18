import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- 1. SYSTEM CONFIG ---
st.set_page_config(page_title="SOVEREIGN ULTIMATE MAX", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: #e0e0e0; }
    div[data-testid="stMetricValue"] { color: #00ffc8; font-size: 1.8rem !important; }
    .stTable { border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

if 'balance' not in st.session_state:
    st.session_state.balance = 1000000.0 

# --- 2. THE GLOBAL ASSET MAP ---
# Adding a massive list of Stocks and Indices
assets = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "NASDAQ 100": "^IXIC",
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "APPLE": "AAPL",
    "TESLA": "TSLA",
    "BITCOIN": "BTC-USD",
    "GOLD": "GC=F",
    "USD/INR": "INR=X"
}

st.title("⚡ SOVEREIGN ULTIMATE : GLOBAL MAX")
st.write("### Multi-Market AI Distribution & Execution")

# --- 3. THE SCROLLING TICKER BAR ---
st.write("---")
t_cols = st.columns(5) # 5 columns to fit more metrics
for i, (name, sym) in enumerate(assets.items()):
    try:
        t_data = yf.Ticker(sym).history(period="1d")
        t_price = t_data['Close'].iloc[-1]
        t_open = t_data['Open'].iloc[0]
        t_change = ((t_price - t_open) / t_open) * 100
        # Distribute metrics across 5 columns
        t_cols[i % 5].metric(name, f"{t_price:,.2f}", f"{t_change:.2f}%")
    except:
        continue

st.write("---")

# --- 4. INTEGRATED AI MODULES ---
tab1, tab2 = st.tabs(["🧠 AI REBOUND SCANNER", "🚀 EXECUTION DESK"])

with tab1:
    st.subheader("Global AI Rebound Distribution")
    
    scan_results = []
    for name, symbol in assets.items():
        try:
            data = yf.Ticker(symbol).history(period="30d")
            curr = data['Close'].iloc[-1]
            peak = data['High'].max()
            dd = ((peak - curr) / peak) * 100
            scan_results.append({"Asset": name, "Symbol": symbol, "Price": curr, "Drawdown": dd})
        except:
            continue
    
    df = pd.DataFrame(scan_results)
    # Filter out assets with no drawdown for clean AI Weighting
    df['Drawdown'] = df['Drawdown'].apply(lambda x: x if x > 0 else 0.1)
    total_dd = df["Drawdown"].sum()
    df["AI Weight %"] = (df["Drawdown"] / total_dd) * 100
    df["Rec. Allocation (₹)"] = (df["AI Weight %"] / 100) * st.session_state.balance

    col_left, col_right = st.columns([3, 2])
    with col_left:
        st.dataframe(df.style.format({
            "Price": "{:,.2f}", 
            "Drawdown": "{:.2f}%", 
            "AI Weight %": "{:.1f}%", 
            "Rec. Allocation (₹)": "₹{:,.0f}"
        }), use_container_width=True)
    
    with col_right:
        fig = px.pie(df, values='AI Weight %', names='Asset', hole=.4, 
                     color_discrete_sequence=px.colors.sequential.Greens_r)
        fig.update_layout(template="plotly_dark", showlegend=True, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("High-Frequency Execution")
    c1, c2 = st.columns([1, 2])
    
    with c1:
        trade_name = st.selectbox("Select Asset to Trade", list(assets.keys()))
        trade_sym = assets[trade_name]
        live_p = df[df['Asset'] == trade_name]['Price'].values[0]
        
        st.metric(f"Current {trade_name}", f"₹{live_p:,.2f}")
        qty = st.number_input("Unit Quantity", min_value=0.01, value=1.0)
        
        if st.button("EXECUTE ORDER"):
            cost = qty * live_p
            if st.session_state.balance >= cost:
                st.session_state.balance -= cost
                st.balloons()
                st.success(f"ORDER FILLED: {qty} units of {trade_name}")
            else:
                st.error("INSUFFICIENT MARGIN")
        
        st.write(f"**Sovereign Balance:** ₹{st.session_state.balance:,.2f}")

    with c2:
        h_data = yf.Ticker(trade_sym).history(period="1mo")
        fig_candlestick = go.Figure(data=[go.Candlestick(
            x=h_data.index, open=h_data['Open'], high=h_data['High'], low=h_data['Low'], close=h_data['Close']
        )])
        fig_candlestick.update_layout(template="plotly_dark", margin=dict(t=0, b=0, l=0, r=0), height=400)
        st.plotly_chart(fig_candlestick, use_container_width=True)

st.write("---")
st.caption("Sovereign Global Max v12.0 | Multi-Exchange Connectivity | AI Core Active")

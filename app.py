import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="SOVEREIGN ULTIMATE", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #010101; color: #ffffff; }
    div[data-testid="stMetricValue"] { color: #00ffc8; font-family: 'Courier New'; font-size: 1.4rem !important; }
    .stTabs [data-baseweb="tab"] { color: #00ffc8; font-weight: bold; }
    .stAlert { background-color: #1a1a1a; border: 1px solid #00ffc8; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ORCHESTRATION ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {"NIFTY 50": 100, "BITCOIN": 0.5, "GOLD": 10, "RELIANCE": 50, "APPLE": 10, "TESLA": 20}

universe = {
    "INDICES": {"NIFTY 50": "^NSEI", "S&P 500": "^GSPC", "NASDAQ": "^IXIC"},
    "EQUITIES": {"RELIANCE": "RELIANCE.NS", "TCS": "TCS.NS", "APPLE": "AAPL", "TESLA": "TSLA"},
    "COMMODITIES": {"GOLD": "GC=F", "SILVER": "SI=F", "COPPER": "HG=F"},
    "CRYPTO": {"BITCOIN": "BTC-USD", "ETHEREUM": "ETH-USD"}
}

@st.cache_data(ttl=300)
def fetch_data():
    all_syms = {name: sym for cat in universe.values() for name, sym in cat.items()}
    data = []
    for name, sym in all_syms.items():
        try:
            ticker = yf.Ticker(sym)
            h = ticker.history(period="1y")
            curr = h['Close'].iloc[-1]
            high_52 = h['High'].max()
            rets = h['Close'].pct_change().dropna()
            cat = next(k for k, v in universe.items() if name in v)
            data.append({"Asset": name, "Price": curr, "History": h, "Category": cat, "Returns": rets, "High52": high_52})
        except: continue
    return pd.DataFrame(data)

df = fetch_data()

# --- 3. GLOBAL PORTFOLIO MATH ---
p_rows = []
total_val = 0
for asset, qty in st.session_state.portfolio.items():
    if asset in df['Asset'].values:
        row = df[df['Asset'] == asset].iloc[0]
        val = row['Price'] * qty
        total_val += val
        p_rows.append({"Asset": asset, "Qty": qty, "Value": val, "Price": row['Price'], "High52": row['High52']})
p_df = pd.DataFrame(p_rows)

# --- 4. DASHBOARD LAYOUT ---
st.title("🏛️ SOVEREIGN ULTIMATE : PY ENGINE")
st.write(f"**Institutional Portfolio Value:** ₹{total_val:,.2f}")

tabs = st.tabs(["📊 ASSETS", "🚀 REBOUND", "🔮 PROJECTION", "🧬 CORRELATION", "🏦 WEALTH", "💼 TAX"])

with tabs[0]: # Portfolio View
    st.plotly_chart(px.pie(p_df, values='Value', names='Asset', hole=0.4, 
                           color_discrete_sequence=px.colors.sequential.Greens_r), use_container_width=True)
    st.dataframe(p_df[['Asset', 'Qty', 'Value']].style.format({"Value": "₹{:,.2f}"}), use_container_width=True)

with tabs[1]: # Rebound Engine + RECONFIRMATION LOGIC
    st.subheader("Automated Recovery Scanner")
    rebs = []
    
    # Check for Tesla Crash specifically for the demo
    tsla_data = p_df[p_df['Asset'] == "TESLA"]
    if not tsla_data.empty:
        tsla_row = tsla_data.iloc[0]
        # Logic: If price is 25% below High
        if tsla_row['Price'] < (tsla_row['High52'] * 0.75):
            st.warning("⚠️ STRATEGY ALERT: Deep Value Detected in TESLA")
            st.write(f"Tesla is currently {((1 - tsla_row['Price']/tsla_row['High52'])*100):.1f}% below 52H High.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirm Reinvestment"):
                    st.balloons()
                    st.success("Trade Executed: 40% Tesla / 60% Nifty BeES")
                    
                    # --- SUCCESS METER ---
                    loss_amount = (tsla_row['High52'] - tsla_row['Price']) * tsla_row['Qty']
                    tax_saved = loss_amount * 0.20 # 2026 STCG Rate
                    
                    st.subheader("📊 Wealth Impact Success Meter")

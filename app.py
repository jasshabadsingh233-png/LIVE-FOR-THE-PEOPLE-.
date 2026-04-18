import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- 1. ZENITH ENGINE CONFIG ---
st.set_page_config(page_title="SOVEREIGN ZENITH | Global Alpha", layout="wide")
from streamlit_autorefresh import st_autorefresh

# Refresh every 30,000 milliseconds (30 seconds)
count = st_autorefresh(interval=30000, limit=100, key="fizzbuzzcounter")
st.markdown("""
    <style>
    .main { background-color: #030303; color: #ffffff; }
    div[data-testid="stMetricValue"] { color: #00ffc8; font-size: 1.2rem !important; font-weight: bold; }
    .stTabs [data-baseweb="tab"] { color: #00ffc8; font-weight: bold; }
    .stDataFrame { border: 1px solid #00ffc8; }
    </style>
    """, unsafe_allow_html=True)

if 'balance' not in st.session_state:
    st.session_state.balance = 10000000.0  # ₹1 Crore Institutional Capital

# --- 2. THE ULTIMATE ASSET UNIVERSE (40+ ASSETS) ---
universe = {
    "🇮🇳 INDIAN INDICES": {
        "NIFTY 50": "^NSEI", "SENSEX": "^BSESN", "BANK NIFTY": "^NSEBANK", 
        "NIFTY IT": "^CNXIT", "NIFTY PHARMA": "^CNXPHARMA", "NIFTY MIDCAP": "^NSEMDCP50"
    },
    "🇺🇸 US & GLOBAL": {
        "S&P 500": "^GSPC", "NASDAQ 100": "^IXIC", "DOW JONES": "^DJI",
        "FTSE 100 (UK)": "^FTSE", "DAX (GER)": "^GDAXI", "NIKKEI 225 (JPN)": "^N225"
    },
    "🏢 BIG TECH & GROWTH": {
        "RELIANCE": "RELIANCE.NS", "TCS": "TCS.NS", "HDFC BANK": "HDFCBANK.NS",
        "INFOSYS": "INFY.NS", "APPLE": "AAPL", "TESLA": "TSLA", "NVIDIA": "NVDA", 
        "GOOGLE": "GOOGL", "MICROSOFT": "MSFT", "AMAZON": "AMZN"
    },
    "🧱 COMMODITIES": {
        "GOLD": "GC=F", "SILVER": "SI=F", "CRUDE OIL": "CL=F", 
        "NATURAL GAS": "NG=F", "COPPER": "HG=F", "ALUMINUM": "ALI=F"
    },
    "📉 DEBT & LIQUID": {
        "LIQUID ETF": "LIQUIDBEES.NS", "US 10Y BOND": "^TNX", 
        "GOLD ETF": "GOLDBEES.NS", "US 2Y BOND": "^IRX"
    },
    "₿ CRYPTO": {
        "BITCOIN": "BTC-USD", "ETHEREUM": "ETH-USD", "SOLANA": "SOL-USD", "CARDANO": "ADA-USD"
    },
    "💱 FOREX": {
        "USD/INR": "INR=X", "EUR/USD": "EURUSD=X", "GBP/INR": "GBPINR=X", "JPY/INR": "JPYINR=X"
    }
}

# --- 3. DATA FETCHING (ZENITH OPTIMIZED) ---
@st.cache_data(ttl=300) # Cache for 5 mins to save processing power
def get_zenith_data():
    scan_data = []
    all_syms = {name: sym for cat in universe.values() for name, sym in cat.items()}
    for name, sym in all_syms.items():
        try:
            ticker = yf.Ticker(sym)
            hist = ticker.history(period="30d")
            if not hist.empty:
                curr = hist['Close'].iloc[-1]
                peak = hist['High'].max()
                dd = ((peak - curr) / peak) * 100
                # Find Category
                cat_name = "Other"
                for c, items in universe.items():
                    if name in items: cat_name = c
                scan_data.append({"Category": cat_name, "Asset": name, "Price": curr, "Drawdown": dd, "Symbol": sym})
        except: continue
    return pd.DataFrame(scan_data)

master_df = get_zenith_data()

# --- 4. HEADER ---
st.title("🌌 SOVEREIGN ZENITH : MAXIMUM CAPACITY")
st.write(f"**Total Assets Monitored:** {len(master_df)} | **Vault Balance:** ₹{st.session_state.balance:,.2f}")

# --- 5. ZENITH TABS ---
t1, t2, t3 = st.tabs(["🛸 ALPHA RADAR", "⚖️ REBOUND ALLOCATOR", "🕹️ TERMINAL EXECUTION"])

with t1:
    st.subheader("Global Market Alpha Map")
    # Tree Map of EVERYTHING
    fig_tree = px.treemap(master_df, path=['Category', 'Asset'], values='Drawdown',
                          color='Drawdown', color_continuous_scale='RdYlGn_r',
                          hover_data=['Price'])
    fig_tree.update_layout(template="plotly_dark", margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig_tree, use_container_width=True)

with t2:
    st.subheader("Sovereign AI Rotation Matrix")
    # Calculate Allocation
    master_df['AI Weight %'] = (master_df['Drawdown'] / master_df['Drawdown'].sum()) * 100
    master_df['Suggested (₹)'] = (master_df['AI Weight %'] / 100) * st.session_state.balance
    
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.dataframe(master_df.drop(columns=['Symbol']).sort_values('Drawdown', ascending=False), use_container_width=True)
    with col_r:
        fig_sun = px.sunburst(master_df, path=['Category', 'Asset'], values='AI Weight %', 
                              color='AI Weight %', color_continuous_scale='Greens')
        fig_sun.update_layout(template="plotly_dark", margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_sun, use_container_width=True)

with t3:
    st.subheader("Multi-Asset Execution Desk")
    cl, cr = st.columns([1, 2])
    with cl:
        target_name = st.selectbox("Select Asset to Buy/Sell", master_df['Asset'].tolist())
        target_info = master_df[master_df['Asset'] == target_name].iloc[0]
        st.metric(f"Spot: {target_name}", f"{target_info['Price']:,.2f}")
        
        amt = st.number_input("Transaction Units", min_value=0.001, value=1.0)
        if st.button("EXECUTE ORDER"):
            cost = amt * target_info['Price']
            if st.session_state.balance >= cost:
                st.session_state.balance -= cost
                st.balloons()
                st.success(f"FILLED: {amt} units of {target_name}")
            else: st.error("INSUFFICIENT FUNDS")
            
    with cr:
        h_data = yf.Ticker(target_info['Symbol']).history(period="3mo")
        fig_cand = go.Figure(data=[go.Candlestick(x=h_data.index, open=h_data['Open'], 
                             high=h_data['High'], low=h_data['Low'], close=h_data['Close'])])
        fig_cand.update_layout(template="plotly_dark", height=400, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_cand, use_container_width=True)

st.write("---")
st.caption(f"SOVEREIGN ZENITH v15.0 | Last Data Refresh: {datetime.now().strftime('%H:%M:%S')} | Jamnagar AI Hub")

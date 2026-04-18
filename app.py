import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- 1. SYSTEM CONFIG ---
st.set_page_config(page_title="SOVEREIGN ULTIMATE", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #010101; color: #ffffff; }
    div[data-testid="stMetricValue"] { color: #00ffc8; font-family: 'Courier New'; font-size: 1.4rem !important; }
    .stTabs [data-baseweb="tab"] { color: #00ffc8; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# Persistent Session Data
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {"NIFTY 50": 100, "BITCOIN": 0.5, "GOLD": 10, "RELIANCE": 50, "APPLE": 10}
if 'balance' not in st.session_state:
    st.session_state.balance = 10000000.0

# --- 2. ASSET UNIVERSE ---
universe = {
    "INDICES": {"NIFTY 50": "^NSEI", "S&P 500": "^GSPC", "NASDAQ": "^IXIC"},
    "EQUITIES": {"RELIANCE": "RELIANCE.NS", "TCS": "TCS.NS", "APPLE": "AAPL", "TESLA": "TSLA"},
    "COMMODITIES": {"GOLD": "GC=F", "SILVER": "SI=F", "COPPER": "HG=F"},
    "CRYPTO": {"BITCOIN": "BTC-USD", "ETHEREUM": "ETH-USD"}
}

@st.cache_data(ttl=300)
def get_ultimate_data():
    all_syms = {name: sym for cat in universe.values() for name, sym in cat.items()}
    master_list = []
    for name, sym in all_syms.items():
        try:
            ticker = yf.Ticker(sym)
            h = ticker.history(period="1y")
            curr = h['Close'].iloc[-1]
            returns = h['Close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)
            sharpe = (returns.mean() * 252) / (volatility) if volatility != 0 else 0
            cat = next(k for k, v in universe.items() if name in v)
            master_list.append({
                "Asset": name, "Price": curr, "Symbol": sym, "History": h, 
                "Category": cat, "Volatility": volatility, "Sharpe": sharpe, "Returns": returns
            })
        except: continue
    return pd.DataFrame(master_list)

master_df = get_ultimate_data()

# --- 3. GLOBAL PORTFOLIO CALCULATION (CRITICAL FIX) ---
# We calculate this OUTSIDE of the tabs so Wealth Architect and Tax Harvest can see it.
global_port_data = []
current_total_val = 0
for asset, qty in st.session_state.portfolio.items():
    try:
        row = master_df[master_df['Asset'] == asset].iloc[0]
        val = row['Price'] * qty
        current_total_val += val
        global_port_data.append({"Asset": asset, "Category": row['Category'], "Value": val, "Qty": qty, "Price": row['Price']})
    except: continue
g_pdf = pd.DataFrame(global_port_data)

# --- 4. UI COMMAND CENTER ---
st.title("🏛️ SOVEREIGN ULTIMATE : QUANTITATIVE TERMINAL")
st.write(f"**Live Portfolio Value:** ₹{current_total_val:,.2f} | **Cash:** ₹{st.session_state.balance:,.2f}")

# --- 5. THE MASTER TABS ---
tabs = st.tabs(["📊 PORTFOLIO", "🚀 REBOUND ENGINE", "🔮 MONTE CARLO", "🧬 RISK DYNAMICS", "🏦 WEALTH ARCHITECT", "💼 TAX HARVEST"])

with tabs[0]:
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.subheader("Holdings Distribution")
        st.dataframe(g_pdf[['Asset', 'Category', 'Qty', 'Value']].style.format({"Value": "₹{:,.2f}"}), use_container_width=True)
    with col_r:
        st.subheader("Sector Exposure")
        fig_sec = px.sunburst(g_pdf, path=['Category', 'Asset'], values='Value', color='Value', color_continuous_scale='Greens')
        fig_sec.update_layout(template="plotly_dark", margin=dict(t=0,b=0,l=0,r=0))
        st.plotly_chart(fig_sec, use_container_width=True)

with tabs[1]:
    st.subheader("Mean Reversion Intelligence")
    rebound_list = []
    for _, row in master_df.iterrows():
        peak = row['History']['High'].max()
        dd = ((peak - row['Price']) / peak) * 100
        req_gain = ((peak / row['Price']) - 1) * 100
        rebound_list.append({"Asset": row['Asset'], "Drawdown %": dd, "Req. Gain %": req_gain, "Sharpe": row['Sharpe']})
    reb_df = pd.DataFrame(rebound_list).sort_values("Drawdown %", ascending=False)
    st.plotly_chart(px.bar(reb_df, x='Asset', y='Req. Gain %', color='Req. Gain %', color_continuous_scale='Reds'), use_container_width=True)

with tabs[2]:
    st.subheader("Probabilistic Future Simulation")
    target_sim = st.selectbox("Select Asset for 252-Day Projection", master_df['Asset'].tolist())
    s_row = master_df[master_df['Asset'] == target_sim].iloc[0]
    mu, sigma, S0 = s_row['Returns'].mean(), s_row['Returns'].std(), s_row['Price']
    fig_mc = go.Figure()
    for i in range(20):
        prices = [S0]
        for d in range(252):
            prices.append(prices[-1] * np.exp((mu - 0.5 * sigma**2) + sigma * np.random.normal()))
        fig_mc.add_trace(go.Scatter(y=prices, mode='lines', line=dict(width=1), opacity=0.3, showlegend=False))
    fig_mc.update_layout(template="plotly_dark", title=f"Monte Carlo Paths for {target_sim}")
    st.plotly_chart(fig_mc, use_container_width=True)

with tabs[3]:
    st.subheader("Genetic Asset Correlation")
    prices_df = pd.concat([row['History']['Close'].rename(row['Asset']) for _, row in master_df.iterrows()], axis=1).corr()
    st.plotly_chart(px.imshow(prices_df, text_auto=True, color_continuous_scale='RdBu_r'), use_container_width=True)

with tabs[4]:
    st.subheader("🏦 Wealth Architect")
    c1, c2 = st.columns(2)
    with c1:
        sal = st.number_input("Monthly Salary (₹)", value=100000, step=5000)
        risk_lvl = st.select_slider("Risk Strategy", options=["Safe", "Balanced", "Sovereign"])
        ratio = 0.2 if risk_lvl == "Safe" else 0.3 if risk_lvl == "Balanced" else 0.45
        monthly_sip = sal * ratio
        st.metric("Recommended SIP", f"₹{monthly_sip:,.0f}")
    with c2:
        goal = st.number_input("Target

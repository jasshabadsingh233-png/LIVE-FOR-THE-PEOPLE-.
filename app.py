import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIG & SYSTEM OVERRIDE ---
st.set_page_config(page_title="SOVEREIGN ULTIMATE", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #010101; color: #ffffff; }
    div[data-testid="stMetricValue"] { color: #00ffc8; font-family: 'Courier New'; font-size: 1.4rem !important; }
    .stTabs [data-baseweb="tab"] { color: #00ffc8; font-weight: bold; }
    .css-1kyx7g3 { background-color: #111; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {"NIFTY 50": 100, "BITCOIN": 0.5, "GOLD": 10, "RELIANCE": 50, "APPLE": 10}
if 'balance' not in st.session_state:
    st.session_state.balance = 10000000.0

# --- 2. THE TOTAL MARKET UNIVERSE ---
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
            volatility = returns.std() * np.sqrt(252) # Annualized Vol
            sharpe = (returns.mean() * 252) / (volatility) if volatility != 0 else 0
            
            # Find Category
            cat = next(k for k, v in universe.items() if name in v)
            master_list.append({
                "Asset": name, "Price": curr, "Symbol": sym, "History": h, 
                "Category": cat, "Volatility": volatility, "Sharpe": sharpe, "Returns": returns
            })
        except: continue
    return pd.DataFrame(master_list)

master_df = get_ultimate_data()

# --- 3. THE COMMAND CENTER ---
st.title("🏛️ SOVEREIGN ULTIMATE : QUANTITATIVE TERMINAL")
st.write(f"**Engine Status:** ACTIVE | **Global Connectivity:** 100% | **Portfolio Liquidity:** ₹{st.session_state.balance:,.2f}")

# --- 4. THE ULTIMATE TABS ---
tabs = st.tabs(["📊 PORTFOLIO", "🚀 REBOUND ENGINE", "🔮 MONTE CARLO", "🧬 RISK DYNAMICS", "🏦 WEALTH ARCHITECT", "💼 TAX HARVEST"])

# TAB 1: PORTFOLIO & SECTORAL CONCENTRATION
with tabs[0]:
    port_data = []
    total_val = 0
    for asset, qty in st.session_state.portfolio.items():
        row = master_df[master_df['Asset'] == asset].iloc[0]
        val = row['Price'] * qty
        total_val += val
        port_data.append({"Asset": asset, "Category": row['Category'], "Value": val, "Qty": qty})
    
    p_df = pd.DataFrame(port_data)
    
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.subheader("Holdings Distribution")
        st.dataframe(p_df.style.format({"Value": "₹{:,.2f}"}), use_container_width=True)
        st.metric("Total Vault Value", f"₹{total_val:,.2f}", f"{((total_val/10000000)-1)*100:.2f}%")
    with col_r:
        st.subheader("Sector Exposure")
        fig_sec = px.sunburst(p_df, path=['Category', 'Asset'], values='Value', color='Value', color_continuous_scale='Greens')
        fig_sec.update_layout(template="plotly_dark", margin=dict(t=0,b=0,l=0,r=0))
        st.plotly_chart(fig_sec, use_container_width=True)

# TAB 2: ADVANCED REBOUND ENGINE
with tabs[1]:
    st.subheader("Mean Reversion Intelligence")
    rebound_list = []
    for _, row in master_df.iterrows():
        peak = row['History']['High'].max()
        dd = ((peak - row['Price']) / peak) * 100
        req_gain = ((peak / row['Price']) - 1) * 100
        rebound_list.append({"Asset": row['Asset'], "Drawdown %": dd, "Req. Gain %": req_gain, "Sharpe": row['Sharpe']})
    
    reb_df = pd.DataFrame(rebound_list).sort_values("Drawdown %", ascending=False)
    
    c_reb1, c_reb2 = st.columns(2)
    with c_reb1:
        st.write("**Recovery Gradient (Bigger = Faster Snapback)**")
        st.plotly_chart(px.bar(reb_df, x='Asset', y='Req. Gain %', color='Req. Gain %', color_continuous_scale='Reds'), use_container_width=True)
    with c_reb2:
        st.write("**Risk-Adjusted Potential (Sharpe Ratio)**")
        st.plotly_chart(px.scatter(reb_df, x='Drawdown %', y='Sharpe', text='Asset', size='Req. Gain %', color='Asset'), use_container_width=True)

# TAB 3: MONTE CARLO PREDICTOR
with tabs[2]:
    st.subheader("Probabilistic Future Simulation")
    target_sim = st.selectbox("Select Asset for 252-Day Projection", master_df['Asset'].tolist())
    sim_row = master_df[master_df['Asset'] == target_sim].iloc[0]
    
    # Monte Carlo Logic
    mu = sim_row['Returns'].mean()
    sigma = sim_row['Returns'].std()
    S0 = sim_row['Price']
    
    simulations = 50
    days = 252
    fig_mc = go.Figure()
    
    for i in range(simulations):
        prices = [S0]
        for d in range(days):
            prices.append(prices[-1] * np.exp((mu - 0.5 * sigma**2) + sigma * np.random.normal()))
        fig_mc.add_trace(go.Scatter(y=prices, mode='lines', line=dict(width=1), opacity=0.3, showlegend=False))
    
    fig_mc.update_layout(template="plotly_dark", title=f"50 Potential Price Paths for {target_sim}", xaxis_title="Trading Days", yaxis_title="Price")
    st.plotly_chart(fig_mc, use_container_width=True)

# TAB 4: RISK CORRELATION
with tabs[3]:
    st.subheader("Genetic Asset Correlation")
    prices_df = pd.concat([row['History']['Close'].rename(row['Asset']) for _, row in master_df.iterrows()], axis=1).corr()
    st.plotly_chart(px.imshow(prices_df, text_auto=True, color_continuous_scale='RdBu_r'), use_container_width=True)

# TAB 5: PERSONAL WEALTH ARCHITECT
with tabs[4]:
    st_col, end_col = st.columns(2)
    with st_col:
        salary = st.number_input("Monthly Salary (₹)", value=150000

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- 1. THE SINGULARITY CONFIG ---
st.set_page_config(page_title="SOVEREIGN SINGULARITY", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #020202; color: #ffffff; }
    div[data-testid="stMetricValue"] { color: #00ffc8; font-family: 'Courier New'; font-weight: bold; }
    .stTabs [data-baseweb="tab"] { color: #00ffc8; font-size: 1.1rem; font-weight: bold; }
    .stDataFrame { border: 1px solid #00ffc8; }
    </style>
    """, unsafe_allow_html=True)

if 'balance' not in st.session_state:
    st.session_state.balance = 10000000.0 

# --- 2. GLOBAL ASSET UNIVERSE ---
universe = {
    "🇮🇳 INDICES": {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "NIFTY IT": "^CNXIT"},
    "🌍 GLOBAL": {"S&P 500": "^GSPC", "NASDAQ": "^IXIC", "GOLD": "GC=F"},
    "🛡️ DEBT/LIQUID": {"LIQUID ETF": "LIQUIDBEES.NS", "US 10Y BOND": "^TNX"},
    "₿ CRYPTO": {"BITCOIN": "BTC-USD", "ETHEREUM": "ETH-USD"},
    "⚙️ INDUSTRIAL": {"BRASS PROXY (COPPER)": "HG=F", "STEEL PROXY": "STEE-F"}
}

# --- 3. DATA ENGINE ---
@st.cache_data(ttl=600)
def fetch_master_data():
    data_list = []
    all_syms = {name: sym for cat in universe.values() for name, sym in cat.items()}
    for name, sym in all_syms.items():
        try:
            h = yf.Ticker(sym).history(period="60d")
            curr = h['Close'].iloc[-1]
            peak = h['High'].max()
            dd = ((peak - curr) / peak) * 100
            cat = next(k for k, v in universe.items() if name in v)
            data_list.append({"Category": cat, "Asset": name, "Price": curr, "Drawdown": dd, "Symbol": sym, "History": h['Close']})
        except: continue
    return pd.DataFrame(data_list)

df = fetch_master_data()

# --- 4. HEADER ---
st.title("🏛️ SOVEREIGN SINGULARITY")
st.write(f"**Institutional Intelligence Hub** | Global Status: **MAX CAPACITY** | Liquidity: ₹{st.session_state.balance:,.2f}")

# --- 5. THE MASTER TABS ---
t1, t2, t3, t4, t5, t6 = st.tabs([
    "🛰️ ALPHA RADAR", "⚖️ REBOUND MATRIX", "📈 ADAPTIVE SIP", 
    "🧬 RISK CORRELATION", "🕹️ EXECUTION", "🏦 PERSONAL WEALTH"
])

with t1:
    st.subheader("Global Market Alpha Map")
    fig_tree = px.treemap(df, path=['Category', 'Asset'], values='Drawdown', color='Drawdown',
                          color_continuous_scale='RdYlGn_r')
    st.plotly_chart(fig_tree, use_container_width=True)

with t2:
    st.subheader("AI Rebound Allocation")
    df['Weight %'] = (df['Drawdown'] / df['Drawdown'].sum()) * 100
    df['Rec. Allocation'] = (df['Weight %'] / 100) * st.session_state.balance
    st.dataframe(df[['Category', 'Asset', 'Price', 'Drawdown', 'Rec. Allocation']].sort_values('Drawdown', ascending=False), use_container_width=True)
    fig_sun = px.sunburst(df, path=['Category', 'Asset'], values='Weight %', color='Weight %', color_continuous_scale='Greens')
    st.plotly_chart(fig_sun, use_container_width=True)

with t3:
    st.subheader("Adaptive SIP Engine")
    base_sip = st.number_input("Base Monthly SIP (₹)", value=25000)
    sip_results = [{"Asset": r['Asset'], "Base": base_sip, "AI Adj. SIP": base_sip * (1 + (r['Drawdown']/10))} for i, r in df.iterrows()]
    st.table(pd.DataFrame(sip_results))

with t4:
    st.subheader("🧬 Diversification Check")
    corr_data = pd.concat([row['History'].rename(row['Asset']) for i, row in df.iterrows()], axis=1).corr()
    st.plotly_chart(px.imshow(corr_data, text_auto=True, color_continuous_scale='Viridis'), use_container_width=True)

with t5:
    st.subheader("Execution Desk")
    cl, cr = st.columns([1, 2])
    with cl:
        target = st.selectbox("Asset", df['Asset'].tolist())
        t_info = df[df['Asset'] == target].iloc[0]
        st.metric(f"Live Price", f"₹{t_info['Price']:,.2f}")
        if st.button("EXECUTE"): st.balloons()
    with cr:
        h_data = yf.Ticker(t_info['Symbol']).history(period="3mo")
        fig_c = go.Figure(data=[go.Candlestick(x=h_data.index, open=h_data['Open'], high=h_data['High'], low=h_data['Low'], close=h_data['Close'])])
        fig_c.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_c, use_container_width=True)

with t6:
    st.subheader("🏦 Personal Wealth Architect")
    sal_col, bud_col = st.columns([1, 2])
    with sal_col:
        salary = st.number_input("Monthly Salary (₹)", value=100000)
        risk = st.select_slider("Risk Mode", options=["Safe", "Moderate", "Aggressive"])
        inv_ratio = 0.20 if risk == "Safe" else 0.35 if risk == "Aggressive" else 0.25
        monthly_inv = salary * inv_ratio
        st.metric("Suggested Monthly Investment", f"₹{monthly_inv:,.0f}")
    with bud_col:
        budget_df = pd.DataFrame({"Cat": ["Expenses", "Lifestyle", "Investment"], "Val": [salary*0.5, salary*(0.5-inv_ratio), monthly_inv]})
        st.plotly_chart(px.pie(budget_df, values='Val', names='Cat', hole=0.4, color_discrete_sequence=['#333', '#555', '#00ffc8']), use_container_width=True)
    
    # Time to 1 Crore Goal
    months = 0; val = 0
    while val < 10000000 and months < 480:
        val = (val + monthly_inv) * (1 + (0.15/12)); months += 1
    st.success(f"With an Aggressive Alpha strategy, you reach ₹1 Crore in {months/12:.1f} years.")

st.write("---")
st.caption(f"SOVEREIGN SINGULARITY v16.0 | Final Build | Jamnagar Hub")

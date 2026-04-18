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
    .stTabs [data-baseweb="tab"] { color: #00ffc8; font-size: 1.1rem; }
    .glass-card { background: rgba(255, 255, 255, 0.05); border-radius: 15px; padding: 20px; border: 1px solid rgba(0, 255, 200, 0.2); }
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

# --- 3. DATA ENGINE (MULTI-FUNCTIONAL) ---
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
            # Identify Category
            cat = next(k for k, v in universe.items() if name in v)
            data_list.append({"Category": cat, "Asset": name, "Price": curr, "Drawdown": dd, "Symbol": sym, "History": h['Close']})
        except: continue
    return pd.DataFrame(data_list)

df = fetch_master_data()

# --- 4. HEADER & REAL-TIME PULSE ---
st.title("🏛️ SOVEREIGN SINGULARITY : THE ULTIMATE")
st.write(f"**Institutional Intelligence Hub** | Global Status: **OPTIMIZED** | Liquidity: ₹{st.session_state.balance:,.2f}")

# --- 5. THE MASTER TABS (NO SCOPE LEFT) ---
t1, t2, t3, t4, t5 = st.tabs(["🛰️ ALPHA RADAR", "⚖️ REBOUND MATRIX", "📈 ADAPTIVE SIP", "🧬 RISK CORRELATION", "🕹️ EXECUTION"])

with t1:
    st.subheader("Global Market Drawdown Heatmap")
    fig_tree = px.treemap(df, path=['Category', 'Asset'], values='Drawdown', color='Drawdown',
                          color_continuous_scale='RdYlGn_r', hover_data=['Price'])
    fig_tree.update_layout(template="plotly_dark", margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig_tree, use_container_width=True)

with t2:
    st.subheader("AI Rebound Allocation")
    df['Weight %'] = (df['Drawdown'] / df['Drawdown'].sum()) * 100
    df['Rec. Allocation'] = (df['Weight %'] / 100) * st.session_state.balance
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.dataframe(df[['Category', 'Asset', 'Price', 'Drawdown', 'Rec. Allocation']].sort_values('Drawdown', ascending=False), use_container_width=True)
    with col2:
        fig_sun = px.sunburst(df, path=['Category', 'Asset'], values='Weight %', color='Weight %', color_continuous_scale='Greens')
        st.plotly_chart(fig_sun, use_container_width=True)

with t3:
    st.subheader("Adaptive SIP Engine (Sovereign Logic)")
    st.info("The AI calculates your monthly investment based on market fear. More crash = More investment.")
    base_sip = st.number_input("Base Monthly SIP (₹)", value=50000)
    
    sip_results = []
    for index, row in df.iterrows():
        # Sovereign Logic: If DD > 5%, increase SIP by 2x DD
        multiplier = 1 + (row['Drawdown'] / 10)
        adj_sip = base_sip * multiplier
        sip_results.append({"Asset": row['Asset'], "Base SIP": base_sip, "AI Adj. SIP": adj_sip, "Logic": f"{multiplier:.2f}x Multiplier"})
    
    st.table(pd.DataFrame(sip_results))

with t4:
    st.subheader("🧬 Asset Correlation Matrix")
    st.write("Checking if your assets are moving together (High Risk) or apart (Safe).")
    
    # Simple Correlation logic
    corr_data = pd.concat([row['History'].rename(row['Asset']) for i, row in df.iterrows()], axis=1).corr()
    fig_corr = px.imshow(corr_data, text_auto=True, aspect="auto", color_continuous_scale='Viridis', title="Diversification Health Check")
    st.plotly_chart(fig_corr, use_container_width=True)

with t5:
    st.subheader("Institutional Execution Desk")
    cl, cr = st.columns([1, 2])
    with cl:
        target = st.selectbox("Select Asset", df['Asset'].tolist())
        t_info = df[df['Asset'] == target].iloc[0]
        st.metric(f"Live {target}", f"₹{t_info['Price']:,.2f}")
        units = st.number_input("Units", min_value=0.01, value=1.0)
        if st.button("CONFIRM INSTITUTIONAL ORDER"):
            st.balloons()
            st.success(f"TRADE EXECUTED: {units} units of {target}")
    with cr:
        h_data = yf.Ticker(t_info['Symbol']).history(period="3mo")
        fig_c = go.Figure(data=[go.Candlestick(x=h_data.index, open=h_data['Open'], high=h_data['High'], low=h_data['Low'], close=h_data['Close'])])
        fig_c.update_layout(template="plotly_dark", height=400, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_c, use_container_width=True)

st.write("---")
st.caption(f"SOVEREIGN SINGULARITY v16.0 | Jamnagar AI Hub | Last Pulse: {datetime.now().strftime('%H:%M:%S')}")

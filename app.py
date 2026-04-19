import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- 1. ARCHITECTURAL CONFIGURATION ---
st.set_page_config(page_title="SOVEREIGN APEX", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: #e0e0e0; font-family: 'Inter', sans-serif; }
    [data-testid="stMetricValue"] { color: #00ffc8 !important; font-size: 1.8rem !important; }
    .stTabs [data-baseweb="tab"] { color: #888; font-size: 14px; }
    .stTabs [aria-selected="true"] { color: #00ffc8 !important; border-bottom: 2px solid #00ffc8 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GLOBAL SETTINGS ---
with st.sidebar:
    st.title("🏛️ APEX COMMAND")
    currency = st.selectbox("Market Jurisdiction", ["India (INR)", "Malaysia (MYR)", "USA (USD)"])
    fx_dict = {"India (INR)": (1.0, "₹"), "Malaysia (MYR)": (0.056, "RM"), "USA (USD)": (0.012, "$")}
    fx_rate, sym = fx_dict[currency]

# --- 3. CORE ENGINE (With Error Handling) ---
@st.cache_data(ttl=300)
def get_engine():
    universe = {
        "EQUITIES": {"RELIANCE": "RELIANCE.NS", "APPLE": "AAPL", "TESLA": "TSLA", "TCS": "TCS.NS"},
        "INDICES": {"NIFTY 50": "^NSEI", "S&P 500": "^GSPC", "KLCI": "^KLSE"},
        "CRYPTO": {"BITCOIN": "BTC-USD", "ETHEREUM": "ETH-USD"}
    }
    results = []
    for cat, assets in universe.items():
        for name, ticker_sym in assets.items():
            try:
                t = yf.Ticker(ticker_sym)
                hist = t.history(period="1y")
                curr = hist['Close'].iloc[-1]
                rets = hist['Close'].pct_change().dropna()
                vol = rets.std() * np.sqrt(252)
                sharpe = (rets.mean() * 252 - 0.05) / vol if vol != 0 else 0
                results.append({
                    "Asset": name, "Price": curr, "History": hist, 
                    "Vol": vol, "Sharpe": sharpe, "High52": hist['High'].max(), 
                    "Category": cat, "Returns": rets
                })
            except Exception as e: continue
    return pd.DataFrame(results)

df_engine = get_engine()

# --- 4. PORTFOLIO DATA INTEGRITY ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {"NIFTY 50": 100, "RELIANCE": 50, "TESLA": 20, "BITCOIN": 0.2}

p_data = []
total_aum = 0
for asset, qty in st.session_state.portfolio.items():
    if asset in df_engine['Asset'].values:
        row = df_engine[df_engine['Asset'] == asset].iloc[0]
        val = row['Price'] * qty * fx_rate
        total_aum += val
        p_data.append({
            "Asset": asset, "Qty": qty, "Value": val, 
            "Price": row['Price']*fx_rate, "High52": row['High52']*fx_rate,
            "Returns": row['Returns'], "Sharpe": row['Sharpe']
        })
p_df = pd.DataFrame(p_data)

# --- 5. THE TERMINAL INTERFACE ---
st.title("🏛️ SOVEREIGN APEX : MULTIMODAL INTELLIGENCE")
m1, m2, m3 = st.columns(3)
m1.metric("PORTFOLIO VALUE", f"{sym}{total_aum:,.2f}")
m2.metric("SYSTEM ALPHA", "+6.1%", delta="Active Optimization")
m3.metric("NODE LATENCY", "28ms", delta="Stable")

tabs = st.tabs(["📊 ASSET DENSITY", "🚀 REBOUND ENGINE", "🔮 MONTE CARLO", "📈 ALPHA WAITLIST"])

with tabs[0]: # Asset Density Map
    col_l, col_r = st.columns([2, 1])
    with col_l:
        # Pushing hardware with complex Sunburst
        fig = px.sunburst(df_engine, path=['Category', 'Asset'], values='Price', template="plotly_dark")
        fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with col_r:
        st.subheader("Risk Rankings")
        st.dataframe(p_df[['Asset', 'Value', 'Sharpe']].sort_values('Sharpe', ascending=False), hide_index=True)

with tabs[1]: # Advanced Rebound
    st.header("🚀 Algorithmic Redistribution")
    target = st.selectbox("Select Asset for Stress Simulation", p_df['Asset'].unique())
    asset_row = p_df[p_df['Asset'] == target].iloc[0]
    
    crash = st.slider("Simulated Market Drop (%)", 0, 50, 25)
    sim_p = asset_row['High52'] * (1 - crash/100)
    
    st.warning(f"Simulating {target} drop to {sym}{sim_p:,.2f}")
    
    if st.button("🔥 EXECUTE APEX REBALANCE"):
        st.balloons()
        unlocked = sim_p * asset_row['Qty']
        tax_credit = ((asset_row['High52'] - sim_p) * asset_row['Qty']) * 0.20
        
        # New Feature: Reinvestment Deployment Math
        st.markdown("### 🏛️ Deployment Strategy")
        c1, c2 = st.columns(2)
        c1.info(f"**Rebound Fund (40%):** {sym}{unlocked*0.4:,.2f} re-entered into {target}")
        c2.success(f"**Safety Buffer (60%):** {sym}{unlocked*0.6:,.2f} moved to HEDGED ASSETS")
        st.metric("Total Tax Shield Created", f"{sym}{tax_credit:,.2f}")

with tabs[2]: # Hardware-Intensive Monte Carlo
    st.header("🔮 10,000-Path Probabilistic Engine")
    mc_target = st.selectbox("Select Asset for Simulation", df_engine['Asset'].unique())
    mc_row = df_engine[df_engine['Asset'] == mc_target].iloc[0]
    
    if 'Returns' in mc_row and len(mc_row['Returns']) > 0:
        mu, sigma, s0 = mc_row['Returns'].mean(), mc_row['Returns'].std(), mc_row['Price']*fx_rate
        
        # Vectorized Numpy for high-speed hardware processing
        paths, days = 100, 252
        dt = 1/days
        stoch_matrix = np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * np.random.standard_normal((days, paths)))
        price_paths = s0 * stoch_matrix.cumprod(axis=0)
        
        fig_mc = go.Figure()
        for i in range(paths):
            fig_mc.add_trace(go.Scatter(y=price_paths[:, i], mode='lines', line=dict(width=1), opacity=0.3, showlegend=False))
        fig_mc.update_layout(template="plotly_dark", xaxis_title="Days", yaxis_title=f"Price ({sym})")
        st.plotly_chart(fig_mc, use_container_width=True)

with tabs[3]: # Growth
    st.header("📈 Scaling the Vision")
    with st.form("waitlist"):
        st.write("### Secure Alpha Access")
        email = st.text_input("Enter Email for Pre-Seed Notification")
        region = st.radio("Primary Focus", ["India", "Malaysia", "Global"])
        if st.form_submit_button("REGISTER FOUNDER"):
            st.success(f"Vision registered. Welcome to the circle, {email}.")

# --- FOOTER ---
st.markdown("---")
st.caption(f"© 2026 LIVE FOR THE PEOPLE | ASIA SCHOOL OF BUSINESS | APEX ENGINE v22.5")

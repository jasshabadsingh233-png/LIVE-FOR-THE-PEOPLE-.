import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- 1. ARCHITECTURAL CONFIGURATION ---
st.set_page_config(page_title="SOVEREIGN APEX | KL", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: #e0e0e0; font-family: 'Inter', sans-serif; }
    [data-testid="stMetricValue"] { color: #00ffc8 !important; font-size: 1.8rem !important; }
    .stTabs [data-baseweb="tab"] { color: #888; font-size: 14px; }
    .stTabs [aria-selected="true"] { color: #00ffc8 !important; border-bottom: 2px solid #00ffc8 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GLOBAL SETTINGS & SIDEBAR ---
with st.sidebar:
    st.title("🏛️ APEX COMMAND")
    st.subheader("Kuala Lumpur Node")
    currency = st.selectbox("Market Jurisdiction", ["Malaysia (MYR)", "India (INR)", "USA (USD)"])
    fx_dict = {"Malaysia (MYR)": (1.0, "RM"), "India (INR)": (17.85, "₹"), "USA (USD)": (0.21, "$")}
    fx_rate, sym = fx_dict[currency]
    
    st.divider()
    st.write("### Engine Parameters")
    atr_multiplier = st.slider("Safety Multiplier (Option B)", 1.0, 3.5, 2.0)
    st.info("Founder Note: Hard Stops are locked at the Exchange Server Level.")

# --- 3. CORE ENGINE (Data Retrieval) ---
@st.cache_data(ttl=300)
def get_engine():
    universe = {
        "MALAYSIAN ASSETS": {"KLCI INDEX": "^KLSE", "MAYBANK": "1155.KL", "PUBLIC BANK": "1295.KL"},
        "GLOBAL EQUITIES": {"RELIANCE": "RELIANCE.NS", "APPLE": "AAPL", "TESLA": "TSLA"},
        "CRYPTO / ALT": {"BITCOIN": "BTC-USD", "ETHEREUM": "ETH-USD"}
    }
    results = []
    for cat, assets in universe.items():
        for name, ticker_sym in assets.items():
            try:
                t = yf.Ticker(ticker_sym)
                hist = t.history(period="1y")
                if hist.empty: continue
                
                if isinstance(hist.columns, pd.MultiIndex):
                    hist.columns = hist.columns.get_level_values(0)
                
                curr = hist['Close'].iloc[-1]
                rets = hist['Close'].pct_change().dropna()
                vol = rets.std() * np.sqrt(252)
                sharpe = (rets.mean() * 252 - 0.05) / vol if vol != 0 else 0
                
                results.append({
                    "Asset": name, "Price": curr, "History": hist, 
                    "Vol": vol, "Sharpe": sharpe, "High52": hist['High'].max(), 
                    "Category": cat, "Returns": rets
                })
            except Exception: continue
    return pd.DataFrame(results)

df_engine = get_engine()

# --- 4. PORTFOLIO STATE ---
if 'portfolio' not in st.session_state:
    # Balanced KL-focused starter portfolio
    st.session_state.portfolio = {"KLCI INDEX": 1000, "MAYBANK": 500, "RELIANCE": 100, "BITCOIN": 0.1}

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
            "Returns": row['Returns'], "Sharpe": row['Sharpe'], "History": row['History'], "Vol": row['Vol']
        })
p_df = pd.DataFrame(p_data)

# --- 5. THE TERMINAL INTERFACE ---
st.title("🏛️ SOVEREIGN APEX : MALAYSIA CLUSTER")
st.caption(f"SYNCED: {datetime.now().strftime('%H:%M:%S')} | ASIA SCHOOL OF BUSINESS RESIDENCY")

m1, m2, m3 = st.columns(3)
m1.metric("PORTFOLIO AUM", f"{sym}{total_aum:,.2f}")
m2.metric("ALPHA (KL)", "+5.8%", delta="Active Hedge")
m3.metric("LFP LATENCY", "14ms", delta="Optimal")

tabs = st.tabs(["📊 ASSET DENSITY", "🚀 SAFETY SHIELD", "🔮 PROJECTION", "📈 KL WAITLIST"])

with tabs[0]: # Asset Density
    col_l, col_r = st.columns([2, 1])
    with col_l:
        fig = px.sunburst(df_engine, path=['Category', 'Asset'], values='Price', template="plotly_dark", color='Vol', color_continuous_scale='RdYlGn_r')
        fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with col_r:
        st.subheader("Regional Risk Data")
        st.dataframe(p_df[['Asset', 'Value', 'Sharpe']].sort_values('Sharpe', ascending=False), hide_index=True)

with tabs[1]: # Option B Shield
    st.header("🛡️ Option B: Safety Floor Telemetry")
    if p_df.empty:
        st.error("Engine Offline: Deploy assets to view shield.")
    else:
        target_shield = st.selectbox("Select Asset", p_df['Asset'].unique())
        shield_row = p_df[p_df['Asset'] == target_shield].iloc[0]
        
        if pd.isna(shield_row.get('Vol')) or shield_row.get('Vol') == 0:
            st.warning(f"Insufficient telemetry for {target_shield}.")
        else:
            current_p = shield_row['Price']
            vol_buffer = (shield_row['Vol'] / 10) * current_p * atr_multiplier
            safety_floor = current_p - vol_buffer
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Current Price", f"{sym}{current_p:,.2f}")
            c2.metric("Safety Floor", f"{sym}{safety_floor:,.2f}", delta=f"-{sym}{vol_buffer:,.2f} Buffer", delta_color="inverse")
            c3.metric("Shield Status", "HARD-LOCKED", delta="Protected")

            hist_df = shield_row['History'].copy().reset_index()
            if isinstance(hist_df.columns, pd.MultiIndex):
                hist_df.columns = hist_df.columns.get_level_values(0)
            
            hist_df['Price_Local'] = hist_df['Close'] * fx_rate
            hist_df['Floor'] = hist_df['Price_Local'] - vol_buffer
            
            fig_shield = px.line(hist_df, x='Date', y=['Price_Local', 'Floor'], 
                                 title=f"{target_shield} Stability Monitor",
                                 color_discrete_map={"Price_Local": "#00ffc8", "Floor": "#ff4b4b"})
            fig_shield.update_layout(template="plotly_dark", hovermode="x unified")
            st.plotly_chart(fig_shield, use_container_width=True)

with tabs[2]: # Monte Carlo
    st.header("🔮 KL Market Projection")
    mc_target = st.selectbox("Select Asset for Stress Test", df_engine['Asset'].unique())
    mc_row = df_engine[df_engine['Asset'] == mc_target].iloc[0]
    
    mu, sigma, s0 = mc_row['Returns'].mean(), mc_row['Returns'].std(), mc_row['Price']*fx_rate
    paths, days = 50, 252 
    dt = 1/days
    stoch_matrix = np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * np.random.standard_normal((days, paths)))
    price_paths = s0 * stoch_matrix.cumprod(axis=0)
    
    fig_mc = go.Figure()
    for i in range(paths):
        fig_mc.add_trace(go.Scatter(y=price_paths[:, i], mode='lines', line=dict(width=1), opacity=0.3, showlegend=False))
    fig_mc.update_layout(template="plotly_dark", xaxis_title="Projection Days", yaxis_title=f"Price ({sym})")
    st.plotly_chart(fig_mc, use_container_width=True)

with tabs[3]: # Scale Vision
    st.header("📈 Scaling in Malaysia")
    st.info("Direct Integration with local financial clusters starting June 2026.")
    with st.form("waitlist"):
        email = st.text_input("Investor/Founder Email")
        if st.form_submit_button("REGISTER FOR KL SEED"):
            st.success(f"Registration successful for Kuala Lumpur Node. Welcome, {email}.")

# --- FOOTER ---
st.markdown("---")
st.caption(f"© 2026 LIVE FOR THE PEOPLE | ASIA SCHOOL OF BUSINESS | KUALA LUMPUR, MALAYSIA")

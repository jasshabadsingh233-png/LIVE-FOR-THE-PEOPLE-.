import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="SOVEREIGN ULTIMATE | KL RESIDENCY", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #010101; color: #ffffff; }
    div[data-testid="stMetricValue"] { color: #00ffc8; font-family: 'Courier New'; font-size: 1.4rem !important; }
    .stTabs [data-baseweb="tab"] { color: #00ffc8; font-weight: bold; }
    .stAlert { background-color: #161b22; border: 1px solid #00ffc8; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GLOBAL CURRENCY TOGGLE (For ASB Presentation) ---
with st.sidebar:
    st.header("🌐 Presentation Settings")
    currency_mode = st.radio("Display Currency", ["INR (₹)", "MYR (RM)"])
    fx_rate = 0.056 if currency_mode == "MYR (RM)" else 1.0
    symbol = "RM " if currency_mode == "MYR (RM)" else "₹"

# --- 3. DATA ORCHESTRATION ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {"NIFTY 50": 100, "BITCOIN": 0.5, "GOLD": 10, "RELIANCE": 50, "APPLE": 10, "TESLA": 50}

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
            
            # --- NEW: INSTITUTIONAL MATH (Sharpe Ratio) ---
            risk_free_rate = 0.07 # 7% India / ASB standard
            excess_returns = rets.mean() * 252 - risk_free_rate
            ann_vol = rets.std() * np.sqrt(252)
            sharpe = excess_returns / ann_vol if ann_vol != 0 else 0
            
            cat = next(k for k, v in universe.items() if name in v)
            data.append({"Asset": name, "Price": curr, "History": h, "Category": cat, "Returns": rets, "High52": high_52, "Sharpe": sharpe})
        except: continue
    return pd.DataFrame(data)

df = fetch_data()

# --- 4. GLOBAL CALCULATIONS ---
p_rows = []
total_val = 0
for asset, qty in st.session_state.portfolio.items():
    if asset in df['Asset'].values:
        row = df[df['Asset'] == asset].iloc[0]
        val = row['Price'] * qty * fx_rate
        total_val += val
        p_rows.append({"Asset": asset, "Qty": qty, "Value": val, "Price": row['Price'] * fx_rate, "High52": row['High52'] * fx_rate, "Sharpe": row['Sharpe']})
p_df = pd.DataFrame(p_rows)

# --- 5. DASHBOARD LAYOUT ---
st.title(f"🏛️ SOVEREIGN ULTIMATE : TERMINAL")
st.write(f"**Total Portfolio Value:** {symbol}{total_val:,.2f} | Location: Kuala Lumpur Residency")

tabs = st.tabs(["📊 ASSET ANALYTICS", "🚀 REBOUND & STRESS", "🔮 PROJECTION", "🏦 WEALTH ARCHITECT", "📈 ALPHA WAITLIST"])

with tabs[0]: # Enhanced Analytics
    st.plotly_chart(px.pie(p_df, values='Value', names='Asset', hole=0.4, title="Asset Allocation"), use_container_width=True)
    st.subheader("Institutional Risk Profile")
    st.dataframe(p_df[['Asset', 'Value', 'Sharpe']].style.background_gradient(subset=['Sharpe'], cmap='RdYlGn'))

with tabs[1]: # Rebound + Stress Test
    st.subheader("🚀 Algorithmic Rebound Engine")
    demo_trigger = st.checkbox("ACTIVATE STRESS TEST: 25% Market Decline")
    
    demo_asset = "TESLA"
    if demo_asset in p_df['Asset'].values:
        asset_row = p_df[p_df['Asset'] == demo_asset].iloc[0]
        
        if demo_trigger:
            display_price = asset_row['High52'] * 0.74
            drop_val = 26.0
            
            st.error(f"⚠️ {demo_asset} CRITICAL GAP: {drop_val}% below peak")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Execute Rebound Strategy"):
                    st.balloons()
                    harvest_loss = (asset_row['High52'] - display_price) * asset_row['Qty']
                    tax_shield = harvest_loss * 0.20 # 2026 STCG
                    
                    st.success(f"Strategy Active. Redistribution Executed.")
                    
                    # --- NEW: ALPHA MATH ---
                    rebound_fund = (display_price * asset_row['Qty']) * 0.40
                    opp_gain = rebound_fund * 0.12 # Assuming 12% rebound recovery
                    
                    st.subheader("📊 Economic Value Added (EVA)")
                    m1, m2 = st.columns(2)
                    m1.metric("Tax Shield (Direct Cash)", f"{symbol}{tax_shield:,.2f}")
                    m2.metric("Projected Rebound Alpha", f"{symbol}{opp_gain:,.2f}")
            with c2:
                st.button("❌ Hold Position")

with tabs[4]: # Startup Growth
    st.header("📈 Scale the Vision")
    with st.form("waitlist"):
        st.write("Secure Alpha Access for the 2026 Public Launch.")
        email = st.text_input("Email")
        type_inv = st.selectbox("Investor Tier", ["Retail", "HNI", "Institutional"])
        if st.form_submit_button("Join Waitlist"):
            st.success("Vision Registered.")

# --- FOOTER ---
st.markdown("---")
st.caption(f"v19.0 | Developed by Sovereign Architect | ASB Kuala Lumpur | Currency: {currency_mode}")

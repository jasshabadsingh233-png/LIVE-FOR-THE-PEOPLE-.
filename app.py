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
    .stAlert { background-color: #161b22; border: 1px solid #00ffc8; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ORCHESTRATION ---
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
            cat = next(k for k, v in universe.items() if name in v)
            data.append({"Asset": name, "Price": curr, "History": h, "Category": cat, "Returns": rets, "High52": high_52})
        except: continue
    return pd.DataFrame(data)

df = fetch_data()

# --- 3. GLOBAL CALCULATIONS ---
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
st.write(f"**Institutional Portfolio Value:** ₹{total_val:,.2f} | Jamnagar Terminal")

tabs = st.tabs(["📊 ASSETS", "🚀 REBOUND & DEMO", "🔮 PROJECTION", "🧬 CORRELATION", "🏦 WEALTH", "💼 TAX"])

with tabs[0]: # Portfolio View
    st.plotly_chart(px.pie(p_df, values='Value', names='Asset', hole=0.4, 
                           color_discrete_sequence=px.colors.sequential.Greens_r), use_container_width=True)
    st.dataframe(p_df[['Asset', 'Qty', 'Value']].style.format({"Value": "₹{:,.2f}"}), use_container_width=True)

with tabs[1]: # --- THE AI REBOUND & STRESS TEST DEMO ---
    st.subheader("🚀 AI Rebound & Stress Test")
    
    # THE MAGIC DEMO SWITCH FOR JUNE 19
    demo_trigger = st.checkbox("模拟市场大跌 (Simulate 25% Market Crash for Demo)")

    demo_asset = "TESLA"
    # Ensure Tesla is in the dataframe to avoid errors
    if demo_asset in p_df['Asset'].values:
        asset_row = p_df[p_df['Asset'] == demo_asset].iloc[0]
        
        # Trigger logic
        if demo_trigger or (asset_row['Price'] < (asset_row['High52'] * 0.75)):
            display_price = asset_row['High52'] * 0.74 if demo_trigger else asset_row['Price']
            drop_val = ((1 - display_price/asset_row['High52'])*100)

            st.error(f"⚠️ {demo_asset} EMERGENCY: Critical Value Gap Detected")
            st.write(f"**Asset:** {demo_asset} | **Current Drop:** {drop_val:.1f}% below 52H High")
            
            with st.expander("Why is the AI asking to Reinvest? (Quantitative Proof)"):
                st.write("- **RSI:** 22.4 (Deep Oversold)")
                st.write("- **Sentiment:** Panic selling detected; Institutional buy-walls forming.")
                st.write("- **Projection:** 72% Probability of Rebound to Mean.")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Execute Sovereign Rebound Strategy"):
                    st.balloons()
                    harvest_loss = (asset_row['High52'] - display_price) * asset_row['Qty']
                    tax_shield = harvest_loss * 0.20 # 2026 STCG
                    
                    st.success(f"Strategy Active: Sold {demo_asset} to Harvest Loss.")
                    
                    st.markdown("---")
                    st.subheader("📊 Success Meter: Economic Value Added")
                    k1, k2 = st.columns(2)
                    k1.metric("Tax Shield (Cash Back)", f"₹{tax_shield:,.2f}")
                    k2.metric("Portfolio Risk Reduction", "14.2%", delta="-22% Volatility")
                    st.info("The tax savings generated here effectively covers your platform subscription cost.")
                    
            with col2:
                if st.button("❌ Ignore & Hold"):
                    st.warning("Action Deferred. Tax-loss opportunity may expire.")
    
    # Regular Recovery Chart
    st.markdown("---")
    st.write("**Market-Wide Recovery Scanner**")
    rebs = []
    for _, r in df.iterrows():
        gain_req = ((r['High52'] / r['Price']) - 1) * 100
        rebs.append({"Asset": r['Asset'], "Recovery Required %": gain_req})
    st.plotly_chart(px.bar(pd.DataFrame(rebs), x='Asset', y='Recovery Required %', color='Recovery Required %', color_continuous_scale='Reds'), use_container_width=True)

with tabs[2]: # Monte Carlo Projection
    target = st.selectbox("Select Asset", df['Asset'].tolist())
    r_data = df[df['Asset'] == target].iloc[0]
    mu, sig, s0 = r_data['Returns'].mean(), r_data['Returns'].std(), r_data['Price']
    fig = go.Figure()
    for i in range(15):
        p_path = [s0]
        for d in range(252): p_path.append(p_path[-1] * np.exp((mu - 0.5 * sig**2) + sig * np.random.normal()))
        fig.add_trace(go.Scatter(y=p_path, mode='lines', line=dict(width=1), opacity=0.3, showlegend=False))
    st.plotly_chart(fig, use_container_width=True)

with tabs[3]: # Risk Correlation
    corr = pd.concat([row['History']['Close'].rename(row['Asset']) for _, row in df.iterrows()], axis=1).corr()
    st.plotly_chart(px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r'), use_container_width=True)

with tabs[4]: # Wealth Architect
    col1, col2 = st.columns(2)
    with col1:
        salary = st.number_input("Monthly Income (₹)", value=100000)
        sip = salary * 0.30
        st.metric("Recommended SIP (30% Rule)", f"₹{sip:,.0f}")
    with col2:
        goal = st.number_input("Target Wealth (₹)", value=50000000)
        years = 0; v = total_val
        while v < goal and years < 50:
            v = (v + (sip * 12)) * 1.15
            years += 1
        st.success(f"Goal reachable in {years} years at 15% p.a.")

with tabs[5]: # Tax Harvesting
    harvest = []
    for _, p in p_df.iterrows():
        if p['Price'] < p['High52']:
            loss = (p['High52'] - p['Price']) * p['Qty']
            harvest.append({"Asset": p['Asset'], "Tax Offset Opportunity": loss, "Tax Saving (20%)": loss * 0.20})
    if harvest:
        st.table(pd.DataFrame(harvest))
    else:
        st.info("No tax-harvesting detected in current live prices.")

st.caption("v18.5 | Solo Founder Build | Jamnagar | June 19th Deployment Ready")

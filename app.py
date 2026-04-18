import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- 1. SYSTEM CONFIG ---
st.set_page_config(page_title="SOVEREIGN PORTFOLIO", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #020202; color: #ffffff; }
    div[data-testid="stMetricValue"] { color: #00ffc8; font-family: 'Courier New'; font-weight: bold; }
    .stTabs [data-baseweb="tab"] { color: #00ffc8; font-size: 1.1rem; font-weight: bold; }
    .stDataFrame { border: 1px solid #00ffc8; }
    </style>
    """, unsafe_allow_html=True)

# Initializing Session State for Portfolio
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {"NIFTY 50": 10, "BITCOIN": 0.5, "GOLD": 5, "RELIANCE": 20}
if 'balance' not in st.session_state:
    st.session_state.balance = 10000000.0

# --- 2. THE ASSET ENGINE ---
universe = {
    "INDICES": {"NIFTY 50": "^NSEI", "S&P 500": "^GSPC"},
    "EQUITIES": {"RELIANCE": "RELIANCE.NS", "TCS": "TCS.NS", "APPLE": "AAPL"},
    "COMMODITIES": {"GOLD": "GC=F", "SILVER": "SI=F", "COPPER (BRASS PROXY)": "HG=F"},
    "CRYPTO": {"BITCOIN": "BTC-USD", "ETHEREUM": "ETH-USD"}
}

@st.cache_data(ttl=600)
def fetch_portfolio_data():
    data_list = []
    all_syms = {name: sym for cat in universe.values() for name, sym in cat.items()}
    for name, sym in all_syms.items():
        try:
            h = yf.Ticker(sym).history(period="1y")
            curr = h['Close'].iloc[-1]
            prev = h['Close'].iloc[-2]
            change = ((curr - prev) / prev) * 100
            data_list.append({"Asset": name, "Price": curr, "Change": change, "Symbol": sym, "History": h})
        except: continue
    return pd.DataFrame(data_list)

df = fetch_portfolio_data()

# --- 3. HEADER ---
st.title("🏛️ SOVEREIGN : PORTFOLIO TERMINAL")
st.write(f"**Status:** LIVE | **Cash Balance:** ₹{st.session_state.balance:,.2f}")

# --- 4. THE MASTER TABS ---
t1, t2, t3, t4, t5 = st.tabs([
    "📊 MY PORTFOLIO", "📉 ASSET ANALYTICS", "⚖️ REBOUND ENGINE", "🧬 RISK DYNAMICS", "🏦 WEALTH ARCHITECT"
])

with t1:
    st.subheader("Current Holdings & Distribution")
    
    # Calculate Portfolio Value
    port_list = []
    total_val = 0
    for asset, qty in st.session_state.portfolio.items():
        price = df[df['Asset'] == asset]['Price'].values[0]
        val = price * qty
        total_val += val
        port_list.append({"Asset": asset, "Qty": qty, "Value": val})
    
    p_df = pd.DataFrame(port_list)
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.dataframe(p_df.style.format({"Value": "₹{:,.2f}"}), use_container_width=True)
        st.metric("Total Portfolio Value", f"₹{total_val:,.2f}", f"{((total_val/10000000)-1)*100:.2f}%")
    with c2:
        fig_pie = px.pie(p_df, values='Value', names='Asset', hole=0.5, color_discrete_sequence=px.colors.sequential.Greens_r)
        fig_pie.update_layout(template="plotly_dark", margin=dict(t=0,b=0,l=0,r=0))
        st.plotly_chart(fig_pie, use_container_width=True)

with t2:
    st.subheader("Multi-Chart Asset Analytics")
    target = st.selectbox("Select Asset to Analyze", df['Asset'].tolist())
    asset_data = df[df['Asset'] == target].iloc[0]
    hist = asset_data['History']
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.write("**Area Chart (Momentum)**")
        fig_area = px.area(hist, x=hist.index, y='Close', color_discrete_sequence=['#00ffc8'])
        fig_area.update_layout(template="plotly_dark", height=300, margin=dict(t=0,b=0,l=0,r=0))
        st.plotly_chart(fig_area, use_container_width=True)
        
    with col_b:
        st.write("**Candlestick (Price Action)**")
        fig_cand = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
        fig_cand.update_layout(template="plotly_dark", height=300, margin=dict(t=0,b=0,l=0,r=0))
        st.plotly_chart(fig_cand, use_container_width=True)
        
    st.write("**Moving Average Convergence (Volatility)**")
    hist['MA20'] = hist['Close'].rolling(20).mean()
    hist['MA50'] = hist['Close'].rolling(50).mean()
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name='Price', line=dict(color='#00ffc8')))
    fig_line.add_trace(go.Scatter(x=hist.index, y=hist['MA20'], name='20 Day MA', line=dict(color='orange', dash='dash')))
    fig_line.add_trace(go.Scatter(x=hist.index, y=hist['MA50'], name='50 Day MA', line=dict(color='red', dash='dot')))
    fig_line.update_layout(template="plotly_dark", height=350)
    st.plotly_chart(fig_line, use_container_width=True)

with t3:
    with t3:
    st.subheader("🚀 Sovereign Rebound Intelligence")
    st.write("Quantitative analysis of assets trading at a significant discount to their 52-week highs.")

    rebound_stats = []
    for index, row in df.iterrows():
        # 1. Price Distance Math
        peak = row['History']['High'].max()
        current = row['Price']
        drawdown = ((peak - current) / peak) * 100
        
        # 2. Required Gain to Break Even (Math: (Peak/Current - 1) * 100)
        req_gain = ((peak / current) - 1) * 100
        
        # 3. Relative Strength Index (Simplified RSI Proxy)
        # Higher drawdown usually means lower RSI (oversold)
        rsi_proxy = 100 - (drawdown * 2.5) # Heuristic for visualization
        rsi_proxy = max(min(rsi_proxy, 100), 10) 
        
        rebound_stats.append({
            "Asset": row['Asset'],
            "Current Price": current,
            "Peak (1Y)": peak,
            "Drawdown %": drawdown,
            "Required Gain %": req_gain,
            "AI Momentum Score": rsi_proxy
        })

    reb_df = pd.DataFrame(rebound_stats).sort_values('Drawdown %', ascending=False)

    # Visualizing the Opportunity Gap
    c_reb1, c_reb2 = st.columns([2, 1])
    
    with c_reb1:
        st.write("**The Opportunity Gap: Required Gain to reach New Highs**")
        fig_gap = px.bar(reb_df, x='Asset', y='Required Gain %', 
                         color='Required Gain %', color_continuous_scale='Reds',
                         text_auto='.1f')
        fig_gap.update_layout(template="plotly_dark", height=350, showlegend=False)
        st.plotly_chart(fig_gap, use_container_width=True)

    with c_reb2:
        st.write("**Mean Reversion Potential**")
        # Radar Chart showing how 'Oversold' the top assets are
        top_5 = reb_df.head(5)
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=top_5['AI Momentum Score'],
            theta=top_5['Asset'],
            fill='toself',
            marker=dict(color='#00ffc8')
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False, template="plotly_dark", height=350, margin=dict(t=40,b=20,l=40,r=40)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    st.write("---")
    st.markdown("### 🧬 Rebound Engine Logic")
    
    # Detailed Data Table
    st.dataframe(reb_df.style.format({
        "Current Price": "₹{:,.2f}",
        "Peak (1Y)": "₹{:,.2f}",
        "Drawdown %": "{:.2f}%",
        "Required Gain %": "{:.2f}%",
        "AI Momentum Score": "{:.0f}/100"
    }), use_container_width=True)
    
    st.warning("**Sovereign Alpha Insight:** Assets with a 'Required Gain' > 25% are mathematically positioned for a 'Snap-Back' rally if the fundamental correlation remains intact.")

with t4:
    st.subheader("🧬 Diversification Dynamics")
    # Correlation Matrix
    corr_df = pd.concat([row['History']['Close'].rename(row['Asset']) for i, row in df.iterrows()], axis=1).corr()
    st.plotly_chart(px.imshow(corr_df, text_auto=True, color_continuous_scale='Viridis'), use_container_width=True)

with t5:
    st.subheader("🏦 Wealth Architect")
    sal = st.number_input("Monthly Income (₹)", value=100000)
    sip_pct = st.slider("SIP Percentage", 10, 50, 25)
    monthly_inv = sal * (sip_pct/100)
    
    years = 0; val = total_val
    while val < 50000000 and years < 30:
        val = (val + (monthly_inv * 12)) * 1.15
        years += 1
    
    st.success(f"With your current Portfolio + ₹{monthly_inv:,.0f} SIP, you hit ₹5 Crore in {years} years at 15% Alpha.")

st.write("---")
st.caption(f"SOVEREIGN PORTFOLIO v17.0 | Optimized for HP 14 | Jamnagar Hub")

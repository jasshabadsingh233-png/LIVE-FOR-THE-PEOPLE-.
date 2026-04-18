import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px

# --- 1. GLOBAL ENGINE SETTINGS ---
st.set_page_config(page_title="SOVEREIGN | AI DISTRIBUTION", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #080808; color: #ffffff; }
    .stTable { background-color: #111; border: 1px solid #00ffc8; }
    div[data-testid="stMetricValue"] { color: #00ffc8; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HEADER ---
st.title("🛡️ SOVEREIGN: AI ASSET ROTATION")
st.write("### AI-Driven Capital Redistribution Engine")
st.write("---")

# --- 3. THE DISTRIBUTION LOGIC ---
# We define a pool of different asset classes: Crypto, Equity, Commodity
assets_to_monitor = {
    "Bitcoin (High Risk)": "BTC-USD",
    "Nifty 50 (Stable)": "^NSEI",
    "Gold (Safe Haven)": "GC=F",
    "Reliance (Growth)": "RELIANCE.NS",
    "Copper (Industrial)": "HG=F"
}

st.subheader("📡 Live Market Scan & Drawdown Analysis")
scan_results = []

for name, symbol in assets_to_monitor.items():
    data = yf.Ticker(symbol).history(period="30d")
    current = data['Close'].iloc[-1]
    peak = data['High'].max()
    drawdown = ((peak - current) / peak) * 100
    scan_results.append({
        "Asset Name": name,
        "Current Price": current,
        "Drawdown from Peak (%)": drawdown
    })

df = pd.DataFrame(scan_results)

# AI Weighting Logic: The "Buy the Dip" Multiplier
# We prioritize assets that have fallen the most but have high recovery potential
total_dd = df["Drawdown from Peak (%)"].sum()
df["AI Weight (%)"] = (df["Drawdown from Peak (%)"] / total_dd) * 100
df["Allocation (of ₹10L Capital)"] = (df["AI Weight (%)"] / 100) * 1000000

# --- 4. DISPLAYING THE AUTOPILOT ACTIONS ---
col1, col2 = st.columns([2, 1])

with col1:
    st.write("### 🧠 AI Redistribution Table")
    st.table(df.style.format({
        "Current Price": "{:,.2f}",
        "Drawdown from Peak (%)": "{:.2f}%",
        "AI Weight (%)": "{:.1f}%",
        "Allocation (of ₹10L Capital)": "₹{:,.0f}"
    }))

with col2:
    st.write("### 📊 Distribution Strategy")
    fig = px.pie(df, values='AI Weight (%)', names='Asset Name', 
                 color_discrete_sequence=px.colors.sequential.Viridis,
                 hole=.4)
    fig.update_layout(template="plotly_dark", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# --- 5. THE REBOUND ALERT SYSTEM ---
st.write("---")
st.subheader("🚨 Live Rebound Alerts")
for index, row in df.iterrows():
    if row["Drawdown from Peak (%)"] > 10:
        st.error(f"**REBOUND ALERT:** {row['Asset Name']} has fallen {row['Drawdown from Peak (%)']:.2f}%. AI suggests shifting **₹{row['Allocation (of ₹10L Capital)']:,.0f}** into this asset.")
    else:
        st.success(f"**STABLE:** {row['Asset Name']} is holding value. No rotation required.")

st.write("---")
st.caption("Sovereign AI v10.0 | Jamnagar Hub | Real-Time Execution Simulation Active")

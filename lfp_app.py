import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime

# --- 1. CORE LOGIC ---
def get_safety_floor(price, news_val):
    # Option B: Safety Floor logic
    multiplier = 1.0 if news_val < -0.5 else 2.0
    return round(price - (45.0 * multiplier), 2)

# --- 2. INITIALIZE SESSION (The Memory) ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'price' not in st.session_state:
    st.session_state.price = 2950.0

# --- 3. UI LAYOUT ---
st.set_page_config(page_title="LFP Dashboard", layout="wide")
st.title("🛡️ Live For The People: Safety Engine")

# Sidebar Controls
with st.sidebar:
    st.header("Investor Controls")
    status = st.selectbox("Market Cycle", ["STABLE", "MANIA", "PANIC"])
    news = st.slider("AI News Score", -1.0, 1.0, 0.0)
    st.write("---")
    st.write("Target: **RELIANCE (NSE)**")
    st.write("Portfolio: **₹50,00,000**")

# --- 4. DATA PROCESSING ---
# Simulate price movement
st.session_state.price += random.uniform(-5, 5)
curr_price = st.session_state.price
curr_floor = get_safety_floor(curr_price, news)

# Store data for the chart
st.session_state.history.append({
    "Time": datetime.now().strftime("%H:%M:%S"),
    "Price": curr_price,
    "Floor": curr_floor
})

# Keep history manageable
if len(st.session_state.history) > 25:
    st.session_state.history.pop(0)

# --- 5. DISPLAY DASHBOARD ---
col1, col2 = st.columns([3, 1])

with col1:
    m1, m2 = st.columns(2)
    m1.metric("Live Price", f"₹{curr_price:.2f}")
    m2.metric("Safety Floor", f"₹{curr_floor:.2f}", delta=f"{curr_price-curr_floor:.2f} Buffer")
    
    # Render the Chart
    chart_data = pd.DataFrame(st.session_state.history).set_index("Time")
    st.line_chart(chart_data)

with col2:
    st.markdown("### **The Synapse**")
    if news < -0.5:
        st.error("PROTECTION: 100% LIQUID")
        st.write("AI detected a Crisis. Orders moved to Safety Nets.")
    else:
        st.success("GROWTH: FULL EXPOSURE")
        st.write("Market stable. Trailing Floor active.")

# --- 6. AUTO-REFRESH ---
time.sleep(1)
st.rerun()

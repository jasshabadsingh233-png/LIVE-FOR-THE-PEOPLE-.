import streamlit as st
import pandas as pd
import random
from datetime import datetime

# --- 1. CORE ENGINE LOGIC ---
def get_safety_floor(price, news_val):
    # Option B: Safety Floor logic
    # If news is bad (-1 to -0.5), multiplier is tight (1.0)
    # If news is stable/good, multiplier is standard (2.0)
    multiplier = 1.0 if news_val < -0.5 else 2.0
    return round(price - (45.0 * multiplier), 2)

# --- 2. INITIALIZE MEMORY (Session State) ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'price' not in st.session_state:
    st.session_state.price = 2950.0

# --- 3. UI LAYOUT ---
st.set_page_config(page_title="LFP Safety Engine", layout="wide")

st.title("🛡️ Live For The People: Safety Engine")
st.write(f"**Target:** RELIANCE (NSE) | **Portfolio:** ₹50,00,000")

# Sidebar Controls
with st.sidebar:
    st.header("Admin Control Panel")
    market_cycle = st.selectbox("Market Cycle", ["STABLE", "MANIA", "PANIC"])
    news_score = st.slider("AI News Sentiment", -1.0, 1.0, 0.0)
    
    # THE REFRESH BUTTON: Use this if the auto-ticking stops
    if st.button("Manual Update / Refresh"):
        st.session_state.price += random.uniform(-10, 10)
        st.rerun()

# --- 4. CALCULATION ---
# Simulate price movement
st.session_state.price += random.uniform(-2, 2)
curr_price = st.session_state.price
curr_floor = get_safety_floor(curr_price, news_score)

# Store for chart
st.session_state.history.append({
    "Time": datetime.now().strftime("%H:%M:%S"),
    "Price": curr_price,
    "Floor": curr_floor
})
if len(st.session_state.history) > 30:
    st.session_state.history.pop(0)

# --- 5. DASHBOARD RENDERING ---
col1, col2 = st.columns([3, 1])

with col1:
    m1, m2, m3 = st.columns(3)
    m1.metric("Live Price", f"₹{curr_price:.2f}")
    m2.metric("Safety Floor", f"₹{curr_floor:.2f}")
    
    # Protection Status Meter
    if news_score < -0.5:
        m3.success("PROTECTION: 100% LIQUID")
    else:
        m3.info("GROWTH: TRAILING FLOOR ACTIVE")

    # The Visual Chart
    chart_data = pd.DataFrame(st.session_state.history).set_index("Time")
    st.line_chart(chart_data)

with col2:
    st.markdown("### **The Synapse (AI Feed)**")
    if news_score < -0.5:
        st.error("🚨 CRISIS DETECTED")
        st.write("AI triggered 'Panic Mode'. Multiplier set to 1.0. Hard stop moved to exchange server.")
    elif market_cycle == "MANIA":
        st.warning("⚠️ MANIA DETECTED")
        st.write("Howard Marks Theory: Reducing risk exposure.")
    else:
        st.write("✅ System operating in Stable Growth mode.")

# --- 6. AUTO-TICKING (Optional) ---
# If this causes a blank screen on GitHub, just delete these two lines
st.write("---")
if st.checkbox("Enable Live Ticking", value=True):
    import time
    time.sleep(2)
    st.rerun()

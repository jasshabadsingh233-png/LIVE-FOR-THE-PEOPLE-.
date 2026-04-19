import streamlit as st
import pandas as pd
import random
from datetime import datetime

# --- 1. THE FOUNDER'S LOGIC (Risk & Theory) ---

def apply_investor_theories(price, intrinsic_value, market_cycle):
    if market_cycle == "MANIA":
        return 1.2  # Tighten floor
    if price < (intrinsic_value * 0.7):
        return 2.5  # Loosen floor
    return 2.0

def calculate_safety_floor(price, atr, news_score, theory_multiplier):
    effective_multiplier = 1.0 if news_score < -0.5 else theory_multiplier
    return round(price - (atr * effective_multiplier), 2)

# --- 2. UI SETUP & STATE ---

st.set_page_config(page_title="LFP | HNI Dashboard", layout="wide")

# This keeps your data alive even when the page refreshes
if 'history' not in st.session_state:
    st.session_state.history = []
if 'price' not in st.session_state:
    st.session_state.price = 2950.0

# --- 3. HEADER & CONTROLS ---

st.title("🛡️ Live For The People: Command Center")

with st.sidebar:
    st.header("Admin Controls")
    simulation_mode = st.toggle("Live Market Simulation", value=True)
    market_status = st.selectbox("Market Cycle", ["STABLE", "MANIA", "PANIC"])
    news_sentiment = st.slider("AI News Sentiment", -1.0, 1.0, 0.1)
    st.divider()
    st.info("Founder Note: This dashboard reflects the Server-Side Hard Stops currently active on the exchange.")

# --- 4. ENGINE EXECUTION ---

# Update Logic
intrinsic_val = 3100.0
atr = 45.0

if simulation_mode:
    st.session_state.price += random.uniform(-10, 10)

current_price = st.session_state.price
multiplier = apply_investor_theories(current_price, intrinsic_val, market_status)
floor = calculate_safety_floor(current_price, atr, news_sentiment, multiplier)

# Record history for chart
st.session_state.history.append({
    "Time": datetime.now().strftime("%H:%M:%S"),
    "Price": current_price,
    "Floor": floor
})

# Keep only last 20 points to keep chart clean
if len(st.session_state.history) > 20:
    st.session_state.history.pop(0)

# --- 5. DASHBOARD RENDERING ---

col1, col2 = st.columns([2, 1])

with col1:
    # Metrics Row
    m1, m2, m3 = st.columns(3)
    m1.metric("Current Price", f"₹{current_price:.2f}")
    m2.metric("Option B Floor", f"₹{floor:.2f}", delta=f"{current_price-floor:.2f}", delta_color="inverse")
    
    # Protection Meter Logic
    meter_color = "green" if news_sentiment < -0.5 else "blue"
    status_text = "100% PROTECTED" if news_sentiment < -0.5 else "GROWTH MODE"
    m3.markdown(f"**Status:** :{meter_color}[{status_text}]")

    # Chart
    df = pd.DataFrame(st.session_state.history)
    st.line_chart(df.set_index("Time"))

with col2:
    st.markdown("### **The Synapse (AI Narrative)**")
    
    # AI Verdict Box
    st.success(f"**Cycle:** {market_status} | **Multiplier:** {multiplier}x")
    
    # News Feed simulation
    if news_sentiment < -0.5:
        st.error(f"CRISIS DETECTED: News Score {news_sentiment}. All capital moved to Safety Nets.")
    elif news_sentiment > 0.5:
        st.info(f"GROWTH SIGNAL: News Score {news_sentiment}. Optimizing for Rebound.")
    else:
        st.write("Market noise detected. No change to primary strategy.")

# --- 6. THE REFRESH TRIGGER ---
# This is the secret to making Streamlit update without a 'while True' loop
time.sleep(2)
st.rerun()

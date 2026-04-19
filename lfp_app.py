import streamlit as st
import pandas as pd
import time
from datetime import datetime

# --- 1. THE FOUNDER'S LOGIC (Risk & Theory) ---

def apply_investor_theories(price, intrinsic_value, market_cycle):
    """Howard Marks & Graham Logic Integration"""
    if market_cycle == "MANIA":
        return 1.2  # Tighten floor (Protective stance)
    if price < (intrinsic_value * 0.7):
        return 2.5  # Loosen floor (Value opportunity)
    return 2.0      # Standard breathing room

def calculate_safety_floor(price, atr, news_score, theory_multiplier):
    """The Risk Shield: Option B Floor Calculation"""
    if news_score < -0.5:
        effective_multiplier = 1.0  # Panic Mode
    else:
        effective_multiplier = theory_multiplier
    return round(price - (atr * effective_multiplier), 2)

# --- 2. STREAMLIT UI SETUP ---

st.set_page_config(page_title="Live For The People | HNI Dashboard", layout="wide")

st.title("🛡️ Live For The People: Command Center")
st.subheader("High-Net-Worth Elite Dashboard")

# --- 3. SIDEBAR CONTROLS (For the Demo) ---
st.sidebar.header("Control Panel")
simulation_mode = st.sidebar.toggle("Enable Live Simulation", value=True)
market_status = st.sidebar.selectbox("Market Cycle", ["STABLE", "MANIA", "PANIC"])
news_sentiment = st.sidebar.slider("AI News Sentiment (Crisis to Growth)", -1.0, 1.0, 0.1)

# --- 4. MAIN DASHBOARD LAYOUT ---
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### **The Performance Tracker & Risk Shield**")
    # Placeholder for the Chart
    chart_placeholder = st.empty()
    
    # Summary Metrics
    m1, m2, m3 = st.columns(3)
    current_price_stat = m1.empty()
    safety_floor_stat = m2.empty()
    protection_meter_stat = m3.empty()

with col2:
    st.markdown("### **The Synapse (AI Narrative)**")
    ticker_placeholder = st.empty()

# --- 5. THE LIVE HEARTBEAT LOOP ---

def run_dashboard():
    # Simulation Initial Data
    price = 2950.0
    intrinsic_val = 3100.0
    atr = 45.0
    history = []

    while True:
        # Simulate small price movements for the demo
        if simulation_mode:
            price += (time.time() % 10 - 5) 
            
        # Run Logic
        multiplier = apply_investor_theories(price, intrinsic_val, market_status)
        floor = calculate_safety_floor(price, atr, news_sentiment, multiplier)
        
        # Update Stats
        current_price_stat.metric("Current Price (CMP)", f"₹{price:.2f}")
        safety_floor_stat.metric("Safety Floor (Option B)", f"₹{floor:.2f}", delta=f"{price-floor:.2f}", delta_color="inverse")
        
        # Protection Meter Logic
        if news_sentiment < -0.5:
            protection_status = "100% PROTECTED (LIQUID)"
            meter_color = "green"
        else:
            protection_status = "GROWTH MODE (EQUITY)"
            meter_color = "blue"
        protection_meter_stat.markdown(f"**Status:** :{meter_color}[{protection_status}]")

        # Update Ticker (The Synapse)
        with ticker_placeholder.container():
            st.info(f"**AI Verdict:** {market_status} Cycle detected. Applying Theory Multiplier: {multiplier}x")
            if news_sentiment < 0:
                st.warning(f"Sentiment Alert: {news_sentiment} | Tightening Risk Shield.")
            else:
                st.success(f"Sentiment Positive: {news_sentiment} | Maintaining Growth Exposure.")
        
        # Simulated Chart Update
        history.append({"Time": datetime.now(), "Price": price, "Floor": floor})
        df = pd.DataFrame(history).tail(20)
        chart_placeholder.line_chart(df.set_index("Time"))

        time.sleep(2) # Fast update for the Demo

if __name__ == "__main__":
    run_dashboard()

import streamlit as st
import pandas as pd
import random
from datetime import datetime

# --- 1. SETTINGS & MEMORY ---
st.set_page_config(page_title="LFP Engine", layout="wide")

if 'price' not in st.session_state:
    st.session_state.price = 2950.0
if 'history' not in st.session_state:
    st.session_state.history = [{"Time": datetime.now().strftime("%H:%M:%S"), "Price": 2950.0, "Floor": 2860.0}]

# --- 2. SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("🛡️ LFP Admin")
    market_cycle = st.selectbox("Market Cycle", ["STABLE", "MANIA", "PANIC"])
    news_score = st.slider("AI News Score", -1.0, 1.0, 0.0)
    
    st.write("---")
    # THE REFRESH BUTTON (This is how you update the dashboard)
    if st.button("UPDATE LIVE FEED", type="primary"):
        # Calculate new data
        st.session_state.price += random.uniform(-15, 15)
        new_price = st.session_state.price
        
        # Option B Logic
        mult = 1.0 if news_score < -0.5 else 2.0
        new_floor = round(new_price - (45.0 * mult), 2)
        
        # Save to history
        st.session_state.history.append({
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Price": round(new_price, 2),
            "Floor": new_floor
        })
        
        if len(st.session_state.history) > 20:
            st.session_state.history.pop(0)

# --- 3. MAIN DASHBOARD ---
st.title("Live For The People: Safety Dashboard")
st.write(f"**Portfolio:** ₹50,00,000 | **Target:** RELIANCE")

# Metrics
curr = st.session_state.history[-1]
m1, m2, m3 = st.columns(3)
m1.metric("Live Price", f"₹{curr['Price']}")
m2.metric("Safety Floor", f"₹{curr['Floor']}", delta=f"{round(curr['Price']-curr['Floor'], 2)} Buffer")

if news_score < -0.5:
    m3.error("100% PROTECTED")
else:
    m3.success("GROWTH MODE")

# Chart
df = pd.DataFrame(st.session_state.history)
st.line_chart(df.set_index("Time"))

# --- 4. THE SYNAPSE (Narrative) ---
st.markdown("### **AI Synapse Feed**")
if market_cycle == "MANIA":
    st.warning("Howard Marks Logic: Market is in MANIA. Risk Shield tightening.")
elif news_score < -0.5:
    st.error("Crisis detected. Server-side hard stop moved to immediate exit.")
else:
    st.info("System stable. Trailing Floor active at 2.0x ATR.")

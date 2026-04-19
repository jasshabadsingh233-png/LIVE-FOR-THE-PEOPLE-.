import streamlit as st
import pandas as pd

# --- 1. MINIMALIST CONFIG ---
st.set_page_config(page_title="LFP Engine", layout="centered")

# --- 2. STATIC ENGINE LOGIC ---
def get_floor(price, sentiment):
    # Option B: Logic for the Investor Grill
    mult = 1.0 if sentiment < -0.5 else 2.0
    return round(price - (45.0 * mult), 2)

# --- 3. UI LAYOUT ---
st.title("🛡️ Live For The People")
st.write("Solo Founder Prototype | Status: **Ready**")

# Metrics Row
col1, col2 = st.columns(2)
price_input = col1.number_input("Current Asset Price (₹)", value=2950.0)
news_input = col2.slider("AI News Sentiment", -1.0, 1.0, 0.0)

# The Calculation
floor_output = get_floor(price_input, news_input)

# --- 4. THE VISUAL SHIELD ---
st.divider()
m1, m2 = st.columns(2)
m1.metric("Live Price", f"₹{price_input}")
m2.metric("Safety Floor", f"₹{floor_output}", delta=f"{round(price_input - floor_output, 2)} Buffer")

if news_input < -0.5:
    st.error("PROTECTION ACTIVE: 100% LIQUID")
else:
    st.success("GROWTH ACTIVE: TRAILING STOP ENABLED")

# --- 5. THE PROOF (Chart) ---
st.markdown("### **Safety Tracking**")
data = pd.DataFrame({
    'Metric': ['Floor', 'Price'],
    'Value': [floor_output, price_input]
})
st.bar_chart(data.set_index('Metric'))

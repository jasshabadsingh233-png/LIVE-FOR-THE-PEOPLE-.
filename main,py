import streamlit as st
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="LFP Engine")

# 2. Simple Logic
def calculate_shield(price, news):
    # Option B Multiplier: 1x for Crisis, 2x for Stable
    mult = 1.0 if news < -0.5 else 2.0
    return price - (45.0 * mult)

# 3. Main Display
st.title("🛡️ LFP: Safety Shield")

# Input Section
val = st.number_input("Enter Market Price (₹)", value=2950.0)
news = st.slider("News Sentiment", -1.0, 1.0, 0.0)

# Shield Calculation
shield_price = calculate_shield(val, news)

# Big Metrics
st.divider()
c1, c2 = st.columns(2)
c1.metric("Current Price", f"₹{val}")
c2.metric("Safety Floor", f"₹{shield_price}")

# Status Narrative
if news < -0.5:
    st.error("SYSTEM STATUS: 100% PROTECTED (EXIT TRIGGERED)")
else:
    st.success("SYSTEM STATUS: GROWTH MODE (TRAILING FLOOR ACTIVE)")

# 4. Simple Visual
st.bar_chart(pd.DataFrame({"Price": [val], "Floor": [shield_price]}).T)

import streamlit as st
import pandas as pd
import numpy as np

# This MUST be the first Streamlit command
st.set_page_config(page_title="Sovereign Finance", layout="wide")

# Now the rest of your code
st.title("⚡ SOVEREIGN: LIVE FOR THE PEOPLE")
st.write("---")

cols = st.columns(4)
cols[0].metric("NIFTY 50", "22,450", "+1.2%")
cols[1].metric("BRASS (IND)", "₹482/kg", "+2.4%")
cols[2].metric("USD/INR", "₹83.45", "-0.1%")
cols[3].metric("AI CONFIDENCE", "94%", "OPTIMAL")

st.write("### 🎯 Hybrid AI Asset Selection")
data = {
    "Asset": ["Equity Alpha", "Commodity Brass", "Fintech Index", "Liquid Gold"],
    "Sentiment": [88, 72, 94, 45],
    "Action": ["STRONG BUY", "HOLD", "STRONG BUY", "REDUCE"]
}
st.table(pd.DataFrame(data))

st.write("---")
st.subheader("📈 Performance Projection")
chart_data = pd.DataFrame(np.random.randn(20, 2), columns=['Market', 'Sovereign AI'])
st.line_chart(chart_data)

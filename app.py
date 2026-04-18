import streamlit as st
import pandas as pd
import yfinance as yf
import datetime

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Sovereign Global Terminal", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    div[data-testid="stMetricValue"] { color: #00ffc8; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌐 SOVEREIGN GLOBAL TERMINAL")
st.caption("Live Data Feed | Powered by Live For The People AI")

# --- 2. LIVE TICKER FUNCTION ---
def get_live_price(ticker_symbol):
    try:
        data = yf.Ticker(ticker_symbol).history(period="1d")
        latest_price = data['Close'].iloc[-1]
        prev_price = data['Open'].iloc[-1]
        delta = ((latest_price - prev_price) / prev_price) * 100
        return round(latest_price, 2), f"{round(delta, 2)}%"
    except:
        return "N/A", "0%"

# --- 3. TOP MARKET BAR ---
st.write("### 🌍 Major Indices")
m1, m2, m3, m4 = st.columns(4)

# Fetching real data
nifty_p, nifty_d = get_live_price("^NSEI")
gold_p, gold_d = get_live_price("GC=F")
btc_p, btc_d = get_live_price("BTC-USD")
oil_p, oil_d = get_live_price("CL=F")

m1.metric("NIFTY 50", nifty_p, nifty_d)
m2.metric("GOLD (OZ)", f"${gold_p}", gold_d)
m3.metric("BITCOIN", f"${btc_p}", btc_d)
m4.metric("CRUDE OIL", f"${oil_p}", oil_d)

# --- 4. INVESTING.COM STYLE SEARCH ---
st.write("---")
st.subheader("🔍 Look up any Asset (Stock, Forex, Crypto)")
search_ticker = st.text_input("Enter Ticker (e.g., RELIANCE.NS, TSLA, EURINR=X)", "RELIANCE.NS")

if search_ticker:
    ticker_data = yf.Ticker(search_ticker)
    hist = ticker_data.history(period="1mo")
    
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.write(f"**Current Price:** ${hist['Close'].iloc[-1]:.2f}")
        st.write(f"**High (1mo):** ${hist['High'].max():.2f}")
        st.write(f"**Low (1mo):** ${hist['Low'].min():.2f}")
    with col_b:
        st.line_chart(hist['Close'])

# --- 5. INDUSTRIAL TRACKER (BRASS) ---
st.write("---")
st.subheader("🛠️ Industrial Commodity Monitor")
st.info("Copper and Brass trends are derived from LME (London Metal Exchange) correlations.")
copper_p, copper_d = get_live_price("HG=F")
st.metric("LME Copper (Base for Brass Pricing)", f"${copper_p}", copper_d)

st.write("---")
st.caption("© 2026 Sovereign Systems | Data provided by Yahoo Finance API")

import streamlit as st
import time

# --- 1. CORE LOGIC CLASS ---
class LFP_Engine:
    def __init__(self, capital):
        self.capital = capital
        self.targets = {'equities': 0.50, 'alternatives': 0.35, 'fixed_income': 0.15}
        
        # State variables for the "New Features"
        self.crash_triggered = False
        self.lowest_price_seen = float('inf')
        self.recovery_threshold = 0.02  # 2% Stability Bounce
        self.fee_buffer = 1.005         # 0.5% extra for fees

    def update(self, open_price, current_price, current_equity_value):
        drop = (open_price - current_price) / open_price
        
        # Phase 1: Detect 10% Crash
        if not self.crash_triggered:
            if drop >= 0.10:
                self.crash_triggered = True
                self.lowest_price_seen = current_price
                return "⚠️ CRASH DETECTED"
        
        # Phase 2: Stability Search
        else:
            if current_price < self.lowest_price_seen:
                self.lowest_price_seen = current_price
            
            bounce = (current_price - self.lowest_price_seen) / self.lowest_price_seen
            if bounce >= self.recovery_threshold:
                return "✅ STABILITY REACHED"
        
        return "MONITORING"

# --- 2. STREAMLIT DASHBOARD SETUP ---
st.set_page_config(page_title="LFP Rebound Dashboard", layout="wide")
st.title("LFP Active Rebound Engine 🚀")

# Initialize Engine in Session State (The "Memory" fix)
if 'engine' not in st.session_state:
    st.session_state.engine = LFP_Engine(capital=10000)

# Sidebar Inputs
st.sidebar.header("Market Feed")
open_p = st.sidebar.number_input("Daily Open ($)", value=100.0)
current_p = st.sidebar.number_input("Current Price ($)", value=100.0)
equity_val = st.sidebar.number_input("Current Stock Value ($)", value=4000.0)

# --- 3. RUN ENGINE & DISPLAY NEW FEATURES ---
status = st.session_state.engine.update(open_p, current_p, equity_val)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Market Change", f"{((current_p - open_p)/open_p):.1%}")

with col2:
    crash_status = "🔴 YES" if st.session_state.engine.crash_triggered else "🟢 NO"
    st.metric("10% Crash Triggered?", crash_status)

with col3:
    if st.session_state.engine.crash_triggered:
        bounce = (current_p - st.session_state.engine.lowest_price_seen) / st.session_state.engine.lowest_price_seen
        st.metric("Stability Bounce", f"{bounce:.1%}", delta="Target: 2%")
    else:
        st.metric("Stability Bounce", "N/A")

# Final Action Output
st.divider()
if status == "✅ STABILITY REACHED":
    target = st.session_state.engine.capital * 0.50
    gap = (target - equity_val) * st.session_state.engine.fee_buffer
    st.success(f"STRATEGY EXECUTED: Buy ${gap:.2f} of Stocks using Crypto.")
    if st.button("Reset Engine"):
        del st.session_state.engine
        st.rerun()
elif st.session_state.engine.crash_triggered:
    st.info("Waiting for 2% stability bounce before buying...")
else:
    st.write("Market is stable. No action required.")

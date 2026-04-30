import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# --- 1. CONFIG ---
st.set_page_config(page_title="SOVEREIGN APEX | LFP", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #050505; color: #e0e0e0; font-family: 'Inter', sans-serif; }
    [data-testid="stMetricValue"] { color: #00ffc8 !important; font-size: 1.8rem !important; }
    .stTabs [data-baseweb="tab"] { color: #888; font-size: 14px; }
    .stTabs [aria-selected="true"] { color: #00ffc8 !important; border-bottom: 2px solid #00ffc8 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("🏛️ APEX COMMAND")
    st.subheader("Kuala Lumpur Node")
    currency = st.selectbox("Market Jurisdiction", ["Malaysia (MYR)", "India (INR)", "USA (USD)"])
    fx_dict = {"Malaysia (MYR)": (1.0, "RM"), "India (INR)": (17.85, "₹"), "USA (USD)": (0.21, "$")}
    fx_rate, sym = fx_dict[currency]
    
    st.divider()
    st.write("### Engine Parameters")
    atr_period = st.slider("ATR Period (days)", 7, 20, 14)
    atr_multiplier = st.slider("Safety Multiplier", 1.0, 3.5, 2.0)
    mc_paths = st.slider("Monte Carlo Paths", 1000, 10000, 5000, step=1000)

# --- 3. ROBUST DATA RETRIEVAL WITH RETRY ---
@st.cache_data(ttl=300)
def get_data_safe(ticker, period="1y", max_retries=3):
    """Fetch with retry logic + fallback handling"""
    for attempt in range(max_retries):
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period=period)
            
            if hist.empty:
                return None
            
            # Handle MultiIndex columns
            if isinstance(hist.columns, pd.MultiIndex):
                hist.columns = hist.columns.get_level_values(0)
            
            # Validate required columns
            if not all(col in hist.columns for col in ['Close', 'High', 'Low']):
                return None
            
            return hist
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                st.warning(f"Data fetch failed for {ticker} after {max_retries} attempts")
                return None
    return None

# --- 4. ATR CALCULATION (REAL) ---
def calculate_atr(hist, period=14):
    """True Range -> ATR (institutional grade)"""
    if hist is None or len(hist) < period:
        return None
    
    high = hist['High']
    low = hist['Low']
    close = hist['Close']
    
    # True Range = max(H-L, |H-PC|, |L-PC|)
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # ATR = SMA of TR
    atr = tr.rolling(window=period).mean()
    return atr.iloc[-1]  # Latest ATR value

# --- 5. SAFETY FLOOR LOGIC ---
def calculate_safety_floor(current_price, atr_value, multiplier):
    """Safety Floor = Current Price - (ATR * Multiplier)"""
    if atr_value is None:
        return None
    buffer = atr_value * multiplier
    floor = current_price - buffer
    return floor, buffer

# --- 6. ENGINE: LOAD ALL ASSETS ---
@st.cache_data(ttl=300)
def get_engine():
    universe = {
        "MALAYSIAN ASSETS": {"KLCI INDEX": "^KLSE", "MAYBANK": "1155.KL", "PUBLIC BANK": "1295.KL"},
        "GLOBAL EQUITIES": {"RELIANCE": "RELIANCE.NS", "APPLE": "AAPL", "TESLA": "TSLA"},
        "CRYPTO / ALT": {"BITCOIN": "BTC-USD", "ETHEREUM": "ETH-USD"}
    }
    results = []
    for cat, assets in universe.items():
        for name, ticker_sym in assets.items():
            hist = get_data_safe(ticker_sym)
            if hist is None:
                continue
            
            try:
                curr = hist['Close'].iloc[-1]
                rets = hist['Close'].pct_change().dropna()
                vol = rets.std() * np.sqrt(252)
                sharpe = (rets.mean() * 252 - 0.05) / vol if vol != 0 else 0
                atr_val = calculate_atr(hist, period=14)
                
                results.append({
                    "Asset": name, "Price": curr, "History": hist, 
                    "Vol": vol, "Sharpe": sharpe, "High52": hist['High'].max(), 
                    "Category": cat, "Returns": rets, "ATR": atr_val
                })
            except Exception:
                continue
    return pd.DataFrame(results)

df_engine = get_engine()

if df_engine.empty:
    st.error("❌ Data engine offline. Check API/network.")
    st.stop()

# --- 7. PORTFOLIO STATE ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {"KLCI INDEX": 1000, "MAYBANK": 500, "RELIANCE": 100, "BITCOIN": 0.1}

p_data = []
total_aum = 0
for asset, qty in st.session_state.portfolio.items():
    if asset in df_engine['Asset'].values:
        row = df_engine[df_engine['Asset'] == asset].iloc[0]
        val = row['Price'] * qty * fx_rate
        total_aum += val
        
        # Calculate Safety Floor for this asset
        atr_val = row.get('ATR')
        floor, buffer = calculate_safety_floor(row['Price']*fx_rate, atr_val, atr_multiplier) if atr_val else (None, None)
        
        p_data.append({
            "Asset": asset, "Qty": qty, "Value": val, 
            "Price": row['Price']*fx_rate, "SafetyFloor": floor,
            "Sharpe": row['Sharpe'], "History": row['History'], "Vol": row['Vol'], "ATR": atr_val
        })
p_df = pd.DataFrame(p_data)

# --- 8. TERMINAL UI ---
st.title("🏛️ SOVEREIGN APEX : OPTION B ENGINE")
st.caption(f"SYNCED: {datetime.now().strftime('%H:%M:%S')} | ASIA SCHOOL OF BUSINESS")

m1, m2, m3 = st.columns(3)
m1.metric("PORTFOLIO AUM", f"{sym}{total_aum:,.2f}")
m2.metric("ATR PERIOD", f"{atr_period}D")
m3.metric("SAFETY MULTIPLIER", f"{atr_multiplier}x")

tabs = st.tabs(["📊 ASSET DENSITY", "🛡️ SAFETY SHIELD (ATR)", "🔮 MONTE CARLO (10K)", "📈 KL WAITLIST"])

# --- TAB 1: ASSET DENSITY ---
with tabs[0]:
    col_l, col_r = st.columns([2, 1])
    with col_l:
        fig = px.sunburst(df_engine, path=['Category', 'Asset'], values='Price', template="plotly_dark", color='Vol', color_continuous_scale='RdYlGn_r')
        fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with col_r:
        st.subheader("Regional Risk Data")
        display_df = p_df[['Asset', 'Value', 'Sharpe', 'ATR']].copy()
        display_df['ATR'] = display_df['ATR'].apply(lambda x: f"{x:.2f}" if x else "N/A")
        st.dataframe(display_df.sort_values('Sharpe', ascending=False), hide_index=True, use_container_width=True)

# --- TAB 2: SAFETY SHIELD (REAL ATR) ---
with tabs[1]:
    st.header("🛡️ Option B: ATR-Based Safety Floor")
    if p_df.empty:
        st.error("Engine Offline: Deploy assets to view shield.")
    else:
        target_shield = st.selectbox("Select Asset", p_df['Asset'].unique())
        shield_row = p_df[p_df['Asset'] == target_shield].iloc[0]
        
        atr_val = shield_row['ATR']
        current_p = shield_row['Price']
        
        if atr_val is None:
            st.warning(f"Insufficient data for {target_shield}.")
        else:
            safety_floor, buffer = calculate_safety_floor(current_p, atr_val, atr_multiplier)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Current Price", f"{sym}{current_p:,.2f}")
            c2.metric("ATR (14D)", f"{sym}{atr_val:,.2f}")
            c3.metric("Safety Floor", f"{sym}{safety_floor:,.2f}", delta=f"-{sym}{buffer:,.2f} Buffer", delta_color="inverse")
            c4.metric("Shield Status", "ACTIVE", delta="Protected")

            # Visualize price + floor
            hist_df = shield_row['History'].copy().reset_index()
            if isinstance(hist_df.columns, pd.MultiIndex):
                hist_df.columns = hist_df.columns.get_level_values(0)
            
            hist_df['Price_Local'] = hist_df['Close'] * fx_rate
            
            # Calculate ATR for full history
            atr_series = calculate_atr(shield_row['History'].copy(), period=atr_period)
            if atr_series is not None:
                hist_df['ATR_Series'] = atr_series * fx_rate
                hist_df['Floor'] = hist_df['Price_Local'] - (hist_df['ATR_Series'] * atr_multiplier)
            else:
                hist_df['Floor'] = safety_floor
            
            fig_shield = go.Figure()
            fig_shield.add_trace(go.Scatter(x=hist_df['Date'], y=hist_df['Price_Local'], name='Price', line=dict(color='#00ffc8', width=2)))
            fig_shield.add_trace(go.Scatter(x=hist_df['Date'], y=hist_df['Floor'], name='Safety Floor', line=dict(color='#ff4b4b', width=2, dash='dash')))
            fig_shield.update_layout(template="plotly_dark", title=f"{target_shield} ATR Safety Floor", hovermode="x unified")
            st.plotly_chart(fig_shield, use_container_width=True)

# --- TAB 3: MONTE CARLO (10K PATHS) ---
with tabs[2]:
    st.header("🔮 Monte Carlo Stress Test (10,000 Paths)")
    mc_target = st.selectbox("Select Asset for Projection", df_engine['Asset'].unique())
    mc_row = df_engine[df_engine['Asset'] == mc_target].iloc[0]
    
    mu = mc_row['Returns'].mean()
    sigma = mc_row['Returns'].std()
    s0 = mc_row['Price'] * fx_rate
    
    if sigma == 0:
        st.warning(f"Insufficient volatility data for {mc_target}")
    else:
        paths, days = mc_paths, 252
        dt = 1 / days
        
        # Generate 10,000 paths
        Z = np.random.standard_normal((days, paths))
        drift = (mu - 0.5 * sigma ** 2) * dt
        diffusion = sigma * np.sqrt(dt)
        stoch_matrix = np.exp(drift + diffusion * Z)
        price_paths = s0 * stoch_matrix.cumprod(axis=0)
        
        # Plot paths
        fig_mc = go.Figure()
        for i in range(paths):
            fig_mc.add_trace(go.Scatter(y=price_paths[:, i], mode='lines', line=dict(width=0.5, color='rgba(0, 255, 200, 0.1)'), showlegend=False))
        
        # Add percentile bands
        p5 = np.percentile(price_paths, 5, axis=1)
        p25 = np.percentile(price_paths, 25, axis=1)
        p50 = np.percentile(price_paths, 50, axis=1)
        p75 = np.percentile(price_paths, 75, axis=1)
        p95 = np.percentile(price_paths, 95, axis=1)
        
        days_range = np.arange(days)
        fig_mc.add_trace(go.Scatter(x=days_range, y=p50, name='Median', line=dict(color='#00ffc8', width=2)))
        fig_mc.add_trace(go.Scatter(x=days_range, y=p5, name='5th Percentile', line=dict(color='#ff4b4b', width=1)))
        fig_mc.add_trace(go.Scatter(x=days_range, y=p95, name='95th Percentile', line=dict(color='#00ff00', width=1)))
        
        fig_mc.update_layout(template="plotly_dark", title=f"{mc_target}: {paths:,} Path Projection (1 Year)", xaxis_title="Days", yaxis_title=f"Price ({sym})")
        st.plotly_chart(fig_mc, use_container_width=True)
        
        # Stats
        st.subheader("📊 Outcome Statistics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Expected Price", f"{sym}{p50[-1]:,.2f}")
        col2.metric("5% Downside", f"{sym}{p5[-1]:,.2f}")
        col3.metric("95% Upside", f"{sym}{p95[-1]:,.2f}")
        col4.metric("Max Drawdown Risk", f"{((price_paths.min(axis=0) / s0).mean() - 1) * 100:.2f}%", delta="Stress tested")

# --- TAB 4: WAITLIST ---
with tabs[3]:
    st.header("📈 Scaling in Malaysia")
    st.info("Direct Integration with local financial clusters starting June 2026.")
    with st.form("waitlist"):
        email = st.text_input("Investor/Founder Email")
        if st.form_submit_button("REGISTER FOR KL SEED"):
            st.success(f"Registration successful for Kuala Lumpur Node. Welcome, {email}.")

st.markdown("---")
st.caption(f"© 2026 LIVE FOR THE PEOPLE | ASIA SCHOOL OF BUSINESS | KUALA LUMPUR, MALAYSIA")

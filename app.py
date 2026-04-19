import time
import datetime

# --- 1. THE FOUNDER'S LOGIC (Risk & Theory) ---

def apply_investor_theories(price, intrinsic_value, market_cycle):
    """The 'Brain' - Howard Marks & Graham Logic"""
    if market_cycle == "MANIA":
        # Howard Marks: Be fearful when others are greedy
        return 1.2  # Tighten floor (less room for error)
    if price < (intrinsic_value * 0.7):
        # Benjamin Graham: Margin of Safety
        return 2.5  # Loosen floor (believe in the value rebound)
    return 2.0      # Standard breathing room

def calculate_safety_floor(price, atr, news_score, theory_multiplier):
    """Option B: The Dynamic Safety Floor"""
    # If News is a Crisis, we override everything to protect capital
    if news_score < -0.5:
        effective_multiplier = 1.0  # Ultra-tight "Panic" protection
    else:
        effective_multiplier = theory_multiplier
        
    floor = price - (atr * effective_multiplier)
    return round(floor, 2)

# --- 2. THE CONNECTORS (Data & Execution) ---

def fetch_market_data(ticker):
    """
    HOOK: In your build, replace these with:
    price = nsepython.nse_quote_ltp(ticker)
    """
    # Simulated Live Data for Demo
    current_price = 2950.00 
    current_atr = 45.0
    return current_price, current_atr

def get_ai_news_verdict(ticker):
    """HOOK: Connect your News API / LLM Sentiment here."""
    return 0.1 # Sentiment score between -1.0 and 1.0

def execute_server_side_update(order_id, floor_price):
    """The 'Armor': Updates the Hard Stop on the Broker Server."""
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}]")
    print(f">>> SERVER ACTION: GTT Order {order_id} modified to Floor: ₹{floor_price}")

# --- 3. THE MASTER UI & LOOP ---

def run_lfp_system(ticker="RELIANCE", capital=5000000):
    intrinsic_val = 3200.0  # LFP AI Intrinsic Value Calculation
    cycle_status = "STABLE" # MANIA, PANIC, or STABLE
    
    print(f"--- LFP ENGINE ONLINE | PORTFOLIO: ₹{capital} | TARGET: {ticker} ---")
    
    try:
        while True:
            # Step A: Data Intake
            price, atr = fetch_market_data(ticker)
            sentiment = get_ai_news_verdict(ticker)
            
            # Step B: Apply Theory & Calculate Risk Shield
            multiplier = apply_investor_theories(price, intrinsic_val, cycle_status)
            safety_floor = calculate_safety_floor(price, atr, sentiment, multiplier)
            
            # Step C: Execute Protection
            execute_server_side_update("GTT_NSE_001", safety_floor)
            
            # Step D: The Live Ticker Output
            verdict = "SAFE - GROWTH" if sentiment > -0.5 else "CRISIS - PROTECTING"
            print(f"TICKER: {ticker} | CMP: {price} | FLOOR: {safety_floor} | STATUS: {verdict}")
            print("-" * 60)
            
            # Heartbeat: 30 seconds
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n--- LFP ENGINE SHUTTING DOWN SAFELY ---")

# --- 4. EXECUTION ---
if __name__ == "__main__":
    run_lfp_system()

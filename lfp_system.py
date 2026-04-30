# LFP_SYSTEM.PY

class LFPUser:
    """Stores user profile and target asset allocations."""
    def __init__(self, income=85000, profession="Software Engineer", capital=10000):
        self.income = income
        self.profession = profession
        self.risk_appetite = 0.62  # Medium-High
        self.total_capital = capital
        
        # Defining your Asset Type buckets 📊
        self.targets = {
            'equities': 0.50,      # 50% Stocks
            'alternatives': 0.35,  # 35% Max Crypto limit
            'fixed_income': 0.15   # 15% Bonds/Cash buffer
        }

class ActiveRebound:
    """Monitors market for a 10% crash and waits for stability."""
    def __init__(self, user):
        self.user = user
        self.crash_triggered = False
        self.lowest_price = float('inf')
        self.fee_buffer = 1.005 # 0.5% extra for fees 💸

    def check_market(self, open_price, current_price, current_equity_value):
        # Calculate daily drop percentage
        drop = (open_price - current_price) / open_price
        
        # Step 1: Detect the 'Big Crash' (10%)
        if not self.crash_triggered and drop >= 0.10:
            self.crash_triggered = True
            self.lowest_price = current_price
            print(f"⚠️ Crash Detected! Price dropped 10%. Monitoring for stability...")

        # Step 2: Once crashed, wait for 2% stability bounce
        if self.crash_triggered:
            if current_price < self.lowest_price:
                self.lowest_price = current_price # Reset to new bottom
            
            bounce = (current_price - self.lowest_price) / self.lowest_price
            if bounce >= 0.02:
                return self.calculate_rebalance(current_equity_value)

        return "Status: Monitoring Market"

    def calculate_rebalance(self, current_equity_value):
        # Calculate "Just Enough" to return Stocks to 50% ⚖️
        target_value = self.user.total_capital * self.user.targets['equities']
        gap = target_value - current_equity_value
        
        # Calculate Crypto sale including the "Little Bit Extra" for fees
        sell_amount = gap * self.fee_buffer
        
        return f"✅ SUCCESS: Sell ${sell_amount:.2f} of Crypto to buy Stocks."

# --- EXECUTION SECTION ---
# This part simulates the engine running
user = LFPUser(capital=10000)
engine = ActiveRebound(user)

# Example: Morning Open is $100, Price drops to $89 (11% crash), then bounces to $91
print(engine.check_market(open_price=100, current_price=89, current_equity_value=4000))
print(engine.check_market(open_price=100, current_price=91, current_equity_value=4000))

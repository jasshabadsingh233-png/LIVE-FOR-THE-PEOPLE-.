class LFP_System:
    def __init__(self, capital=10000):
        # 1. User Profile & Risk 0.62
        self.capital = capital
        self.targets = {
            'equities': 0.50,      # 50% Stocks
            'alternatives': 0.35,  # 35% Max Crypto
            'fixed_income': 0.15   # 15% Bonds/Cash
        }
        
        # 2. Logic State
        self.crash_triggered = False
        self.lowest_price_seen = float('inf')
        self.recovery_threshold = 0.02  # 2% Stability Bounce
        self.fee_buffer = 1.005         # 0.5% extra for fees

    def update(self, open_price, current_price, current_equity_value):
        drop = (open_price - current_price) / open_price
        
        # PHASE 1: Detection
        if not self.crash_triggered:
            if drop >= 0.10:
                self.crash_triggered = True
                self.lowest_price_seen = current_price
                print(f"--- ⚠️ CRASH DETECTED ({drop:.1%}) ---")
                print(f"Action: Holding until price stabilizes 2% above ${current_price}")
            else:
                print(f"Status: Monitoring. Current change: -{drop:.1%}")

        # PHASE 2: Stability Search
        else:
            if current_price < self.lowest_price_seen:
                self.lowest_price_seen = current_price
                print(f"--- 📉 NEW LOW: ${current_price} ---")
            
            bounce = (current_price - self.lowest_price_seen) / self.lowest_price_seen
            
            if bounce >= self.recovery_threshold:
                return self.execute(current_equity_value)
            else:
                print(f"Status: Waiting for stability. Current bounce: {bounce:.1%}/2.0%")

        return None

    def execute(self, current_equity_value):
        target_value = self.capital * self.targets['equities']
        gap = target_value - current_equity_value
        total_to_sell = gap * self.fee_buffer
        
        print(f"--- ✅ STABILITY DETECTED ---")
        print(f"Result: Selling ${total_to_sell:.2f} of Crypto to rebalance Stocks.")
        return total_to_sell

# --- TEST THE SYSTEM ---
lfp = LFP_System(capital=10000)

# Simulate the sequence:
print("Step 1: Small dip...")
lfp.update(100, 95, 4500) 

print("\nStep 2: The 10% Crash...")
lfp.update(100, 89, 4000) 

print("\nStep 3: A small wobble (not 2% yet)...")
lfp.update(100, 89.5, 4000) 

print("\nStep 4: The 2% Recovery...")
lfp.update(100, 91, 4000)

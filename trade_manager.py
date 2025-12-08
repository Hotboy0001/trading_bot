import MetaTrader5 as mt5
from config import Config

class TradeManager:
    @staticmethod
    def manage_positions():
        """
        Manages open positions:
        1. Checks for Trailing Stop conditions
        """
        if not Config.TRAILING_ENABLE:
            return

        # Filter by Magic Number to avoid managing manual/other bot trades
        positions = mt5.positions_get()
        if positions is None or len(positions) == 0:
            return

        for pos in positions:
            # Skip trades not belonging to this bot
            if pos.magic != Config.MAGIC_NUMBER:
                continue
                
            symbol = pos.symbol
            ticket = pos.ticket
            entry_price = pos.price_open
            current_price = pos.price_current
            sl = pos.sl
            tp = pos.tp
            pos_type = pos.type # 0 = BUY, 1 = SELL
            
            # Calculate Risk (R) distance
            # Initial SL distance is needed. Since we don't store it, we can estimate 
            # or we can just use the current price distance if SL hasn't moved.
            # But better: We know our strategy uses dynamic SL. 
            # Let's assume the initial risk was (Entry - SL).
            # If SL has already been moved, this calculation changes.
            # A robust way is to check the comment or just use current price vs entry.
            
            if pos_type == mt5.ORDER_TYPE_BUY:
                if sl == 0: continue # No SL, can't calc R
                
                # Current R-Multiple
                # Note: If SL was moved to BE, 'initial_risk' is lost. 
                # We'll use a simplified logic: 
                # If Price > Entry + (3.5 * (Entry - OriginalSL)) -> Move SL
                # Since we don't know OriginalSL, we can infer it or just use a fixed pip trail?
                # User said "Activate at 1:3.5".
                # Let's assume the current SL is the initial SL if it's below entry.
                
                # Problem: If we moved SL, we lose the reference.
                # Solution: We can't perfectly know initial risk without a database.
                # Heuristic: We will trail based on current price distance.
                # Let's calculate the "Current Profit Pips".
                
                profit_points = current_price - entry_price
                
                # We need the 'Risk' value. 
                # Let's try to deduce it from the TP? TP is usually set at 3R, 5R, 7R.
                # So Risk = (TP - Entry) / RR.
                # If we can't find RR, we assume a standard risk?
                # Or better: Just use the current SL if it's below entry.
                
                current_risk = entry_price - sl
                if current_risk <= 0: current_risk = 0.0001 # Prevent div by zero (SL above entry)
                
                # If SL is already above entry (locked profit), we use a different logic?
                # No, let's just use the 'current_risk' as the unit R if SL < Entry.
                # If SL > Entry, we need to know the original risk.
                # This is tricky without storage.
                
                # ALTERNATIVE: Use the comment! 
                # We saved "Score:X" in comment. We know Score 1=1:3, 2=1:5, 3=1:7.
                # So we can reverse calc the risk!
                
                rr_target = 3.0
                if "Score:2" in pos.comment: rr_target = 5.0
                if "Score:3" in pos.comment: rr_target = 7.0
                
                # Initial Risk = (TP - Entry) / rr_target
                if tp > 0:
                    initial_risk = (tp - entry_price) / rr_target
                else:
                    initial_risk = 0.0010 # Fallback 10 pips
                
                current_r = profit_points / initial_risk
                
                if current_r >= Config.TRAILING_ACTIVATE_RR:
                    # Activate Trailing
                    # Target SL = CurrentPrice - (1.5 * InitialRisk)
                    new_sl = current_price - (Config.TRAILING_DIST_RR * initial_risk)
                    
                    # Only move SL up
                    if new_sl > sl:
                        print(f"[TRAIL] Updating BUY {ticket}: Profit {current_r:.2f}R. Moving SL to {new_sl:.5f}")
                        request = {
                            "action": mt5.TRADE_ACTION_SLTP,
                            "position": ticket,
                            "sl": new_sl,
                            "tp": tp,
                            "magic": Config.MAGIC_NUMBER,
                        }
                        mt5.order_send(request)

            elif pos_type == mt5.ORDER_TYPE_SELL:
                if sl == 0: continue
                
                profit_points = entry_price - current_price
                
                rr_target = 3.0
                if "Score:2" in pos.comment: rr_target = 5.0
                if "Score:3" in pos.comment: rr_target = 7.0
                
                if tp > 0:
                    initial_risk = (entry_price - tp) / rr_target
                else:
                    initial_risk = 0.0010
                
                current_r = profit_points / initial_risk
                
                if current_r >= Config.TRAILING_ACTIVATE_RR:
                    # Target SL = CurrentPrice + (1.5 * InitialRisk)
                    new_sl = current_price + (Config.TRAILING_DIST_RR * initial_risk)
                    
                    # Only move SL down
                    if new_sl < sl or sl == 0:
                        print(f"[TRAIL] Updating SELL {ticket}: Profit {current_r:.2f}R. Moving SL to {new_sl:.5f}")
                        request = {
                            "action": mt5.TRADE_ACTION_SLTP,
                            "position": ticket,
                            "sl": new_sl,
                            "tp": tp,
                            "magic": Config.MAGIC_NUMBER,
                        }
                        mt5.order_send(request)

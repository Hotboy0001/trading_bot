import time
import sys
import os
import MetaTrader5 as mt5
from config import Config
from market_data import MarketData
from strategy import TurtleSoupStrategy
from execution import Execution
from risk_manager import RiskManager

from news_manager import NewsManager
from trade_manager import TradeManager
from datetime import datetime

def main():
    print("Starting Turtle Soup Trading Bot...")
    
    # Check if setup has been run, but don't enforce it
    if not os.path.exists('.env'):
        pass # Silent fallback to manual login

    print("Starting Turtle Soup Trading Bot...")
    
    # Initialize Market Data
    md = MarketData()
    if not md.connect():
        sys.exit(1)
        
    # Initialize Managers
    news_manager = NewsManager()
    
    # Daily Loss Tracking
    current_day = datetime.now().day
    daily_start_balance = 0.0
    
    # Get initial balance
    account_info = mt5.account_info()
    if account_info:
        daily_start_balance = account_info.balance
    
    try:
        while True:
            # 0. Manage Open Positions (Trailing Stop)
            TradeManager.manage_positions()
            
            # Get account info
            account_info = mt5.account_info()
            if account_info is None:
                print("Failed to get account info. Skipping this cycle.")
                time.sleep(60)
                continue
            
            # 1. Daily Loss Limit Check
            # Reset daily balance if new day
            now = datetime.now()
            if now.day != current_day:
                current_day = now.day
                daily_start_balance = account_info.balance
                print(f"[DAILY] New Day! Resetting Daily Start Balance to ${daily_start_balance:.2f}")
            
            current_equity = account_info.equity
            daily_loss_percent = ((daily_start_balance - current_equity) / daily_start_balance) * 100
            
            if daily_loss_percent >= Config.DAILY_LOSS_LIMIT:
                print(f"🛑 DAILY LOSS LIMIT HIT! Loss: {daily_loss_percent:.2f}% (Limit: {Config.DAILY_LOSS_LIMIT}%). Pausing trading for today.")
                time.sleep(3600) # Sleep 1 hour
                continue
            
            account_balance = account_info.balance
            # print(f"Account Balance: ${account_balance:.2f} | Daily Loss: {daily_loss_percent:.2f}%")
            
            for base_symbol in Config.SYMBOLS:
                # 2. News Filter Check
                if news_manager.is_news_impact(base_symbol):
                    continue
                
                # Resolve Broker Specific Symbol (handles suffixes like EURUSD.m)
                symbol = md.resolve_symbol(base_symbol)
                if not symbol:
                    continue
                    
                print(f"--- Analyzing {symbol} ---")
                
                # 3. Analyze Higher Timeframes (HTF)
                htf_bias = None
                confluence_score = 0
                biases = []
                
                for tf in Config.HTF_TIMEFRAMES:
                    # print(f"Analyzing HTF: {tf}") # Reduce noise
                    df_htf = md.get_rates(symbol, tf, num_bars=500)
                    if df_htf is not None and not df_htf.empty:
                        strategy_htf = TurtleSoupStrategy(df_htf)
                        bias = strategy_htf.analyze_htf()
                        
                        if bias:
                            print(f"[{symbol}] HTF SETUP DETECTED on {tf}: {bias}")
                            biases.append(bias)
                
                # Check Confluence
                if biases:
                    # Check if all detected biases are in the same direction
                    if all(b == 'BULLISH' for b in biases):
                        htf_bias = 'BULLISH'
                        confluence_score = len(biases)
                    elif all(b == 'BEARISH' for b in biases):
                        htf_bias = 'BEARISH'
                        confluence_score = len(biases)
                    else:
                        print(f"[{symbol}] Conflicting HTF signals. Skipping.")
                        htf_bias = None
                
                # 4. Execute on Lower Timeframes (LTF) if Bias exists
                if htf_bias:
                    # Determine Risk:Reward Ratio and Max Lot Cap based on Confluence
                    rr_ratio = 3.0
                    max_lot_cap = 0.03  # Low confidence cap
                    
                    if confluence_score == 2:
                        rr_ratio = 5.0
                        max_lot_cap = 0.06 # Medium confidence cap
                    elif confluence_score >= 3:
                        rr_ratio = 7.0
                        max_lot_cap = 0.10 # High confidence cap
                    
                    print(f"[{symbol}] Switching to LTF Execution for {htf_bias} bias (Score: {confluence_score}, RR: 1:{rr_ratio}, MaxLot: {max_lot_cap})...")
                    
                    # Check LTF for Entry
                    for tf in Config.LTF_TIMEFRAMES:
                        # print(f"Checking LTF: {tf}")
                        df_ltf = md.get_rates(symbol, tf, num_bars=500)
                        if df_ltf is not None and not df_ltf.empty:
                            strategy_ltf = TurtleSoupStrategy(df_ltf)
                            signal = strategy_ltf.check_ltf_entry(htf_bias, rr_ratio=rr_ratio)
                            
                            if signal:
                                print(f"[{symbol}] LTF ENTRY SIGNAL on {tf}: {signal}")
                                
                                # Calculate position size based on risk
                                sl_distance = abs(signal['sl'] - signal['entry'])
                                volume = RiskManager.calculate_lot_size(
                                    symbol=symbol,
                                    sl_distance_price=sl_distance,
                                    risk_percent=Config.RISK_PERCENT,
                                    account_balance=account_balance,
                                    max_lots=max_lot_cap
                                )
                                
                                if volume > 0:
                                    Execution.place_order(
                                        symbol=symbol,
                                        order_type=signal['signal'],
                                        volume=volume,
                                        sl=signal['sl'],
                                        tp=signal['tp'],
                                        comment=f"Turtle Soup {tf} Score:{confluence_score}"
                                    )
                                # Reset bias after trade? Or keep looking?
                                # For safety, let's break and wait for next loop
                                break
                else:
                    # print(f"[{symbol}] No HTF Setup found.")
                    pass
            
            print("Finished cycle. Waiting 60s...")
            # Sleep cycle
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("Stopping bot...")
        md.disconnect()

if __name__ == "__main__":
    main()

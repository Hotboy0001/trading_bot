import time
import sys
import os
import MetaTrader5 as mt5
from config import Config
from market_data import MarketData
from strategy import TurtleSoupStrategy
from execution import Execution
from risk_manager import RiskManager

def main():
    print("Starting Turtle Soup Trading Bot...")
    
    # Initialize Market Data
    md = MarketData()
    if not md.connect():
        sys.exit(1)
        
    try:
        while True:
            # Get account balance for position sizing
            account_info = mt5.account_info()
            if account_info is None:
                print("Failed to get account info. Skipping this cycle.")
                time.sleep(60)
                continue
            
            account_balance = account_info.balance
            print(f"Account Balance: ${account_balance:.2f}")
            
            for symbol in Config.SYMBOLS:
                print(f"--- Analyzing {symbol} ---")
                
                # 1. Analyze Higher Timeframes (HTF)
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
                
                # 2. Execute on Lower Timeframes (LTF) if Bias exists
                if htf_bias:
                    # Determine Risk:Reward Ratio based on Confluence
                    rr_ratio = 3.0
                    
                    if confluence_score == 2:
                        rr_ratio = 5.0
                    elif confluence_score >= 3:
                        rr_ratio = 7.0
                    
                    print(f"[{symbol}] Switching to LTF Execution for {htf_bias} bias (Score: {confluence_score}, RR: 1:{rr_ratio})...")
                    
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
                                    account_balance=account_balance
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

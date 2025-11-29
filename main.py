import time
import sys
from config import Config
from market_data import MarketData
from strategy import TurtleSoupStrategy
from execution import Execution

def main():
    print("Starting Turtle Soup Trading Bot...")
    
    # Initialize Market Data
    md = MarketData()
    if not md.connect():
        sys.exit(1)
        
    symbol = Config.SYMBOL
    timeframe = Config.TIMEFRAME
    
    print(f"Monitoring {symbol} on {timeframe}...")
    
    try:
        while True:
            # 1. Analyze Higher Timeframes (HTF)
            htf_bias = None
            confluence_score = 0
            biases = []
            
            for tf in Config.HTF_TIMEFRAMES:
                print(f"Analyzing HTF: {tf}")
                df_htf = md.get_rates(symbol, tf, num_bars=500)
                if df_htf is not None and not df_htf.empty:
                    strategy_htf = TurtleSoupStrategy(df_htf)
                    bias = strategy_htf.analyze_htf()
                    
                    if bias:
                        print(f"HTF SETUP DETECTED on {tf}: {bias}")
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
                    print("Conflicting HTF signals. Skipping.")
                    htf_bias = None
            
            # 2. Execute on Lower Timeframes (LTF) if Bias exists
            if htf_bias:
                # Determine Risk Settings based on Confluence
                rr_ratio = 3.0
                volume = 0.01
                
                if confluence_score == 2:
                    rr_ratio = 5.0
                    volume = 0.02
                elif confluence_score >= 3:
                    rr_ratio = 7.0
                    volume = 0.03
                
                print(f"Switching to LTF Execution for {htf_bias} bias (Score: {confluence_score}, RR: 1:{rr_ratio}, Vol: {volume})...")
                
                # Check LTF for Entry
                for tf in Config.LTF_TIMEFRAMES:
                    print(f"Checking LTF: {tf}")
                    df_ltf = md.get_rates(symbol, tf, num_bars=500)
                    if df_ltf is not None and not df_ltf.empty:
                        strategy_ltf = TurtleSoupStrategy(df_ltf)
                        signal = strategy_ltf.check_ltf_entry(htf_bias, rr_ratio=rr_ratio)
                        
                        if signal:
                            print(f"LTF ENTRY SIGNAL on {tf}: {signal}")
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
                print("No HTF Setup found. Waiting...")
            
            # Sleep cycle
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("Stopping bot...")
        md.disconnect()

if __name__ == "__main__":
    main()

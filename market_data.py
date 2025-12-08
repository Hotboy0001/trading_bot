import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
from config import Config

class MarketData:
    def __init__(self):
        self.connected = False

    def connect(self):
        # Try to initialize with explicit path first
        mt5_paths = [
            r"C:\Program Files\MetaTrader 5\terminal64.exe",
            r"C:\Program Files (x86)\MetaTrader 5\terminal64.exe",
        ]
        
        initialized = False
        
        # Try with explicit paths
        for path in mt5_paths:
            import os
            if os.path.exists(path):
                print(f"Trying MT5 at: {path}")
                # Increase timeout to 60 seconds
                if mt5.initialize(path=path, timeout=60000):
                    initialized = True
                    break
        
        # Try without path (auto-detect)
        if not initialized:
            print("Trying auto-detect...")
            # Increase timeout to 60 seconds
            if mt5.initialize(timeout=60000):
                initialized = True
        
        if not initialized:
            error = mt5.last_error()
            print("=" * 50)
            print("FAILED TO CONNECT TO MT5")
            print("=" * 50)
            print(f"Error Code: {error}")
            print()
            print("Troubleshooting Steps:")
            print("1. Ensure MT5 is running as Administrator")
            print("2. Disable 'Algo Trading' button in MT5 and re-enable it")
            print("3. Check Tools -> Options -> Expert Advisors -> Allow WebRequest")
            print("4. Restart MT5 Terminal")
            print("=" * 50)
            return False
            
        self.connected = True
        print(f"✅ Connected to MT5: {mt5.terminal_info()}")
        return True

    def disconnect(self):
        mt5.shutdown()
        self.connected = False

    def get_rates(self, symbol, timeframe, num_bars=1000):
        # Map string timeframe to MT5 constant
        tf_map = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "H1": mt5.TIMEFRAME_H1,
            "H2": mt5.TIMEFRAME_H2,
            "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1,
        }
        mt5_tf = tf_map.get(timeframe, mt5.TIMEFRAME_H1)

        rates = mt5.copy_rates_from_pos(symbol, mt5_tf, 0, num_bars)
        if rates is None:
            print(f"Failed to get rates for {symbol}")
            return None

        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

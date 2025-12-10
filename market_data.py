import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
from config import Config

class MarketData:
    def __init__(self):
        self.connected = False

    def connect(self):
        initialized = False

        # 1. ATTEMPT 1: Try auto-detect (Connect to existing open terminal)
        # This is the preferred method for VPS/Manual usage
        print("Attempting to connect to running MT5 terminal...")
        if mt5.initialize(timeout=60000):
            initialized = True
            print("✓ Found open MT5 terminal")
            
        # 2. ATTEMPT 2: Try with credentials (if provided in config)
        if not initialized and Config.MT5_LOGIN != 0:
            print("Trying auto-detect with credentials...")
            if mt5.initialize(login=Config.MT5_LOGIN, password=Config.MT5_PASSWORD, server=Config.MT5_SERVER, timeout=60000):
                initialized = True

        # 3. ATTEMPT 3: Try explicit paths (Fallback for local PC)
        if not initialized:
            mt5_paths = [
                r"C:\Program Files\MetaTrader 5\terminal64.exe",
                r"C:\Program Files (x86)\MetaTrader 5\terminal64.exe",
                r"C:\Program Files\Exness MetaTrader 5\terminal64.exe", # Added Exness path
            ]
            
            for path in mt5_paths:
                import os
                if os.path.exists(path):
                    print(f"Trying explicit path: {path}")
                    if mt5.initialize(path=path, timeout=60000):
                        initialized = True
                        break

        if not initialized:
            error = mt5.last_error()
            print("=" * 50)
            print("FAILED TO CONNECT TO MT5")
            print("=" * 50)
            print(f"Error Code: {error}")
            print()
            print("TROUBLESHOOTING:")
            print("1. Close ALL MetaTrader windows.")
            print("2. Open ONLY your Exness MT5.")
            print("3. Login to your account manually.")
            print("4. Try running the bot again.")
            print("=" * 50)
            return False
            
        # Check if authorized
        account_info = mt5.account_info()
        if account_info is None:
            print("=" * 50)
            print("❌ CONNECTED BUT NOT AUTHORIZED")
            print("The bot found a terminal, but it is not logged in.")
            print("Please ensure you are logged into your trading account in MT5.")
            print(f"MT5 Info: {mt5.terminal_info()}")
            print("=" * 50)
            # We don't return False here because sometimes account_info takes a split second, 
            # but usually it means auth failed. Let's try to proceed or fail hard?
            # User wants script bot. Fail hard is safer.
            return False

        self.connected = True
        print(f"✅ Connected to Account: {account_info.login}")
        return True

    def disconnect(self):
        mt5.shutdown()
        self.connected = False

    def get_rates(self, symbol, timeframe, num_bars=1000):
        # Ensure symbol is selected in Market Watch
        if not mt5.symbol_select(symbol, True):
            print(f"Failed to select symbol: {symbol}")
            return None

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
            print(f"Failed to get rates for {symbol} (Error: {mt5.last_error()})")
            return None

        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

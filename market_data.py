import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
from config import Config

class MarketData:
    def __init__(self):
        self.connected = False

    def connect(self):
        if not mt5.initialize(login=Config.MT5_LOGIN, password=Config.MT5_PASSWORD, server=Config.MT5_SERVER):
            print("initialize() failed, error code =", mt5.last_error())
            return False
        self.connected = True
        print(f"Connected to MT5: {mt5.terminal_info()}")
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

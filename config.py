import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MT5 Login Credentials
    MT5_LOGIN = int(os.getenv("MT5_LOGIN", "0"))
    MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
    MT5_SERVER = os.getenv("MT5_SERVER", "")


    # Trading Settings
    # Trading Settings
    SYMBOLS = ["XAUUSD", "EURUSD", "BTCUSD", "GBPUSD", "NZDUSD"]

    
    # Timeframes
    # Analysis (Higher Timeframes)
    HTF_TIMEFRAMES = ["H4", "H2", "H1"]
    # Execution (Lower Timeframes)
    LTF_TIMEFRAMES = ["M15", "M5", "M1"]
    
    VOLUME = 0.01      # Lot size (deprecated, now calculated dynamically)
    RISK_PERCENT = 3.0 # Maximum risk per trade (% of account balance)
    DAILY_LOSS_LIMIT = 15.0 # Stop trading if daily loss exceeds this %
    
    # Trailing Stop Settings
    TRAILING_ENABLE = True
    TRAILING_ACTIVATE_RR = 3.5 # Activate when price reaches 3.5R profit
    TRAILING_DIST_RR = 2.0     # Trail behind price by 2.0R (Looser trail)
    
    # News Filter Settings
    NEWS_FILTER_ENABLE = True
    NEWS_PAUSE_MINS_BEFORE = 30
    NEWS_PAUSE_MINS_AFTER = 30
    
    DEVIATION = 20     # Slippage in points
    MAGIC_NUMBER = 123456

    # Strategy Settings
    SWING_PERIOD = 50
    FVG_LENGTH = 120
    MSS_LENGTH = 80

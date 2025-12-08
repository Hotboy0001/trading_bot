import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MT5 Login Credentials
    # Credentials are now handled by the MT5 Terminal itself
    # Ensure you are logged into your account in the MT5 app


    # Trading Settings
    # Trading Settings
    SYMBOLS = ["XAUUSD", "EURUSD", "BTCUSD", "GBPUSD", "NZDUSD"]

    
    # Timeframes
    # Analysis (Higher Timeframes)
    HTF_TIMEFRAMES = ["H4", "H2", "H1"]
    # Execution (Lower Timeframes)
    LTF_TIMEFRAMES = ["M15", "M5", "M1"]
    
    VOLUME = 0.01      # Lot size (deprecated, now calculated dynamically)
    RISK_PERCENT = 5.0 # Maximum risk per trade (% of account balance)
    DEVIATION = 20     # Slippage in points
    MAGIC_NUMBER = 123456

    # Strategy Settings
    SWING_PERIOD = 50
    FVG_LENGTH = 120
    MSS_LENGTH = 80

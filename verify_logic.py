import pandas as pd
import numpy as np
from strategy import TurtleSoupStrategy

def create_synthetic_data():
    # Create a sequence of candles
    data = {
        'time': pd.date_range(start='2023-01-01', periods=100, freq='H'),
        'open': [1.0] * 100,
        'high': [1.0] * 100,
        'low': [1.0] * 100,
        'close': [1.0] * 100,
        'tick_volume': [100] * 100,
        'spread': [1] * 100,
        'real_volume': [100] * 100
    }
    df = pd.DataFrame(data)
    
    # 1. Establish a Major Swing High at index 20
    # Price goes up to 1.0500 then down
    df.loc[15:25, 'high'] = 1.0500
    df.loc[20, 'high'] = 1.0600 # The Major High
    df.loc[20, 'close'] = 1.0550
    
    # 2. Price drops to form a minor low at index 30
    df.loc[30, 'low'] = 1.0400 # Minor Low
    df.loc[30, 'close'] = 1.0450
    
    # 3. Price rallies to SWEEP the Major High at index 40
    df.loc[40, 'high'] = 1.0650 # Sweep (1.0650 > 1.0600)
    df.loc[40, 'close'] = 1.0580 # Close back inside (Turtle Soup)
    
    # 4. Price drops and breaks the Minor Low (MSS) at index 45
    df.loc[45, 'close'] = 1.0350 # Break (1.0350 < 1.0400)
    
    # 5. Form a Bearish FVG at index 46-48
    # Candle 46 Low: 1.0300
    # Candle 47 (The big drop)
    # Candle 48 High: 1.0200
    # Gap is 1.0200 - 1.0300 (Bearish FVG)
    df.loc[46, 'low'] = 1.0300
    df.loc[46, 'high'] = 1.0350
    df.loc[47, 'open'] = 1.0300
    df.loc[47, 'close'] = 1.0200
    df.loc[47, 'high'] = 1.0300
    df.loc[47, 'low'] = 1.0200
    df.loc[48, 'high'] = 1.0200 # Gap exists between 48 High (1.02) and 46 Low (1.03)
    
    # 6. Price retraces into FVG at index 55
    df.loc[55, 'high'] = 1.0250 # Inside FVG (1.0200 - 1.0300)
    df.loc[55, 'close'] = 1.0220
    
    return df

def test_strategy():
    print("Creating synthetic data...")
    df = create_synthetic_data()
    
    print("Initializing Strategy...")
    strategy = TurtleSoupStrategy(df)
    
    print("Checking for Signal at index 55 (Retrace into FVG)...")
    signal = strategy.check_signal(current_index=55)
    
    if signal:
        print("SUCCESS: Signal Detected!")
        print(signal)
    else:
        print("FAILURE: No Signal Detected.")
        # Debugging
        print(df.iloc[55])

if __name__ == "__main__":
    test_strategy()

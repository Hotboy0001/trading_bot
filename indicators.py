import pandas as pd
import numpy as np

class Indicators:
    @staticmethod
    def identify_swings(df, period=50):
        """
        Identifies Major Swing Highs and Lows similar to ta.pivothigh/low(period, period).
        Returns a DataFrame with 'is_swing_high' and 'is_swing_low' columns.
        Note: This is a lagging indicator for historical analysis. 
        For real-time, we look at past confirmed swings.
        """
        df['swing_high'] = df['high'].rolling(window=period*2+1, center=True).max()
        df['swing_low'] = df['low'].rolling(window=period*2+1, center=True).min()
        
        df['is_swing_high'] = (df['high'] == df['swing_high'])
        df['is_swing_low'] = (df['low'] == df['swing_low'])
        
        return df

    @staticmethod
    def identify_mss_swings(df, left=2, right=1):
        """
        Identifies minor swings for Market Structure Shift (MSS).
        Pine: ta.pivothigh(2, 1)
        """
        # We can't easily use centered rolling for asymmetric windows efficiently in one go without custom logic
        # But for 2,1 it's simple: High[i] > High[i-1], High[i] > High[i-2], High[i] > High[i+1]
        
        # Shifted comparison
        # i is the potential pivot
        # i-1, i-2 are left neighbors
        # i+1 is right neighbor (future)
        
        # In a real-time loop, we check if index-1 was a pivot once index closes.
        
        df['is_minor_high'] = False
        df['is_minor_low'] = False
        
        for i in range(2, len(df)-1):
            # Pivot High
            if (df['high'].iloc[i] > df['high'].iloc[i-1] and 
                df['high'].iloc[i] > df['high'].iloc[i-2] and 
                df['high'].iloc[i] > df['high'].iloc[i+1]):
                df.at[df.index[i], 'is_minor_high'] = True
                
            # Pivot Low
            if (df['low'].iloc[i] < df['low'].iloc[i-1] and 
                df['low'].iloc[i] < df['low'].iloc[i-2] and 
                df['low'].iloc[i] < df['low'].iloc[i+1]):
                df.at[df.index[i], 'is_minor_low'] = True
                
        return df

    @staticmethod
    def find_fvg(df):
        """
        Identifies Fair Value Gaps.
        Bullish FVG: Low[i] > High[i-2]
        Bearish FVG: High[i] < Low[i-2]
        """
        df['bullish_fvg'] = False
        df['bearish_fvg'] = False
        df['fvg_top'] = np.nan
        df['fvg_bottom'] = np.nan
        
        for i in range(2, len(df)):
            # Bullish FVG
            if df['low'].iloc[i] > df['high'].iloc[i-2]:
                df.at[df.index[i], 'bullish_fvg'] = True
                df.at[df.index[i], 'fvg_top'] = df['low'].iloc[i]
                df.at[df.index[i], 'fvg_bottom'] = df['high'].iloc[i-2]
                
            # Bearish FVG
            if df['high'].iloc[i] < df['low'].iloc[i-2]:
                df.at[df.index[i], 'bearish_fvg'] = True
                df.at[df.index[i], 'fvg_top'] = df['low'].iloc[i-2]
                df.at[df.index[i], 'fvg_bottom'] = df['high'].iloc[i]
                
        return df

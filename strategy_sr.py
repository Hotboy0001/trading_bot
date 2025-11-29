import pandas as pd
import numpy as np

class SRStrategy:
    def __init__(self, df, lookback=20, vol_len=2, box_width_atr=1.0):
        self.df = df
        self.lookback = lookback
        self.vol_len = vol_len
        self.box_width_atr = box_width_atr
        self.process_data()

    def process_data(self):
        # 1. Calculate Delta Volume (Approximate)
        # Pine: if close > open posVol else negVol
        self.df['delta_vol'] = np.where(self.df['close'] > self.df['open'], 
                                        self.df['tick_volume'], 
                                        -self.df['tick_volume'])
        
        # 2. Calculate Vol Thresholds
        # Pine: ta.highest(Vol/2.5, vol_len)
        # We use absolute delta vol for magnitude checking? 
        # Pine: Vol = upAndDownVolume() -> This returns net volume.
        # Wait, the Pine Script accumulates volume? 
        # "posVol += volume" inside the function? No, it's a local var in function, reset every call?
        # Actually, upAndDownVolume() in Pine just returns current bar's signed volume.
        
        # Pine: vol_hi = ta.highest(Vol/2.5, vol_len)
        # It compares current signed volume to recent highs of signed volume?
        # If Vol is negative, highest() would be the least negative (closest to 0) or positive?
        # Let's assume it checks magnitude or just raw signed value.
        # "Vol > vol_hi" (Support) -> Positive Volume > Recent Highs (Strong Buying)
        # "Vol < vol_lo" (Resistance) -> Negative Volume < Recent Lows (Strong Selling)
        
        self.df['vol_hi'] = (self.df['delta_vol'] / 2.5).rolling(window=self.vol_len).max()
        self.df['vol_lo'] = (self.df['delta_vol'] / 2.5).rolling(window=self.vol_len).min()
        
        # 3. ATR for Box Width
        self.df['atr'] = self.calculate_atr(self.df)
        
        # 4. Identify Pivots
        self.df['pivot_high'] = self.df['high'].rolling(window=self.lookback*2+1, center=True).max()
        self.df['pivot_low'] = self.df['low'].rolling(window=self.lookback*2+1, center=True).min()
        
        self.df['is_pivot_high'] = (self.df['high'] == self.df['pivot_high'])
        self.df['is_pivot_low'] = (self.df['low'] == self.df['pivot_low'])
        
        # 5. Identify S/R Boxes
        self.df['sr_support'] = np.nan
        self.df['sr_resistance'] = np.nan
        
        # Iterate to find boxes (simulating Pine's var box logic)
        # We need to propagate the *active* support/resistance levels
        
        active_support = np.nan
        active_resistance = np.nan
        
        # Lists to store broken levels for confirmation
        self.df['broken_support'] = False
        self.df['broken_resistance'] = False
        
        for i in range(self.lookback, len(self.df)):
            # Check for New Support (Pivot Low + High Buy Volume)
            if self.df['is_pivot_low'].iloc[i] and self.df['delta_vol'].iloc[i] > self.df['vol_hi'].iloc[i]:
                active_support = self.df['low'].iloc[i]
                
            # Check for New Resistance (Pivot High + High Sell Volume)
            if self.df['is_pivot_high'].iloc[i] and self.df['delta_vol'].iloc[i] < self.df['vol_lo'].iloc[i]:
                active_resistance = self.df['high'].iloc[i]
            
            # Store current active levels
            self.df.at[self.df.index[i], 'sr_support'] = active_support
            self.df.at[self.df.index[i], 'sr_resistance'] = active_resistance
            
            # Check Breakouts
            # Break Support: Close < Support (or High < Support_1 in Pine?)
            # Pine: brekout_sup := ta.crossunder(high, supportLevel_1) -> Price went BELOW the box bottom
            # Box bottom = supportLevel - width
            
            width = self.df['atr'].iloc[i] * self.box_width_atr
            
            if not np.isnan(active_support):
                support_bottom = active_support - width
                if self.df['close'].iloc[i] < support_bottom:
                     self.df.at[self.df.index[i], 'broken_support'] = True
            
            if not np.isnan(active_resistance):
                resistance_top = active_resistance + width
                if self.df['close'].iloc[i] > resistance_top:
                    self.df.at[self.df.index[i], 'broken_resistance'] = True

    @staticmethod
    def calculate_atr(df, period=14):
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        return true_range.rolling(period).mean()

    def get_latest_status(self):
        """
        Returns the latest S/R status.
        """
        latest = self.df.iloc[-1]
        return {
            'active_support': latest['sr_support'],
            'active_resistance': latest['sr_resistance'],
            'broken_support': latest['broken_support'],
            'broken_resistance': latest['broken_resistance']
        }

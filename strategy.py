from indicators import Indicators
from strategy_sr import SRStrategy
import pandas as pd

class TurtleSoupStrategy:
    def __init__(self, df):
        self.df = df
        self.process_data()
        
    def process_data(self):
        # Calculate indicators
        self.df = Indicators.identify_swings(self.df)
        self.df = Indicators.identify_mss_swings(self.df)
        self.df = Indicators.find_fvg(self.df)
        
        # Calculate S/R Strategy
        self.sr_strategy = SRStrategy(self.df)
        # Merge S/R columns into main df for easier access if needed
        self.df['broken_support'] = self.sr_strategy.df['broken_support']
        self.df['broken_resistance'] = self.sr_strategy.df['broken_resistance']
        
    def analyze_htf(self, current_index=-1):
        """
        Analyzes Higher Timeframe for Setup (Sweep + S/R Break).
        Returns: 'BULLISH', 'BEARISH', or None
        """
        df = self.df
        curr_idx = df.index[current_index]
        
        # 1. Check for Bearish Setup (Sweep High + Break Support)
        last_major_highs = df[df['is_swing_high']].loc[:curr_idx].tail(5)
        if not last_major_highs.empty:
            major_high = last_major_highs.iloc[-1]
            if self._check_sweep(df, major_high['high'], major_high.name, curr_idx, 'HIGH'):
                # Check for S/R Confirmation (Break of Support)
                # We look for ANY recent break of support since the sweep
                sweep_bar = self._get_sweep_bar(df, major_high['high'], major_high.name, curr_idx, 'HIGH')
                if sweep_bar and df['broken_support'].loc[sweep_bar:curr_idx].any():
                    return 'BEARISH'

        # 2. Check for Bullish Setup (Sweep Low + Break Resistance)
        last_major_lows = df[df['is_swing_low']].loc[:curr_idx].tail(5)
        if not last_major_lows.empty:
            major_low = last_major_lows.iloc[-1]
            if self._check_sweep(df, major_low['low'], major_low.name, curr_idx, 'LOW'):
                # Check for S/R Confirmation (Break of Resistance)
                sweep_bar = self._get_sweep_bar(df, major_low['low'], major_low.name, curr_idx, 'LOW')
                if sweep_bar and df['broken_resistance'].loc[sweep_bar:curr_idx].any():
                    return 'BULLISH'
                    
        return None

    def check_ltf_entry(self, bias, rr_ratio=3.0, current_index=-1):
        """
        Checks Lower Timeframe for Entry (MSS + FVG) in direction of bias.
        Returns: dict with trade details or None
        """
        df = self.df
        curr_row = df.iloc[current_index]
        
        # We assume the bias is active, so we look for immediate entry signals
        # For simplicity, we check if we are currently in an FVG that formed after a recent MSS
        
        if bias == 'BEARISH':
            # Look for recent MSS Low
            # And current price inside Bearish FVG
            if curr_row['bearish_fvg']:
                 pass # FVG Creation
            
            # Check if we are in a valid FVG
            # In a real LTF loop, we'd track the MSS and FVG more precisely
            # Here we check if we are in *any* recent unmitigated FVG
            
            # Simple check: Are we in a bearish FVG?
            # And did we have a recent MSS?
            
            # Let's just check for FVG presence for now as the trigger
            if curr_row['bearish_fvg']:
                 return None # Wait for retrace? Or enter on close?
                 
            # Find recent FVGs
            recent_fvgs = df[df['bearish_fvg']].tail(10)
            for idx, fvg in recent_fvgs.iterrows():
                if fvg['fvg_bottom'] <= curr_row['high'] <= fvg['fvg_top']:
                     sl_dist = fvg['fvg_top'] + 0.0005 - curr_row['close']
                     tp_dist = sl_dist * rr_ratio
                     
                     return {
                        'signal': 'SELL',
                        'sl': fvg['fvg_top'] + 0.0005,
                        'tp': curr_row['close'] - tp_dist,
                        'entry': curr_row['close'],
                        'comment': f'LTF Entry RR 1:{rr_ratio}'
                    }

        elif bias == 'BULLISH':
            recent_fvgs = df[df['bullish_fvg']].tail(10)
            for idx, fvg in recent_fvgs.iterrows():
                if fvg['fvg_bottom'] <= curr_row['low'] <= fvg['fvg_top']:
                     sl_dist = curr_row['close'] - (fvg['fvg_bottom'] - 0.0005)
                     tp_dist = sl_dist * rr_ratio
                     
                     return {
                        'signal': 'BUY',
                        'sl': fvg['fvg_bottom'] - 0.0005,
                        'tp': curr_row['close'] + tp_dist,
                        'entry': curr_row['close'],
                        'comment': f'LTF Entry RR 1:{rr_ratio}'
                    }
        
        return None

    def _check_sweep(self, df, level, start_time, end_time, type):
        subset = df.loc[start_time:end_time].iloc[1:]
        for idx, row in subset.iterrows():
            if type == 'HIGH' and row['high'] > level:
                return True
            if type == 'LOW' and row['low'] < level:
                return True
        return False

    def _get_sweep_bar(self, df, level, start_time, end_time, type):
        subset = df.loc[start_time:end_time].iloc[1:]
        for idx, row in subset.iterrows():
            if type == 'HIGH' and row['high'] > level:
                return idx
            if type == 'LOW' and row['low'] < level:
                return idx
        return None

    def get_latest_bar(self):
        return self.df.iloc[-1]

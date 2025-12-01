import MetaTrader5 as mt5

class RiskManager:
    @staticmethod
    def calculate_lot_size(symbol, sl_distance_price, risk_percent, account_balance):
        """
        Calculate lot size based on risk percentage and stop loss distance.
        
        Args:
            symbol: Trading symbol (e.g., "EURUSD")
            sl_distance_price: Stop loss distance in price units
            risk_percent: Risk percentage (e.g., 5.0 for 5%)
            account_balance: Account balance
            
        Returns:
            Calculated lot size, capped at max allowed
        """
        # Get symbol info
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            print(f"Failed to get symbol info for {symbol}")
            return 0.01  # Default fallback
        
        # Calculate risk amount in account currency
        risk_amount = account_balance * (risk_percent / 100.0)
        
        # Get contract size (e.g., 100,000 for standard lot)
        contract_size = symbol_info.trade_contract_size
        
        # Calculate pip value for 1 lot
        # For forex pairs like EURUSD, 1 pip = 0.0001
        # Pip value = (0.0001 / current_price) * contract_size for XXX/USD
        # For USD/XXX, pip value = 0.0001 * contract_size
        
        tick_size = symbol_info.point  # Minimum price change
        tick_value = symbol_info.trade_tick_value  # Value of 1 tick for 1 lot
        
        # Calculate how many ticks in the SL distance
        sl_distance_ticks = abs(sl_distance_price / tick_size)
        
        # Calculate risk per lot based on SL distance
        risk_per_lot = sl_distance_ticks * tick_value
        
        if risk_per_lot <= 0:
            print(f"Invalid risk calculation for {symbol}")
            return 0.01
        
        # Calculate lot size
        lot_size = risk_amount / risk_per_lot
        
        # Apply min/max limits
        min_lot = symbol_info.volume_min
        max_lot = symbol_info.volume_max
        lot_step = symbol_info.volume_step
        
        # Round to lot step
        lot_size = round(lot_size / lot_step) * lot_step
        
        # Clamp to limits
        lot_size = max(min_lot, min(lot_size, max_lot))
        
        print(f"[RISK] {symbol}: Balance=${account_balance:.2f}, Risk={risk_percent}%, SL Distance={sl_distance_price:.5f}, Lot Size={lot_size:.2f}")
        
        return lot_size

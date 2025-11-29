import MetaTrader5 as mt5
from config import Config

class Execution:
    @staticmethod
    def place_order(symbol, order_type, volume, price=None, sl=None, tp=None, comment="Turtle Soup Bot"):
        """
        Places a trade on MT5.
        order_type: 'BUY' or 'SELL'
        """
        
        # Check symbol info
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            print(f"{symbol} not found")
            return None
            
        if not symbol_info.visible:
            if not mt5.symbol_select(symbol, True):
                print(f"symbol_select({symbol}) failed")
                return None
                
        action = mt5.TRADE_ACTION_DEAL
        type_op = mt5.ORDER_TYPE_BUY if order_type == 'BUY' else mt5.ORDER_TYPE_SELL
        
        # Calculate price if not provided (Market Order)
        if price is None:
            price = mt5.symbol_info_tick(symbol).ask if order_type == 'BUY' else mt5.symbol_info_tick(symbol).bid
            
        request = {
            "action": action,
            "symbol": symbol,
            "volume": volume,
            "type": type_op,
            "price": price,
            "sl": sl if sl else 0.0,
            "tp": tp if tp else 0.0,
            "deviation": Config.DEVIATION,
            "magic": Config.MAGIC_NUMBER,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Order failed: {result.retcode} - {result.comment}")
            return None
            
        print(f"Order placed: {result.order}")
        return result

    @staticmethod
    def close_all_positions(symbol):
        positions = mt5.positions_get(symbol=symbol)
        if positions:
            for pos in positions:
                type_op = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(symbol).bid if type_op == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(symbol).ask
                
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": pos.volume,
                    "type": type_op,
                    "position": pos.ticket,
                    "price": price,
                    "deviation": Config.DEVIATION,
                    "magic": Config.MAGIC_NUMBER,
                    "comment": "Close Position",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                mt5.order_send(request)

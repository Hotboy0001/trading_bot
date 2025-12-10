import MetaTrader5 as mt5
from datetime import datetime, timedelta
from config import Config

class NewsManager:
    def __init__(self):
        self.high_impact_events = []
        self.last_update = datetime.min
        
    def refresh_calendar(self):
        """
        Fetches high-impact economic events for the current week.
        """
        # Update only once per hour to save resources
        if datetime.now() - self.last_update < timedelta(hours=1):
            return

        try:
            # Note: The native MT5 Python API does not support calendar_events as of 5.0.45.
            # To avoid external dependencies (requests/beautifulsoup) for a simple script,
            # we will temporarily disable the internal fetcher.
            
            # Use external API or custom implementation here if needed.
            # For now, we keep the list empty to prevent crashes.
            self.high_impact_events = []
            
            # print("[NEWS] Native calendar API not available. News filter inactive.")
            self.last_update = datetime.now()
            
        except Exception as e:
            print(f"[NEWS] Error fetching calendar: {e}")

    def is_news_impact(self, symbol):
        """
        Checks if we are currently in a news blackout window.
        """
        if not Config.NEWS_FILTER_ENABLE:
            return False
            
        self.refresh_calendar()
        
        now = datetime.now()
        
        for event in self.high_impact_events:
            event_time = datetime.fromtimestamp(event.time) # Assuming timestamp
            
            # Define blackout window
            start_block = event_time - timedelta(minutes=Config.NEWS_PAUSE_MINS_BEFORE)
            end_block = event_time + timedelta(minutes=Config.NEWS_PAUSE_MINS_AFTER)
            
            if start_block <= now <= end_block:
                print(f"[NEWS] 🛑 TRADING PAUSED: High Impact Event at {event_time}")
                return True
                
        return False

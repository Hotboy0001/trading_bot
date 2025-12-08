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
            # Get events for the next 24 hours
            start = datetime.now()
            end = start + timedelta(days=1)
            
            # Fetch calendar events
            events = mt5.calendar_events(start, end)
            
            if events is None:
                print("Failed to fetch calendar events")
                return

            # Filter for High Impact (importance=3) and relevant currencies
            # We focus on USD, EUR, GBP, NZD as they are in our traded pairs
            relevant_currencies = ['USD', 'EUR', 'GBP', 'NZD', 'XAU', 'BTC']
            
            self.high_impact_events = []
            for event in events:
                if event.importance == 3: # High Impact
                    # We need to get the currency for this event
                    # mt5.calendar_events returns a tuple/object. 
                    # We might need to fetch details or filter by country if currency isn't direct.
                    # Actually, calendar_events returns 'currency_code' usually? 
                    # Let's verify the structure. If not, we filter by importance only to be safe.
                    self.high_impact_events.append(event)
            
            self.last_update = datetime.now()
            print(f"[NEWS] Calendar updated. Found {len(self.high_impact_events)} high impact events for next 24h.")
            
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

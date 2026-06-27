"""Pi Calendar TUI - Main entry point."""
import asyncio
import logging
from datetime import datetime
from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive

from src.config import Config
from src.cache import EventCache
from src.event_fetcher import EventFetcher
from src.calendar_view import CalendarMonthView
from src.widgets.event_list import EventList

# Setup logging
log_path = Path(__file__).parent.parent / "data" / "calendar.log"
log_path.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PiCalendarApp(App):
    """Main calendar application."""
    
    CSS = """
    Screen {
        align: center middle;
    }
    
    #main-container {
        width: 100%;
        height: 100%;
    }
    
    #calendar-panel {
        width: 70%;
        height: 100%;
        border: solid green;
    }
    
    #sidebar {
        width: 30%;
        height: 100%;
        border: solid blue;
    }
    
    #events-header {
        height: 3;
        content-align: center middle;
        text-style: bold;
    }
    
    DataTable {
        width: 100%;
        height: 100%;
    }
    
    ListView {
        width: 100%;
        height: 1fr;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("t", "today", "Today"),
        ("left", "prev_month", "Previous"),
        ("right", "next_month", "Next"),
        ("h", "show_help", "Help"),
    ]
    
    config = None
    cache = None
    fetcher = None
    all_events = reactive([])
    
    def __init__(self, config_path: str = "config/calendar.yaml"):
        super().__init__()
        self.config = Config(config_path)
        self.cache = EventCache(self.config.cache_db_path)
        self.fetcher = EventFetcher(self.cache, self.config._data.get("refresh", {}).get("timeout_seconds", 30))
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Horizontal(id="main-container"):
            with Vertical(id="calendar-panel"):
                first_day = 6 if self.config.display.get("first_day_of_week", "sunday") == "sunday" else 0
                yield CalendarMonthView(first_weekday=first_day, id="calendar")
            
            with Vertical(id="sidebar"):
                yield EventList(id="event-list")
        
        yield Footer()
    
    async def on_mount(self):
        """Initialize and load events."""
        self.title = "Pi Calendar"
        
        # Validate config
        errors = self.config.validate()
        if errors:
            self.notify("\n".join(errors), severity="error", timeout=10)
            logger.error(f"Config errors: {errors}")
            return
        
        # Initial fetch
        await self._refresh_events()
        
        # Start background refresh timer
        self.set_interval(self.config.refresh_interval * 60, self._refresh_events)
    
    async def _refresh_events(self):
        """Fetch events from all calendars."""
        all_events = []
        
        for cal in self.config.calendars:
            try:
                events = self.fetcher.fetch_calendar(
                    cal["name"], 
                    cal["url"]
                )
                # Tag events with calendar color
                for event in events:
                    event["color"] = cal.get("color", "#ffffff")
                all_events.extend(events)
                logger.info(f"Loaded {len(events)} events from {cal['name']}")
            except Exception as e:
                logger.error(f"Failed to load {cal['name']}: {e}")
                self.notify(f"Failed to load {cal['name']}", severity="warning")
        
        self.all_events = all_events
        
        # Update widgets
        calendar = self.query_one("#calendar", CalendarMonthView)
        calendar.events = all_events
        
        event_list = self.query_one("#event-list", EventList)
        event_list.events = all_events
        
        self.notify(f"Loaded {len(all_events)} events")
    
    def action_refresh(self):
        """Manual refresh."""
        self.run_worker(self._refresh_events)
    
    def action_today(self):
        """Jump to today."""
        calendar = self.query_one("#calendar", CalendarMonthView)
        calendar.go_today()
        event_list = self.query_one("#event-list", EventList)
        event_list.selected_date = datetime.now()
    
    def action_prev_month(self):
        """Previous month."""
        calendar = self.query_one("#calendar", CalendarMonthView)
        calendar.prev_month()
    
    def action_next_month(self):
        """Next month."""
        calendar = self.query_one("#calendar", CalendarMonthView)
        calendar.next_month()
    
    def action_show_help(self):
        """Show help dialog."""
        help_text = """
        Keyboard Shortcuts:
        
        q           Quit
        r           Refresh calendars
        t           Jump to today
        left/right  Previous/Next month
        h           Show this help
        
        The calendar auto-refreshes every 30 minutes.
        """
        self.notify(help_text, title="Help", timeout=10)


def main():
    """Entry point."""
    import sys
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/calendar.yaml"
    app = PiCalendarApp(config_path)
    app.run()


if __name__ == "__main__":
    main()

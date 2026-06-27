"""Event list widget for showing daily events."""
from datetime import datetime
from typing import List, Dict
from textual.widgets import Static, ListView, ListItem, Label
from textual.reactive import reactive


class EventList(Static):
    """Display list of events for selected date."""
    
    events = reactive([])
    selected_date = reactive(datetime.now())
    
    def __init__(self, theme=None, **kwargs):
        super().__init__(**kwargs)
        self.theme = theme
    
    def compose(self):
        yield Static("Events", id="events-header")
        yield ListView(id="events-list")
    
    def on_mount(self):
        self.update_events()
    
    def watch_selected_date(self):
        self.update_events()
    
    def watch_events(self):
        self.update_events()
    
    def update_events(self):
        """Update the events list for selected date."""
        list_view = self.query_one("#events-list", ListView)
        list_view.clear()
        
        header = self.query_one("#events-header", Static)
        header.update(self.selected_date.strftime("%A, %B %d"))
        
        # Filter events for selected date
        date_str = self.selected_date.strftime("%Y-%m-%d")
        day_events = []
        
        for event in self.events:
            try:
                event_start = event.get("start", "")
                if not event_start:
                    continue
                # Extract date part (handle both datetime and date-only)
                if 'T' in event_start:
                    event_date = event_start.split('T')[0]
                else:
                    event_date = event_start
                
                if event_date == date_str:
                    day_events.append(event)
            except (ValueError, KeyError):
                continue
        
        # Sort by start time
        day_events.sort(key=lambda e: e.get("start", ""))
        
        if not day_events:
            list_view.append(ListItem(Label("No events")))
            return
        
        for event in day_events:
            time_str = ""
            try:
                start = event.get("start", "")
                if 'T' in start:
                    # Parse datetime
                    dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    time_str = dt.strftime("%I:%M %p").lstrip("0")
            except:
                pass
            
            summary = event.get("summary", "Untitled")
            location = event.get("location", "")
            
            display = f"{time_str} {summary}" if time_str else summary
            if location:
                display += f"\n    [dim]{location}[/dim]"
            
            list_view.append(ListItem(Label(display)))

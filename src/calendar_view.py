"""Calendar month view widget."""
from datetime import datetime, timedelta
from typing import List, Dict
from textual.widgets import Static, DataTable
from textual.reactive import reactive


class CalendarMonthView(Static):
    """A month-view calendar widget."""
    
    current_date = reactive(datetime.now())
    events = reactive([])
    
    def __init__(self, first_weekday: int = 6, theme=None, **kwargs):  # 6 = Sunday
        super().__init__(**kwargs)
        self.first_weekday = first_weekday  # 0=Mon, 6=Sun
        self.theme = theme
        self._event_map: Dict[str, List[Dict]] = {}
    
    def compose(self):
        """Build the calendar grid."""
        yield DataTable(zebra_stripes=False, show_header=True, show_cursor=False)
    
    def on_mount(self):
        """Initialize the calendar grid."""
        table = self.query_one(DataTable)
        table.clear()
        table.add_columns("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")
        self._build_calendar()
    
    def watch_current_date(self):
        """Rebuild when date changes."""
        self._build_calendar()
    
    def watch_events(self):
        """Rebuild when events change."""
        self._build_event_map()
        self._build_calendar()
    
    def _build_event_map(self):
        """Index events by date for quick lookup."""
        self._event_map = {}
        for event in self.events:
            try:
                start = event.get("start", "")
                if not start:
                    continue
                # Handle both datetime (has T) and date-only
                if 'T' in start:
                    date_key = start.split('T')[0]
                else:
                    date_key = start
                if date_key not in self._event_map:
                    self._event_map[date_key] = []
                self._event_map[date_key].append(event)
            except (ValueError, KeyError):
                continue
    
    def _build_calendar(self):
        """Build the month grid."""
        table = self.query_one(DataTable)
        table.clear()
        
        # Ensure columns exist (they may get cleared)
        if len(table.columns) == 0:
            table.add_columns("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")
        
        year = self.current_date.year
        month = self.current_date.month
        
        # Get first day and number of days in month
        first_of_month = datetime(year, month, 1)
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        
        days_in_month = (next_month - first_of_month).days
        
        # Adjust for first weekday (Sunday = 6)
        start_weekday = first_of_month.weekday()
        if self.first_weekday == 6:  # Sunday start
            start_offset = (start_weekday + 1) % 7
        else:  # Monday start
            start_offset = start_weekday
        
        # Build rows
        day = 1
        current_row = []
        
        # Empty cells before month starts
        for i in range(start_offset):
            current_row.append("")
        
        col = start_offset
        while day <= days_in_month:
            date_key = f"{year}-{month:02d}-{day:02d}"
            events = self._event_map.get(date_key, [])
            
            # Format cell: day number + event indicators
            if self.theme:
                event_char = self.theme.get_style("event_indicator", "·")
                today_shape = self.theme.get_style("today_shape", "◆")
            else:
                event_char = "·"
                today_shape = "◆"
            
            if events:
                dots = event_char * min(len(events), 3)  # Max 3 indicators
                cell = f"{day:2d}\n{dots}"
            else:
                cell = f"{day:2d}"
            
            # Highlight today
            today = datetime.now()
            if today.year == year and today.month == month and today.day == day:
                if self.theme:
                    cell = f"[bold {self.theme.get_color('today_bg')[1:]}]{today_shape} {day}[/]"
                else:
                    cell = f"[bold cyan]{today_shape} {day}[/]"
            
            current_row.append(cell)
            
            col += 1
            if col > 6:
                table.add_row(*current_row)
                current_row = []
                col = 0
            
            day += 1
        
        # Add remaining row if not empty
        if current_row:
            # Pad with empty cells
            while len(current_row) < 7:
                current_row.append("")
            table.add_row(*current_row)
    
    def next_month(self):
        """Navigate to next month."""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
    
    def prev_month(self):
        """Navigate to previous month."""
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
    
    def go_today(self):
        """Jump to current month."""
        self.current_date = datetime.now().replace(day=1)

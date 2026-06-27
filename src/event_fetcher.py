"""iCal fetcher and parser."""
import logging
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
import icalendar
import recurring_ical_events

logger = logging.getLogger(__name__)


class EventFetcher:
    """Fetch and parse iCal feeds."""
    
    def __init__(self, cache, timeout: int = 30):
        self.cache = cache
        self.timeout = timeout
    
    def fetch_calendar(self, name: str, url: str, 
                       force: bool = False) -> List[Dict]:
        """Fetch and parse a calendar, returning events."""
        # Check if we need to fetch
        if not force:
            last_fetch = self.cache.get_last_fetch(name)
            if last_fetch and (datetime.now() - last_fetch) < timedelta(minutes=30):
                logger.info(f"Using cached events for {name}")
                return self.cache.get_events(
                    datetime.now() - timedelta(days=1),
                    datetime.now() + timedelta(days=365),
                    name
                )
        
        try:
            logger.info(f"Fetching {name} from {url}")
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            events = self._parse_ical(response.text, name)
            self.cache.store_events(name, events)
            
            return events
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {name}: {e}")
            # Return cached events if available
            return self.cache.get_events(
                datetime.now() - timedelta(days=1),
                datetime.now() + timedelta(days=365),
                name
            )
    
    def _parse_ical(self, ical_data: str, calendar_name: str) -> List[Dict]:
        """Parse iCal data and extract events."""
        calendar = icalendar.Calendar.from_ical(ical_data)
        
        # Get events for next year (including recurring)
        start = datetime.now()
        end = start + timedelta(days=365)
        
        events = []
        for component in recurring_ical_events.of(calendar).between(start, end):
            if component.name == "VEVENT":
                event = self._event_to_dict(component, calendar_name)
                if event:
                    events.append(event)
        
        return events
    
    def _event_to_dict(self, component, calendar_name: str) -> Optional[Dict]:
        """Convert iCal event component to dict."""
        try:
            start = component.get("dtstart").dt
            end = component.get("dtend")
            end_dt = end.dt if end else None
            
            # Handle date vs datetime
            if hasattr(start, 'date') and not isinstance(start, datetime):
                start = datetime.combine(start, datetime.min.time())
            if end_dt and hasattr(end_dt, 'date') and not isinstance(end_dt, datetime):
                end_dt = datetime.combine(end_dt, datetime.min.time())
            
            uid = component.get("uid", "")
            # Generate stable ID if no UID
            if not uid:
                uid = hashlib.md5(
                    f"{calendar_name}:{start}:{component.get('summary', '')}".encode()
                ).hexdigest()
            
            return {
                "id": uid,
                "calendar_name": calendar_name,
                "summary": str(component.get("summary", "")),
                "start": start.isoformat() if isinstance(start, datetime) else str(start),
                "end": end_dt.isoformat() if end_dt else None,
                "location": str(component.get("location", "")),
                "description": str(component.get("description", "")),
            }
        except Exception as e:
            logger.warning(f"Failed to parse event: {e}")
            return None

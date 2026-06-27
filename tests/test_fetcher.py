import pytest
import sys
import os
from datetime import datetime
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from event_fetcher import EventFetcher


@pytest.fixture
def mock_cache():
    cache = Mock()
    cache.get_last_fetch.return_value = None
    cache.get_events.return_value = []
    return cache


def test_fetch_calendar_uses_cache_when_recent(mock_cache):
    """Test cache is used for recent fetches."""
    mock_cache.get_last_fetch.return_value = datetime.now()
    
    fetcher = EventFetcher(mock_cache)
    events = fetcher.fetch_calendar("Test", "http://example.com/cal.ics")
    
    # Should not make HTTP request
    assert mock_cache.get_events.called


def test_parse_ical_extracts_events():
    """Test iCal parsing."""
    from datetime import datetime, timedelta
    
    # Use tomorrow's date so event falls within the 365-day window
    tomorrow = datetime.now() + timedelta(days=1)
    dt_str = tomorrow.strftime("%Y%m%d")
    
    sample_ical = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//EN
BEGIN:VEVENT
UID:test-event-1
DTSTART:{dt_str}T100000Z
DTEND:{dt_str}T110000Z
SUMMARY:Test Meeting
LOCATION:Room 101
DESCRIPTION:Important meeting
END:VEVENT
END:VCALENDAR"""
    
    fetcher = EventFetcher(Mock())
    events = fetcher._parse_ical(sample_ical, "Test")
    
    assert len(events) == 1
    assert events[0]["summary"] == "Test Meeting"
    assert events[0]["location"] == "Room 101"


def test_event_to_dict_handles_all_day():
    """Test all-day event parsing."""
    import icalendar
    from datetime import datetime, timedelta
    
    # Use tomorrow's date
    tomorrow = datetime.now() + timedelta(days=1)
    
    cal = icalendar.Calendar()
    event = icalendar.Event()
    event.add('summary', 'Birthday')
    event.add('dtstart', tomorrow.date())
    event.add('uid', 'birthday-1')
    cal.add_component(event)
    
    fetcher = EventFetcher(Mock())
    events = fetcher._parse_ical(cal.to_ical().decode(), "Test")
    
    assert len(events) == 1
    assert events[0]["summary"] == "Birthday"
    # All-day events are stored as date strings (YYYY-MM-DD)
    assert len(events[0]["start"]) == 10  # YYYY-MM-DD

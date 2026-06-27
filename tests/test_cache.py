import pytest
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cache import EventCache


@pytest.fixture
def cache():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield EventCache(Path(tmpdir) / "test.db")


def test_store_and_retrieve(cache):
    """Test basic store/retrieve cycle."""
    events = [
        {
            "id": "test-1",
            "summary": "Test Event",
            "start": datetime(2024, 6, 27, 10, 0).isoformat(),
            "end": datetime(2024, 6, 27, 11, 0).isoformat(),
        }
    ]
    
    cache.store_events("Personal", events)
    
    retrieved = cache.get_events(
        datetime(2024, 6, 1),
        datetime(2024, 6, 30)
    )
    
    assert len(retrieved) == 1
    assert retrieved[0]["summary"] == "Test Event"


def test_get_events_by_calendar(cache):
    """Test filtering by calendar name."""
    cache.store_events("Personal", [{"id": "p1", "summary": "Personal", "start": datetime(2024, 6, 27).isoformat()}])
    cache.store_events("Work", [{"id": "w1", "summary": "Work", "start": datetime(2024, 6, 27).isoformat()}])
    
    personal = cache.get_events(datetime(2024, 6, 1), datetime(2024, 6, 30), "Personal")
    assert len(personal) == 1
    assert personal[0]["summary"] == "Personal"


def test_get_last_fetch(cache):
    """Test last fetch tracking."""
    # No fetch yet
    assert cache.get_last_fetch("Test") is None
    
    # Store events
    cache.store_events("Test", [{"id": "1", "summary": "Event", "start": datetime(2024, 6, 27).isoformat()}])
    
    # Should have timestamp
    last_fetch = cache.get_last_fetch("Test")
    assert last_fetch is not None
    assert (datetime.now() - last_fetch).total_seconds() < 5

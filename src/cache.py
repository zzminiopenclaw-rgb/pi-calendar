"""SQLite cache for calendar events."""
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    calendar_name TEXT NOT NULL,
    summary TEXT,
    start_datetime TEXT NOT NULL,
    end_datetime TEXT,
    location TEXT,
    description TEXT,
    raw_data TEXT,
    fetched_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_start ON events(start_datetime);
CREATE INDEX IF NOT EXISTS idx_calendar ON events(calendar_name);
CREATE INDEX IF NOT EXISTS idx_fetched ON events(fetched_at);
"""


class EventCache:
    """SQLite-backed event cache."""
    
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(SCHEMA)
    
    def store_events(self, calendar_name: str, events: List[Dict]):
        """Store events for a calendar, replacing existing."""
        fetched_at = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Delete old events for this calendar
            conn.execute("DELETE FROM events WHERE calendar_name = ?", (calendar_name,))
            
            # Insert new events
            for event in events:
                conn.execute("""
                    INSERT INTO events (id, calendar_name, summary, start_datetime, 
                                       end_datetime, location, description, raw_data, fetched_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event["id"],
                    calendar_name,
                    event.get("summary", ""),
                    event["start"],
                    event.get("end"),
                    event.get("location"),
                    event.get("description"),
                    json.dumps(event),
                    fetched_at
                ))
            
            conn.commit()
        
        logger.info(f"Cached {len(events)} events for {calendar_name}")
    
    def get_events(self, start: datetime, end: datetime, 
                   calendar_name: Optional[str] = None) -> List[Dict]:
        """Get events in date range."""
        start_str = start.isoformat()
        end_str = end.isoformat()
        
        query = """
            SELECT raw_data FROM events 
            WHERE start_datetime >= ? AND start_datetime <= ?
        """
        params = [start_str, end_str]
        
        if calendar_name:
            query += " AND calendar_name = ?"
            params.append(calendar_name)
        
        query += " ORDER BY start_datetime"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
        
        return [json.loads(row[0]) for row in rows]
    
    def get_last_fetch(self, calendar_name: str) -> Optional[datetime]:
        """Get timestamp of last fetch for a calendar."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT MAX(fetched_at) FROM events WHERE calendar_name = ?",
                (calendar_name,)
            )
            result = cursor.fetchone()
            if result and result[0]:
                return datetime.fromisoformat(result[0])
        return None
    
    def cleanup_old(self, retention_days: int = 90):
        """Remove events older than retention period."""
        cutoff = (datetime.now() - timedelta(days=retention_days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM events WHERE fetched_at < ?",
                (cutoff,)
            )
            conn.commit()
            logger.info(f"Cleaned up {cursor.rowcount} old events")

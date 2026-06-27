"""Configuration loader for pi-calendar."""
import os
from pathlib import Path
from typing import List, Dict, Any
import yaml

DEFAULT_CONFIG = {
    "calendars": [],
    "display": {
        "first_day_of_week": "sunday",
        "show_week_numbers": False,
        "default_view": "month",
    },
    "refresh": {
        "interval_minutes": 30,
        "timeout_seconds": 30,
    },
    "cache": {
        "db_path": "data/events.db",
        "retention_days": 90,
    },
}


class Config:
    """Calendar configuration."""
    
    def __init__(self, config_path: str = "config/calendar.yaml"):
        self.config_path = Path(config_path)
        self._data = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """Load config from YAML, merging with defaults."""
        data = DEFAULT_CONFIG.copy()
        
        if self.config_path.exists():
            with open(self.config_path) as f:
                user_config = yaml.safe_load(f) or {}
                data = self._merge(data, user_config)
        
        return data
    
    def _merge(self, default: Dict, user: Dict) -> Dict:
        """Deep merge user config into defaults."""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge(result[key], value)
            else:
                result[key] = value
        return result
    
    @property
    def calendars(self) -> List[Dict]:
        return self._data.get("calendars", [])
    
    @property
    def display(self) -> Dict[str, Any]:
        return self._data.get("display", {})
    
    @property
    def refresh_interval(self) -> int:
        return self._data.get("refresh", {}).get("interval_minutes", 30)
    
    @property
    def cache_db_path(self) -> Path:
        path = self._data.get("cache", {}).get("db_path", "data/events.db")
        return Path(path).expanduser()
    
    def validate(self) -> List[str]:
        """Return list of validation errors."""
        errors = []
        
        if not self.calendars:
            errors.append("No calendars configured. Add at least one iCal URL to config/calendar.yaml")
        
        for i, cal in enumerate(self.calendars):
            if not cal.get("url"):
                errors.append(f"Calendar {i+1} missing 'url' field")
            if not cal.get("name"):
                errors.append(f"Calendar {i+1} missing 'name' field")
        
        return errors

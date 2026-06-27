import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import Config


def test_default_config():
    """Test config loads defaults when file doesn't exist."""
    config = Config("/nonexistent/config.yaml")
    assert config.refresh_interval == 30
    assert config.calendars == []


def test_config_merge():
    """Test user config overrides defaults."""
    import tempfile
    import yaml
    
    test_config = {
        "calendars": [{"name": "Test", "url": "http://test.com/ical.ics", "color": "#ff0000"}],
        "refresh": {"interval_minutes": 15},
    }
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(test_config, f)
        temp_path = f.name
    
    try:
        config = Config(temp_path)
        assert config.refresh_interval == 15
        assert len(config.calendars) == 1
        assert config.calendars[0]["name"] == "Test"
    finally:
        os.unlink(temp_path)


def test_config_validation():
    """Test validation catches missing fields."""
    config = Config("/nonexistent/config.yaml")
    errors = config.validate()
    assert "No calendars configured" in errors[0]

"""Theme loader and CSS generator."""
from pathlib import Path
from typing import Dict, Any
import yaml

DEFAULT_THEME = {
    "name": "Default",
    "colors": {
        "background": "#0a0a0f",
        "foreground": "#e0e0e0",
        "primary": "#00f0ff",
        "secondary": "#ff00ff",
        "accent": "#ffaa00",
        "border": "#00f0ff",
        "today_bg": "#ff00ff",
        "today_fg": "#ffffff",
        "header_bg": "#1a0a2e",
        "header_fg": "#00f0ff",
        "sidebar_bg": "#0f0a1a",
        "sidebar_fg": "#e0e0e0",
        "calendar_bg": "#0a0a0f",
        "calendar_fg": "#e0e0e0",
        "grid_lines": "#1a1a2e",
    },
    "calendar_colors": ["#00f0ff", "#ff00ff", "#ffaa00", "#00ff88"],
    "style": {
        "border_type": "solid",
        "border_width": 1,
        "header_art": "synthwave",
        "show_grid": True,
        "today_shape": "◆",
        "event_indicator": "█",
        "font_style": "bold",
    }
}


class Theme:
    """Color theme manager."""
    
    def __init__(self, themes_path: str = "config/themes.yaml"):
        self.themes_path = Path(themes_path)
        self._data = self._load()
        self._active = self._data.get("active_theme", "synthwave")
        self._theme = self._get_theme(self._active)
    
    def _load(self) -> Dict[str, Any]:
        """Load themes from YAML."""
        if self.themes_path.exists():
            with open(self.themes_path) as f:
                return yaml.safe_load(f) or {}
        return {"active_theme": "synthwave", "schemes": {}}
    
    def _get_theme(self, name: str) -> Dict[str, Any]:
        """Get a specific theme by name."""
        schemes = self._data.get("schemes", {})
        return schemes.get(name, DEFAULT_THEME)
    
    @property
    def name(self) -> str:
        return self._theme.get("name", "Unknown")
    
    @property
    def colors(self) -> Dict[str, str]:
        return {**DEFAULT_THEME["colors"], **self._theme.get("colors", {})}
    
    @property
    def calendar_colors(self) -> list:
        return self._theme.get("calendar_colors", DEFAULT_THEME["calendar_colors"])
    
    @property
    def style(self) -> Dict[str, Any]:
        return {**DEFAULT_THEME["style"], **self._theme.get("style", {})}
    
    def get_color(self, name: str, default: str = "#ffffff") -> str:
        """Get a color by name."""
        return self.colors.get(name, default)
    
    def get_style(self, name: str, default: Any = None):
        """Get a style property."""
        return self.style.get(name, default)
    
    def generate_css(self) -> str:
        """Generate Textual CSS from theme."""
        c = self.colors
        s = self.style
        
        border_style = s.get("border_type", "solid")
        
        css = f'''
/* Theme: {self.name} */
/* Auto-generated from config/themes.yaml */

Screen {{
    align: center middle;
    background: {c["background"]};
}}

#main-container {{
    width: 100%;
    height: 100%;
    background: {c["background"]};
}}

#calendar-panel {{
    width: 70%;
    height: 100%;
    border: {border_style} {c["border"]};
    background: {c["calendar_bg"]};
}}

#sidebar {{
    width: 30%;
    height: 100%;
    border: {border_style} {c["border"]};
    background: {c["sidebar_bg"]};
}}

#events-header {{
    height: 3;
    content-align: center middle;
    text-style: {s.get("font_style", "bold")};
    color: {c["header_fg"]};
    background: {c["sidebar_bg"]};
}}

Header {{
    background: {c["header_bg"]};
    color: {c["header_fg"]};
}}

Header .title {{
    color: {c["header_fg"]};
}}

Header .clock {{
    color: {c["muted"]};
}}

DataTable {{
    width: 100%;
    height: 100%;
    background: {c["calendar_bg"]};
    color: {c["calendar_fg"]};
}}

DataTable > .datatable--header {{
    color: {c["primary"]};
    text-style: bold;
}}

DataTable > .datatable--row-hover {{
    background: {c["grid_lines"]};
}}

ListView {{
    width: 100%;
    height: 1fr;
    background: {c["sidebar_bg"]};
}}

ListItem {{
    color: {c["sidebar_fg"]};
}}

ListItem:hover {{
    background: {c["grid_lines"]};
}}

Footer {{
    background: {c["header_bg"]};
}}

Footer .key {{
    color: {c["primary"]};
}}

.today {{
    background: {c["today_bg"]};
    color: {c["today_fg"]};
}}

.event-dot {{
    color: {c["primary"]};
}}

/* Scrollbar styling */
Scrollbar {{
    background: {c["background"]};
}}

Scrollbar .thumb {{
    background: {c["muted"]};
}}

Scrollbar .thumb:hover {{
    background: {c["primary"]};
}}
'''
        return css

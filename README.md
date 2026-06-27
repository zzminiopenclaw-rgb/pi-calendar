# 📅 Pi Calendar

A lightweight TUI calendar display for Raspberry Pi Zero. No browser required.

**RAM Usage:** ~30-50MB  
**Auto-start:** Yes, via systemd  
**Offline capable:** Cached events work without network

---

## Quick Start

```bash
# Clone from GitHub
cd ~
git clone https://github.com/zzminiopenclaw-rgb/pi-calendar.git
cd pi-calendar

# Run setup (installs deps + configures auto-start on display)
sudo ./setup.sh

# Configure your calendars
nano config/calendar.yaml

# Start
sudo systemctl start pi-calendar
```

---

## Configuration

Edit `config/calendar.yaml`:

```yaml
calendars:
  - name: "Personal"
    url: "https://calendar.google.com/calendar/ical/.../basic.ics"
    color: "#3b82f6"
  - name: "Work"
    url: "https://outlook.office365.com/owa/calendar/.../calendar.ics"
    color: "#ef4444"

display:
  first_day_of_week: "sunday"  # or "monday"
  default_view: "month"

refresh:
  interval_minutes: 30
```

---

## Controls

| Key | Action |
|-----|--------|
| `q` | Quit |
| `r` | Refresh calendars |
| `t` | Jump to today |
| `←` / `→` | Previous/Next month |
| `h` | Show help |

---

## Systemd Commands

```bash
# Start/stop
sudo systemctl start pi-calendar
sudo systemctl stop pi-calendar

# Auto-start on boot
sudo systemctl enable pi-calendar

# View logs
sudo journalctl -u pi-calendar -f

# Check status
sudo systemctl status pi-calendar
```

---

## Hardware Notes

Tested on:
- Raspberry Pi Zero 2 W (512MB RAM)
- Raspberry Pi Zero W (512MB RAM)

Display: HDMI monitor or PiTFT (auto-detected TTY)

---

## iCal URLs

**Google Calendar:**
- Settings → Settings for my calendars → Integrate calendar → Secret address in iCal format

**Outlook/Office365:**
- Settings → View all Outlook settings → Calendar → Shared calendars → Publish calendar → ICS link

**Apple iCloud:**
- Calendar app → Calendar info → Make public → Copy URL (replace `webcal://` with `https://`)

---

## Troubleshooting

**Calendar not starting:**
```bash
# Check logs
sudo journalctl -u pi-calendar -n 50

# Verify config
sudo -u pi /home/pi/pi-calendar/.venv/bin/python -c "from src.config import Config; c = Config(); print(c.validate())"
```

**Display issues on TTY:**
```bash
# Force TTY mode
export TERM=linux
export TERMINFO=/lib/terminfo
```

---

## Project Structure

```
~/pi-calendar/
├── src/                   # Python source
│   ├── main.py           # TUI app entry
│   ├── config.py         # Config loader
│   ├── cache.py          # SQLite cache
│   ├── event_fetcher.py  # iCal fetcher
│   ├── calendar_view.py  # Month view widget
│   └── widgets/          # UI widgets
├── config/               # Configuration
├── data/                 # SQLite cache (gitignored)
├── systemd/              # Systemd service
├── tests/                # Unit tests
├── requirements.txt      # Python deps
└── install.sh            # One-command install
```

---

## License

MIT

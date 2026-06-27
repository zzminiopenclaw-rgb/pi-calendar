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

# Run full installation (creates venv, installs deps, configures autologin)
sudo ./install.sh

# Configure your calendars
nano config/calendar.yaml

# Reboot to start on display
sudo reboot
```

After reboot, the calendar appears on TTY1 (the physical display). SSH in separately to configure.

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

## Updating

To get the latest code and restart:

```bash
cd ~/pi-calendar
git pull
./restart.sh
```

If dependencies changed (new packages in requirements.txt), reinstall:

```bash
cd ~/pi-calendar
source .venv/bin/activate
pip install -r requirements.txt
./restart.sh
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

## Restarting After Code Updates

```bash
cd ~/pi-calendar
git pull
./restart.sh
```

Or manually:
```bash
sudo pkill -f "src.main"
```

Wait 5 seconds, then calendar auto-restarts on TTY1.

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
# Check if process is running
ps aux | grep src.main

# Check logs in data/calendar.log
cat ~/pi-calendar/data/calendar.log

# Verify config
source ~/pi-calendar/.venv/bin/activate
python -c "from src.config import Config; c = Config(); print(c.validate())"
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
├── install.sh           # Auto-start on TTY1 setup
├── restart.sh           # Quick restart script
└── README.md
```

---

## License

MIT

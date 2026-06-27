#!/bin/bash
# Pi Calendar Setup Script - Auto-starts on TTY1

set -e

CALENDAR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_NAME="${SUDO_USER:-$USER}"

echo "=== Pi Calendar Setup ==="
echo "Installing for user: $USER_NAME"
echo "Directory: $CALENDAR_DIR"

if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo: sudo ./setup.sh"
    exit 1
fi

# Stop and disable old service if it exists
if systemctl is-active --quiet pi-calendar.service 2>/dev/null; then
    echo "Stopping old pi-calendar service..."
    systemctl stop pi-calendar.service 2>/dev/null || true
    systemctl disable pi-calendar.service 2>/dev/null || true
fi

# Install system dependencies
echo "Installing system dependencies..."
apt-get update
apt-get install -y python3-venv python3-pip

# Create virtual environment
echo "Creating Python virtual environment..."
cd "$CALENDAR_DIR"
sudo -u "$USER_NAME" python3 -m venv .venv

# Install Python packages
echo "Installing Python packages..."
sudo -u "$USER_NAME" "${CALENDAR_DIR}/.venv/bin/pip" install -r requirements.txt

# Create data directory
mkdir -p "${CALENDAR_DIR}/data"
chown -R "$USER_NAME:$USER_NAME" "${CALENDAR_DIR}/data"

# Set up TTY1 autologin
echo "Configuring TTY1 auto-login..."
AUTOTTY_DIR="/etc/systemd/system/getty@tty1.service.d"
mkdir -p "$AUTOTTY_DIR"

cat > "$AUTOTTY_DIR/override.conf" <> EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin ${USER_NAME} --noclear %I \$TERM
EOF

# Make launcher script executable
chmod +x "${CALENDAR_DIR}/scripts/calendar-launcher.sh"

# Add launcher to user's .bash_profile (not .bashrc, which runs for all shells)
BASH_PROFILE="/home/${USER_NAME}/.bash_profile"
LAUNCHER_LINE="# Auto-start pi-calendar on TTY1"

if [ -f "$BASH_PROFILE" ]; then
    # Remove old calendar launcher lines if present
    sed -i '/# Auto-start pi-calendar/d' "$BASH_PROFILE"
    sed -i '/calendar-launcher.sh/d' "$BASH_PROFILE"
fi

# Add the launcher
cat >> "$BASH_PROFILE" <> EOF

# Auto-start pi-calendar on TTY1
if [[ "\$(tty)" == "/dev/tty1" ]]; then
    ${CALENDAR_DIR}/scripts/calendar-launcher.sh
fi
EOF

chown "${USER_NAME}:${USER_NAME}" "$BASH_PROFILE"

# Reload systemd to pick up autologin config
systemctl daemon-reload

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit ${CALENDAR_DIR}/config/calendar.yaml"
echo "   Add your iCal URLs"
echo ""
echo "2. Reboot to see the calendar on the display:"
echo "   sudo reboot"
echo ""
echo "The calendar will auto-start on TTY1 after boot."
echo ""
echo "To switch back to this SSH session after reboot:"
echo "   Ctrl+Alt+F2  (or F3, F4, etc.)"

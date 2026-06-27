#!/bin/bash
# Pi Calendar Installation Script

set -e

CALENDAR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_NAME="${SUDO_USER:-$USER}"

echo "=== Pi Calendar Installer ==="
echo "Installing for user: $USER_NAME"
echo "Directory: $CALENDAR_DIR"

# Check if running as root for systemd
if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo: sudo ./install.sh"
    exit 1
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

# Install systemd service
echo "Installing systemd service..."
sed "s|%I|${USER_NAME}|g" "${CALENDAR_DIR}/systemd/pi-calendar.service" > /etc/systemd/system/pi-calendar.service

# Reload and enable systemd
systemctl daemon-reload
systemctl enable pi-calendar.service

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit ${CALENDAR_DIR}/config/calendar.yaml"
echo "   Add your iCal URLs"
echo ""
echo "2. Start the calendar:"
echo "   sudo systemctl start pi-calendar"
echo ""
echo "3. Check status:"
echo "   sudo systemctl status pi-calendar"
echo ""
echo "4. View logs:"
echo "   sudo journalctl -u pi-calendar -f"
echo ""
echo "The calendar will auto-start on boot."

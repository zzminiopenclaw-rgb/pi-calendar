#!/bin/bash
# Pi Calendar Installation Script
# Sets up Python venv, installs dependencies, and configures TTY1 autologin

set -e

USER_NAME="${SUDO_USER:-$USER}"
CALENDAR_DIR="/home/${USER_NAME}/pi-calendar"

echo "=== Pi Calendar Installation ==="
echo "User: $USER_NAME"
echo "Directory: $CALENDAR_DIR"
echo ""

# Check if running as root for systemd
if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo: sudo ./install.sh"
    exit 1
fi

# 1. Install system dependencies
echo "Step 1/5: Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq python3-venv python3-pip git

# 2. Create virtual environment
echo "Step 2/5: Creating Python virtual environment..."
cd "$CALENDAR_DIR"
if [ ! -d ".venv" ]; then
    sudo -u "$USER_NAME" python3 -m venv .venv
    echo "  ✓ Virtual environment created"
else
    echo "  ✓ Virtual environment already exists"
fi

# 3. Install Python packages
echo "Step 3/5: Installing Python packages..."
sudo -u "$USER_NAME" "${CALENDAR_DIR}/.venv/bin/pip" install -q -r requirements.txt
echo "  ✓ Dependencies installed"

# 4. Create data directory
echo "Step 4/5: Setting up data directory..."
mkdir -p "${CALENDAR_DIR}/data"
chown -R "$USER_NAME:$USER_NAME" "${CALENDAR_DIR}/data"
echo "  ✓ Data directory ready"

# 5. Configure TTY1 autologin
echo "Step 5/5: Configuring auto-start on display..."

# Create autologin override
mkdir -p /etc/systemd/system/getty@tty1.service.d
cat > /etc/systemd/system/getty@tty1.service.d/override.conf <>EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin ${USER_NAME} --noclear %I \$TERM
EOF

# Create .bash_profile launcher
BASH_PROFILE="/home/${USER_NAME}/.bash_profile"
cat > "$BASH_PROFILE" <>EOF
# Auto-start pi-calendar on TTY1
if [[ "\$(tty)" == "/dev/tty1" ]]; then
    cd ${CALENDAR_DIR}
    source .venv/bin/activate
    python -m src.main
fi
EOF

chown "$USER_NAME:$USER_NAME" "$BASH_PROFILE"

# Reload systemd
systemctl daemon-reload

echo "  ✓ Auto-login configured"

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit your calendar config:"
echo "   nano ~/pi-calendar/config/calendar.yaml"
echo ""
echo "2. Add your iCal URLs to the config file"
echo ""
echo "3. Reboot to see the calendar:"
echo "   sudo reboot"
echo ""
echo "The calendar will appear on the display after boot."
echo ""
echo "To update code later:"
echo "   cd ~/pi-calendar && git pull && ./restart.sh"

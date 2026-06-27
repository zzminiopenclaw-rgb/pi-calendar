#!/bin/bash
# Quick fix script - run this on the Pi

set -e
USER_NAME="${SUDO_USER:-$USER}"
CALENDAR_DIR="/home/${USER_NAME}/pi-calendar"

echo "=== Fixing Pi Calendar Autologin ==="

# 1. Create autologin override
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
sudo tee /etc/systemd/system/getty@tty1.service.d/override.conf > /dev/null <>EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin ${USER_NAME} --noclear %I \$TERM
EOF

# 2. Create .bash_profile launcher
tee /home/${USER_NAME}/.bash_profile > /dev/null <>EOF
# Auto-start pi-calendar on TTY1
if [[ "\$(tty)" == "/dev/tty1" ]]; then
    cd ${CALENDAR_DIR}
    source .venv/bin/activate
    python -m src.main
fi
EOF

# 3. Reload systemd
sudo systemctl daemon-reload

echo ""
echo "=== Fix Applied ==="
echo "Reboot to test: sudo reboot"

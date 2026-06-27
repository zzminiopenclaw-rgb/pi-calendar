#!/bin/bash
# Quick fix script - run this on the Pi

set -e
USER_NAME="${SUDO_USER:-$USER}"
CALENDAR_DIR="/home/${USER_NAME}/pi-calendar"

echo "=== Fixing Pi Calendar Autologin ==="
echo "User: $USER_NAME"
echo "Directory: $CALENDAR_DIR"

# 1. Create autologin override directory
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d

# 2. Write autologin config (line by line, no heredoc)
echo "Creating autologin override..."
echo '[Service]' | sudo tee /etc/systemd/system/getty@tty1.service.d/override.conf > /dev/null
echo 'ExecStart=' | sudo tee -a /etc/systemd/system/getty@tty1.service.d/override.conf > /dev/null
echo "ExecStart=-/sbin/agetty --autologin ${USER_NAME} --noclear %I \$TERM" | sudo tee -a /etc/systemd/system/getty@tty1.service.d/override.conf > /dev/null

# 3. Create .bash_profile (line by line)
echo "Creating .bash_profile..."
echo '# Auto-start pi-calendar on TTY1' > /home/${USER_NAME}/.bash_profile
echo 'if [[ "$(tty)" == "/dev/tty1" ]]; then' >> /home/${USER_NAME}/.bash_profile
echo "    cd ${CALENDAR_DIR}" >> /home/${USER_NAME}/.bash_profile
echo '    source .venv/bin/activate' >> /home/${USER_NAME}/.bash_profile
echo '    python -m src.main' >> /home/${USER_NAME}/.bash_profile
echo 'fi' >> /home/${USER_NAME}/.bash_profile

# 4. Reload systemd
echo "Reloading systemd..."
sudo systemctl daemon-reload

echo ""
echo "=== Fix Applied ==="
echo "Reboot to test: sudo reboot"

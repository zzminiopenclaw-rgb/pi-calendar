#!/bin/bash
# Auto-launch calendar on TTY1

if [[ "$(tty)" == "/dev/tty1" ]]; then
    cd ~/pi-calendar
    source .venv/bin/activate
    
    # Clear screen and run calendar
    clear
    python -m src.main
    
    # If calendar exits, drop to shell
    echo "Calendar exited. Press Enter for shell..."
    read
fi

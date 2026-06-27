#!/bin/bash
# Quick restart script for pi-calendar

echo "=== Restarting Pi Calendar ==="

# Kill any running calendar processes
sudo pkill -9 -f "src.main" 2>/dev/null || true

# Wait a moment
sleep 2

echo "Killed old process"
echo "Calendar will auto-restart on TTY1 in ~5 seconds"
echo ""
echo "Switch to TTY1 with: sudo chvt 1"

#!/bin/bash
#
# TrustLab Security Monitoring Service - Stop Script
#

# Directory where scripts are located
SCRIPT_DIR="$(dirname "$0")"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"

# Function to log messages with timestamps
log() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_DIR/service.log"
}

# Create log directory if it doesn't exist (for logging)
mkdir -p "$LOG_DIR"

# Stop APT Monitor
if pgrep -f "python3 $PROJECT_ROOT/main.py --monitor" > /dev/null; then
    log "Stopping APT Monitor service..."
    pkill -f "python3 $PROJECT_ROOT/main.py --monitor"
    log "APT Monitor service stopped"
    
    # Remove PID file if it exists
    if [ -f "$SCRIPT_DIR/.apt_monitor.pid" ]; then
        rm "$SCRIPT_DIR/.apt_monitor.pid"
    fi
else
    log "APT Monitor is not running"
fi

# Remove bruteforce detector from crontab
if crontab -l 2>/dev/null | grep -q "bruteforce_detector.py"; then
    log "Removing bruteforce detector from cron jobs..."
    crontab -l 2>/dev/null | grep -v "bruteforce_detector.py" | crontab -
    log "Bruteforce detector removed from scheduled tasks"
else
    log "No bruteforce detector cron job found"
fi

echo
echo "==================================================="
echo "   TrustLab Security Monitoring System Stopped"
echo "==================================================="
echo "APT Monitor        : Stopped"
echo "Bruteforce Detector: Removed from scheduled tasks"
echo "==================================================="

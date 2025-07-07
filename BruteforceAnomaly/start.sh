#!/bin/bash
# Start script for SSH Brute Force Detection & APT Correlation System
# This script sets up cron jobs for brute force detection and starts APT monitoring

# Get absolute path for the project
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR" || {
    echo "❌ Failed to change directory to script location"
    exit 1
}

echo "🚀 Starting SSH Brute Force Detection & APT Correlation System..."

# Check if we're running as root (needed for some operations)
if [ "$(id -u)" -ne 0 ]; then
    echo "⚠️ Warning: Some operations may require root privileges"
    echo "   Consider running with sudo if you encounter permission issues"
fi

# Setup cron job to run the brute force detector every 60 seconds
echo "🕒 Setting up cron job for periodic brute force detection..."
CRON_TEMP=$(mktemp)
crontab -l > "$CRON_TEMP" 2>/dev/null || echo "" > "$CRON_TEMP"
CRON_ENTRY="* * * * * cd $SCRIPT_DIR && python3 $SCRIPT_DIR/src/bruteforce_detector.py > /dev/null 2>&1"

if ! grep -q "bruteforce_detector.py" "$CRON_TEMP"; then
    echo "$CRON_ENTRY" >> "$CRON_TEMP"
    crontab "$CRON_TEMP"
    echo "✅ Cron job set up to run bruteforce detector every minute"
else
    echo "✅ Bruteforce detector cron job already exists"
fi
rm -f "$CRON_TEMP"

# Ask if the user wants to start APT monitoring
read -p "🔍 Do you want to start APT monitoring service? (y/n): " START_APT
if [[ "$START_APT" =~ ^[Yy]$ ]]; then
    echo "🔍 Starting APT monitoring service..."
    
    # Check if we should use systemd or direct execution
    if [ -f "/etc/systemd/system/bruteforce-anomaly.service" ]; then
        echo "🔧 Using systemd service for APT monitoring..."
        sudo systemctl start bruteforce-anomaly
        
        # Check status
        if systemctl is-active --quiet bruteforce-anomaly; then
            echo "✅ APT monitoring service started successfully via systemd"
        else
            echo "❌ Failed to start APT monitoring service via systemd"
            echo "   Attempting direct execution..."
            nohup python3 "$SCRIPT_DIR/main.py" --monitor > /dev/null 2>&1 &
            echo "✅ APT monitoring started in background"
        fi
    else
        echo "🔧 Starting APT monitoring directly..."
        nohup python3 "$SCRIPT_DIR/main.py" --monitor > /dev/null 2>&1 &
        echo "✅ APT monitoring started in background"
    fi
else
    echo "ℹ️ Skipping APT monitoring service"
fi

echo ""
echo "✅ System successfully started"
echo "   - Bruteforce detection runs via cron job every minute"
if [[ "$START_APT" =~ ^[Yy]$ ]]; then
    echo "   - APT monitoring service is running in background"
fi
echo ""
echo "📋 System Management:"
echo "   - To stop services: ./stop.sh"
echo "   - To check status: crontab -l (for cron jobs)"
if [[ "$START_APT" =~ ^[Yy]$ ]]; then
    echo "                   sudo systemctl status bruteforce-anomaly (for APT monitoring)"
fi
echo ""
echo "📝 Log files will be available in the logs/ directory"

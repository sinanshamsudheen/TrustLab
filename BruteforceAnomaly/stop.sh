#!/bin/bash
# Stop script for SSH Brute Force Detection & APT Correlation System
# This script removes cron jobs for brute force detection and stops APT monitoring

# Get absolute path for the project
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR" || {
    echo "❌ Failed to change directory to script location"
    exit 1
}

echo "🛑 Stopping SSH Brute Force Detection & APT Correlation System..."

# Check if we're running as root (needed for some operations)
if [ "$(id -u)" -ne 0 ]; then
    echo "⚠️ Warning: Some operations may require root privileges"
    echo "   Consider running with sudo if you encounter permission issues"
fi

# Remove cron job for brute force detector
echo "🕒 Removing cron job for brute force detection..."
if crontab -l 2>/dev/null | grep -q "bruteforce_detector.py"; then
    crontab -l | grep -v "bruteforce_detector.py" | crontab -
    echo "✅ Bruteforce detector cron job removed successfully"
else
    echo "ℹ️ No bruteforce detector cron job found"
fi

# Ask if the user wants to stop APT monitoring
read -p "🔍 Do you want to stop APT monitoring service? (y/n): " STOP_APT
if [[ "$STOP_APT" =~ ^[Yy]$ ]]; then
    echo "🔍 Stopping APT monitoring service..."
    
    # Check if we should use systemd or direct kill
    if [ -f "/etc/systemd/system/bruteforce-anomaly.service" ]; then
        echo "🔧 Using systemd to stop APT monitoring service..."
        sudo systemctl stop bruteforce-anomaly
        
        # Check status
        if ! systemctl is-active --quiet bruteforce-anomaly; then
            echo "✅ APT monitoring service stopped successfully via systemd"
        else
            echo "❌ Failed to stop APT monitoring service via systemd"
            echo "   Attempting direct process kill..."
            pkill -f "python3.*main.py --monitor" || echo "ℹ️ No running process found"
        fi
    else
        echo "🔧 Stopping APT monitoring directly..."
        pkill -f "python3.*main.py --monitor" || echo "ℹ️ No running process found"
        echo "✅ APT monitoring stopped"
    fi
else
    echo "ℹ️ Leaving APT monitoring service running"
fi

echo ""
echo "✅ System components stopped"
echo "   - Bruteforce detection cron job removed"
if [[ "$STOP_APT" =~ ^[Yy]$ ]]; then
    echo "   - APT monitoring service stopped"
fi
echo ""
echo "📋 System Management:"
echo "   - To start services again: ./start.sh"
echo "   - You can verify no processes are running with:"
echo "     ps aux | grep 'bruteforce\\|apt_monitor'"
echo ""
echo "📝 Log files are still available in the logs/ directory for inspection"

#!/bin/bash
# setup_cron.sh - Set up automatic retraining cron job
# This script adds a cron job to retrain the anomaly detection model
# every week or at a custom interval you specify

# Default values
INSTALL_DIR="/opt/PostfixAnomaly"
DEFAULT_FREQUENCY="weekly"
RETRAINING_SCRIPT="$INSTALL_DIR/retrain_model.sh"
TEMP_CRON_FILE="/tmp/anomaly_crontab"

# Ensure script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "This script needs root privileges to set up the cron job."
  echo "Please run with sudo: sudo $0"
  exit 1
fi

# Make sure retrain_model.sh exists and is executable
if [ ! -f "$RETRAINING_SCRIPT" ]; then
  echo "ERROR: Retraining script not found at $RETRAINING_SCRIPT"
  exit 1
fi

chmod +x "$RETRAINING_SCRIPT"

# Check parameters
FREQUENCY="${1:-$DEFAULT_FREQUENCY}"

case "$FREQUENCY" in
    "daily")
        CRON_SCHEDULE="0 2 * * *"  # Every day at 2:00 AM
        DESCRIPTION="daily (every day at 2:00 AM)"
        ;;
    "weekly")
        CRON_SCHEDULE="0 2 * * 0"  # Every Sunday at 2:00 AM
        DESCRIPTION="weekly (every Sunday at 2:00 AM)"
        ;;
    "monthly")
        CRON_SCHEDULE="0 2 1 * *"  # Every 1st day of the month at 2:00 AM
        DESCRIPTION="monthly (on the 1st of every month at 2:00 AM)"
        ;;
    *)
        echo "Invalid frequency: $FREQUENCY"
        echo "Valid options are: daily, weekly, monthly"
        exit 1
        ;;
esac

# Backup existing crontab
crontab -l > "$TEMP_CRON_FILE" 2>/dev/null || echo "" > "$TEMP_CRON_FILE"

# Check if cron job already exists
if grep -q "$RETRAINING_SCRIPT" "$TEMP_CRON_FILE"; then
    # Update existing cron job
    sed -i "/.*$RETRAINING_SCRIPT.*/d" "$TEMP_CRON_FILE"
    echo "Updated existing cron job."
fi

# Add new cron job
echo "# PostfixAnomaly: Automated model retraining ($DESCRIPTION)" >> "$TEMP_CRON_FILE"
echo "$CRON_SCHEDULE $RETRAINING_SCRIPT >> $INSTALL_DIR/logs/retraining.log 2>&1" >> "$TEMP_CRON_FILE"

# Install new crontab
crontab "$TEMP_CRON_FILE"

# Clean up
rm "$TEMP_CRON_FILE"

echo "✅ Cron job set up successfully for $DESCRIPTION retraining"
echo "📅 Schedule: $CRON_SCHEDULE"
echo "📝 Logs will be written to: $INSTALL_DIR/logs/retraining.log"
echo ""
echo "To change the frequency later, run:"
echo "  sudo $INSTALL_DIR/setup_cron.sh [daily|weekly|monthly]"
echo ""
echo "To verify the cron job:"
echo "  sudo crontab -l"

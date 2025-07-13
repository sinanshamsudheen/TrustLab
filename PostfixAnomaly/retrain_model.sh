#!/bin/bash
# retrain_model.sh - Script to retrain the anomaly detection model
# This script should be run by a scheduled cron job or manually
# when you want to update the model with new log data
#
# Usage:
#   ./retrain_model.sh [max_lines]
#
# Example:
#   ./retrain_model.sh 50000    # Process the last 50,000 lines from each log file

# Define constants
INSTALL_DIR="/opt/PostfixAnomaly"
LOG_DIR="/var/log"
POSTFIX_LOGS="${LOG_DIR}/mail.log"
ROUNDCUBE_LOGS="${LOG_DIR}/cse_roundcube_userlogins.log"
RETRAINING_LOGS="${INSTALL_DIR}/logs/retraining.log"
TEMP_DIR="/tmp/anomaly_retraining"
MAX_LINES=${1:-100000}  # Default: 100,000 lines (1 lakh), can be overridden by command-line parameter

# Create logs directory if it doesn't exist
mkdir -p "$(dirname $RETRAINING_LOGS)"

# Function for logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$RETRAINING_LOGS"
}

# Start retraining process
log "====== Starting model retraining ======"
log "Install directory: $INSTALL_DIR"
log "Postfix logs: $POSTFIX_LOGS"
log "Roundcube logs: $ROUNDCUBE_LOGS"
log "Max lines to process per log: $MAX_LINES"

# Check if log files exist
if [ ! -f "$POSTFIX_LOGS" ]; then
    log "ERROR: Postfix log file not found at $POSTFIX_LOGS"
    log "Retraining aborted."
    exit 1
fi

if [ ! -f "$ROUNDCUBE_LOGS" ]; then
    log "ERROR: Roundcube log file not found at $ROUNDCUBE_LOGS"
    log "Retraining aborted."
    exit 1
fi

# Ensure temporary directory exists
mkdir -p "$TEMP_DIR"
log "Created temporary directory: $TEMP_DIR"

# Run the retraining script
log "Running retraining script..."

# Move to the installation directory
cd "$INSTALL_DIR"

# Run the retrain.py script
python3 "$INSTALL_DIR/src/retrain.py" \
    --postfix-logs="$POSTFIX_LOGS" \
    --roundcube-logs="$ROUNDCUBE_LOGS" \
    --output-dir="$INSTALL_DIR/models" \
    --contamination=0.001 \
    --n-estimators=100 \
    --max-lines="$MAX_LINES" \
    --temp-dir="$TEMP_DIR"

# Check if retraining was successful
RETRAIN_EXIT_CODE=$?
if [ $RETRAIN_EXIT_CODE -ne 0 ]; then
    log "ERROR: Retraining failed with exit code $RETRAIN_EXIT_CODE"
    log "Check the logs for details."
    exit 1
fi

log "Model retraining completed successfully!"

# Restart the service if it's running
if systemctl is-active --quiet anomalypostfix; then
    log "Restarting anomaly detection service to use the new model..."
    systemctl restart anomalypostfix
    
    # Check if restart was successful
    if [ $? -eq 0 ]; then
        log "Service restarted successfully."
    else
        log "WARNING: Failed to restart the service. You may need to restart it manually."
    fi
else
    log "Anomaly detection service is not running. No need to restart."
fi

# Clean up temporary files
rm -rf "$TEMP_DIR"
log "Removed temporary directory"

log "====== Retraining process completed ======"
log ""

exit 0

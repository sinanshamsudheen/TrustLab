#!/bin/bash
#
# TrustLab Security Monitoring Service
# Starts both the bruteforce detection and APT monitoring services
#

# Directory where scripts are located
PROJECT_NAME="BruteforceAnomaly"
PROJECT_ROOT="/opt/$PROJECT_NAME"
SCRIPT_DIR="$PROJECT_ROOT/config"
LOG_DIR="$PROJECT_ROOT/logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to log messages with timestamps
log() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_DIR/service.log"
}

# Function to check if a process is already running
is_running() {
    pgrep -f "$1" > /dev/null
    return $?
}

# Make sure we're in the project root directory
cd "$PROJECT_ROOT" || {
    log "ERROR: Could not change to project root directory $PROJECT_ROOT"
    exit 1
}

# Start APT Monitor if not already running
if is_running "python3 main.py --monitor"; then
    log "APT Monitor is already running"
else
    log "Starting APT Monitor service..."
    python3 "$PROJECT_ROOT/main.py" --monitor > "$LOG_DIR/apt_monitor_$TIMESTAMP.log" 2>&1 &
    APT_PID=$!
    log "APT Monitor started with PID: $APT_PID"
    
    # Save PID for service management
    echo "$APT_PID" > "$SCRIPT_DIR/.apt_monitor.pid"
fi

# Set up a cron job for bruteforce detector if not already set up
setup_bruteforce_cron() {
    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "bruteforce_detector.py"; then
        log "Bruteforce detector cron job already exists"
    else
        log "Setting up cron job for bruteforce detector"
        # Run every minute
        (crontab -l 2>/dev/null; echo "* * * * * cd $SCRIPT_DIR && python3 $SCRIPT_DIR/bruteforce_detector.py >> $LOG_DIR/bruteforce_detector.log 2>&1") | crontab -
        log "Cron job added: bruteforce detector will run every minute"
    fi
}

# Setup logs for rotation
setup_logrotate() {
    if [ ! -f "/etc/logrotate.d/trustlab" ]; then
        log "Setting up log rotation for TrustLab services"
        cat > /tmp/trustlab_logrotate << EOF
$LOG_DIR/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 root root
}
EOF
        # Move to logrotate.d if running as root, otherwise inform user
        if [ $(id -u) -eq 0 ]; then
            mv /tmp/trustlab_logrotate /etc/logrotate.d/trustlab
            log "Log rotation configured"
        else
            log "Please run as root to install logrotate configuration:"
            log "sudo mv /tmp/trustlab_logrotate /etc/logrotate.d/trustlab"
        fi
    fi
}

# Set up bruteforce detector cron job
setup_bruteforce_cron

# Set up log rotation if possible
setup_logrotate

# Initial run of bruteforce detector
log "Running initial bruteforce detection scan..."
python3 "$SCRIPT_DIR/bruteforce_detector.py" >> "$LOG_DIR/bruteforce_detector.log" 2>&1

log "TrustLab Security Monitoring Services started successfully"
log "APT Monitor is running as a background service"
log "Bruteforce Detector will run every minute via cron"
log "Logs are available in $LOG_DIR"

# Display status
echo
echo "==================================================="
echo "   TrustLab Security Monitoring System Started"
echo "==================================================="
echo "APT Monitor       : Running (PID: $APT_PID)"
echo "Bruteforce Detector: Scheduled (every minute via cron)"
echo "Log Directory     : $LOG_DIR"
echo
echo "Use 'tail -f $LOG_DIR/apt_monitor_$TIMESTAMP.log' to view APT monitoring"
echo "Use 'tail -f $LOG_DIR/bruteforce_detector.log' to view bruteforce detection"
echo "==================================================="

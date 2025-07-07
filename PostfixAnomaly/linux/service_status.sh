#!/bin/bash
# AnomalyPostfix V2 Service Status for Linux

# Define the installation directory using relative paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
INSTALL_DIR="$(dirname "$SCRIPT_DIR")"

SERVICE_NAME="anomalypostfix"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "This script requires root privileges for detailed service information."
    echo "Running with limited information. For full details, run with sudo."
fi

echo "==== AnomalyPostfix Service Status ===="
echo

# Get service status
systemctl status ${SERVICE_NAME} --no-pager

echo
echo "==== Log Information ===="
echo

# Show recent logs
journalctl -u ${SERVICE_NAME} --no-pager -n 20

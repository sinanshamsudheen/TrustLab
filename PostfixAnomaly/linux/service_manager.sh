#!/bin/bash
# AnomalyPostfix V2 Service Manager for Linux

# Get the directory where this script is located and navigate to parent
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
INSTALL_DIR="$(dirname "$SCRIPT_DIR")"

SERVICE_NAME="anomalypostfix"
SERVICE_FILE="${SCRIPT_DIR}/anomalypostfix.service"
SERVICE_DEST="/etc/systemd/system/${SERVICE_NAME}.service"

function show_usage {
    echo "Usage: $0 [install|start|stop|restart|uninstall]"
    echo
    echo "Commands:"
    echo "  install    - Install the service"
    echo "  start      - Start the service"
    echo "  stop       - Stop the service"
    echo "  restart    - Restart the service"
    echo "  uninstall  - Uninstall the service"
    exit 1
}

function check_root {
    if [ "$EUID" -ne 0 ]; then
        echo "This operation requires root privileges."
        echo "Please run with sudo: sudo $0 $1"
        exit 1
    fi
}

case "$1" in
    install)
        check_root "$1"
        echo "Installing ${SERVICE_NAME} service..."
        
        # Copy service file from installation directory
        cp "${SERVICE_FILE}" "${SERVICE_DEST}"
        
        # Reload systemd
        systemctl daemon-reload
        
        echo "Service installed. Use 'sudo systemctl enable ${SERVICE_NAME}' to enable at boot."
        echo "Start with: sudo systemctl start ${SERVICE_NAME}"
        ;;
        
    start)
        check_root "$1"
        echo "Starting ${SERVICE_NAME} service..."
        systemctl start ${SERVICE_NAME}
        ;;
        
    stop)
        check_root "$1"
        echo "Stopping ${SERVICE_NAME} service..."
        systemctl stop ${SERVICE_NAME}
        ;;
        
    restart)
        check_root "$1"
        echo "Restarting ${SERVICE_NAME} service..."
        systemctl restart ${SERVICE_NAME}
        ;;
        
    uninstall)
        check_root "$1"
        echo "Uninstalling ${SERVICE_NAME} service..."
        
        # Stop the service if running
        systemctl stop ${SERVICE_NAME}
        systemctl disable ${SERVICE_NAME}
        
        # Remove service file
        rm -f ${SERVICE_DEST}
        
        # Reload systemd
        systemctl daemon-reload
        
        echo "Service uninstalled."
        ;;
        
    *)
        show_usage
        ;;
esac

#!/bin/bash
# backup_restore.sh - Script for backing up and restoring the anomaly detection system
# This script can create backups of models and configuration files, and restore from those backups.
#
# Usage:
#   ./backup_restore.sh backup [destination]  # Create a backup archive
#   ./backup_restore.sh restore [archive]     # Restore from a backup archive
#   ./backup_restore.sh list                  # List available backups

# Define constants
INSTALL_DIR="/opt/PostfixAnomaly"
DEFAULT_BACKUP_DIR="/opt/PostfixAnomaly/backups"
LOG_FILE="${INSTALL_DIR}/logs/backup_restore.log"

# Make sure the logs directory exists
mkdir -p "$(dirname $LOG_FILE)"

# Function for logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to create a backup
create_backup() {
    local backup_dir="${1:-$DEFAULT_BACKUP_DIR}"
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_file="${backup_dir}/anomaly_backup_${timestamp}.tar.gz"
    
    # Ensure backup directory exists
    mkdir -p "$backup_dir"
    
    # Start backup process
    log "====== Creating backup ======"
    log "Backup destination: $backup_file"
    
    # Create a temporary directory for organizing files
    local temp_dir="/tmp/anomaly_backup_${timestamp}"
    mkdir -p "$temp_dir"
    
    # Copy important files to temp directory
    log "Copying models..."
    mkdir -p "$temp_dir/models"
    cp -r "$INSTALL_DIR/models/"*.pkl "$temp_dir/models/" 2>/dev/null || log "No model files found to backup"
    
    log "Copying configuration..."
    mkdir -p "$temp_dir/config"
    cp -r "$INSTALL_DIR/config/"* "$temp_dir/config/" 2>/dev/null || log "No configuration files found to backup"
    
    log "Copying regex patterns..."
    mkdir -p "$temp_dir/regexes"
    cp -r "$INSTALL_DIR/regexes/"* "$temp_dir/regexes/" 2>/dev/null || log "No regex files found to backup"
    
    log "Copying feature selections..."
    mkdir -p "$temp_dir/features"
    cp -r "$INSTALL_DIR/features/"* "$temp_dir/features/" 2>/dev/null || log "No feature selection files found to backup"
    
    log "Copying metrics..."
    mkdir -p "$temp_dir/metrics"
    cp -r "$INSTALL_DIR/metrics/"* "$temp_dir/metrics/" 2>/dev/null || log "No metrics files found to backup"
    
    # Create metadata file
    echo "Postfix Anomaly Detection Backup" > "$temp_dir/backup_info.txt"
    echo "Created: $(date '+%Y-%m-%d %H:%M:%S')" >> "$temp_dir/backup_info.txt"
    echo "From: $INSTALL_DIR" >> "$temp_dir/backup_info.txt"
    echo "Contains:" >> "$temp_dir/backup_info.txt"
    find "$temp_dir" -type f | grep -v backup_info.txt | sort >> "$temp_dir/backup_info.txt"
    
    # Create archive
    log "Creating archive..."
    tar -czf "$backup_file" -C "$temp_dir" .
    
    # Check if backup was successful
    if [ $? -eq 0 ]; then
        log "✅ Backup created successfully: $backup_file"
        log "Backup size: $(du -h "$backup_file" | cut -f1)"
        
        # Cleanup
        rm -rf "$temp_dir"
        log "Temporary files cleaned up"
        return 0
    else
        log "❌ Backup failed"
        rm -rf "$temp_dir"
        return 1
    fi
}

# Function to restore from a backup
restore_from_backup() {
    local backup_file="$1"
    
    # Check if backup file exists
    if [ ! -f "$backup_file" ]; then
        log "❌ Backup file not found: $backup_file"
        return 1
    fi
    
    # Start restore process
    log "====== Restoring from backup ======"
    log "Backup file: $backup_file"
    
    # Create a temporary directory for extraction
    local temp_dir="/tmp/anomaly_restore_$(date '+%Y%m%d_%H%M%S')"
    mkdir -p "$temp_dir"
    
    # Extract archive
    log "Extracting backup..."
    tar -xzf "$backup_file" -C "$temp_dir"
    
    if [ $? -ne 0 ]; then
        log "❌ Failed to extract backup"
        rm -rf "$temp_dir"
        return 1
    fi
    
    # Display backup info
    if [ -f "$temp_dir/backup_info.txt" ]; then
        log "Backup information:"
        cat "$temp_dir/backup_info.txt" | while read line; do
            log "  $line"
        done
    fi
    
    # Ask for confirmation before overwriting
    read -p "This will overwrite existing files in $INSTALL_DIR. Continue? (y/n): " confirm
    if [ "$confirm" != "y" ]; then
        log "Restore canceled by user"
        rm -rf "$temp_dir"
        return 1
    fi
    
    # Stop service if running
    if systemctl is-active --quiet anomalypostfix; then
        log "Stopping anomaly detection service..."
        systemctl stop anomalypostfix
    fi
    
    # Restore models
    if [ -d "$temp_dir/models" ] && [ "$(ls -A "$temp_dir/models")" ]; then
        log "Restoring models..."
        mkdir -p "$INSTALL_DIR/models"
        cp -r "$temp_dir/models/"* "$INSTALL_DIR/models/"
    fi
    
    # Restore configuration
    if [ -d "$temp_dir/config" ] && [ "$(ls -A "$temp_dir/config")" ]; then
        log "Restoring configuration..."
        mkdir -p "$INSTALL_DIR/config"
        cp -r "$temp_dir/config/"* "$INSTALL_DIR/config/"
    fi
    
    # Restore regexes
    if [ -d "$temp_dir/regexes" ] && [ "$(ls -A "$temp_dir/regexes")" ]; then
        log "Restoring regex patterns..."
        mkdir -p "$INSTALL_DIR/regexes"
        cp -r "$temp_dir/regexes/"* "$INSTALL_DIR/regexes/"
    fi
    
    # Restore features
    if [ -d "$temp_dir/features" ] && [ "$(ls -A "$temp_dir/features")" ]; then
        log "Restoring feature selections..."
        mkdir -p "$INSTALL_DIR/features"
        cp -r "$temp_dir/features/"* "$INSTALL_DIR/features/"
    fi
    
    # Restore metrics
    if [ -d "$temp_dir/metrics" ] && [ "$(ls -A "$temp_dir/metrics")" ]; then
        log "Restoring metrics..."
        mkdir -p "$INSTALL_DIR/metrics"
        cp -r "$temp_dir/metrics/"* "$INSTALL_DIR/metrics/"
    fi
    
    # Fix permissions
    log "Fixing permissions..."
    chown -R root:root "$INSTALL_DIR"
    chmod -R 755 "$INSTALL_DIR"
    
    # Restart service
    if systemctl list-unit-files | grep -q anomalypostfix.service; then
        log "Restarting anomaly detection service..."
        systemctl start anomalypostfix
        
        if systemctl is-active --quiet anomalypostfix; then
            log "Service restarted successfully"
        else
            log "⚠️ Warning: Service failed to restart. Check logs for details"
        fi
    fi
    
    # Cleanup
    rm -rf "$temp_dir"
    
    log "✅ Restore completed successfully"
    return 0
}

# Function to list available backups
list_backups() {
    local backup_dir="${1:-$DEFAULT_BACKUP_DIR}"
    
    if [ ! -d "$backup_dir" ]; then
        log "Backup directory does not exist: $backup_dir"
        return 1
    fi
    
    log "====== Available backups ======"
    log "Looking in: $backup_dir"
    
    # Find and list backup files
    local backups=$(find "$backup_dir" -name "anomaly_backup_*.tar.gz" -type f | sort -r)
    
    if [ -z "$backups" ]; then
        log "No backups found"
        return 0
    fi
    
    log "Found $(echo "$backups" | wc -l) backups:"
    
    echo "$backups" | while read backup; do
        local size=$(du -h "$backup" | cut -f1)
        local date=$(echo "$backup" | grep -o '[0-9]\{8\}_[0-9]\{6\}' | sed 's/\([0-9]\{4\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)_\([0-9]\{2\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)/\1-\2-\3 \4:\5:\6/')
        local file=$(basename "$backup")
        
        log "- $file (Size: $size, Date: $date)"
    done
    
    return 0
}

# Main function
main() {
    case "$1" in
        backup)
            create_backup "$2"
            ;;
        restore)
            if [ -z "$2" ]; then
                log "❌ Error: Backup file path is required"
                log "Usage: $0 restore /path/to/backup.tar.gz"
                exit 1
            fi
            restore_from_backup "$2"
            ;;
        list)
            list_backups "$2"
            ;;
        *)
            echo "Usage: $0 {backup|restore|list} [args]"
            echo ""
            echo "Commands:"
            echo "  backup [destination]  Create a backup archive (default: $DEFAULT_BACKUP_DIR)"
            echo "  restore <archive>     Restore from a backup archive"
            echo "  list [directory]      List available backups (default: $DEFAULT_BACKUP_DIR)"
            exit 1
            ;;
    esac
    
    exit $?
}

# Run main function
main "$@"

#!/bin/bash
# AnomalyPostfix V2 Setup Script for Linux
echo "Setting up AnomalyPostfix V2..."
echo

# Define installation directory
INSTALL_DIR="/opt/PostfixAnomaly"
CURRENT_DIR=$(pwd)

# Check if running as root (needed to write to /opt)
if [ "$EUID" -ne 0 ]; then
  echo "This script needs root privileges to install to $INSTALL_DIR"
  echo "Please run with sudo: sudo $0"
  exit 1
fi

# Create installation directory if it doesn't exist
echo "Creating installation directory at $INSTALL_DIR..."
mkdir -p $INSTALL_DIR

# Copy all files to installation directory
echo "Copying files to installation directory..."
cp -r "$CURRENT_DIR"/* $INSTALL_DIR/
cd $INSTALL_DIR
echo "Working directory changed to: $(pwd)"
echo

# Create necessary directories if they don't exist
echo "Creating directories..."
mkdir -p $INSTALL_DIR/output $INSTALL_DIR/logs

# Make all scripts executable
echo "Setting script permissions..."
find "$INSTALL_DIR" -name "*.sh" -exec chmod +x {} \;

# Check for required Python packages
echo "Checking for required packages..."
python3 -m pip install -r $INSTALL_DIR/requirements.txt

# Check for model files
echo "Checking model files..."
if [ ! -f "$INSTALL_DIR/models/anomaly_det.pkl" ]; then
  echo "ERROR: Model file not found at $INSTALL_DIR/models/anomaly_det.pkl"
  echo "Please ensure the model file exists"
  exit 1
fi

if [ ! -f "$INSTALL_DIR/models/scaler.pkl" ]; then
  echo "ERROR: Scaler file not found at $INSTALL_DIR/models/scaler.pkl"
  echo "Please ensure the scaler file exists"
  exit 1
fi

# Check configuration
echo "Checking configuration..."
if [ ! -f "$INSTALL_DIR/config/config.yaml" ]; then
  echo "ERROR: Configuration file not found at $INSTALL_DIR/config/config.yaml"
  echo "Please ensure the configuration file exists"
  exit 1
fi

# Update the service file to use the new paths
echo "Updating service file paths..."
sed -i "s|WorkingDirectory=.*|WorkingDirectory=$INSTALL_DIR|g" "$INSTALL_DIR/linux/anomalypostfix.service"
sed -i "s|ExecStart=.*|ExecStart=/usr/bin/python3 $INSTALL_DIR/src/kafka_anomaly_detector.py|g" "$INSTALL_DIR/linux/anomalypostfix.service"

# Create a symlink for easy access
echo "Creating executable symlink..."
ln -sf "$INSTALL_DIR/run.sh" /usr/local/bin/anomalypostfix

echo
echo "Setup complete! The application has been installed to $INSTALL_DIR"
echo
echo "You can now run the anomaly detector with:"
echo "  1. From any directory: anomalypostfix"
echo "  2. From the install directory: $INSTALL_DIR/run.sh"
echo
echo "To install as a service:"
echo "  sudo $INSTALL_DIR/linux/service_manager.sh install"
echo

#!/bin/bash
# AnomalyPostfix V2 Setup Script for Linux
echo "Setting up AnomalyPostfix V2..."
echo

# First run the make_ready.sh script to prepare the repository
echo "Running make_ready.sh to prepare repository..."
./make_ready.sh
echo

# Use current directory as the installation directory
INSTALL_DIR=$(pwd)
echo "Installation directory: $INSTALL_DIR"
echo

# Create necessary directories if they don't exist
echo "Creating directories..."
mkdir -p output logs

# Set proper permissions for output and logs directories
echo "Setting directory permissions..."
chmod -R 755 output logs

# Make all scripts executable
echo "Setting script permissions..."
find . -name "*.sh" -exec chmod +x {} \;
chmod +x src/retrain.py

# Check for required Python packages
echo "Checking for required packages..."
python3 -m pip install -r requirements.txt

# Check for model files
echo "Checking model files..."
if [ ! -f "models/anomaly_det.pkl" ]; then
  echo "ERROR: Model file not found at models/anomaly_det.pkl"
  echo "Please ensure the model file exists"
  exit 1
fi

if [ ! -f "models/scaler.pkl" ]; then
  echo "ERROR: Scaler file not found at models/scaler.pkl"
  echo "Please ensure the scaler file exists"
  exit 1
fi

# Check configuration
echo "Checking configuration..."
if [ ! -f "config/config.yaml" ]; then
  echo "ERROR: Configuration file not found at config/config.yaml"
  echo "Please ensure the configuration file exists"
  exit 1
fi

# Update the service file to use the current path
echo "Updating service file paths..."
sed -i "s|WorkingDirectory=.*|WorkingDirectory=$INSTALL_DIR|g" "linux/anomalypostfix.service"
sed -i "s|ExecStart=.*|ExecStart=/usr/bin/python3 $INSTALL_DIR/src/kafka_anomaly_detector.py|g" "linux/anomalypostfix.service"

# Create a symlink for easy access
echo "Creating executable symlink..."
if [ "$EUID" -eq 0 ]; then
  ln -sf "$INSTALL_DIR/run.sh" /usr/local/bin/anomalypostfix
  echo "Symlink created at /usr/local/bin/anomalypostfix"
else
  echo "Not running as root, skipping symlink creation to /usr/local/bin"
  echo "You can create the symlink later with: sudo ln -sf '$INSTALL_DIR/run.sh' /usr/local/bin/anomalypostfix"
fi

echo
echo "Setup complete! The application has been set up in the current directory: $INSTALL_DIR"
echo
echo "You can now run the anomaly detector with:"
echo "  1. From this directory: ./run.sh"
if [ "$EUID" -eq 0 ]; then
  echo "  2. From any directory: anomalypostfix"
fi
echo
echo "To install as a service:"
echo "  sudo ./linux/service_manager.sh install"
echo
echo "To set up automatic model retraining (weekly by default):"
echo "  sudo ./setup_cron.sh"
echo
echo "To manually retrain the model:"
echo "  sudo ./retrain_model.sh"
echo

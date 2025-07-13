#!/bin/bash
# make_ready.sh - Prepare the repository for production use
#
# This script:
# 1. Creates required directories
# 2. Sets correct file permissions
# 3. Removes unnecessary/temporary files
# 4. Validates the installation

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "================================================"
echo "PostfixAnomaly Production Readiness Script"
echo "================================================"
echo "Running from: $SCRIPT_DIR"
echo ""

# 1. Create required directories
echo "Creating required directories..."
mkdir -p "$SCRIPT_DIR/logs"
mkdir -p "$SCRIPT_DIR/output"
mkdir -p "$SCRIPT_DIR/metrics"
print_status "Directories created"

# 2. Clean up any unnecessary files
echo ""
echo "Cleaning up unnecessary files..."

# Remove any Python cache files
find "$SCRIPT_DIR" -type d -name "__pycache__" -exec rm -rf {} +  2>/dev/null || true
find "$SCRIPT_DIR" -name "*.pyc" -delete
find "$SCRIPT_DIR" -name "*.pyo" -delete
find "$SCRIPT_DIR" -name "*.pyd" -delete
print_status "Python cache files removed"

# Remove any temporary files
find "$SCRIPT_DIR" -name "*~" -delete
find "$SCRIPT_DIR" -name ".*.swp" -delete
find "$SCRIPT_DIR" -name ".*.swo" -delete
print_status "Temporary editor files removed"

# 3. Set correct permissions
echo ""
echo "Setting correct file permissions..."
chmod -R 755 "$SCRIPT_DIR"

# Make shell scripts executable
find "$SCRIPT_DIR" -name "*.sh" -exec chmod +x {} \;
chmod +x "$SCRIPT_DIR/setup.sh" 2>/dev/null || true
chmod +x "$SCRIPT_DIR/run.sh" 2>/dev/null || true
chmod +x "$SCRIPT_DIR/linux/service_manager.sh" 2>/dev/null || true
chmod +x "$SCRIPT_DIR/linux/service_status.sh" 2>/dev/null || true
chmod +x "$SCRIPT_DIR/retrain_model.sh" 2>/dev/null || true
chmod +x "$SCRIPT_DIR/backup_restore.sh" 2>/dev/null || true
chmod +x "$SCRIPT_DIR/setup_cron.sh" 2>/dev/null || true
print_status "File permissions set"

# 4. Validate Python dependencies
echo ""
echo "Validating Python dependencies..."
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    if command -v pip &> /dev/null; then
        MISSING_DEPS=0
        while IFS= read -r package; do
            if ! python -c "import $(echo $package | sed 's/[>=<].*//' | sed 's/-/_/g')" &> /dev/null; then
                if [ $MISSING_DEPS -eq 0 ]; then
                    echo "Missing dependencies:"
                fi
                MISSING_DEPS=1
                print_warning "  - $package"
            fi
        done < "$SCRIPT_DIR/requirements.txt"
        
        if [ $MISSING_DEPS -eq 1 ]; then
            echo ""
            echo "To install missing dependencies, run:"
            echo "pip install -r $SCRIPT_DIR/requirements.txt"
            echo ""
        else
            print_status "All Python dependencies are installed"
        fi
    else
        print_warning "pip not found. Cannot verify Python dependencies."
    fi
else
    print_warning "requirements.txt not found. Cannot verify Python dependencies."
fi

# 5. Check for essential files
echo ""
echo "Checking for essential files..."
MISSING_FILES=0

check_file() {
    if [ ! -f "$1" ]; then
        print_error "Missing: $1"
        MISSING_FILES=1
    fi
}

check_file "$SCRIPT_DIR/src/kafka_anomaly_detector.py"
check_file "$SCRIPT_DIR/src/retrain.py"
check_file "$SCRIPT_DIR/config/config.yaml"
check_file "$SCRIPT_DIR/models/anomaly_det.pkl"
check_file "$SCRIPT_DIR/models/scaler.pkl"

if [ $MISSING_FILES -eq 0 ]; then
    print_status "All essential files present"
fi

echo ""
if [ $MISSING_FILES -eq 0 ]; then
    echo -e "${GREEN}=============================================="
    echo -e "✓ Repository is ready for production use!"
    echo -e "===============================================${NC}"
else
    echo -e "${YELLOW}=============================================="
    echo -e "⚠ Repository has issues that need to be addressed"
    echo -e "===============================================${NC}"
fi

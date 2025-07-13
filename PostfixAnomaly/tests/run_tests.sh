#!/bin/bash
# run_tests.sh - Run all tests for the Postfix Anomaly Detection system
# 
# This script runs both unit tests and integration tests.
# Usage:
#   ./run_tests.sh [unit|integration|all]
#
# Examples:
#   ./run_tests.sh unit       # Run only unit tests
#   ./run_tests.sh integration # Run only integration tests
#   ./run_tests.sh all        # Run all tests (default)

# Set default test type
TEST_TYPE=${1:-all}
PROJECT_ROOT="$(dirname "$(readlink -f "$0")")/.."
TEST_DIR="${PROJECT_ROOT}/tests"

# Function to print colored output
print_color() {
    local color=$1
    local message=$2
    
    case $color in
        "red")
            echo -e "\e[31m${message}\e[0m"
            ;;
        "green")
            echo -e "\e[32m${message}\e[0m"
            ;;
        "yellow")
            echo -e "\e[33m${message}\e[0m"
            ;;
        "blue")
            echo -e "\e[34m${message}\e[0m"
            ;;
        *)
            echo "${message}"
            ;;
    esac
}

# Function to run unit tests
run_unit_tests() {
    print_color "blue" "=== Running Unit Tests ==="
    python -m unittest discover -s "${TEST_DIR}" -p "test_anomaly_detection.py"
    
    local status=$?
    if [ $status -eq 0 ]; then
        print_color "green" "✅ Unit tests passed successfully"
    else
        print_color "red" "❌ Unit tests failed"
    fi
    
    return $status
}

# Function to run integration tests
run_integration_tests() {
    print_color "blue" "=== Running Integration Tests ==="
    python -m unittest discover -s "${TEST_DIR}" -p "test_integration.py"
    
    local status=$?
    if [ $status -eq 0 ]; then
        print_color "green" "✅ Integration tests passed successfully"
    else
        print_color "red" "❌ Integration tests failed"
    fi
    
    return $status
}

# Main function
main() {
    cd "${PROJECT_ROOT}"
    
    print_color "blue" "Starting Postfix Anomaly Detection Test Suite"
    print_color "blue" "Test type: ${TEST_TYPE}"
    
    # Check dependencies
    print_color "yellow" "Checking dependencies..."
    
    missing_deps=()
    
    # Check Python dependencies
    for pkg in pandas numpy scikit-learn joblib matplotlib seaborn; do
        if ! python -c "import ${pkg}" &>/dev/null; then
            missing_deps+=("${pkg}")
        fi
    done
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        print_color "red" "Missing Python dependencies: ${missing_deps[*]}"
        print_color "yellow" "Installing missing dependencies..."
        
        python -m pip install --quiet ${missing_deps[*]}
        
        if [ $? -ne 0 ]; then
            print_color "red" "Failed to install dependencies. Please install them manually:"
            print_color "red" "pip install ${missing_deps[*]}"
            exit 1
        else
            print_color "green" "Dependencies installed successfully"
        fi
    else
        print_color "green" "All dependencies are installed"
    fi
    
    # Run tests based on the specified type
    unit_status=0
    integration_status=0
    
    case $TEST_TYPE in
        "unit")
            run_unit_tests
            unit_status=$?
            ;;
        "integration")
            run_integration_tests
            integration_status=$?
            ;;
        "all")
            run_unit_tests
            unit_status=$?
            
            echo ""  # Add a separator
            
            run_integration_tests
            integration_status=$?
            ;;
        *)
            print_color "red" "Invalid test type: ${TEST_TYPE}"
            print_color "red" "Valid options: unit, integration, all"
            exit 1
            ;;
    esac
    
    # Print summary
    echo ""
    print_color "blue" "=== Test Summary ==="
    
    if [ $TEST_TYPE = "unit" ] || [ $TEST_TYPE = "all" ]; then
        if [ $unit_status -eq 0 ]; then
            print_color "green" "✅ Unit tests: PASSED"
        else
            print_color "red" "❌ Unit tests: FAILED"
        fi
    fi
    
    if [ $TEST_TYPE = "integration" ] || [ $TEST_TYPE = "all" ]; then
        if [ $integration_status -eq 0 ]; then
            print_color "green" "✅ Integration tests: PASSED"
        else
            print_color "red" "❌ Integration tests: FAILED"
        fi
    fi
    
    # Set exit status
    if [ $TEST_TYPE = "unit" ]; then
        exit $unit_status
    elif [ $TEST_TYPE = "integration" ]; then
        exit $integration_status
    else
        # Exit with failure if either test suite failed
        if [ $unit_status -ne 0 ] || [ $integration_status -ne 0 ]; then
            exit 1
        else
            exit 0
        fi
    fi
}

# Run the main function
main

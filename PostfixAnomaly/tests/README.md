# Postfix Anomaly Detection Test Suite

This directory contains tests for the Postfix Anomaly Detection system. The test suite includes both unit tests and integration tests to verify the functionality of the system.

## Test Types

### Unit Tests
Unit tests verify the functionality of individual components of the system, such as:
- Log parsing and feature extraction
- Model training and evaluation
- Anomaly scoring and detection

### Integration Tests
Integration tests verify the end-to-end functionality of the system, including:
- The complete retraining pipeline
- Model persistence and loading
- Anomaly detection on test logs
- Service management (when applicable)

## Running Tests

You can run the tests using the provided `run_tests.sh` script:

```bash
# Run all tests
./run_tests.sh all

# Run only unit tests
./run_tests.sh unit

# Run only integration tests
./run_tests.sh integration
```

The script will automatically check for and install any missing dependencies before running the tests.

## Test Files

- `test_anomaly_detection.py`: Unit tests for the core functionality
- `test_integration.py`: Integration tests for the complete pipeline
- `run_tests.sh`: Test runner script

## Adding New Tests

When adding new tests:

1. Unit tests should be added to `test_anomaly_detection.py` or a new file following the naming convention `test_*.py`
2. Integration tests should be added to `test_integration.py` or a similar file
3. All test files should use the `unittest` framework
4. Follow the existing patterns for setting up test data and fixtures

## Test Data

The tests use synthetic log data generated within the test files themselves. This ensures that the tests are self-contained and do not depend on external data files.

## Test Environment

The tests are designed to run in any environment where the system's dependencies are installed. In a CI/CD pipeline, some tests may be skipped if certain dependencies are not available.

## Troubleshooting

If tests fail:

1. Check that all dependencies are installed:
   ```bash
   pip install pandas numpy scikit-learn joblib matplotlib seaborn
   ```

2. Verify that the paths in the test files match your installation:
   - The tests assume the project is installed in the standard location
   - Adjust paths in the tests if you have a custom installation

3. Check the error messages for specific failures:
   - Log parsing issues may indicate changes in the log format
   - Model training failures may indicate issues with the training data or parameters

## Coverage

To generate a test coverage report:

```bash
# Install coverage tool
pip install coverage

# Run tests with coverage
coverage run -m unittest discover -s tests

# Generate report
coverage report -m
coverage html  # For HTML report
```

The coverage report will show which parts of the code are covered by tests and which parts need more testing.

## Continuous Integration

These tests are designed to be run as part of a CI/CD pipeline. In a CI environment, some tests (such as those requiring Kafka) may be skipped or mocked.

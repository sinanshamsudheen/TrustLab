@echo off
:: AnomalyPostfix V2 Setup Script
echo Setting up AnomalyPostfix V2...
echo.

:: Create necessary directories if they don't exist
echo Creating directories...
if not exist "output" mkdir "output"
if not exist "logs" mkdir "logs"

:: Check for required Python packages
echo Checking for required packages...
pip install -r ../requirements.txt

:: Check for model files
echo Checking model files...
if not exist "models\anomaly_det.pkl" (
  echo ERROR: Model file not found at models\anomaly_det.pkl
  echo Please ensure the model file exists
  exit /b 1
)
if not exist "models\scaler.pkl" (
  echo ERROR: Scaler file not found at models\scaler.pkl
  echo Please ensure the scaler file exists
  exit /b 1
)

:: Check configuration
echo Checking configuration...
if not exist "config\config.yaml" (
  echo ERROR: Configuration file not found at config\config.yaml
  echo Please ensure the configuration file exists
  exit /b 1
)

echo.
echo Setup complete! You can now run the anomaly detector with:
echo   cd src
echo   python kafka_anomaly_detector.py
echo.

pause

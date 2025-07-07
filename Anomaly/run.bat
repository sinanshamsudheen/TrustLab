@echo off
:: AnomalyPostfix V2 Run Script
echo Starting AnomalyPostfix V2 Anomaly Detector...
echo.

cd src
python kafka_anomaly_detector.py
pause

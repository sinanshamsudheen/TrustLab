# Unified Kafka Consumer with Real-time Anomaly Detection

## Overview
**Single unified consumer** for log parsing and real-time anomaly detection using ML model.

## What's New
- ✅ **Unified approach**: One process handles all processing
- ✅ **Real-time anomaly detection**: ML model analyzes every log
- ✅ **All original functionality preserved**: Same parsing and output files
- ✅ **More efficient**: No duplicate processing of messages

## Files
- `kafka_anomaly_detector.py` - **MAIN**: Unified consumer (parsing + anomaly detection)
- `core/regex_loader.py` - Regex patterns for log field extraction
- `setup.bat` - One-time setup script
- `run.bat` - Start the unified consumer
- `requirements.txt` - Python dependencies
- `config/kafka_config.yaml` - Kafka configuration

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup (one-time):**
   ```bash
   setup.bat
   ```

3. **Update Kafka config:**
   Edit `config/kafka_config.yaml` and replace `<KAFKA-IP-ADD>` with your Kafka broker IP.

4. **Run unified consumer:**
   ```bash
   run.bat
   # OR
   python kafka_anomaly_detector.py
   ```

## What It Does

The unified consumer:
1. **Connects to Kafka** topics
2. **Parses logs** using regex patterns 
3. **Detects anomalies** using ML model in real-time
4. **Saves all data** (parsed logs + anomaly results)
5. **Shows real-time alerts** on console

## Output

### Console Output:
```
Unified Kafka Consumer with Anomaly Detection
==================================================
Model: Isolation Forest (10 features)
Kafka: your-kafka-server:9092
Topics: ['postfix', 'mail_login']
Output: output/
==================================================
Connected to Kafka

Jun 26 14:30:01 mail postfix/qmgr[290008]: ABC123: from=<user1@company.com>, size=1024, nrcpt=1 (queue active)
ANOMALY DETECTED!! [size:99999,log_hour:15,user_frequency:100] Jun 26 15:45:02 mail postfix/qmgr[290009]: XYZ789: from=<user2@company.com>, size=99999, nrcpt=1 (queue active)
Jun 26 16:30:01 mail postfix/qmgr[290010]: DEF456: from=<user3@company.com>, size=2048, nrcpt=1 (queue active)
STATS: 1000 processed, 12 anomalies (1.2%)
```

### File Outputs:
- **`output/postfix_logs.json`** - All parsed postfix logs (same as original parser)
- **`output/mail_login_logs.json`** - All parsed mail_login logs (same as original parser)
- **`output/all_detections.jsonl`** - Every log with anomaly analysis (NEW)
- **`output/anomalies.jsonl`** - Only detected anomalies with explanations (NEW)

## Configuration
- **Model**: Isolation Forest with 1% sensitivity (optimized for your data)
- **Kafka consumer group**: `unified-parser-anomaly-detection`
- **Regex patterns**: Uses existing patterns in `regexes/` directory
- **Features**: 10 optimized features (message_length, size, log_hour, etc.)

## Benefits of Unified Approach
- **More efficient**: Single consumer instead of two
- **No message duplication**: Each log processed once
- **Real-time alerts**: Immediate anomaly detection
- **Backward compatible**: All original parsing functionality preserved
- **Easy deployment**: Just run one script

## Migration
If you were using the original `kafka_parser.py`:
- **OLD**: `python core/kafka_parser.py`
- **NEW**: `python kafka_anomaly_detector.py`

All output files remain the same + you get anomaly detection for free!

2. **Configure Kafka**:
   Edit `config/kafka_config.yaml` and replace `<KAFKA-IP-ADD>` with your Kafka broker IP.

3. **Run**:
   ```cmd
   run.bat
   ```

## Output

- **Console**: Real-time anomaly alerts
- **`output/all_detections.jsonl`**: All log analyses  
- **`output/anomalies.jsonl`**: Only detected anomalies

## Anomaly Types

- 🚨 **HIGH**: Critical anomalies (score < -0.1)
- ⚠️ **MEDIUM**: Moderate anomalies (score < -0.05)
- 🔍 **LOW**: Minor anomalies (score < 0)
- ✅ **NORMAL**: No anomaly detected

## Features Monitored

The system monitors 10 key features:
- Message length and patterns
- Email size and frequency
- Time-based patterns (off-hours, weekends)
- Process types (bounce, postsuper, etc.)
- User activity patterns

## Files

- **`kafka_anomaly_detector.py`**: Main detection script
- **`setup.bat`**: One-time setup script  
- **`run.bat`**: Run script
- **Model files**: Pre-trained ML models (copied during setup)
- **`config/kafka_config.yaml`**: Kafka configuration

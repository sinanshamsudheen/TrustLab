# PostfixAnomaly Production Deployment Checklist

This checklist ensures your PostfixAnomaly system is properly configured and ready for production use.

## Pre-Installation

- [ ] Server has Python 3.8+ installed
- [ ] Server has access to Kafka brokers
- [ ] Server has access to log files (Postfix and Roundcube)
- [ ] Server has sufficient disk space (recommend 5GB+)
- [ ] Server has sufficient memory (recommend 4GB+)
- [ ] Necessary ports are open for Kafka communication

## Installation

- [ ] Repository cloned to appropriate location (recommend `/opt/PostfixAnomaly`)
- [ ] `make_ready.sh` script executed successfully
- [ ] All dependencies installed via `pip install -r requirements.txt`
- [ ] `setup.sh` executed successfully 
- [ ] All scripts have executable permissions

## Configuration

- [ ] `config/config.yaml` updated with correct:
  - [ ] Kafka broker address and port
  - [ ] Appropriate topics
  - [ ] Correct path to log files
  - [ ] Appropriate anomaly thresholds

## Service Setup

- [ ] Service installed via `sudo ./linux/service_manager.sh install`
- [ ] Service starts successfully
- [ ] Service survives reboot (test with `sudo reboot`)

## Scheduled Retraining

- [ ] Cron job set up via `sudo ./setup_cron.sh`
- [ ] Appropriate frequency chosen (daily, weekly, monthly)
- [ ] Initial model training completed successfully

## Monitoring

- [ ] Log directory properly set up
- [ ] Output directory properly set up
- [ ] Metrics directory properly set up
- [ ] System monitoring in place (CPU, memory, disk space)
- [ ] Process monitoring in place

## Backup & Recovery

- [ ] Initial backup created via `sudo ./backup_restore.sh backup`
- [ ] Backup stored in a secure location
- [ ] Backup recovery tested
- [ ] Regular backup schedule established

## Security

- [ ] All files owned by appropriate user
- [ ] Appropriate permissions set on files and directories
- [ ] Sensitive information not hardcoded in scripts
- [ ] Log rotation configured to avoid disk filling

## Documentation

- [ ] Installation process documented
- [ ] Configuration parameters documented
- [ ] Troubleshooting procedures documented
- [ ] Contact information for support documented

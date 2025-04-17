# Network Configuration Manager

A comprehensive tool for managing, backing up, comparing, deploying, and validating network device configurations.

## Overview

The Network Configuration Manager is designed to help network engineers maintain and manage configurations across multiple network devices. It provides a suite of tools for configuration backup, deployment, comparison, and compliance validation.

## Features

- Automated configuration backup from network devices
- Configuration comparison to identify changes
- Controlled deployment of configurations to devices
- Configuration validation against compliance rules
- Detailed reporting on device configurations
- Support for multiple device types (Cisco IOS, Juniper, etc.)

## Requirements

- Python 3.6+
- Required Python packages:
  - paramiko
  - netmiko
  - pyyaml

## Installation

Install the required dependencies:

```bash
pip install paramiko netmiko pyyaml
```

## Configuration

The tool uses a YAML configuration file to define devices and settings:

```yaml
backup_dir: /path/to/backup/directory
template_dir: /path/to/template/directory
devices:
  - name: switch1
    ip: 192.168.1.10
    device_type: cisco_ios
    username: admin
  - name: router1
    ip: 192.168.1.1
    device_type: cisco_ios
    username: admin
```

## Usage

The tool provides several commands for different configuration management tasks:

### Backup Configurations

```bash
python network_config_manager.py backup -c config.yaml [-d DEVICE_NAME]
```

### Compare Configurations

```bash
python network_config_manager.py compare FILE1 FILE2
```

### Deploy Configuration

```bash
python network_config_manager.py deploy -c config.yaml -d DEVICE_NAME -f CONFIG_FILE [--dry-run]
```

### Validate Configuration

```bash
python network_config_manager.py validate CONFIG_FILE RULES_FILE
```

### Generate Report

```bash
python network_config_manager.py report -c config.yaml [-d DEVICE_NAME]
```

## Compliance Rules

Configuration validation uses JSON rule files with the following format:

```json
[
  {
    "name": "Password Encryption",
    "type": "pattern",
    "pattern": "service password-encryption",
    "severity": "error"
  },
  {
    "name": "No Telnet Access",
    "type": "not_pattern",
    "pattern": "transport input telnet",
    "severity": "error"
  },
  {
    "name": "NTP Configuration",
    "type": "pattern",
    "pattern": "ntp server",
    "severity": "warning"
  }
]
```

## Best Practices for Configuration Management

1. **Regular Backups**
   - Schedule automated backups at least daily
   - Store backups in a secure, version-controlled repository
   - Maintain multiple backup versions for each device

2. **Change Control**
   - Always use the dry-run option before deploying changes
   - Compare configurations before and after changes
   - Document all configuration changes with reasons and approvals

3. **Standardization**
   - Use configuration templates for consistent deployments
   - Validate all configurations against compliance rules
   - Maintain a standard naming convention for devices and files

4. **Security**
   - Never store passwords in plain text in configuration files
   - Use SSH for device connections, avoid Telnet
   - Implement role-based access control for configuration management

## Example Workflow

1. Create a configuration file defining your network devices
2. Set up regular automated backups
3. When changes are needed:
   - Create or modify configuration files
   - Validate against compliance rules
   - Perform a dry-run deployment
   - Deploy to production after verification
4. Compare configurations to verify changes
5. Generate reports for documentation and auditing

## Troubleshooting

- **Connection Issues**: Verify IP addresses, credentials, and network connectivity
- **Timeout Errors**: Increase timeout values for larger configurations
- **Authentication Failures**: Check username/password and device authentication settings
- **Deployment Failures**: Use dry-run mode to identify potential issues before deployment

## License

This tool is provided as part of a network engineering portfolio and is intended for educational and professional demonstration purposes.

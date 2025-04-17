#!/usr/bin/env python3
"""
Network Configuration Manager

This script helps manage network device configurations by providing tools to:
- Backup configurations from network devices
- Compare configurations to detect changes
- Deploy configurations to devices
- Validate configurations against compliance rules

Author: Network Engineer
"""

import argparse
import os
import sys
import re
import difflib
import datetime
import json
import getpass
import paramiko
import netmiko
import yaml
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException, NetMikoAuthenticationException

class NetworkConfigManager:
    def __init__(self, config_file=None):
        """
        Initialize the Network Configuration Manager.
        
        Args:
            config_file (str): Path to the configuration file
        """
        self.config_file = config_file
        self.devices = []
        self.backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../configs/backups')
        self.template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../configs/templates')
        
        # Ensure directories exist
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(self.template_dir, exist_ok=True)
        
        # Load configuration if provided
        if config_file and os.path.exists(config_file):
            self.load_config()
    
    def load_config(self):
        """
        Load device configuration from YAML file.
        """
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
                
                if 'devices' in config:
                    self.devices = config['devices']
                
                if 'backup_dir' in config:
                    self.backup_dir = config['backup_dir']
                    os.makedirs(self.backup_dir, exist_ok=True)
                
                if 'template_dir' in config:
                    self.template_dir = config['template_dir']
                    os.makedirs(self.template_dir, exist_ok=True)
                
                print(f"Loaded configuration with {len(self.devices)} devices")
        except Exception as e:
            print(f"Error loading configuration: {e}")
    
    def add_device(self, name, ip, device_type, username=None, password=None):
        """
        Add a device to the configuration.
        
        Args:
            name (str): Device name
            ip (str): Device IP address
            device_type (str): Device type (cisco_ios, juniper, etc.)
            username (str): SSH username
            password (str): SSH password
        """
        device = {
            'name': name,
            'ip': ip,
            'device_type': device_type
        }
        
        if username:
            device['username'] = username
        
        if password:
            device['password'] = password
        
        self.devices.append(device)
        print(f"Added device: {name} ({ip})")
    
    def save_config(self, output_file=None):
        """
        Save the current configuration to a YAML file.
        
        Args:
            output_file (str): Path to save the configuration
        """
        if not output_file:
            output_file = self.config_file
        
        if not output_file:
            print("No output file specified")
            return False
        
        try:
            config = {
                'backup_dir': self.backup_dir,
                'template_dir': self.template_dir,
                'devices': self.devices
            }
            
            with open(output_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            print(f"Configuration saved to {output_file}")
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def connect_to_device(self, device):
        """
        Establish a connection to a network device.
        
        Args:
            device (dict): Device information
            
        Returns:
            netmiko.ConnectHandler: Connection to the device
        """
        # Get credentials if not provided
        username = device.get('username')
        password = device.get('password')
        
        if not username:
            username = input(f"Enter username for {device['name']} ({device['ip']}): ")
        
        if not password:
            password = getpass.getpass(f"Enter password for {device['name']} ({device['ip']}): ")
        
        # Prepare connection parameters
        device_params = {
            'device_type': device['device_type'],
            'ip': device['ip'],
            'username': username,
            'password': password,
            'timeout': 60
        }
        
        try:
            print(f"Connecting to {device['name']} ({device['ip']})...")
            connection = ConnectHandler(**device_params)
            print(f"Connected to {device['name']}")
            return connection
        except NetMikoTimeoutException:
            print(f"Connection timeout for {device['name']} ({device['ip']})")
        except NetMikoAuthenticationException:
            print(f"Authentication failed for {device['name']} ({device['ip']})")
        except Exception as e:
            print(f"Error connecting to {device['name']} ({device['ip']}): {e}")
        
        return None
    
    def backup_device_config(self, device):
        """
        Backup configuration from a network device.
        
        Args:
            device (dict): Device information
            
        Returns:
            str: Path to the backup file
        """
        connection = self.connect_to_device(device)
        if not connection:
            return None
        
        try:
            # Get device configuration
            if device['device_type'] == 'cisco_ios':
                config = connection.send_command('show running-config')
            elif device['device_type'] == 'juniper':
                config = connection.send_command('show configuration | display set')
            else:
                config = connection.send_command('show running-config')
            
            # Create backup filename
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(self.backup_dir, f"{device['name']}_{timestamp}.cfg")
            
            # Save configuration to file
            with open(backup_file, 'w') as f:
                f.write(config)
            
            print(f"Configuration backed up to {backup_file}")
            return backup_file
        except Exception as e:
            print(f"Error backing up configuration for {device['name']}: {e}")
        finally:
            connection.disconnect()
        
        return None
    
    def backup_all_devices(self):
        """
        Backup configurations from all devices.
        
        Returns:
            list: Paths to all backup files
        """
        backup_files = []
        
        for device in self.devices:
            backup_file = self.backup_device_config(device)
            if backup_file:
                backup_files.append(backup_file)
        
        return backup_files
    
    def get_latest_backup(self, device_name):
        """
        Get the latest backup file for a device.
        
        Args:
            device_name (str): Device name
            
        Returns:
            str: Path to the latest backup file
        """
        backup_files = []
        
        for filename in os.listdir(self.backup_dir):
            if filename.startswith(f"{device_name}_") and filename.endswith('.cfg'):
                backup_files.append(os.path.join(self.backup_dir, filename))
        
        if not backup_files:
            print(f"No backup files found for {device_name}")
            return None
        
        # Sort by modification time (newest first)
        backup_files.sort(key=os.path.getmtime, reverse=True)
        return backup_files[0]
    
    def compare_configs(self, file1, file2):
        """
        Compare two configuration files and show differences.
        
        Args:
            file1 (str): Path to the first configuration file
            file2 (str): Path to the second configuration file
            
        Returns:
            str: Unified diff of the configurations
        """
        try:
            with open(file1, 'r') as f1, open(file2, 'r') as f2:
                file1_lines = f1.readlines()
                file2_lines = f2.readlines()
            
            diff = difflib.unified_diff(
                file1_lines,
                file2_lines,
                fromfile=os.path.basename(file1),
                tofile=os.path.basename(file2),
                n=3
            )
            
            diff_text = ''.join(diff)
            return diff_text
        except Exception as e:
            print(f"Error comparing configurations: {e}")
            return None
    
    def deploy_config(self, device, config_file, dry_run=True):
        """
        Deploy configuration to a network device.
        
        Args:
            device (dict): Device information
            config_file (str): Path to the configuration file
            dry_run (bool): If True, only show what would be deployed
            
        Returns:
            bool: True if deployment was successful
        """
        try:
            with open(config_file, 'r') as f:
                config_lines = f.read().splitlines()
            
            if dry_run:
                print(f"Dry run: Would deploy {len(config_lines)} lines to {device['name']} ({device['ip']})")
                print("First 10 lines:")
                for line in config_lines[:10]:
                    print(f"  {line}")
                return True
            
            connection = self.connect_to_device(device)
            if not connection:
                return False
            
            try:
                print(f"Deploying configuration to {device['name']} ({device['ip']})...")
                
                # Enter configuration mode
                connection.config_mode()
                
                # Send configuration lines
                output = connection.send_config_set(config_lines)
                
                # Save configuration
                if device['device_type'] == 'cisco_ios':
                    connection.send_command('write memory')
                elif device['device_type'] == 'juniper':
                    connection.send_command('commit')
                
                print(f"Configuration deployed to {device['name']}")
                return True
            except Exception as e:
                print(f"Error deploying configuration: {e}")
                return False
            finally:
                connection.disconnect()
        except Exception as e:
            print(f"Error reading configuration file: {e}")
            return False
    
    def validate_config(self, config_file, rules_file):
        """
        Validate a configuration against compliance rules.
        
        Args:
            config_file (str): Path to the configuration file
            rules_file (str): Path to the rules file (JSON)
            
        Returns:
            dict: Validation results
        """
        try:
            # Load configuration
            with open(config_file, 'r') as f:
                config = f.read()
            
            # Load rules
            with open(rules_file, 'r') as f:
                rules = json.load(f)
            
            results = {
                'passed': [],
                'failed': [],
                'warnings': []
            }
            
            # Check each rule
            for rule in rules:
                rule_name = rule.get('name', 'Unnamed rule')
                rule_type = rule.get('type', 'pattern')
                rule_pattern = rule.get('pattern', '')
                rule_severity = rule.get('severity', 'error')
                
                if rule_type == 'pattern':
                    # Check if pattern exists in configuration
                    if re.search(rule_pattern, config, re.MULTILINE):
                        results['passed'].append({
                            'rule': rule_name,
                            'pattern': rule_pattern
                        })
                    else:
                        if rule_severity == 'warning':
                            results['warnings'].append({
                                'rule': rule_name,
                                'pattern': rule_pattern
                            })
                        else:
                            results['failed'].append({
                                'rule': rule_name,
                                'pattern': rule_pattern
                            })
                elif rule_type == 'not_pattern':
                    # Check if pattern does not exist in configuration
                    if not re.search(rule_pattern, config, re.MULTILINE):
                        results['passed'].append({
                            'rule': rule_name,
                            'pattern': rule_pattern
                        })
                    else:
                        if rule_severity == 'warning':
                            results['warnings'].append({
                                'rule': rule_name,
                                'pattern': rule_pattern
                            })
                        else:
                            results['failed'].append({
                                'rule': rule_name,
                                'pattern': rule_pattern
                            })
            
            return results
        except Exception as e:
            print(f"Error validating configuration: {e}")
            return None
    
    def generate_report(self, device_name=None):
        """
        Generate a report of device configurations.
        
        Args:
            device_name (str): Device name to filter (optional)
            
        Returns:
            str: Path to the report file
        """
        report_file = os.path.join(self.backup_dir, f"config_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
        try:
            with open(report_file, 'w') as f:
                f.write("Network Configuration Management Report\n")
                f.write("======================================\n\n")
                f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Filter devices if needed
                devices = self.devices
                if device_name:
                    devices = [d for d in self.devices if d['name'] == device_name]
                
                f.write(f"Devices: {len(devices)}\n")
                f.write("-" * 50 + "\n\n")
                
                for device in devices:
                    f.write(f"Device: {device['name']}\n")
                    f.write(f"IP: {device['ip']}\n")
                    f.write(f"Type: {device['device_type']}\n")
                    
                    # Get latest backup
                    latest_backup = self.get_latest_backup(device['name'])
                    if latest_backup:
                        backup_time = datetime.datetime.fromtimestamp(os.path.getmtime(latest_backup))
                        f.write(f"Latest Backup: {os.path.basename(latest_backup)}\n")
                        f.write(f"Backup Time: {backup_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        
                        # Get file size
                        file_size = os.path.getsize(latest_backup)
                        f.write(f"Config Size: {file_size} bytes\n")
                    else:
                        f.write("No backups available\n")
                    
                    f.write("\n")
            
            print(f"Report generated: {report_file}")
            return report_file
        except Exception as e:
            print(f"Error generating report: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description='Network Configuration Manager')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Backup device configurations')
    backup_parser.add_argument('-c', '--config', help='Path to the configuration file')
    backup_parser.add_argument('-d', '--device', help='Device name to backup (optional)')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare configurations')
    compare_parser.add_argument('file1', help='First configuration file')
    compare_parser.add_argument('file2', help='Second configuration file')
    
    # Deploy command
    deploy_parser = subparsers.add_parser('deploy', help='Deploy configuration to a device')
    deploy_parser.add_argument('-c', '--config', help='Path to the configuration file')
    deploy_parser.add_argument('-d', '--device', help='Device name to deploy to')
    deploy_parser.add_argument('-f', '--file', help='Configuration file to deploy')
    deploy_parser.add_argument('--dry-run', action='store_true', help='Perform a dry run (no changes)')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate configuration against rules')
    validate_parser.add_argument('config', help='Configuration file to validate')
    validate_parser.add_argument('rules', help='Rules file (JSON)')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate a report')
    report_parser.add_argument('-c', '--config', help='Path to the configuration file')
    report_parser.add_argument('-d', '--device', help='Device name to report on (optional)')
    
    args = parser.parse_args()
    
    if args.command == 'backup':
        manager = NetworkConfigManager(args.config)
        
        if args.device:
            # Find device in configuration
            device = next((d for d in manager.devices if d['name'] == args.device), None)
            if device:
                manager.backup_device_config(device)
            else:
                print(f"Device not found: {args.device}")
        else:
            manager.backup_all_devices()
    
    elif args.command == 'compare':
        manager = NetworkConfigManager()
        diff = manager.compare_configs(args.file1, args.file2)
        if diff:
            print(diff)
    
    elif args.command == 'deploy':
        manager = NetworkConfigManager(args.config)
        
        if not args.device:
            print("Device name is required")
            return
        
        if not args.file:
            print("Configuration file is required")
            return
        
        # Find device in configuration
        device = next((d for d in manager.devices if d['name'] == args.device), None)
        if device:
            manager.deploy_config(device, args.file, args.dry_run)
        else:
            print(f"Device not found: {args.device}")
    
    elif args.command == 'validate':
        manager = NetworkConfigManager()
        results = manager.validate_config(args.config, args.rules)
        
        if results:
            print(f"Validation Results:")
            print(f"Passed: {len(results['passed'])} rules")
            print(f"Failed: {len(results['failed'])} rules")
            print(f"Warnings: {len(results['warnings'])} rules")
            
            if results['failed']:
                print("\nFailed Rules:")
                for rule in results['failed']:
                    print(f"- {rule['rule']} (pattern: {rule['pattern']})")
            
            if results['warnings']:
                print("\nWarnings:")
                for rule in results['warnings']:
                    print(f"- {rule['rule']} (pattern: {rule['pattern']})")
    
    elif args.command == 'report':
        manager = NetworkConfigManager(args.config)
        manager.generate_report(args.device)
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

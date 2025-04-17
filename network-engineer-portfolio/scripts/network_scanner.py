#!/usr/bin/env python3
"""
Network Scanner Tool

This script performs network scanning to discover active hosts and open ports
on a specified network range. It's useful for network inventory and security auditing.

Author: Network Engineer
"""

import argparse
import socket
import ipaddress
import concurrent.futures
import subprocess
import platform
import time
from datetime import datetime

def ping(host):
    """
    Ping a host to check if it's reachable.
    
    Args:
        host (str): IP address to ping
        
    Returns:
        bool: True if host responds to ping, False otherwise
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', '-W', '1', str(host)]
    
    try:
        subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
        return True
    except subprocess.CalledProcessError:
        return False

def scan_port(ip, port, timeout=1):
    """
    Scan a specific port on a host.
    
    Args:
        ip (str): IP address to scan
        port (int): Port number to scan
        timeout (int): Connection timeout in seconds
        
    Returns:
        tuple: (port, service_name) if port is open, None otherwise
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    
    try:
        result = sock.connect_ex((str(ip), port))
        if result == 0:
            try:
                service = socket.getservbyport(port)
            except:
                service = "unknown"
            return (port, service)
    except:
        pass
    finally:
        sock.close()
    
    return None

def scan_host(ip, ports=None):
    """
    Scan a host for open ports.
    
    Args:
        ip (str): IP address to scan
        ports (list): List of ports to scan, defaults to common ports
        
    Returns:
        dict: Dictionary with host information and open ports
    """
    if ports is None:
        # Common network service ports
        ports = [21, 22, 23, 25, 53, 80, 88, 110, 123, 137, 138, 139, 143, 389, 
                443, 445, 464, 587, 636, 993, 995, 1433, 1521, 3306, 3389, 5060, 5061, 8080]
    
    host_info = {
        'ip': str(ip),
        'status': 'down',
        'hostname': None,
        'open_ports': []
    }
    
    # Check if host is up
    if ping(ip):
        host_info['status'] = 'up'
        
        # Try to get hostname
        try:
            host_info['hostname'] = socket.gethostbyaddr(str(ip))[0]
        except socket.herror:
            pass
        
        # Scan ports
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            future_to_port = {executor.submit(scan_port, ip, port): port for port in ports}
            for future in concurrent.futures.as_completed(future_to_port):
                result = future.result()
                if result:
                    host_info['open_ports'].append(result)
    
    return host_info

def scan_network(network, ports=None):
    """
    Scan a network range for active hosts and open ports.
    
    Args:
        network (str): Network range in CIDR notation (e.g., 192.168.1.0/24)
        ports (list): List of ports to scan
        
    Returns:
        list: List of dictionaries with host information
    """
    try:
        network = ipaddress.ip_network(network)
    except ValueError as e:
        print(f"Error: {e}")
        return []
    
    hosts = list(network.hosts())
    results = []
    
    print(f"Starting scan of {network} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Scanning {len(hosts)} hosts...")
    
    start_time = time.time()
    
    # First pass: ping sweep to find active hosts
    active_hosts = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        future_to_ip = {executor.submit(ping, ip): ip for ip in hosts}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_ip)):
            ip = future_to_ip[future]
            try:
                is_active = future.result()
                if is_active:
                    active_hosts.append(ip)
                
                # Print progress
                if (i + 1) % 25 == 0 or i + 1 == len(hosts):
                    print(f"Progress: {i + 1}/{len(hosts)} hosts scanned, {len(active_hosts)} active hosts found")
            except Exception as e:
                print(f"Error scanning {ip}: {e}")
    
    print(f"\nFound {len(active_hosts)} active hosts. Scanning ports...")
    
    # Second pass: port scan active hosts
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_ip = {executor.submit(scan_host, ip, ports): ip for ip in active_hosts}
        for future in concurrent.futures.as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                host_info = future.result()
                results.append(host_info)
                
                # Print host details
                hostname = f" ({host_info['hostname']})" if host_info['hostname'] else ""
                open_ports = ", ".join([f"{port} ({service})" for port, service in host_info['open_ports']])
                print(f"Host: {ip}{hostname} - Open ports: {open_ports if host_info['open_ports'] else 'None'}")
            except Exception as e:
                print(f"Error scanning ports on {ip}: {e}")
    
    elapsed_time = time.time() - start_time
    print(f"\nScan completed in {elapsed_time:.2f} seconds")
    
    return results

def export_results(results, filename):
    """
    Export scan results to a file.
    
    Args:
        results (list): Scan results
        filename (str): Output filename
    """
    with open(filename, 'w') as f:
        f.write("Network Scan Results\n")
        f.write(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        for host in results:
            hostname = f" ({host['hostname']})" if host['hostname'] else ""
            f.write(f"Host: {host['ip']}{hostname}\n")
            f.write(f"Status: {host['status']}\n")
            
            if host['status'] == 'up':
                if host['open_ports']:
                    f.write("Open Ports:\n")
                    for port, service in host['open_ports']:
                        f.write(f"  - {port}/tcp ({service})\n")
                else:
                    f.write("No open ports found\n")
            
            f.write("\n")
        
        f.write("=" * 80 + "\n")
        f.write(f"Total hosts scanned: {len(results)}\n")
        f.write(f"Active hosts: {sum(1 for host in results if host['status'] == 'up')}\n")

def main():
    parser = argparse.ArgumentParser(description='Network Scanner Tool')
    parser.add_argument('network', help='Network range to scan (CIDR notation, e.g., 192.168.1.0/24)')
    parser.add_argument('-p', '--ports', help='Comma-separated list of ports to scan')
    parser.add_argument('-o', '--output', help='Output file for scan results')
    
    args = parser.parse_args()
    
    ports = None
    if args.ports:
        try:
            ports = [int(p) for p in args.ports.split(',')]
        except ValueError:
            print("Error: Ports must be integers")
            return
    
    results = scan_network(args.network, ports)
    
    if args.output:
        export_results(results, args.output)
        print(f"Results exported to {args.output}")

if __name__ == '__main__':
    main()

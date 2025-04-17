# Network Scanner Tool

A Python-based network scanning utility for discovering active hosts and open ports on a network.

## Overview

The Network Scanner Tool is designed to help network engineers discover and inventory devices on a network. It performs a two-phase scan:
1. A ping sweep to identify active hosts
2. A port scan on active hosts to identify open services

This tool is particularly useful for:
- Network inventory and asset management
- Security auditing and vulnerability assessment
- Troubleshooting network connectivity issues
- Documenting network infrastructure

## Features

- Fast multi-threaded scanning for efficient network discovery
- Service identification for open ports
- Customizable port selection for targeted scanning
- Detailed reporting with hostname resolution
- Export results to text files for documentation

## Requirements

- Python 3.6+
- Standard Python libraries (no external dependencies)
- Network access with appropriate permissions

## Usage

```bash
python network_scanner.py <network_cidr> [-p PORTS] [-o OUTPUT_FILE]
```

### Arguments

- `network_cidr`: Network range to scan in CIDR notation (e.g., 192.168.1.0/24)
- `-p, --ports`: Comma-separated list of ports to scan (optional)
- `-o, --output`: Output file for scan results (optional)

### Examples

Scan a network with default ports:
```bash
python network_scanner.py 192.168.1.0/24
```

Scan specific ports and save results:
```bash
python network_scanner.py 10.0.0.0/24 -p 22,80,443,3389 -o scan_results.txt
```

## Output

The tool provides real-time output during scanning and can export detailed results to a text file. The output includes:
- Active host IP addresses
- Resolved hostnames (when available)
- Open ports with service identification
- Summary statistics

## Best Practices

- Always ensure you have proper authorization before scanning networks
- Use during maintenance windows for production environments
- Limit concurrent scans to avoid network congestion
- Consider using smaller CIDR ranges for large networks

## Troubleshooting

- If scans are slow, try reducing the port list to essential services
- Some networks may block ICMP (ping), resulting in fewer discovered hosts
- Firewalls may affect scan results by blocking probe packets

## License

This tool is provided as part of a network engineering portfolio and is intended for educational and professional demonstration purposes.

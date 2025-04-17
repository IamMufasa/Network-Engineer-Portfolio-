# Wireless Survey Analysis Tool

A Python-based tool for processing and visualizing wireless survey data to optimize Wi-Fi network deployments.

## Overview

The Wireless Survey Analysis Tool helps network engineers analyze wireless survey data to create signal strength heatmaps and generate coverage reports. This tool is essential for planning, deploying, and troubleshooting wireless networks to ensure optimal coverage and performance.

## Features

- Generate signal strength heatmaps from survey data
- Analyze coverage statistics and identify weak spots
- Visualize access point locations and channel assignments
- Generate comprehensive coverage reports with recommendations
- Support for both 2.4GHz and 5GHz frequency bands
- Sample data generation for demonstration purposes

## Requirements

- Python 3.6+
- Required Python packages:
  - matplotlib
  - numpy
  - scipy

## Installation

Install the required dependencies:

```bash
pip install matplotlib numpy scipy
```

## Usage

```bash
python wireless_survey_analyzer.py <survey_file> [-f FLOOR_PLAN] [-o OUTPUT_DIR] [-g]
```

### Arguments

- `survey_file`: Path to the survey data CSV file
- `-f, --floor-plan`: Path to the floor plan image (optional)
- `-o, --output-dir`: Directory to save output files (optional)
- `-g, --generate-sample`: Generate sample survey data instead of analyzing

### Input Data Format

The tool expects survey data in CSV format with the following columns:
- `x_pos`: X-coordinate position in meters
- `y_pos`: Y-coordinate position in meters
- `rssi_dbm`: Signal strength in dBm
- `snr_db`: Signal-to-noise ratio in dB
- `ap_mac`: MAC address of the access point
- `ap_ssid`: SSID of the access point
- `channel`: Channel number
- `band`: Frequency band (2.4GHz or 5GHz)

### Examples

Analyze survey data:
```bash
python wireless_survey_analyzer.py survey_data.csv -f floor_plan.png -o reports/
```

Generate sample data for demonstration:
```bash
python wireless_survey_analyzer.py sample_data.csv -g
```

## Output

The tool generates several outputs:

1. **Signal Strength Heatmap**: A color-coded visualization showing signal strength across the surveyed area
2. **Coverage Analysis Report**: A text report containing:
   - Coverage statistics (good, acceptable, poor)
   - Access point information
   - Channel utilization analysis
   - Recommendations for improvement

## Wireless Survey Best Practices

When conducting wireless surveys:

1. **Pre-Survey Planning**:
   - Obtain accurate floor plans
   - Identify coverage requirements for different areas
   - Note potential sources of interference

2. **During Survey**:
   - Use consistent measurement heights
   - Take readings at regular intervals
   - Survey during normal business hours to capture typical interference

3. **Post-Survey Analysis**:
   - Identify areas with insufficient coverage
   - Check for channel overlap and interference
   - Verify that coverage meets requirements for voice/video applications

## Interpreting Results

- **Signal Strength (RSSI)**:
  - Excellent: > -65 dBm
  - Good: -65 to -70 dBm
  - Fair: -70 to -75 dBm
  - Poor: < -75 dBm

- **Signal-to-Noise Ratio (SNR)**:
  - Excellent: > 25 dB
  - Good: 20-25 dB
  - Fair: 15-20 dB
  - Poor: < 15 dB

## License

This tool is provided as part of a network engineering portfolio and is intended for educational and professional demonstration purposes.

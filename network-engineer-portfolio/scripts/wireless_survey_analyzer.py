#!/usr/bin/env python3
"""
Wireless Survey Analysis Tool

This script processes wireless survey data to generate heatmaps and reports.
It demonstrates skills in wireless network planning and analysis.

Author: Network Engineer
"""

import argparse
import csv
import os
import math
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

class WirelessSurveyAnalyzer:
    def __init__(self, survey_file, floor_plan=None, output_dir=None):
        """
        Initialize the wireless survey analyzer.
        
        Args:
            survey_file (str): Path to the survey data CSV file
            floor_plan (str): Path to the floor plan image (optional)
            output_dir (str): Directory to save output files (optional)
        """
        self.survey_file = survey_file
        self.floor_plan = floor_plan
        self.output_dir = output_dir or os.path.dirname(survey_file)
        self.survey_data = []
        self.ap_locations = []
        self.floor_dimensions = (0, 0)  # width, height in meters
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    def load_survey_data(self):
        """
        Load survey data from CSV file.
        Expected format:
        x_pos,y_pos,rssi_dbm,snr_db,ap_mac,ap_ssid,channel,band
        """
        try:
            with open(self.survey_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert string values to appropriate types
                    data_point = {
                        'x_pos': float(row['x_pos']),
                        'y_pos': float(row['y_pos']),
                        'rssi_dbm': float(row['rssi_dbm']),
                        'snr_db': float(row['snr_db']),
                        'ap_mac': row['ap_mac'],
                        'ap_ssid': row['ap_ssid'],
                        'channel': int(row['channel']),
                        'band': row['band']
                    }
                    self.survey_data.append(data_point)
                    
                    # Update floor dimensions
                    self.floor_dimensions = (
                        max(self.floor_dimensions[0], data_point['x_pos']),
                        max(self.floor_dimensions[1], data_point['y_pos'])
                    )
                    
                    # Track AP locations
                    ap_entry = {
                        'mac': data_point['ap_mac'],
                        'ssid': data_point['ap_ssid'],
                        'x': data_point['x_pos'],
                        'y': data_point['y_pos'],
                        'channel': data_point['channel'],
                        'band': data_point['band']
                    }
                    if ap_entry not in self.ap_locations:
                        self.ap_locations.append(ap_entry)
            
            print(f"Loaded {len(self.survey_data)} data points from {self.survey_file}")
            print(f"Detected {len(self.ap_locations)} access points")
            print(f"Floor dimensions: {self.floor_dimensions[0]}m x {self.floor_dimensions[1]}m")
            
            return True
        except Exception as e:
            print(f"Error loading survey data: {e}")
            return False
    
    def generate_signal_heatmap(self):
        """
        Generate a heatmap of signal strength (RSSI) across the surveyed area.
        """
        if not self.survey_data:
            print("No survey data loaded")
            return False
        
        # Create a grid for the heatmap
        grid_size = 0.5  # 0.5 meter resolution
        x_grid = np.arange(0, self.floor_dimensions[0] + grid_size, grid_size)
        y_grid = np.arange(0, self.floor_dimensions[1] + grid_size, grid_size)
        
        # Initialize grid with minimum RSSI values
        rssi_grid = np.full((len(y_grid), len(x_grid)), -100)
        
        # Fill grid with survey data
        for point in self.survey_data:
            x_idx = int(point['x_pos'] / grid_size)
            y_idx = int(point['y_pos'] / grid_size)
            
            if 0 <= x_idx < len(x_grid) and 0 <= y_idx < len(y_grid):
                # If multiple readings at same location, use the strongest
                rssi_grid[y_idx, x_idx] = max(rssi_grid[y_idx, x_idx], point['rssi_dbm'])
        
        # Interpolate missing values
        from scipy.interpolate import griddata
        points = []
        values = []
        
        for y_idx in range(len(y_grid)):
            for x_idx in range(len(x_grid)):
                if rssi_grid[y_idx, x_idx] > -100:  # Only use actual readings
                    points.append([x_grid[x_idx], y_grid[y_idx]])
                    values.append(rssi_grid[y_idx, x_idx])
        
        grid_x, grid_y = np.meshgrid(x_grid, y_grid)
        interpolated = griddata(points, values, (grid_x, grid_y), method='cubic', fill_value=-100)
        
        # Create the heatmap
        plt.figure(figsize=(12, 10))
        
        # If floor plan is provided, use it as background
        if self.floor_plan and os.path.exists(self.floor_plan):
            img = plt.imread(self.floor_plan)
            plt.imshow(img, extent=[0, self.floor_dimensions[0], 0, self.floor_dimensions[1]], alpha=0.5)
        
        # Plot the heatmap
        heatmap = plt.imshow(interpolated, extent=[0, self.floor_dimensions[0], 0, self.floor_dimensions[1]], 
                            origin='lower', cmap='jet', vmin=-90, vmax=-30, alpha=0.7)
        
        # Add AP locations
        for ap in self.ap_locations:
            plt.plot(ap['x'], ap['y'], 'ko', markersize=8)
            plt.text(ap['x'] + 0.5, ap['y'] + 0.5, f"{ap['ssid']}\nCh: {ap['channel']}", fontsize=8)
        
        # Add colorbar and labels
        cbar = plt.colorbar(heatmap)
        cbar.set_label('Signal Strength (dBm)')
        
        plt.title('Wireless Signal Strength Heatmap')
        plt.xlabel('X Position (meters)')
        plt.ylabel('Y Position (meters)')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Save the heatmap
        output_file = os.path.join(self.output_dir, 'signal_strength_heatmap.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Signal strength heatmap saved to {output_file}")
        return output_file
    
    def generate_coverage_analysis(self):
        """
        Generate a coverage analysis report.
        """
        if not self.survey_data:
            print("No survey data loaded")
            return False
        
        # Calculate coverage statistics
        total_points = len(self.survey_data)
        good_signal_points = sum(1 for point in self.survey_data if point['rssi_dbm'] >= -65)
        acceptable_signal_points = sum(1 for point in self.survey_data if -75 <= point['rssi_dbm'] < -65)
        poor_signal_points = sum(1 for point in self.survey_data if point['rssi_dbm'] < -75)
        
        good_coverage_pct = (good_signal_points / total_points) * 100
        acceptable_coverage_pct = (acceptable_signal_points / total_points) * 100
        poor_coverage_pct = (poor_signal_points / total_points) * 100
        
        # Calculate channel utilization
        channels_2ghz = {}
        channels_5ghz = {}
        
        for point in self.survey_data:
            if point['band'] == '2.4GHz':
                channels_2ghz[point['channel']] = channels_2ghz.get(point['channel'], 0) + 1
            else:  # 5GHz
                channels_5ghz[point['channel']] = channels_5ghz.get(point['channel'], 0) + 1
        
        # Generate report
        report_file = os.path.join(self.output_dir, 'wireless_coverage_report.txt')
        with open(report_file, 'w') as f:
            f.write("Wireless Network Coverage Analysis Report\n")
            f.write("=======================================\n\n")
            f.write(f"Survey Date: {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write(f"Survey File: {os.path.basename(self.survey_file)}\n")
            f.write(f"Floor Dimensions: {self.floor_dimensions[0]}m x {self.floor_dimensions[1]}m\n\n")
            
            f.write("Coverage Summary\n")
            f.write("---------------\n")
            f.write(f"Total Survey Points: {total_points}\n")
            f.write(f"Good Signal Coverage (>= -65 dBm): {good_signal_points} points ({good_coverage_pct:.1f}%)\n")
            f.write(f"Acceptable Signal Coverage (-75 to -65 dBm): {acceptable_signal_points} points ({acceptable_coverage_pct:.1f}%)\n")
            f.write(f"Poor Signal Coverage (< -75 dBm): {poor_signal_points} points ({poor_coverage_pct:.1f}%)\n\n")
            
            f.write("Access Point Information\n")
            f.write("----------------------\n")
            for i, ap in enumerate(self.ap_locations, 1):
                f.write(f"AP {i}:\n")
                f.write(f"  SSID: {ap['ssid']}\n")
                f.write(f"  MAC Address: {ap['mac']}\n")
                f.write(f"  Location: ({ap['x']:.1f}m, {ap['y']:.1f}m)\n")
                f.write(f"  Channel: {ap['channel']} ({ap['band']})\n\n")
            
            f.write("Channel Utilization\n")
            f.write("------------------\n")
            f.write("2.4 GHz Channels:\n")
            for channel, count in sorted(channels_2ghz.items()):
                f.write(f"  Channel {channel}: {count} data points\n")
            
            f.write("\n5 GHz Channels:\n")
            for channel, count in sorted(channels_5ghz.items()):
                f.write(f"  Channel {channel}: {count} data points\n")
            
            f.write("\nRecommendations\n")
            f.write("--------------\n")
            
            # Generate recommendations based on coverage
            if poor_coverage_pct > 20:
                f.write("- Consider adding additional access points to improve coverage in poor signal areas\n")
            
            if len(self.ap_locations) > 0:
                f.write("- Optimize channel assignments to minimize interference:\n")
                f.write("  * 2.4 GHz: Use channels 1, 6, and 11 to avoid overlap\n")
                f.write("  * 5 GHz: Utilize DFS channels where possible to expand available spectrum\n")
            
            f.write("- Conduct a follow-up survey after implementing changes to verify improvements\n")
        
        print(f"Coverage analysis report saved to {report_file}")
        return report_file
    
    def run_analysis(self):
        """
        Run the complete wireless survey analysis.
        """
        if self.load_survey_data():
            self.generate_signal_heatmap()
            self.generate_coverage_analysis()
            return True
        return False

def generate_sample_data(output_file, floor_width=30, floor_height=20, num_aps=3, num_points=200):
    """
    Generate sample wireless survey data for demonstration purposes.
    
    Args:
        output_file (str): Path to save the generated CSV file
        floor_width (int): Width of the floor in meters
        floor_height (int): Height of the floor in meters
        num_aps (int): Number of access points to simulate
        num_points (int): Number of survey data points to generate
    """
    # Generate random AP locations
    ap_locations = []
    for i in range(num_aps):
        ap = {
            'mac': f'00:11:22:33:44:{i+10:02x}',
            'ssid': f'Sample-WiFi-{i+1}',
            'x': random.uniform(5, floor_width-5),
            'y': random.uniform(5, floor_height-5),
            'channel': random.choice([1, 6, 11]) if i % 2 == 0 else random.choice([36, 40, 44, 48]),
            'band': '2.4GHz' if i % 2 == 0 else '5GHz'
        }
        ap_locations.append(ap)
    
    # Generate survey data points
    survey_data = []
    for _ in range(num_points):
        x = random.uniform(0, floor_width)
        y = random.uniform(0, floor_height)
        
        # Find closest AP and calculate signal strength based on distance
        closest_ap = None
        min_distance = float('inf')
        
        for ap in ap_locations:
            distance = math.sqrt((x - ap['x'])**2 + (y - ap['y'])**2)
            if distance < min_distance:
                min_distance = distance
                closest_ap = ap
        
        # Simple path loss model: RSSI = -40 - 20*log10(distance)
        rssi = -40 - 20 * math.log10(max(1, min_distance))
        # Add some random variation
        rssi += random.uniform(-5, 5)
        
        # SNR calculation (simplified)
        noise_floor = -90 + random.uniform(-5, 5)
        snr = rssi - noise_floor
        
        data_point = {
            'x_pos': x,
            'y_pos': y,
            'rssi_dbm': rssi,
            'snr_db': snr,
            'ap_mac': closest_ap['mac'],
            'ap_ssid': closest_ap['ssid'],
            'channel': closest_ap['channel'],
            'band': closest_ap['band']
        }
        survey_data.append(data_point)
    
    # Write to CSV
    with open(output_file, 'w', newline='') as f:
        fieldnames = ['x_pos', 'y_pos', 'rssi_dbm', 'snr_db', 'ap_mac', 'ap_ssid', 'channel', 'band']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        for point in survey_data:
            writer.writerow(point)
    
    print(f"Generated sample survey data with {num_points} points and {num_aps} APs")
    print(f"Saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Wireless Survey Analysis Tool')
    parser.add_argument('survey_file', help='Path to the survey data CSV file')
    parser.add_argument('-f', '--floor-plan', help='Path to the floor plan image (optional)')
    parser.add_argument('-o', '--output-dir', help='Directory to save output files (optional)')
    parser.add_argument('-g', '--generate-sample', action='store_true', 
                        help='Generate sample survey data instead of analyzing')
    
    args = parser.parse_args()
    
    if args.generate_sample:
        import random
        generate_sample_data(args.survey_file)
    else:
        analyzer = WirelessSurveyAnalyzer(args.survey_file, args.floor_plan, args.output_dir)
        analyzer.run_analysis()

if __name__ == '__main__':
    main()

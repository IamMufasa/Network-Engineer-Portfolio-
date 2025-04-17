# Wireless Survey Report

## Executive Summary

This report presents the findings of a wireless site survey conducted at the University of Florida's Engineering Building on April 10, 2025. The survey was performed to assess the current wireless coverage, identify areas of improvement, and provide recommendations for optimizing the wireless network infrastructure.

The survey results indicate that while most areas have adequate coverage, there are several locations with signal strength below the recommended threshold for reliable connectivity. Channel utilization analysis shows some overlap in the 2.4GHz band that may be causing interference in high-density areas.

## Survey Methodology

The survey was conducted using Ekahau Pro wireless site survey software with the following equipment:
- Ekahau Sidekick measurement device
- Dell XPS 15 laptop running Ekahau Pro 11.2
- Custom measurement cart at standard desk height (30")

Both passive and active surveys were performed:
- **Passive Survey**: Measured existing RF environment and AP signal coverage
- **Active Survey**: Tested actual client connectivity, throughput, and roaming

Survey data was collected at 3-meter intervals throughout the building, with special attention to high-density areas such as classrooms, conference rooms, and common spaces.

## Coverage Analysis

### Signal Strength Distribution

| Signal Quality | Signal Strength (dBm) | Coverage Area |
|----------------|----------------------|--------------|
| Excellent      | > -65 dBm            | 68%          |
| Good           | -65 to -70 dBm       | 17%          |
| Fair           | -70 to -75 dBm       | 10%          |
| Poor           | < -75 dBm            | 5%           |

### Problem Areas Identified

1. **Northeast Corner Offices (Rooms 301-310)**
   - Signal strength: -76 to -82 dBm
   - Potential cause: Distance from nearest AP and signal attenuation through concrete walls

2. **Conference Room 210**
   - Signal strength: -73 to -78 dBm
   - Potential cause: Interference from adjacent department's wireless network

3. **Basement Laboratory Area**
   - Signal strength: -79 to -85 dBm
   - Potential cause: Insufficient AP coverage and signal blockage from equipment

## Channel Utilization

### 2.4GHz Band

| Channel | APs | Co-Channel Interference | Utilization |
|---------|-----|-------------------------|-------------|
| 1       | 8   | Moderate                | 65%         |
| 6       | 7   | Moderate                | 72%         |
| 11      | 9   | High                    | 83%         |

### 5GHz Band

| Channel Group | APs | Co-Channel Interference | Utilization |
|---------------|-----|-------------------------|-------------|
| 36-48         | 12  | Low                     | 45%         |
| 52-64 (DFS)   | 8   | Low                     | 28%         |
| 100-116 (DFS) | 6   | Minimal                 | 18%         |
| 132-144 (DFS) | 5   | Minimal                 | 15%         |

## Access Point Inventory

| AP Model           | Quantity | Firmware Version | Notes                      |
|--------------------|----------|------------------|----------------------------|
| Cisco 9120AX       | 18       | 17.6.1           | Main academic areas        |
| Cisco 9115AX       | 12       | 17.6.1           | Offices and meeting rooms  |
| Cisco 9105AX       | 8        | 17.6.1           | Low-density areas          |
| Cisco 3802i (EOL)  | 6        | 8.10.151.0       | Scheduled for replacement  |

## Capacity Analysis

| Area Type      | Peak Users | Current APs | Required APs | Deficit |
|----------------|------------|-------------|--------------|---------|
| Lecture Halls  | 120-150    | 2           | 3            | 1       |
| Classrooms     | 30-50      | 1           | 1            | 0       |
| Labs           | 20-30      | 1           | 1            | 0       |
| Common Areas   | 40-60      | 1           | 2            | 1       |
| Office Areas   | 15-25      | 1 per 2     | 1 per 2      | 0       |

## Recommendations

Based on the survey findings, the following recommendations are provided to improve wireless coverage and performance:

1. **Additional Access Points**
   - Install 3 new Cisco 9120AX APs in the following locations:
     - Northeast corner hallway to improve coverage for rooms 301-310
     - Conference Room 210
     - Basement Laboratory central area

2. **Channel Plan Optimization**
   - Reconfigure 2.4GHz channel assignments to reduce co-channel interference
   - Implement a more balanced distribution across channels 1, 6, and 11
   - Increase utilization of DFS channels in the 5GHz band

3. **AP Replacement**
   - Replace the 6 Cisco 3802i APs with Cisco 9120AX models
   - Prioritize replacement in high-density areas

4. **Power Level Adjustments**
   - Reduce transmit power on APs in areas with high AP density
   - Recommended power levels:
     - High-density areas: 14-17 dBm
     - Medium-density areas: 17-20 dBm
     - Low-density areas: 20 dBm

5. **Controller Configuration**
   - Enable Band Select to encourage 5GHz connections
   - Implement Cisco CleanAir for automatic interference detection and avoidance
   - Configure Optimized Roaming to improve client roaming experience

## Implementation Plan

| Phase | Task | Timeline | Priority |
|-------|------|----------|----------|
| 1     | Replace EOL Cisco 3802i APs | Week 1-2 | High |
| 2     | Install new APs in coverage gap areas | Week 2-3 | High |
| 3     | Optimize channel plan | Week 3 | Medium |
| 4     | Adjust power levels | Week 3 | Medium |
| 5     | Configure controller features | Week 4 | Medium |
| 6     | Post-implementation validation survey | Week 5 | High |

## Conclusion

The wireless network at the Engineering Building provides adequate coverage for most areas but requires targeted improvements to address identified coverage gaps and performance issues. By implementing the recommendations in this report, the wireless network will be able to provide reliable connectivity and sufficient capacity to meet the needs of faculty, staff, and students.

A follow-up survey is recommended after implementation to validate improvements and make any necessary adjustments.

## Appendices

- Appendix A: Heat Maps
- Appendix B: Spectrum Analysis
- Appendix C: AP Locations
- Appendix D: Detailed Measurement Data

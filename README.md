# Network Monitoring Tool

## Project Overview

The Network Monitoring Tool is a Python-based command-line application developed for the Computer Networks PBL activity.

The tool monitors and analyzes different aspects of a local network, including interface traffic, subnet devices, network latency, packet composition, threshold alerts, and historical traffic data.

The application integrates four core modules and two extension modules into a single menu-driven program.

---

## Implemented Modules

### C1 - Interface Traffic Monitor

Monitors the selected network interface continuously.

Features:

- Detects active network interfaces
- Allows the user to select an interface
- Displays upload throughput in Mbps
- Displays download throughput in Mbps
- Displays packets sent
- Displays packets received
- Updates approximately every second
- Supports configurable download traffic alerts
- Stores traffic measurements for historical analysis

---

### C2 - Local Subnet Host Discovery

Discovers active devices on the local IPv4 subnet.

Features:

- Obtains the IPv4 address of the selected interface
- Obtains the subnet mask automatically
- Calculates the network address
- Calculates the broadcast address
- Determines the usable host range
- Performs ARP-based host discovery
- Displays IP addresses
- Displays MAC addresses
- Attempts hostname resolution
- Displays the total number of live devices

---

### C3 - Reachability and Latency Monitor

Continuously monitors important network targets.

Targets include:

- Default gateway
- Google Public DNS (8.8.8.8)
- google.com

Features:

- Displays UP/DOWN status
- Measures RTT
- Calculates minimum RTT
- Calculates average RTT
- Calculates maximum RTT
- Calculates jitter
- Calculates packet loss percentage
- Uses a sliding measurement window
- Supports configurable latency thresholds
- Supports configurable packet-loss thresholds
- Prevents repeated duplicate alerts

---

### C4 - Traffic Composition Analyzer

Captures packets from the selected network interface and analyzes traffic composition.

Features:

- Captures packets using Scapy
- Counts packets by protocol
- Calculates bytes by protocol
- Identifies TCP traffic
- Identifies UDP traffic
- Identifies ICMP traffic
- Identifies ARP traffic
- Identifies DNS traffic
- Identifies HTTP traffic
- Identifies HTTPS traffic
- Displays top source IP addresses by bytes
- Displays top destination IP addresses by bytes

---

## Extension Modules

### E1 - Threshold Alerting

Provides configurable threshold-based alerts.

Supported alerts:

- High latency
- High packet loss
- High download throughput

Alerts are displayed in the terminal and stored with timestamps in:

`data/alerts.log`

Duplicate alerts are prevented while the same threshold condition remains active.

---

### E3 - Historical Logging and Charting

Stores traffic measurements for later analysis.

Historical data is stored in:

`data/traffic_history.csv`

Stored information includes:

- Timestamp
- Interface
- Upload Mbps
- Download Mbps
- Packets sent
- Packets received

Matplotlib is used to generate a throughput-over-time chart.

The generated chart is saved as:

`charts/throughput_history.png`

---

## Technologies Used

- Python
- psutil
- Scapy
- Rich
- Matplotlib

Python standard-library modules are also used for networking, subprocess execution, CSV handling, timestamps, and IP address calculations.

---

## Project Structure

```text
CN PBL/
│
├── main.py
├── README.md
├── requirements.txt
│
├── modules/
│   ├── __init__.py
│   ├── traffic_monitor.py
│   ├── host_discovery.py
│   ├── latency_monitor.py
│   ├── traffic_analyzer.py
│   ├── alerts.py
│   └── history.py
│
├── data/
│   ├── alerts.log
│   └── traffic_history.csv
│
├── charts/
│   └── throughput_history.png
│
└── venv/
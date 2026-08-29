import socket
from datetime import datetime
import socket
from datetime import datetime
import psutil
from modules.traffic_monitor import get_active_interfaces, monitor_traffic
from modules.host_discovery import (
    get_interface_ipv4,
    get_network_info,
    scan_network,
)
from modules.latency_monitor import live_latency_monitor
from modules.traffic_analyzer import run_traffic_analyzer
from modules.history import generate_traffic_chart

def display_system_information():
    """Display system information required for PBL screenshots."""

    # Get the computer hostname.
    hostname = socket.gethostname()

    ip_address = "Not Available"
    network_range = "Not Available"

    # Find IPv4 information from an active network interface.
    for interface_name in get_active_interfaces():
        ipv4, subnet_mask = get_interface_ipv4(interface_name)

        if ipv4 and subnet_mask:
            ip_address = ipv4

            # Calculate the IPv4 network range dynamically.
            network = get_network_info(ipv4, subnet_mask)
            network_range = str(network)
            break

    # Read the current system date and time.
    current_time = datetime.now()

    print("\n" + "=" * 50)
    print("              SYSTEM INFORMATION")
    print("=" * 50)
    print(f"Hostname      : {hostname}")
    print(f"IPv4 Address  : {ip_address}")
    print(f"Network Range : {network_range}")
    print(f"System Date   : {current_time.strftime('%d-%m-%Y')}")
    print(f"System Time   : {current_time.strftime('%H:%M:%S')}")

def select_interface():
    """Let the user select an active network interface."""

    active_interfaces = get_active_interfaces()

    if not active_interfaces:
        print("\nNo active network interfaces found.")
        return None

    print("\nActive Network Interfaces:")

    for index, interface_name in enumerate(active_interfaces, start=1):
        print(f"{index}. {interface_name}")

    try:
        choice = int(input("\nSelect interface number: "))

        if choice < 1 or choice > len(active_interfaces):
            print("Invalid interface selection.")
            return None

        return active_interfaces[choice - 1]

    except ValueError:
        print("Please enter a valid number.")
        return None


def run_host_discovery():
    """Run C2 Local Subnet Host Discovery."""

    selected_interface = select_interface()

    if not selected_interface:
        return

    ip_address, subnet_mask = get_interface_ipv4(selected_interface)

    if not ip_address or not subnet_mask:
        print("\nCould not determine IPv4 address or subnet mask.")
        return

    network = get_network_info(ip_address, subnet_mask)
    hosts = list(network.hosts())

    print("\nNetwork Information")
    print("-" * 50)

    print(f"Interface        : {selected_interface}")
    print(f"IPv4 Address     : {ip_address}")
    print(f"Subnet Mask      : {subnet_mask}")
    print(f"Network Address  : {network.network_address}")
    print(f"Broadcast Address: {network.broadcast_address}")
    print(f"Network Range    : {network}")
    print(f"First Usable IP  : {hosts[0]}")
    print(f"Last Usable IP   : {hosts[-1]}")
    print(f"Total Host IPs   : {len(hosts)}")

    print("\nScanning local network...")

    devices = scan_network(network)

    print("\nLive Devices")
    print("-" * 70)

    if not devices:
        print("No live devices found.")
    else:
        for device in devices:
            print(
                f"IP: {device['ip']} | "
                f"MAC: {device['mac']} | "
                f"Hostname: {device['hostname']}"
            )

        print(f"\nTotal Live Devices: {len(devices)}")


def main():
    """Main menu for the Network Monitoring Tool."""

    while True:
        display_system_information()
        print("\n" + "=" * 50)
        print("          NETWORK MONITORING TOOL")
        print("=" * 50)

        print("1. Interface Traffic Monitor")
        print("2. Local Subnet Host Discovery")
        print("3. Reachability and Latency Monitor")
        print("4. Traffic Composition Analyzer")
        print("5. Historical Traffic Chart")
        print("6. Exit")

        try:
            choice = int(input("\nEnter your choice: "))
        except ValueError:
            print("\nPlease enter a valid number.")
            continue

        # C1
        if choice == 1:
            selected_interface = select_interface()

            if selected_interface:
                monitor_traffic(selected_interface)

        # C2
        elif choice == 2:
            run_host_discovery()

        # C3
        elif choice == 3:
            live_latency_monitor()

        # C4
        elif choice == 4:
            selected_interface = select_interface()

            if selected_interface:
                run_traffic_analyzer(selected_interface)

        # E3
        elif choice == 5:
            generate_traffic_chart()

        # Exit
        elif choice == 6:
            print("\nExiting Network Monitoring Tool.")
            break

        else:
            print("\nInvalid choice. Please try again.")
            
if __name__ == "__main__":
    main()
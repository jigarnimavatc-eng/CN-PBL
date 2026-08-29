from scapy.all import ARP, DNS, ICMP, IP, TCP, UDP, sniff


def capture_packets(interface_name, packet_count=20):
    """Capture a fixed number of packets from the selected interface."""

    print(
        f"\nCapturing {packet_count} packets "
        f"on interface: {interface_name}"
    )

    try:
        packets = sniff(
            iface=interface_name,
            count=packet_count,
        )

        return packets

    except PermissionError:
        print("\nPermission denied while capturing packets.")
        print("Try running the terminal as Administrator.")
        return []

    except Exception as error:
        print(f"\nPacket capture failed: {error}")
        return []


def analyze_protocols(packets):
    """Count packets and bytes for each traffic category."""

    protocol_counts = {
        "TCP": 0,
        "UDP": 0,
        "ICMP": 0,
        "ARP": 0,
        "DNS": 0,
        "HTTP": 0,
        "HTTPS": 0,
        "Other": 0,
    }

    protocol_bytes = {
        "TCP": 0,
        "UDP": 0,
        "ICMP": 0,
        "ARP": 0,
        "DNS": 0,
        "HTTP": 0,
        "HTTPS": 0,
        "Other": 0,
    }

    for packet in packets:
        packet_size = len(packet)

        if packet.haslayer(DNS):
            protocol_counts["DNS"] += 1
            protocol_bytes["DNS"] += packet_size

        elif packet.haslayer(ARP):
            protocol_counts["ARP"] += 1
            protocol_bytes["ARP"] += packet_size

        elif packet.haslayer(ICMP):
            protocol_counts["ICMP"] += 1
            protocol_bytes["ICMP"] += packet_size

        elif packet.haslayer(TCP):
            source_port = packet[TCP].sport
            destination_port = packet[TCP].dport

            if source_port == 80 or destination_port == 80:
                protocol_counts["HTTP"] += 1
                protocol_bytes["HTTP"] += packet_size

            elif source_port == 443 or destination_port == 443:
                protocol_counts["HTTPS"] += 1
                protocol_bytes["HTTPS"] += packet_size

            else:
                protocol_counts["TCP"] += 1
                protocol_bytes["TCP"] += packet_size

        elif packet.haslayer(UDP):
            protocol_counts["UDP"] += 1
            protocol_bytes["UDP"] += packet_size

        else:
            protocol_counts["Other"] += 1
            protocol_bytes["Other"] += packet_size

    return protocol_counts, protocol_bytes


def analyze_top_talkers(packets):
    """Find busiest source and destination IPv4 addresses by bytes."""

    source_bytes = {}
    destination_bytes = {}

    for packet in packets:
        if packet.haslayer(IP):
            source_ip = packet[IP].src
            destination_ip = packet[IP].dst
            packet_size = len(packet)

            source_bytes[source_ip] = (
                source_bytes.get(source_ip, 0)
                + packet_size
            )

            destination_bytes[destination_ip] = (
                destination_bytes.get(destination_ip, 0)
                + packet_size
            )

    top_sources = sorted(
        source_bytes.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    top_destinations = sorted(
        destination_bytes.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return top_sources, top_destinations


def run_traffic_analyzer(interface_name, packet_count=20):
    """Run the complete C4 Traffic Composition Analyzer."""

    packets = capture_packets(
        interface_name,
        packet_count,
    )

    if not packets:
        print("\nNo packets were captured.")
        return

    print(f"\nCaptured Packets: {len(packets)}")

    protocol_counts, protocol_bytes = analyze_protocols(
        packets
    )

    print("\nProtocol Summary")
    print("-" * 45)

    for protocol in protocol_counts:
        print(
            f"{protocol}: "
            f"{protocol_counts[protocol]} packets | "
            f"{protocol_bytes[protocol]} bytes"
        )

    top_sources, top_destinations = analyze_top_talkers(
        packets
    )

    print("\nTop Source IPs")
    print("-" * 40)

    if top_sources:
        for ip, byte_count in top_sources[:5]:
            print(f"{ip} | {byte_count} bytes")
    else:
        print("No IPv4 source addresses found.")

    print("\nTop Destination IPs")
    print("-" * 40)

    if top_destinations:
        for ip, byte_count in top_destinations[:5]:
            print(f"{ip} | {byte_count} bytes")
    else:
        print("No IPv4 destination addresses found.")
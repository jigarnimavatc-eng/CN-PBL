import ipaddress
import socket

import psutil
from scapy.all import ARP, Ether, srp


def get_interface_ipv4(interface_name):
    """Return IPv4 address and subnet mask for the selected interface."""

    addresses = psutil.net_if_addrs()

    if interface_name not in addresses:
        return None, None

    for address in addresses[interface_name]:
        if address.family == socket.AF_INET:
            return address.address, address.netmask

    return None, None


def get_network_info(ip_address, subnet_mask):
    """Return network information derived from IP address and subnet mask."""

    network = ipaddress.IPv4Network(
        f"{ip_address}/{subnet_mask}",
        strict=False,
    )

    return network


def scan_network(network):
    """Scan the local subnet and return live devices."""

    arp_request = ARP(pdst=str(network))
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = broadcast / arp_request

    try:
        answered = srp(
            packet,
            timeout=3,
            verbose=False,
        )[0]

    except PermissionError:
        print("\nPermission denied while scanning the network.")
        print("Try running the terminal as Administrator.")
        return []

    except Exception as error:
        print(f"\nNetwork scan failed: {error}")
        return []

    devices = []

    for sent, received in answered:
        ip = received.psrc
        mac = received.hwsrc

        try:
            hostname = socket.gethostbyaddr(ip)[0]

        except (socket.herror, socket.gaierror):
            hostname = "Unknown"

        devices.append(
            {
                "ip": ip,
                "mac": mac,
                "hostname": hostname,
            }
        )

    return devices

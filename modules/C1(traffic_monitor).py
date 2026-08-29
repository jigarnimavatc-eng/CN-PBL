import time

import psutil

from modules.alerts import check_throughput_alert, log_alert
from modules.history import log_traffic_history


def get_active_interfaces():
    """Return a list of active network interfaces."""

    interfaces = psutil.net_if_stats()
    active_interfaces = []

    for interface_name, stats in interfaces.items():
        if (
            stats.isup
            and interface_name != "Loopback Pseudo-Interface 1"
        ):
            active_interfaces.append(interface_name)

    return active_interfaces


def get_throughput_threshold():
    """Ask the user for a download throughput alert threshold."""

    try:
        value = input(
            "\nEnter download threshold in Mbps [20]: "
        ).strip()

        if value:
            threshold = float(value)
        else:
            threshold = 20

        if threshold < 0:
            raise ValueError

        return threshold

    except ValueError:
        print(
            "\nInvalid threshold value. "
            "Using default threshold of 20 Mbps."
        )
        return 20


def monitor_traffic(interface_name):
    """Continuously monitor throughput and packet rate."""

    threshold = get_throughput_threshold()

    print("\nTraffic Alert Configuration")
    print("-" * 40)
    print(f"Download Threshold : {threshold:.2f} Mbps")

    print(f"\nMonitoring: {interface_name}")
    print("Press Ctrl + C to stop.\n")

    counters = psutil.net_io_counters(pernic=True)

    if interface_name not in counters:
        print("Selected interface is not available.")
        return

    previous = counters[interface_name]
    alert_active = False

    try:
        while True:
            time.sleep(1)

            counters = psutil.net_io_counters(pernic=True)

            if interface_name not in counters:
                print("\nInterface is no longer available.")
                break

            current = counters[interface_name]

            bytes_sent_diff = (
                current.bytes_sent - previous.bytes_sent
            )

            bytes_recv_diff = (
                current.bytes_recv - previous.bytes_recv
            )

            packets_sent_diff = (
                current.packets_sent - previous.packets_sent
            )

            packets_recv_diff = (
                current.packets_recv - previous.packets_recv
            )

            upload_mbps = (bytes_sent_diff * 8) / 1_000_000
            download_mbps = (bytes_recv_diff * 8) / 1_000_000

            print(
                f"Upload: {upload_mbps:.2f} Mbps | "
                f"Download: {download_mbps:.2f} Mbps | "
                f"Packets Sent: {packets_sent_diff} | "
                f"Packets Received: {packets_recv_diff}"
            )

            # Save measurement to CSV
            log_traffic_history(
                interface_name,
                upload_mbps,
                download_mbps,
                packets_sent_diff,
                packets_recv_diff,
            )

            alert_message = check_throughput_alert(
                download_mbps,
                threshold=threshold,
            )

            if alert_message:
                if not alert_active:
                    print(f"\n{alert_message}\n")

                    log_alert(
                        f"{interface_name} - {alert_message}"
                    )

                    alert_active = True
            else:
                alert_active = False

            previous = current

    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

    except Exception as error:
        print(f"\nTraffic monitoring error: {error}")

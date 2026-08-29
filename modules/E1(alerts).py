import os
from datetime import datetime


def check_latency_alert(avg_rtt, threshold=150):
    """Check whether average latency exceeds the threshold."""

    if avg_rtt > threshold:
        return (
            f"ALERT: High latency detected! "
            f"Average RTT = {avg_rtt:.2f} ms "
            f"(Threshold = {threshold} ms)"
        )

    return None


def check_packet_loss_alert(packet_loss, threshold=20):
    """Check whether packet loss exceeds the threshold."""

    if packet_loss > threshold:
        return (
            f"ALERT: High packet loss detected! "
            f"Loss = {packet_loss:.2f}% "
            f"(Threshold = {threshold}%)"
        )

    return None


def check_throughput_alert(download_mbps, threshold=20):
    """Check whether download throughput exceeds the threshold."""

    if download_mbps > threshold:
        return (
            f"ALERT: High download traffic detected! "
            f"Download = {download_mbps:.2f} Mbps "
            f"(Threshold = {threshold} Mbps)"
        )

    return None


def log_alert(message):
    """Write an alert with date and time to the alert log."""

    os.makedirs("data", exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(
        "data/alerts.log",
        "a",
        encoding="utf-8",
    ) as file:
        file.write(f"[{timestamp}] {message}\n")

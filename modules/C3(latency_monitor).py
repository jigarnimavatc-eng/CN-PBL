import re
import subprocess
import time
from collections import deque

from rich.console import Console
from rich.live import Live
from rich.table import Table

from modules.alerts import (
    check_latency_alert,
    check_packet_loss_alert,
    log_alert,
)


console = Console()

WINDOW_SIZE = 5


def ping_target(target):
    """Ping one target once and return status and RTT."""

    try:
        result = subprocess.run(
            ["ping", "-n", "1", target],
            capture_output=True,
            text=True,
            timeout=5,
        )

        output = result.stdout

        if result.returncode == 0:
            match = re.search(r"time[=<](\d+)ms", output)

            if match:
                return True, float(match.group(1))

            return True, None

        return False, None

    except subprocess.TimeoutExpired:
        return False, None

    except Exception:
        return False, None


def get_default_gateway():
    """Detect the default IPv4 gateway on Windows."""

    try:
        result = subprocess.run(
            ["ipconfig"],
            capture_output=True,
            text=True,
        )

        for line in result.stdout.splitlines():
            if "Default Gateway" in line and ":" in line:
                gateway = line.split(":")[-1].strip()

                if gateway:
                    return gateway

        return None

    except Exception:
        return None


def calculate_statistics(history):
    """Calculate RTT statistics from the sliding window."""

    total_samples = len(history)

    if total_samples == 0:
        return {
            "status": "DOWN",
            "min": 0,
            "avg": 0,
            "max": 0,
            "jitter": 0,
            "loss": 100,
        }

    successful_rtts = [
        rtt
        for rtt in history
        if rtt is not None
    ]

    lost_packets = total_samples - len(successful_rtts)
    packet_loss = (lost_packets / total_samples) * 100

    if not successful_rtts:
        return {
            "status": "DOWN",
            "min": 0,
            "avg": 0,
            "max": 0,
            "jitter": 0,
            "loss": packet_loss,
        }

    min_rtt = min(successful_rtts)
    avg_rtt = sum(successful_rtts) / len(successful_rtts)
    max_rtt = max(successful_rtts)

    jitter_values = []

    for i in range(1, len(successful_rtts)):
        difference = abs(
            successful_rtts[i]
            - successful_rtts[i - 1]
        )

        jitter_values.append(difference)

    if jitter_values:
        jitter = sum(jitter_values) / len(jitter_values)
    else:
        jitter = 0

    return {
        "status": "UP",
        "min": min_rtt,
        "avg": avg_rtt,
        "max": max_rtt,
        "jitter": jitter,
        "loss": packet_loss,
    }


def check_target_alerts(
    target_type,
    target,
    stats,
    alert_states,
    latency_threshold,
    packet_loss_threshold,
):
    """Raise alerts only when a threshold is newly crossed."""

    alert_messages = []

    latency_key = f"{target}_latency"
    loss_key = f"{target}_loss"

    latency_alert = check_latency_alert(
        stats["avg"],
        threshold=latency_threshold,
    )

    packet_loss_alert = check_packet_loss_alert(
        stats["loss"],
        threshold=packet_loss_threshold,
    )

    # Latency alert
    if latency_alert:
        if not alert_states.get(latency_key, False):
            message = (
                f"{target_type} ({target}) - "
                f"{latency_alert}"
            )

            alert_messages.append(message)
            log_alert(message)

            alert_states[latency_key] = True
    else:
        alert_states[latency_key] = False

    # Packet loss alert
    if packet_loss_alert:
        if not alert_states.get(loss_key, False):
            message = (
                f"{target_type} ({target}) - "
                f"{packet_loss_alert}"
            )

            alert_messages.append(message)
            log_alert(message)

            alert_states[loss_key] = True
    else:
        alert_states[loss_key] = False

    return alert_messages


def build_table(
    targets,
    histories,
    alert_states,
    latency_threshold,
    packet_loss_threshold,
):
    """Build the live latency table."""

    table = Table(
        title=(
            "Reachability and Latency Monitor "
            f"- Window: {WINDOW_SIZE}"
        )
    )

    table.add_column("Type")
    table.add_column("Target")
    table.add_column("Status")
    table.add_column("Min RTT")
    table.add_column("Avg RTT")
    table.add_column("Max RTT")
    table.add_column("Jitter")
    table.add_column("Loss")

    alerts = []

    for target_type, target in targets:
        stats = calculate_statistics(
            histories[target]
        )

        target_alerts = check_target_alerts(
            target_type,
            target,
            stats,
            alert_states,
            latency_threshold,
            packet_loss_threshold,
        )

        alerts.extend(target_alerts)

        table.add_row(
            target_type,
            target,
            stats["status"],
            f"{stats['min']:.2f} ms",
            f"{stats['avg']:.2f} ms",
            f"{stats['max']:.2f} ms",
            f"{stats['jitter']:.2f} ms",
            f"{stats['loss']:.2f}%",
        )

    return table, alerts


def get_thresholds():
    """Ask the user for alert thresholds."""

    try:
        latency_input = input(
            "\nEnter latency threshold in ms [150]: "
        ).strip()

        loss_input = input(
            "Enter packet loss threshold % [20]: "
        ).strip()

        if latency_input:
            latency_threshold = float(latency_input)
        else:
            latency_threshold = 150

        if loss_input:
            packet_loss_threshold = float(loss_input)
        else:
            packet_loss_threshold = 20

        if latency_threshold < 0:
            raise ValueError

        if packet_loss_threshold < 0 or packet_loss_threshold > 100:
            raise ValueError

        return latency_threshold, packet_loss_threshold

    except ValueError:
        console.print("\nInvalid threshold value.")

        console.print(
            "Using default thresholds: "
            "150 ms latency and 20% packet loss."
        )

        return 150, 20


def live_latency_monitor():
    """Run the live reachability and latency monitor."""

    gateway = get_default_gateway()

    targets = []

    if gateway:
        targets.append(
            ("Gateway", gateway)
        )

    targets.append(
        ("Public DNS", "8.8.8.8")
    )

    targets.append(
        ("Website", "google.com")
    )

    latency_threshold, packet_loss_threshold = get_thresholds()

    histories = {}

    for _, target in targets:
        histories[target] = deque(
            maxlen=WINDOW_SIZE
        )

    alert_states = {}

    console.print("\nAlert Configuration")
    console.print("-" * 40)

    console.print(
        f"Latency Threshold    : "
        f"{latency_threshold:.2f} ms"
    )

    console.print(
        f"Packet Loss Threshold: "
        f"{packet_loss_threshold:.2f}%"
    )

    console.print(
        "\nPress Ctrl + C to stop.\n"
    )

    try:
        with Live(
            console=console,
            refresh_per_second=1,
        ) as live:

            while True:
                for _, target in targets:
                    status, rtt = ping_target(target)

                    if status and rtt is not None:
                        histories[target].append(rtt)
                    else:
                        histories[target].append(None)

                table, alerts = build_table(
                    targets,
                    histories,
                    alert_states,
                    latency_threshold,
                    packet_loss_threshold,
                )

                live.update(table)

                if alerts:
                    for alert in alerts:
                        console.print(
                            f"\n{alert}"
                        )

                time.sleep(1)

    except KeyboardInterrupt:
        console.print(
            "\nLatency monitoring stopped."
        )

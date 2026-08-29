import csv
import os
from datetime import datetime

import matplotlib.pyplot as plt


def log_traffic_history(
    interface_name,
    upload_mbps,
    download_mbps,
    packets_sent,
    packets_received,
):
    """Save traffic measurement to CSV."""

    os.makedirs("data", exist_ok=True)

    file_path = "data/traffic_history.csv"
    file_exists = os.path.exists(file_path)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(
        file_path,
        "a",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(
                [
                    "Timestamp",
                    "Interface",
                    "Upload_Mbps",
                    "Download_Mbps",
                    "Packets_Sent",
                    "Packets_Received",
                ]
            )

        writer.writerow(
            [
                timestamp,
                interface_name,
                f"{upload_mbps:.2f}",
                f"{download_mbps:.2f}",
                packets_sent,
                packets_received,
            ]
        )


def generate_traffic_chart():
    """Create graph from saved traffic history."""

    file_path = "data/traffic_history.csv"

    if not os.path.exists(file_path):
        print("Traffic history file not found.")
        return

    timestamps = []
    upload_values = []
    download_values = []

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            timestamp = datetime.strptime(
                row["Timestamp"],
                "%Y-%m-%d %H:%M:%S",
            )

            timestamps.append(timestamp)
            upload_values.append(float(row["Upload_Mbps"]))
            download_values.append(float(row["Download_Mbps"]))

    if not timestamps:
        print("No traffic history available.")
        return

    os.makedirs("charts", exist_ok=True)

    chart_path = "charts/throughput_history.png"

    plt.figure(figsize=(10, 5))

    plt.plot(
        timestamps,
        upload_values,
        label="Upload Mbps",
    )

    plt.plot(
        timestamps,
        download_values,
        label="Download Mbps",
    )

    plt.title("Network Throughput History")
    plt.xlabel("Time")
    plt.ylabel("Throughput (Mbps)")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(chart_path)

    print(f"Chart saved to: {chart_path}")

    plt.show()


if __name__ == "__main__":
    generate_traffic_chart()

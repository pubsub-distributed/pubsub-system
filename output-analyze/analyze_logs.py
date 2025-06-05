import os
import re
from datetime import datetime
import numpy as np

log_dir = "./logs"
latency_pattern = re.compile(r"Latency:\s*([0-9.]+)s")
sender_pattern = re.compile(r"Sender:\s*\[([A-Z])\]")
time_pattern = re.compile(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]")

def percentile(arr, p):
    """Compute the pth percentile of a list."""
    if not arr:
        return 0
    return np.percentile(arr, p)

# Collect all node_X.log (not sender)
log_files = []
for filename in os.listdir(log_dir):
    # Only keep node_X.log, X in A-J, and skip sender logs
    if re.fullmatch(r"node_[A-J]\.log", filename):
        log_files.append(filename)

# Sort logs as node_A, node_B, ..., node_J
log_files.sort(key=lambda x: x[5])  # node_X.log, X is at position 5

output_lines = []

for filename in log_files:
    path = os.path.join(log_dir, filename)
    latencies = []
    senders = {}
    times = []
    with open(path, "r") as f:
        for line in f:
            # Extract latency value from log line
            m = latency_pattern.search(line)
            if m:
                lat = float(m.group(1))
                latencies.append(lat)
            # Count message senders
            m2 = sender_pattern.search(line)
            if m2:
                senders[m2.group(1)] = senders.get(m2.group(1), 0) + 1
            # Extract timestamp
            m3 = time_pattern.search(line)
            if m3:
                t = datetime.strptime(m3.group(1), "%Y-%m-%d %H:%M:%S")
                times.append(t)

    count = len(latencies)
    avg_latency = sum(latencies) / count if count else 0
    max_latency = max(latencies) if latencies else 0
    min_latency = min(latencies) if latencies else 0
    std_latency = np.std(latencies) if latencies else 0
    p95 = percentile(latencies, 95)
    p99 = percentile(latencies, 99)

    # Calculate throughput: total messages / total seconds
    throughput = 0
    if times:
        duration = (max(times) - min(times)).total_seconds()
        if duration > 0:
            throughput = count / duration

    result = (
        f"==== {filename} ====\n"
        f"Total messages: {count}\n"
        f"Senders breakdown: {senders}\n"
        f"Average latency:  {avg_latency*1000:.2f} ms\n"
        f"Min latency:      {min_latency*1000:.2f} ms\n"
        f"Max latency:      {max_latency*1000:.2f} ms\n"
        f"Std deviation:    {std_latency*1000:.2f} ms\n"
        f"P95 latency:      {p95*1000:.2f} ms\n"
        f"P99 latency:      {p99*1000:.2f} ms\n"
        f"Throughput:       {throughput:.2f} messages/sec\n"
        "\n"
    )
    print(result)
    output_lines.append(result)

# Write results to a report file
with open("analysis_report.txt", "w") as fout:
    fout.writelines(output_lines)
print("Analysis results have been written to analysis_report.txt")

import os
import re
import numpy as np

log_dir = "./logs"
latency_pattern = re.compile(r"Latency:\s*([0-9.]+)s")
sender_pattern = re.compile(r"Sender:\s*\[([A-Z])\]")

def percentile(arr, p):
    """Compute the pth percentile of a list."""
    if not arr:
        return 0
    return np.percentile(arr, p)

output_lines = []

for filename in os.listdir(log_dir):
    if not filename.endswith(".log"):
        continue
    path = os.path.join(log_dir, filename)
    latencies = []
    senders = {}
    with open(path, "r") as f:
        for line in f:
            # Extract latency values from log lines
            m = latency_pattern.search(line)
            if m:
                lat = float(m.group(1))
                latencies.append(lat)
            # Count message senders
            m2 = sender_pattern.search(line)
            if m2:
                senders[m2.group(1)] = senders.get(m2.group(1), 0) + 1

    count = len(latencies)
    avg_latency = sum(latencies) / count if count else 0
    max_latency = max(latencies) if latencies else 0
    min_latency = min(latencies) if latencies else 0
    std_latency = np.std(latencies) if latencies else 0
    p95 = percentile(latencies, 95)
    p99 = percentile(latencies, 99)

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
        "\n"
    )
    print(result)
    output_lines.append(result)

# Write results to file
with open("analysis_report.txt", "w") as fout:
    fout.writelines(output_lines)
print("Analysis results have been written to analysis_report.txt")

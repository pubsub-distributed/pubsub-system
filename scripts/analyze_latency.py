# analyze_latency.py
import os
import re

def analyze_node_latency_log(filename):
    if not os.path.exists(filename):
        print(f"Latency log {filename} not found.")
        return

    node_latencies = []
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            match = re.search(r'Latency:\s*([0-9.]+)s', line)
            if match:
                latency = float(match.group(1))
                node_latencies.append(latency)

    if node_latencies:
        avg = sum(node_latencies) / len(node_latencies)
        out_path = "../output/node_latency_metrics.log"
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "a") as f:
            f.write(
                f"\n[Node Latency Metrics from {filename}]\n"
                f"Count: {len(node_latencies)}\n"
                f"Average delivery latency: {avg:.4f}s\n"
                f"Min: {min(node_latencies):.4f}s\n"
                f"Max: {max(node_latencies):.4f}s\n"
            )
        abs_out_path = os.path.abspath(out_path)
        print(f"\n[Node Latency Metrics from {filename}]")
        print(f"  Count: {len(node_latencies)}")
        print(f"  Average delivery latency: {avg:.4f}s")
        print(f"  Min: {min(node_latencies):.4f}s")
        print(f"  Max: {max(node_latencies):.4f}s")
        print(f"  Metrics written to: {abs_out_path}")
    else:
        print(f"No latency data found in {filename}")

if __name__ == "__main__":
    analyze_node_latency_log("../output/node_latency.log")

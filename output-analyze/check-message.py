import os
import re
from collections import defaultdict

log_dir = "./logs"

# Patterns
msg_id_pattern = re.compile(r"\|\s*msg_id:\s*([a-fA-F0-9]{64})")
topic_pattern = re.compile(r"\|\s*Topic:\s*([a-zA-Z0-9_]+)\s*\|")
sender_pattern = re.compile(r"\|\s*Sender:\s*\[([A-Z])\]\s*\|")
node_log_pattern = re.compile(r"node_([A-Z])\.log")
sender_log_pattern = re.compile(r"node_([A-Z])_sender\.log")

# --- 1. Extract sent messages from sender logs ---
# sent_msgs[sender][topic] = {msg_id: line}
sent_msgs = defaultdict(lambda: defaultdict(dict))
for filename in os.listdir(log_dir):
    m = sender_log_pattern.match(filename)
    if not m:
        continue
    sender = m.group(1)
    with open(os.path.join(log_dir, filename), "r") as f:
        for line in f:
            msg_id_match = msg_id_pattern.search(line)
            topic_match = topic_pattern.search(line)
            if msg_id_match and topic_match:
                msg_id = msg_id_match.group(1)
                topic = topic_match.group(1)
                sent_msgs[sender][topic][msg_id] = line.strip()

# --- 2. Extract received messages from node logs ---
# received_msgs[node][topic] = list of (msg_id, line)
received_msgs = defaultdict(lambda: defaultdict(list))
for filename in os.listdir(log_dir):
    m = node_log_pattern.match(filename)
    if not m:
        continue
    node = m.group(1)
    with open(os.path.join(log_dir, filename), "r") as f:
        for line in f:
            msg_id_match = msg_id_pattern.search(line)
            topic_match = topic_pattern.search(line)
            sender_match = sender_pattern.search(line)
            if msg_id_match and topic_match:
                msg_id = msg_id_match.group(1)
                topic = topic_match.group(1)
                received_msgs[node][topic].append((msg_id, line.strip()))

report = []

# --- 3. For each sender/topic, compare against each node ---
for sender in sorted(sent_msgs.keys()):
    for topic in sorted(sent_msgs[sender].keys()):
        sent_ids = set(sent_msgs[sender][topic].keys())
        report.append(f"\n=== Sender [{sender}] Topic [{topic}] ({len(sent_ids)} sent messages) ===\n")
        for node in sorted(received_msgs.keys()):
            # Only compare if the node actually received this topic
            received_list = received_msgs[node][topic]
            received_ids = [msg_id for msg_id, _ in received_list]
            received_set = set(received_ids)

            correctly_received = sent_ids & received_set
            lost_ids = sent_ids - received_set
            # Duplicates: count > 1 for any msg_id
            duplicate_ids = [msg_id for msg_id in sent_ids if received_ids.count(msg_id) > 1]
            accuracy = len(correctly_received) / len(sent_ids) if sent_ids else 1.0

            report.append(f"\n  Node [{node}] statistics:")
            report.append(f"\n    Correctly received: {len(correctly_received)}")
            report.append(f"\n    Lost (not received): {len(lost_ids)}")
            report.append(f"\n    Duplicates: {len(set(duplicate_ids))}")
            report.append(f"\n    Accuracy: {accuracy*100:.2f}%")

            # List lost messages with original send log
            if lost_ids:
                report.append(f"\n    Lost msg_ids:")
                for msg_id in sorted(lost_ids):
                    send_line = sent_msgs[sender][topic].get(msg_id, 'N/A')
                    report.append(f"\n      {msg_id}  (Sent: {send_line})")
            # List duplicate messages
            if duplicate_ids:
                report.append(f"\n    Duplicate msg_ids:")
                for msg_id in sorted(set(duplicate_ids)):
                    count = received_ids.count(msg_id)
                    # Find all lines with this msg_id in the node log
                    dup_lines = [line for mid, line in received_list if mid == msg_id]
                    for dup_line in dup_lines:
                        report.append(f"\n      {msg_id} (count: {count}): {dup_line}")
            report.append("\n")

# --- 4. Check for nodes missing logs ---
all_nodes = set(received_msgs.keys())
for sender in sorted(sent_msgs.keys()):
    for topic in sent_msgs[sender].keys():
        # Which nodes didn't receive any messages of this topic
        missing_nodes = [node for node in all_nodes if not received_msgs[node][topic]]
        if missing_nodes:
            report.append(f"\n=== Sender [{sender}] Topic [{topic}] not received at all by nodes: {missing_nodes}\n")

# --- 5. Write to file ---
with open("check-message-report.txt", "w") as fout:
    fout.writelines(report)

print("Per-node, per-topic comparison complete. See check-message-report.txt for results.")

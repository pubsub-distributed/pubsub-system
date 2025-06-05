import os
import re

log_dir = "./logs"
msg_id_pattern = re.compile(r"\|\s*msg_id:\s*([a-fA-F0-9]{64})")
node_log_pattern = re.compile(r"node_([A-Z])\.log")
sender_log_pattern = re.compile(r"node_([A-Z])_sender\.log")

# 1. Find all sender logs and extract sent msg_ids per sender
senders = {}  # sender -> set(msg_ids)
sender_lines = {}  # sender -> {msg_id: line}
for filename in os.listdir(log_dir):
    m = sender_log_pattern.match(filename)
    if m:
        sender = m.group(1)
        senders[sender] = set()
        sender_lines[sender] = {}
        with open(os.path.join(log_dir, filename), "r") as f:
            for line in f:
                msg_id_match = msg_id_pattern.search(line)
                if msg_id_match:
                    msg_id = msg_id_match.group(1)
                    senders[sender].add(msg_id)
                    sender_lines[sender][msg_id] = line.strip()

# 2. Find all node logs and extract received msg_ids per node
node_received = {}  # node -> list of msg_ids (may have duplicates)
for filename in os.listdir(log_dir):
    m = node_log_pattern.match(filename)
    if m:
        node = m.group(1)
        node_received[node] = []
        with open(os.path.join(log_dir, filename), "r") as f:
            for line in f:
                msg_id_match = msg_id_pattern.search(line)
                if msg_id_match:
                    node_received[node].append(msg_id_match.group(1))

# 3. For each sender, compare with each node
report = []
for sender in sorted(senders.keys()):
    sent_ids = senders[sender]
    report.append(f"\n=== Sender [{sender}] ({len(sent_ids)} sent messages) ===\n")
    for node in sorted(node_received.keys()):
        # Which sent messages are received by this node
        received_ids = node_received[node]
        received_set = set(received_ids)
        correctly_received = sent_ids & received_set
        lost_ids = sent_ids - received_set
        # Duplicates: count per msg_id
        duplicate_ids = [msg_id for msg_id in sent_ids if received_ids.count(msg_id) > 1]

        accuracy = len(correctly_received) / len(sent_ids) if sent_ids else 1.0
        report.append(f"\n  Node [{node}] statistics:")
        report.append(f"\n    Correctly received: {len(correctly_received)}")
        report.append(f"\n    Lost (not received): {len(lost_ids)}")
        report.append(f"\n    Duplicates: {len(duplicate_ids)}")
        report.append(f"\n    Accuracy: {accuracy*100:.2f}%")

        # List lost messages
        if lost_ids:
            report.append(f"\n    Lost msg_ids:")
            for msg_id in sorted(lost_ids):
                report.append(f"\n      {msg_id}  (Sent: {sender_lines[sender].get(msg_id, 'N/A')})")
        # List duplicate messages
        if duplicate_ids:
            report.append(f"\n    Duplicate msg_ids:")
            for msg_id in sorted(set(duplicate_ids)):
                count = received_ids.count(msg_id)
                report.append(f"\n      {msg_id} (count: {count})")
        report.append("\n")

# 4. If some node did not receive any messages, still report it
all_nodes = set(node_received.keys())
for sender in sorted(senders.keys()):
    missing_nodes = all_nodes - set(node_received.keys())
    if missing_nodes:
        report.append(f"\n=== Sender [{sender}] has nodes with no logs: {missing_nodes}\n")

# 5. Write to file
with open("check-message-report.txt", "w") as fout:
    fout.writelines(report)

print("Per-node comparison complete. See check-message-report.txt for results.")

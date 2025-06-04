import json
import requests

with open("peers.json", "r") as f:
    peers = json.load(f)

# Map: topic -> [list of node_ids]
topic_to_nodes = {}

for node_id, (ip, port) in peers.items():
    try:
        url = f"http://{ip}:{port}/status"
        resp = requests.get(url, timeout=3)
        data = resp.json()
        subscriptions = data["subscriptions"]
        for topic in subscriptions:
            topic_to_nodes.setdefault(topic, []).append(node_id)
    except Exception as e:
        print(f"Failed to get status from node {node_id} ({ip}:{port}): {e}")

print("Topic -> Nodes")
for topic, nodes in topic_to_nodes.items():
    print(f"{topic}: {nodes}")
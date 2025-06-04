# show_subscribers.py
import json
import requests
import sys

if len(sys.argv) > 1:
    my_node_id = sys.argv[1]
else:
    my_node_id = None

with open("../peers.json", "r") as f:
    peers = json.load(f)

topic_to_nodes = {}

for node_id, (ip, port) in peers.items():
    if my_node_id is not None and node_id == my_node_id:
        ip = "127.0.0.1"
    try:
        url = f"http://{ip}:{port}/status"
        resp = requests.get(url, timeout=3)
        data = resp.json()
        subscriptions = data["subscriptions"]
        for topic in subscriptions:
            topic_to_nodes.setdefault(topic, []).append(node_id)
    except Exception as e:
        # print(f"Failed to get status from node {node_id} ({ip}:{port}): {e}")
        print(f"Failed to get status from node {node_id} ({ip}:{port})")

print("Topic -> Nodes")
for topic, nodes in topic_to_nodes.items():
    print(f"{topic}: {nodes}")
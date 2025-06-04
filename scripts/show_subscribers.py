import json
import requests
import socket


with open("../peers.json", "r") as f:
    peers = json.load(f)

my_ips = ["127.0.0.1", "localhost"]
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

# Map: topic -> [list of node_ids]
topic_to_nodes = {}

for node_id, (ip, port) in peers.items():
    if ip == local_ip:
        ip = "127.0.0.1"
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
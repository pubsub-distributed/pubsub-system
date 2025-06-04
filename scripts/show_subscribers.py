import requests

# List all your node API ports here
NODE_PORTS = [8000, 8001, 8002, 8003, 8004, 8005]

# Map: topic -> [list of node_ids]
topic_to_nodes = {}

for port in NODE_PORTS:
    try:
        url = f"http://localhost:{port}/status"
        resp = requests.get(url, timeout=2)
        data = resp.json()
        node_id = data["node_id"]
        subscriptions = data["subscriptions"]
        for topic in subscriptions:
            topic_to_nodes.setdefault(topic, []).append(node_id)
    except Exception as e:
        # print(f"Failed to get status from port {port}: {e}")
        print("", end="")

print("Topic -> Nodes")
for topic, nodes in topic_to_nodes.items():
    print(f"{topic}: {nodes}")
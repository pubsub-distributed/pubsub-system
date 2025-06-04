# subscribe_topic.py
import requests
import sys
import json
import os

def usage():
    print("Usage: python subscribe_topic.py <node_letter> <topic>")
    print("Example: python subscribe_topic.py A news")
    sys.exit(1)

if len(sys.argv) != 3:
    usage()

node_letter = sys.argv[1].upper()
topic = sys.argv[2]

peers_path = os.path.join(os.path.dirname(__file__), "../peers.json")
with open(peers_path, "r") as f:
    peers = json.load(f)

if node_letter not in peers:
    print(f"Error: Node {node_letter} not found in peers.json.")
    sys.exit(1)

ip, port = peers[node_letter]
node_api_url = f"http://{ip}:{port}"

try:
    url = f"{node_api_url}/subscribe"
    payload = {"topic": topic}
    resp = requests.post(url, json=payload, timeout=5)
    print(f"Subscribe status: {resp.status_code} {resp.reason}")
    if resp.text.strip():
        print("Response:", resp.text.strip())
except requests.RequestException as e:
    print(f"Failed to subscribe: {e}")
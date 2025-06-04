# send_test_messages.py
import requests
import sys
import time
import json
import os

def usage():
    print("Usage: python send_test_messages.py <sender> <topic> <message> <count>")
    print('Example: python send_test_messages.py A news "Hello world!" 1')
    sys.exit(1)

if len(sys.argv) != 5:
    usage()

sender = sys.argv[1].upper()
topic = sys.argv[2]
message_template = sys.argv[3]
try:
    count = int(sys.argv[4])
except ValueError:
    print("Error: <count> must be an integer.")
    usage()

if len(sender) != 1 or not sender.isalpha():
    print("Error: <sender> must be a single letter (e.g., 'A', 'B', ...).")
    usage()

peers_json_path = os.path.join(os.path.dirname(__file__), "../peers.json")
with open(peers_json_path, "r") as f:
    peers = json.load(f)

if sender not in peers:
    print(f"Error: sender '{sender}' not found in peers.json")
    sys.exit(1)

ip, port = peers[sender]
node_api_url = f"http://{ip}:{port}/publish"

for i in range(count):
    payload = {
        "topic": topic,
        "message": f"{message_template}",
        "sender": sender,
    }
    try:
        res = requests.post(node_api_url, json=payload, timeout=5)
        print(f"[{sender}] Sent message {i} | HTTP {res.status_code}")
    except Exception as e:
        print(f"[{sender}] Error sending message {i}: {e}")
    # time.sleep(0.01)  # Optional: Uncomment to slow down the message rate

print(f"All {count} messages sent to {node_api_url}.")
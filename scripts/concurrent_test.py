import requests
import sys
import time
import json
import os
import threading

def usage():
    print("Usage: python send_multi_sender_test_messages.py <sender1> <sender2> <topic> <message> <count>")
    print('Example: python send_multi_sender_test_messages.py A B news "Hello world!" 10')
    sys.exit(1)

if len(sys.argv) != 6:
    usage()

sender1 = sys.argv[1].upper()
sender2 = sys.argv[2].upper()
topic = sys.argv[3]
message_template = sys.argv[4]
try:
    count = int(sys.argv[5])
except ValueError:
    print("Error: <count> must be an integer.")
    usage()

if len(sender1) != 1 or not sender1.isalpha() or len(sender2) != 1 or not sender2.isalpha():
    print("Error: <sender> must be a single letter (e.g., 'A', 'B', ...).")
    usage()

peers_json_path = os.path.join(os.path.dirname(__file__), "../peers.json")
with open(peers_json_path, "r") as f:
    peers = json.load(f)

for sender in [sender1, sender2]:
    if sender not in peers:
        print(f"Error: sender '{sender}' not found in peers.json")
        sys.exit(1)

def send_messages(sender):
    ip, port = peers[sender]
    node_api_url = f"http://{ip}:{port}/publish"
    for i in range(count):
        payload = {
            "topic": topic,
            "message": f"{message_template} (from {sender} #{i})",
            "sender": sender,
        }
        try:
            res = requests.post(node_api_url, json=payload, timeout=5)
            print(f"[{sender}] Sent message {i} | HTTP {res.status_code}")
        except Exception as e:
            print(f"[{sender}] Error sending message {i}: {e}")

threads = [
    threading.Thread(target=send_messages, args=(sender1,)),
    threading.Thread(target=send_messages, args=(sender2,))
]

for t in threads:
    t.start()
for t in threads:
    t.join()

print(f"All messages sent from both {sender1} and {sender2}.")
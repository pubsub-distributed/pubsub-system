import requests
import sys
import time
import json
import os
import threading

def usage():
    print("Usage: python send_multi_sender_test_messages.py <sender1> [<sender2> ...] <topic> <message> <count>")
    print('Example: python send_multi_sender_test_messages.py A B C news "Hello world!" 10')
    sys.exit(1)

if len(sys.argv) < 5:
    usage()

# Parse senders (all before topic/message/count)
senders = []
for arg in sys.argv[1:]:
    if len(arg) == 1 and arg.isalpha():
        senders.append(arg.upper())
    else:
        break

num_senders = len(senders)
# topic/message/count are the last three args
if len(sys.argv) != 1 + num_senders + 3:
    usage()

topic = sys.argv[1 + num_senders]
message_template = sys.argv[2 + num_senders]
try:
    count = int(sys.argv[3 + num_senders])
except ValueError:
    print("Error: <count> must be an integer.")
    usage()

peers_json_path = os.path.join(os.path.dirname(__file__), "../peers.json")
with open(peers_json_path, "r") as f:
    peers = json.load(f)

for sender in senders:
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

# Create and start threads for each sender
threads = [
    threading.Thread(target=send_messages, args=(sender,))
    for sender in senders
]

for t in threads:
    t.start()
for t in threads:
    t.join()

print(f"All messages sent from: {', '.join(senders)}.")
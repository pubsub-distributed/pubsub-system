# subscribe_topic.py
import requests
import sys

def usage():
    print("Usage: python subscribe_topic.py <node_letter> <topic>")
    print("Example: python subscribe_topic.py A news")
    sys.exit(1)

if len(sys.argv) != 3:
    usage()

node_letter = sys.argv[1]
topic = sys.argv[2]

if len(node_letter) != 1 or not node_letter.isalpha():
    print("Error: <node_letter> must be a single letter (e.g., 'a', 'B').")
    usage()

node_port = ord(node_letter.lower()) - ord('a') + 8000
node_api_url = f"http://localhost:{node_port}"

try:
    url = f"{node_api_url}/subscribe"
    payload = {"topic": topic}
    resp = requests.post(url, json=payload, timeout=5)
    print(f"Subscribe status: {resp.status_code} {resp.reason}")
    if resp.text.strip():
        print("Response:", resp.text.strip())
except requests.RequestException as e:
    print(f"Failed to subscribe: {e}")

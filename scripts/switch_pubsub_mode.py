# switch_pubsub_mode.py
import sys
import requests
import json

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("gossip", "leader"):
        print("Usage: python switch_pubsub_mode.py [gossip|leader] [peers.json]")
        return

    mode = sys.argv[1]
    peers_path = sys.argv[2] if len(sys.argv) > 2 else "../peers.json"

    with open(peers_path, "r") as f:
        peers = json.load(f)

    for node_id, (ip, port) in peers.items():
        try:
            url = f"http://{ip}:{port}/switch_mode"
            resp = requests.post(url, json={"mode": mode}, timeout=2)
            print(f"[{node_id} {ip}:{port}] {resp.text.strip()}")
        except Exception as e:
            print(f"[{node_id} {ip}:{port}] Error: {e}")

if __name__ == "__main__":
    main()
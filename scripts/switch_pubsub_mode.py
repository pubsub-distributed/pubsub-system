# switch_pubsub_mode.py
import sys
import requests

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("gossip", "leader"):
        print("Usage: python switch_pubsub_mode.py [gossip|leader]")
        return

    mode = sys.argv[1]
    base_ports = [8000, 8001, 8002, 8003, 8004, 8005]
    for port in base_ports:
        try:
            url = f"http://localhost:{port}/switch_mode"
            resp = requests.post(url, json={"mode": mode}, timeout=2)
            print(f"[Port {port}] {resp.text.strip()}")
        except Exception as e:
            # print(f"[Port {port}] Error: {e}")
            print("", end="")

if __name__ == "__main__":
    main()
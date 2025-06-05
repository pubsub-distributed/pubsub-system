import os
import sys
import asyncio
import argparse
import json
import aiohttp

sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from core.broker import Broker
from core.node import Node
from core.grpc_server import serve
from core.node import start_http_server

def parse_peer_addrs(peers_str=None, peers_config=None):
    """
    Parse peer addresses from a string or a config file.
    String format: "A:3.92.123.45:8000,B:3.101.234.67:8001,C:54.205.55.12:8002"
    Config file (JSON) format:
    {
      "A": ["3.92.123.45", 8000],
      "B": ["3.101.234.67", 8001],
      "C": ["54.205.55.12", 8002]
    }
    """
    peers = {}
    if peers_config:
        with open(peers_config, 'r') as f:
            config = json.load(f)
        for peer_id, (ip, http_port) in config.items():
            grpc_port = int(http_port) + 1000
            peers[peer_id] = (ip, grpc_port)
    elif peers_str:
        for item in peers_str.split(","):
            peer_id, ip, http_port = item.split(":")
            grpc_port = int(http_port) + 1000
            peers[peer_id] = (ip, grpc_port)
    else:
        raise ValueError("You must provide either peers_str or peers_config.")
    print(f"Parsed peer addresses: {peers}")  # Debug log
    return peers

async def fetch_leader_from_peers(node, peer_addrs):
    for peer_id, (ip, grpc_port) in peer_addrs.items():
        if peer_id == node.node_id:
            continue
        http_port = int(grpc_port) - 1000  # 你的 gRPC 端口-1000=HTTP端口
        url = f"http://{ip}:{http_port}/status"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=2) as resp:
                    if resp.status == 200:
                        info = await resp.json()
                        leader = info.get("leader_id")
                        if leader:
                            return leader
        except Exception:
            continue
    return None

async def main(args):
    node_id = args.node_id
    http_port = args.port
    grpc_port = http_port + 1000

    # Parse peer addresses
    peer_addrs = parse_peer_addrs(args.peer_addrs, args.peer_addrs_config)
    all_peers = list(peer_addrs.keys())

    print(f"Starting node {node_id}")
    print(f"HTTP port: {http_port}")
    print(f"gRPC port: {grpc_port}")
    print(f"Peers: {all_peers}")
    print(f"Peer addresses: {peer_addrs}")

    broker = Broker()
    mode = args.mode
    node = Node(node_id, all_peers, broker, peer_addrs=peer_addrs,
                is_publisher=True, is_subscriber=True, mode=mode)
    
    leader_from_peers = await fetch_leader_from_peers(node, peer_addrs)
    if leader_from_peers:
        print(f"Found leader from peers: {leader_from_peers}, overriding local leader.")
        node.leader_id = leader_from_peers
    else:
        print(f"No leader found from peers, using local leader selection ({node.leader_id})")

    print(f"Starting gRPC server on port {grpc_port}")
    grpc_task = asyncio.create_task(serve(node, grpc_port))

    print(f"Starting HTTP server on port {http_port}")
    http_task = asyncio.create_task(start_http_server(node, http_port))

    await asyncio.sleep(2)

    asyncio.create_task(node.gossip.push_seen_msgs())
    asyncio.create_task(node.check_leader_loop())

    node.subscribe("chat")
    print(f"[{node_id}] Node started as daemon, use HTTP API to publish/subscribe.")

    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        print(f"Shutting down node {node_id}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--node_id", type=str, required=True, help="Node ID, e.g. A")
    parser.add_argument("--port", type=int, required=True, help="HTTP port, e.g. 8000")
    parser.add_argument("--peer_addrs", type=str, default=None,
                        help='Peer addresses, e.g. "A:3.92.123.45:8000,B:3.101.234.67:8001"')
    parser.add_argument("--peer_addrs_config", type=str, default=None,
                        help='Peer address config file in JSON format (overrides --peer_addrs if given)')
    parser.add_argument("--mode", type=str, default="gossip",
                        choices=["gossip", "leader"], help="gossip or leader")
    args = parser.parse_args()

    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        print("\nShutting down...")
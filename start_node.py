# start_node.py
import os
import sys
import asyncio
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from core.broker import Broker
from core.node import Node
from core.grpc_server import serve

from aiohttp import web
from core.node import start_http_server

async def main():
    node_id = os.getenv("NODE_ID")
    all_peers = os.getenv("ALL_PEERS").split(",")
    broker = Broker()
    mode = os.getenv("PUBSUB_MODE", "gossip")
    node = Node(node_id, all_peers, broker, is_publisher=True, is_subscriber=True, mode=mode)

    asyncio.create_task(serve(node, 5000))
    asyncio.create_task(start_http_server(node, 8000))
    await asyncio.sleep(2)
    asyncio.create_task(node.gossip.push_seen_msgs())
    asyncio.create_task(node.check_leader_loop())

    node.subscribe("chat")

    print(f"[{node_id}] Node started as daemon, use HTTP API to publish/subscribe.")
    while True:
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
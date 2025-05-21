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
    node = Node(node_id, all_peers, broker, is_publisher=True, is_subscriber=True)

    asyncio.create_task(serve(node, 5000))
    asyncio.create_task(start_http_server(node, 8000))

    # Startup handshake: broadcast and collect pubkeys
    await asyncio.sleep(1)
    await node.broadcast_public_key()
    print(f"[{node_id}] Waiting for all peer public keys ...")
    await node.wait_for_all_keys()
    print(f"[{node_id}] All peer keys received. Proceeding to daemon mode.")

    node.subscribe("chat")

    print(f"[{node_id}] Node started as daemon, use HTTP API to publish/subscribe.")
    while True:
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
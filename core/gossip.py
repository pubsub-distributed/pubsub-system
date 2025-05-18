import random
import asyncio

class GossipAgent:
    def __init__(self, node_id, peers):
        self.node_id = node_id
        self.peers = peers  # peer IDs

    async def broadcast(self, message, fanout=3):
        selected = random.sample(self.peers, min(fanout, len(self.peers)))
        for peer_id in selected:
            await self.send(peer_id, message)

    async def send(self, peer_id, message):
        # Replace this with gRPC or ZeroMQ call
        print(f"[{self.node_id}] sending to {peer_id}: {message}")
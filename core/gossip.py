import random
import asyncio
import grpc.aio
from core import gossip_pb2, gossip_pb2_grpc


class GossipAgent:
    def __init__(self, node_id, peers, node=None):
        self.node_id = node_id
        self.peers = peers
        self.node = node  # pass node for callback

    async def send_public_key(self, peer_id, public_key_bytes):
        peer_service = f"node_{peer_id.lower()}"
        async with grpc.aio.insecure_channel(f"{peer_service}:5000") as channel:
            stub = gossip_pb2_grpc.GossipServiceStub(channel)
            msg = gossip_pb2.PublicKeyMessage(sender=self.node_id, public_key=public_key_bytes)
            try:
                await stub.RegisterPublicKey(msg)
                print(f"[{self.node_id}] Sent public key to {peer_id}")
            except Exception as e:
                print(f"[{self.node_id}] Failed to send public key to {peer_id}: {e}")

    async def broadcast(self, message, fanout=3):
        selected = random.sample(self.peers, min(fanout, len(self.peers)))
        for peer_id in selected:
            await self.send(peer_id, message)

    async def send(self, peer_id, message):
        peer_service = f"node_{peer_id.lower()}"
        # print(f"[{self.node_id}] Preparing to send to {peer_id} at {peer_service}:5000")
        async with grpc.aio.insecure_channel(f"{peer_service}:5000") as channel:
            stub = gossip_pb2_grpc.GossipServiceStub(channel)
            grpc_message = gossip_pb2.GossipMessage(
                topic=message['topic'],
                content=message['content'],
                sender=self.node_id
            )
            try:
                response = await stub.SendMessage(grpc_message)
                # if response.success:
                #     print(f"[{self.node_id}] sent message to {peer_id}")
            except Exception as e:
                print(f"[{self.node_id}] failed to send to {peer_id}: {e}")
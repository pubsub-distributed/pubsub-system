# gossip.py
import random
import asyncio
import grpc.aio
from core import gossip_pb2, gossip_pb2_grpc


class GossipAgent:
    def __init__(self, node_id, peers, node=None):
        self.node_id = node_id
        self.peers = peers
        self.node = node  # pass node for callback
        self.seen_msgs = set()
        self.msg_store = {}
        self.peer_unavailable = {peer: False for peer in peers}

    async def broadcast(self, message, fanout=3):
        msg_id = message['msg_id']
        if msg_id in self.seen_msgs:
            return
        self.seen_msgs.add(msg_id)
        self.msg_store[msg_id] = message
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
                sender=message['sender'],
                timestamp=message['timestamp'],
                msg_id=message['msg_id']
            )
            try:
                await stub.SendMessage(grpc_message)
                # response = await stub.SendMessage(grpc_message)
                # if response.success:
                #     print(f"[{self.node_id}] sent message to {peer_id}")
                if self.peer_unavailable[peer_id]:
                    print(f"[{self.node_id}] Peer {peer_id} back online.")
                self.peer_unavailable[peer_id] = False
            except grpc.aio.AioRpcError as e:
                if e.code() == grpc.StatusCode.UNAVAILABLE:
                    if not self.peer_unavailable[peer_id]:
                        print(f"[{self.node_id}] Peer {peer_id} unavailable (probably stopped).")
                        self.peer_unavailable[peer_id] = True
                else:
                    print(f"[{self.node_id}] gRPC error with {peer_id}: {e}")
    
    async def push_seen_msgs(self, interval=5):
        while True:
            tasks = [self.send_seen_msgs(peer_id) for peer_id in self.peers]
            await asyncio.gather(*tasks)
            await asyncio.sleep(interval)

    async def send_seen_msgs(self, peer_id):
        peer_service = f"node_{peer_id.lower()}"
        async with grpc.aio.insecure_channel(f"{peer_service}:5000") as channel:
            stub = gossip_pb2_grpc.GossipServiceStub(channel)
            grpc_message = gossip_pb2.SeenMsgs(
                sender=self.node_id,
                msg_ids=list(self.seen_msgs)
            )
            try:
                await stub.SyncSeenMsgs(grpc_message)
                if self.peer_unavailable[peer_id]:
                    print(f"[{self.node_id}] Peer {peer_id} back online.")
                self.peer_unavailable[peer_id] = False
            except grpc.aio.AioRpcError as e:
                if e.code() == grpc.StatusCode.UNAVAILABLE:
                    if not self.peer_unavailable[peer_id]:
                        print(f"[{self.node_id}] Peer {peer_id} unavailable (probably stopped).")
                        self.peer_unavailable[peer_id] = True
                else:
                    print(f"[{self.node_id}] gRPC error with {peer_id}: {e}")

    async def on_receive_seen_msgs(self, peer_id, their_msg_ids):
        their_set = set(their_msg_ids)
        missing = self.seen_msgs - their_set
        for msg_id in missing:
            await self.send(peer_id, self.msg_store[msg_id])
    
    async def ping(self, peer_id):
        peer_service = f"node_{peer_id.lower()}"
        async with grpc.aio.insecure_channel(f"{peer_service}:5000") as channel:
            stub = gossip_pb2_grpc.GossipServiceStub(channel)
            await stub.Ping(gossip_pb2.PingRequest())
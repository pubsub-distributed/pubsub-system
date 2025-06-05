# gossip.py
import random
import asyncio
import grpc.aio
from core import gossip_pb2, gossip_pb2_grpc


class GossipAgent:
    def __init__(self, node_id, peers, node=None, peer_addrs=None):
        self.node_id = node_id
        self.peers = peers
        self.node = node  # pass node for callback
        self.seen_msgs = self.load_seen_msgs_from_disk(f"{node_id}_seen_msgs.log")
        self.msg_store = {}
        self.peer_unavailable = {peer: False for peer in peers}
        self.peer_addrs = peer_addrs or {}
        print(f"[{self.node_id}] GossipAgent peers={self.peers}")
    
    def get_peer_addr(self, peer_id):
        if self.peer_addrs and peer_id in self.peer_addrs:
            ip, port = self.peer_addrs[peer_id]
            return f"{ip}:{port}"
        raise ValueError(f"No address for peer {peer_id} in peer_addrs!")
    
    def load_seen_msgs_from_disk(self, path="seen_msgs.log"):
        try:
            with open(path, "r") as f:
                return set(line.strip() for line in f)
        except Exception:
            return set()

    def save_seen_msg(self, msg_id, path="seen_msgs.log"):
        try:
            with open(path, "a") as f:
                f.write(msg_id + "\n")
        except Exception:
            pass

    async def broadcast(self, message, fanout=3):
        msg_id = message['msg_id']
        if msg_id in self.seen_msgs:
            # print(f"[{self.node_id}] broadcast(): msg_id {msg_id} already seen.")
            return
        # self.seen_msgs.add(msg_id)
        # self.save_seen_msg(msg_id, f"{self.node_id}_seen_msgs.log")
        # self.msg_store[msg_id] = message
        selected = random.sample(self.peers, min(fanout, len(self.peers)))
        for peer_id in selected:
            await self.send(peer_id, message)

    async def send(self, peer_id, message):
        peer_addr = self.get_peer_addr(peer_id)
        # print(f"[{self.node_id}] send() called, peer={peer_id}, msg_id={message.get('msg_id')}, content={message.get('content')[:50]}")
        # print(f"[{self.node_id}] Preparing to send to {peer_id} at {peer_addr}")
        async with grpc.aio.insecure_channel(peer_addr) as channel:
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
                response = await stub.SendMessage(grpc_message)
                if response.success:
                    print(f"[{self.node_id}] sent message to {peer_id}")
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
        peer_addr = self.get_peer_addr(peer_id)
        async with grpc.aio.insecure_channel(peer_addr) as channel:
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
            if msg_id in self.msg_store:
                await self.send(peer_id, self.msg_store[msg_id])
            else:
                print(f"[{self.node_id}] Warning: asked to resend msg_id={msg_id} but not found in msg_store")
    
    async def ping(self, peer_id):
        peer_addr = self.get_peer_addr(peer_id)
        async with grpc.aio.insecure_channel(peer_addr) as channel:
            stub = gossip_pb2_grpc.GossipServiceStub(channel)
            await stub.Ping(gossip_pb2.PingRequest())
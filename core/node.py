# node.py
import asyncio
import json
import time
import hashlib
from aiohttp import web
from core.broker import Broker
from core.gossip import GossipAgent
from core.publisher import Publisher
from core.subscriber import Subscriber
from security.crypto_utils import encrypt_message, decrypt_message

class Node:
    def __init__(self, node_id, all_peers, broker: Broker, is_publisher=False, is_subscriber=False):
        self.node_id = node_id
        self.broker = broker
        self.is_publisher = is_publisher
        self.is_subscriber = is_subscriber
        self.peers = [peer for peer in all_peers if peer != self.node_id]
        self.gossip = GossipAgent(node_id, self.peers, self)
        self.publisher = Publisher(node_id, broker, self.gossip) if is_publisher else None
        self.subscriber = Subscriber(node_id) if is_subscriber else None
        # self.private_key, self.public_key = generate_keys()
        # self.peer_public_keys = {self.node_id: self.public_key}  # always have own pubkey

    # async def broadcast_public_key(self):
    #     for peer in self.peers:
    #         await self.gossip.send_public_key(peer, self.public_key)

    # async def register_peer_key(self, peer_id, peer_pubkey_bytes):
    #     self.peer_public_keys[peer_id] = peer_pubkey_bytes

    # async def wait_for_all_keys(self):
    #     while len(self.peer_public_keys) < len(self.peers) + 1:
    #         await asyncio.sleep(0.1)
    #     print(f"[{self.node_id}] All peer public keys received!")

    async def publish(self, topic, message):
        if not self.is_publisher:
            raise Exception(f"[{self.node_id}] is not a publisher.")
        timestamp = time.time()
        raw_id = f"{self.node_id}-{timestamp}-{message}"
        msg_id = hashlib.sha256(raw_id.encode()).hexdigest()
        msg_payload = {
            "sender": self.node_id,
            "message": message,
            "timestamp": timestamp,
        }
        # for peer in self.peers:
        #     target_pubkey = self.peer_public_keys[peer]
        #     encrypted_payload = hybrid_encrypt(target_pubkey, json.dumps(msg_payload))
        #     encrypted_msg = json.dumps(encrypted_payload)
        #     if peer == self.peers[0]:
        #         print(f"[{self.node_id}] Publishing | Topic: {topic}")
        #     await self.publisher.publish(peer, topic, encrypted_msg)
        encrypted_payload = encrypt_message(json.dumps(msg_payload))
        encrypted_msg = json.dumps(encrypted_payload)
        msg = {
            "topic": topic,
            "content": encrypted_msg,
            "sender": self.node_id,
            "timestamp": timestamp,
            "msg_id": msg_id
        }
        print(f"[{self.node_id}] Publishing | Topic: {topic}")
        await self.gossip.broadcast(msg)

    def subscribe(self, topic):
        if not self.is_subscriber:
            raise Exception(f"[{self.node_id}] is not a subscriber.")
        self.subscriber.subscribe(topic, self.broker)
    
    def get_subscribe(self):
        return list(self.subscriber.topics)

    def unsubscribe(self, topic):
        if self.is_subscriber:
            self.subscriber.unsubscribe(topic, self.broker)

    def receive(self, msg):
        if not self.is_subscriber:
            return
        try:
            encrypted_payload = json.loads(msg['content'])
            decrypted_payload = decrypt_message(encrypted_payload)
            msg_payload = json.loads(decrypted_payload)
            msg_payload["msg_id"] = msg.get("msg_id")
            msg_payload["sender"] = msg.get("sender")
            msg_payload["timestamp"] = msg.get("timestamp")
            self.subscriber.receive({"topic": msg["topic"], "content": msg_payload})
            # print(f"[{self.node_id}] Received | Topic: {msg['topic']} | Message: {msg_payload['message']}")
            # filtered = {"topic": msg["topic"], "content": msg_payload}
            # self.subscriber.receive(filtered)
            asyncio.create_task(self.gossip.broadcast(msg))
        except Exception as e:
            print(f"[{self.node_id}] Failed to decrypt message: {e}")

    # def get_public_key(self):
    #     return self.public_key

# ---- HTTP ----

def create_app(node: Node):
    routes = web.RouteTableDef()

    @routes.post('/publish')
    async def publish_api(request):
        data = await request.json()
        topic = data['topic']
        message = data['message']
        await node.publish(topic, message)
        return web.Response(text="Message published!")

    @routes.post('/subscribe')
    async def subscribe_api(request):
        data = await request.json()
        topic = data['topic']
        node.subscribe(topic)
        return web.Response(text=f"Subscribed to {topic}")

    @routes.post('/unsubscribe')
    async def unsubscribe_api(request):
        data = await request.json()
        topic = data['topic']
        node.unsubscribe(topic)
        return web.Response(text=f"Unsubscribed from {topic}")

    @routes.get('/status')
    async def status_api(request):
        print("Topic -> Nodes")
        nodes = node.node_id
        subscriptions = node.get_subscribe()
        for topic in subscriptions:
            print(f"{topic}: {nodes}")
        return web.json_response({
            "node_id": node.node_id,
            "subscriptions": node.get_subscribe(),
        })

    app = web.Application()
    app.add_routes(routes)
    return app

async def start_http_server(node, port=8000):
    app = create_app(node)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"[{node.node_id}] HTTP API server started on port {port}")

# async def status_api(request):
#     node = request.app['node']
#     return web.json_response({"node_id": node.node_id, "subscriptions": node.get_subscriptions()})

# async def main():
#     import os
#     node_id = os.getenv("NODE_ID")
#     all_peers = os.getenv("ALL_PEERS").split(",")
#     broker = Broker()
#     node = Node(node_id, all_peers, broker, is_publisher=True, is_subscriber=True)
#     from core.grpc_server import serve
#     asyncio.create_task(serve(node, 5000))

#     asyncio.create_task(start_http_server(node, 8000))

#     # await asyncio.sleep(1)
#     # await node.broadcast_public_key()
#     # await node.wait_for_all_keys()
#     node.subscribe("chat")

#     print(f"[{node_id}] Node started as daemon, use HTTP API to publish/subscribe.")

#     while True:
#         await asyncio.sleep(60)

# if __name__ == "__main__":
#     asyncio.run(main())
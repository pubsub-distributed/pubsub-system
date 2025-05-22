import asyncio
import json
from aiohttp import web
from core.broker import Broker
from core.gossip import GossipAgent
from core.publisher import Publisher
from core.subscriber import Subscriber
from security.crypto_utils import generate_keys, hybrid_encrypt, hybrid_decrypt

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
        self.private_key, self.public_key = generate_keys()
        self.peer_public_keys = {self.node_id: self.public_key}  # always have own pubkey

    async def broadcast_public_key(self):
        for peer in self.peers:
            await self.gossip.send_public_key(peer, self.public_key)

    async def register_peer_key(self, peer_id, peer_pubkey_bytes):
        self.peer_public_keys[peer_id] = peer_pubkey_bytes

    async def wait_for_all_keys(self):
        while len(self.peer_public_keys) < len(self.peers) + 1:
            await asyncio.sleep(0.1)
        print(f"[{self.node_id}] All peer public keys received!")

    async def publish(self, topic, message):
        if not self.is_publisher:
            raise Exception(f"[{self.node_id}] is not a publisher.")
        for peer in self.peers:
            target_pubkey = self.peer_public_keys[peer]
            encrypted_payload = hybrid_encrypt(target_pubkey, message)
            encrypted_msg = json.dumps(encrypted_payload)
            print(f"[{self.node_id}] publishing to peer {peer}")
            await self.publisher.publish(peer, topic, encrypted_msg)

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
        # print(f"[{self.node_id}] receive() called with: {msg}")
        if not self.is_subscriber:
            return
        try:
            payload = json.loads(msg['content'])
            decrypted = hybrid_decrypt(self.private_key, payload)
            filtered = {"topic": msg["topic"], "content": decrypted}
            self.subscriber.receive(filtered)
        except Exception as e:
            print(f"[{self.node_id}] Failed to decrypt message: {e}")

    def get_public_key(self):
        return self.public_key

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
        return web.json_response({
            "node_id": node.node_id,
            "subscriptions": node.get_subscribe(),
            # "peers": node.peers,
            # "public_keys": list(node.peer_public_keys.keys())
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

async def main():
    import os
    node_id = os.getenv("NODE_ID")
    all_peers = os.getenv("ALL_PEERS").split(",")
    broker = Broker()
    node = Node(node_id, all_peers, broker, is_publisher=True, is_subscriber=True)
    from core.grpc_server import serve
    asyncio.create_task(serve(node, 5000))

    asyncio.create_task(start_http_server(node, 8000))

    await asyncio.sleep(1)
    await node.broadcast_public_key()
    await node.wait_for_all_keys()
    node.subscribe("chat")

    print(f"[{node_id}] Node started as daemon, use HTTP API to publish/subscribe.")

    while True:
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
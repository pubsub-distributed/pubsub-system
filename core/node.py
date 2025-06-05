# node.py
import os
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
    def __init__(self, node_id, all_peers, broker: Broker, peer_addrs=None, is_publisher=False, is_subscriber=False, mode="gossip"):
        self.node_id = node_id
        self.broker = broker
        self.is_publisher = is_publisher
        self.is_subscriber = is_subscriber
        self.peers = [peer for peer in all_peers if peer != self.node_id]
        self.gossip = GossipAgent(node_id, self.peers, self, peer_addrs=peer_addrs)
        self.publisher = Publisher(node_id, broker, self.gossip) if is_publisher else None
        self.subscriber = Subscriber(node_id, self.gossip) if is_subscriber else None
        self.lamport = 0
        self.mode = mode
        self.leader_id = self.calc_leader()
        self.load_subscriptions()

        log_path = "./output/node_latency.log"
        
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        print(f"[{self.node_id}] Leader is {self.leader_id}")
    
    def calc_leader(self, alive_peers=None):
        if alive_peers is None:
            alive_peers = self.peers
        return min([self.node_id] + alive_peers)

    def load_subscriptions(self):
        try:
            with open(f"../subscription/subs_{self.node_id}.json", "r") as f:
                topics = json.load(f)
            for topic in topics:
                self.subscriber.subscribe(topic, self.broker)
        except Exception:
            pass

    def save_subscriptions(self):
        os.makedirs("../subscription", exist_ok=True)
        with open(f"../subscription/subs_{self.node_id}.json", "w") as f:
            json.dump(list(self.subscriber.topics), f)
    
    def is_leader(self):
        return self.node_id == self.leader_id
    
    def update_lamport(self, received_lamport=None):
        if received_lamport is not None:
            self.lamport = max(self.lamport, received_lamport) + 1
        else:
            self.lamport += 1
    
    async def check_leader_loop(self, interval=5):
        while True:
            await asyncio.sleep(interval)
            if not await self.is_leader_alive():
                alive_peers = []
                for peer in self.peers:
                    if await self.is_peer_alive(peer):
                        alive_peers.append(peer)
                new_leader = self.calc_leader(alive_peers)
                if new_leader != self.leader_id:
                    print(f"[{self.node_id}] Leader changed from {self.leader_id} to {new_leader}")
                    self.leader_id = new_leader
    
    async def is_leader_alive(self):
        if self.node_id == self.leader_id:
            return True
        try:
            await self.gossip.ping(self.leader_id)
            return True
        except Exception:
            return False

    async def is_peer_alive(self, peer_id):
        try:
            await self.gossip.ping(peer_id)
            return True
        except Exception:
            return False

    async def publish(self, topic, message):
        if not self.is_publisher:
            raise Exception(f"[{self.node_id}] is not a publisher.")
        
        # Lamport clock tick
        self.update_lamport()

        timestamp = time.time()
        raw_id = f"{self.node_id}-{timestamp}-{message}"
        msg_id = hashlib.sha256(raw_id.encode()).hexdigest()
        msg_payload = {
            "sender": self.node_id,
            "message": message,
            "timestamp": timestamp,
            "lamport": self.lamport
        }

        encrypted_payload = encrypt_message(json.dumps(msg_payload))
        encrypted_msg = json.dumps(encrypted_payload)
        msg = {
            "topic": topic,
            "content": encrypted_msg,
            "sender": self.node_id,
            "timestamp": timestamp,
            "msg_id": msg_id,
            "lamport": self.lamport
        }

        sender_log_path = "./output/sender.log"
        os.makedirs(os.path.dirname(sender_log_path), exist_ok=True)

        with open("./output/sender.log", "a") as f:
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{now}] [{self.node_id}] Publishing | Topic: {topic} | Message: {message} | Lamport: {self.lamport} | msg_id: {msg_id}\n")
        print(f"[{now}] [{self.node_id}] Publishing | Topic: {topic} | Message: {message} | Lamport: {self.lamport}\n")

        if self.mode == "gossip":
            await self.gossip.broadcast(msg)
        elif self.mode == "leader":
            if self.is_leader():
                print(f"[{self.node_id}] I am the leader, distributing message to all peers.")
                for peer in self.peers:
                    await self.gossip.send(peer, msg)
                self.receive(msg) 
            else:
                print(f"[{self.node_id}] Not leader, sending message to leader [{self.leader_id}] for distribution.")
                await self.gossip.send(self.leader_id, msg)
        else:
            raise ValueError("Unknown pub-sub mode")

    def subscribe(self, topic):
        if not self.is_subscriber:
            raise Exception(f"[{self.node_id}] is not a subscriber.")
        self.subscriber.subscribe(topic, self.broker)
        self.save_subscriptions()
    
    def get_subscribe(self):
        return list(self.subscriber.topics)

    def unsubscribe(self, topic):
        if self.is_subscriber:
            self.subscriber.unsubscribe(topic, self.broker)
            self.save_subscriptions()

    def receive(self, msg):
        if not self.is_subscriber:
            return
        try:
            encrypted_payload = json.loads(msg['content'])
            decrypted_payload = decrypt_message(encrypted_payload)
            msg_payload = json.loads(decrypted_payload)

            msg_id = msg.get("msg_id")

            if msg_id in self.gossip.seen_msgs:
                return

            self.gossip.seen_msgs.add(msg_id)
            self.gossip.save_seen_msg(msg_id, f"{self.node_id}_seen_msgs.log")
            self.gossip.msg_store[msg_id] = msg
            # if msg_id not in self.gossip.seen_msgs:

            received_lamport = msg.get("lamport", 0)
            self.update_lamport(received_lamport)
            current_lamport = self.lamport

            msg_payload["msg_id"] = msg.get("msg_id")
            msg_payload["sender"] = msg.get("sender")
            msg_payload["timestamp"] = msg.get("timestamp")
            msg_payload["lamport"] = current_lamport
            # print("receiving message ...")
            self.subscriber.receive({"topic": msg["topic"], "content": msg_payload})

            if self.mode == "leader" and self.is_leader() and msg["sender"] != self.node_id:
                print(f"[{self.node_id}] (Leader) Received message from [{msg['sender']}], forwarding to other peers.")
                for peer in self.peers:
                    if peer != msg["sender"]:
                        asyncio.create_task(self.gossip.send(peer, msg))
            elif self.mode == "gossip":
                asyncio.create_task(self.gossip.broadcast(msg))

        except Exception as e:
            print(f"[{self.node_id}] Failed to decrypt message: {e}")

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
            "leader_id": node.leader_id, 
        })
    
    @routes.post('/switch_mode')
    async def switch_mode_api(request):
        data = await request.json()
        mode = data.get("mode")
        if mode not in ("gossip", "leader"):
            return web.Response(text="Mode must be 'gossip' or 'leader'", status=400)
        node.mode = mode
        print(f"[{node.node_id}] PubSub mode switched to {mode}")
        return web.Response(text=f"Mode switched to {mode}")

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

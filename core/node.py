import asyncio
from core.broker import Broker
from core.gossip import GossipAgent
from core.publisher import Publisher
from core.subscriber import Subscriber
from security.crypto_utils import generate_keys, encrypt_message, decrypt_message

class Node:
    def __init__(self, node_id, all_peers, broker: Broker, is_publisher=False, is_subscriber=False):
        self.node_id = node_id
        self.broker = broker
        self.is_publisher = is_publisher
        self.is_subscriber = is_subscriber

        self.peers = [peer for peer in all_peers if peer != self.node_id]
        self.gossip = GossipAgent(node_id, self.peers)

        self.publisher = Publisher(node_id, broker, self.gossip) if is_publisher else None
        self.subscriber = Subscriber(node_id) if is_subscriber else None

        # Keys for secure communication
        self.private_key, self.public_key = generate_keys()

    async def publish(self, topic, message):
        if not self.is_publisher:
            raise Exception(f"[{self.node_id}] is not a publisher.")
        encrypted_msg = encrypt_message(self.public_key, message)  # Self-encrypted for test/demo
        await self.publisher.publish(topic, encrypted_msg)

    def subscribe(self, topic):
        if not self.is_subscriber:
            raise Exception(f"[{self.node_id}] is not a subscriber.")
        self.subscriber.subscribe(topic, self.broker)

    def unsubscribe(self, topic):
        if self.is_subscriber:
            self.subscriber.unsubscribe(topic, self.broker)

    def receive(self, msg):
        if not self.is_subscriber:
            return
        try:
            decrypted = decrypt_message(self.private_key, msg['content'])
            filtered = {"topic": msg["topic"], "content": decrypted}
            self.subscriber.receive(filtered)
        except Exception as e:
            print(f"[{self.node_id}] Failed to decrypt message: {e}")

    def get_public_key(self):
        return self.public_key
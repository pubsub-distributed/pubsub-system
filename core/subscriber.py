class Subscriber:
    def __init__(self, node_id):
        self.node_id = node_id
        self.topics = set()

    def receive(self, msg):
        import time
        msg_payload = msg.get("content")
        publish_time = msg_payload.get("timestamp")
        if msg["topic"] in self.topics:
            now = time.time()
            latency = now - publish_time if publish_time else None
            with open(f"/app/output/node_latency.log", "a") as f:
                f.write(f"[{self.node_id}] Received | Sender: [{msg_payload.get('sender')}] | Topic: {msg['topic']} | Message: {msg_payload.get('message')} | Latency: {latency:.4f}s\n")
            print(f"[{self.node_id}] Received | Topic: {msg['topic']} | Message: {msg_payload.get('message')} | Latency: {latency:.4f}s")

    def subscribe(self, topic, broker):
        broker.subscribe(topic, self.node_id)
        self.topics.add(topic)
        print(f"[{self.node_id}] Subscribed to topic: '{topic}'")

    def unsubscribe(self, topic, broker):
        broker.unsubscribe(topic, self.node_id)
        self.topics.discard(topic)
        print(f"[{self.node_id}] Unsubscribed from topic: '{topic}'")
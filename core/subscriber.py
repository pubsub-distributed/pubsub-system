# subscriber.py
class Subscriber:
    def __init__(self, node_id):
        self.node_id = node_id
        self.topics = set()
        self.seen_msgs = set()

    def receive(self, msg):
        import time
        msg_payload = msg.get("content")
        msg_id = msg_payload.get("msg_id")
        lamport = msg_payload.get("lamport")


        if msg_id in self.seen_msgs:
            return
        self.seen_msgs.add(msg_id)
        publish_time = msg_payload.get("timestamp")
        if msg["topic"] in self.topics:
            now = time.time()
            latency = now - publish_time if publish_time else None
            
            with open(f"./output/node_latency.log", "a") as f:
                now = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{self.node_id}] Received | Sender: [{msg_payload.get('sender')}] | Topic: {msg['topic']} | Message: {msg_payload.get('message')} | Latency: {latency:.4f}s | Lamport: {lamport}\n")
            print(f"[{now}] [{self.node_id}] Received | Sender: [{msg_payload.get('sender')}] | Topic: {msg['topic']} | Message: {msg_payload.get('message')} | Latency: {latency:.4f}s | Lamport: {lamport}\n")

    def subscribe(self, topic, broker):
        broker.subscribe(topic, self.node_id)
        self.topics.add(topic)
        print(f"[{self.node_id}] Subscribed to topic: '{topic}'")

    def unsubscribe(self, topic, broker):
        broker.unsubscribe(topic, self.node_id)
        self.topics.discard(topic)
        print(f"[{self.node_id}] Unsubscribed from topic: '{topic}'")
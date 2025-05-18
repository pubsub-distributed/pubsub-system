class Subscriber:
    def __init__(self, node_id):
        self.node_id = node_id
        self.topics = set()

    def receive(self, msg):
        if msg["topic"] in self.topics:
            print(f"[{self.node_id}] received: {msg}")

    def subscribe(self, topic, broker):
        broker.subscribe(topic, self.node_id)
        self.topics.add(topic)

    def unsubscribe(self, topic, broker):
        broker.unsubscribe(topic, self.node_id)
        self.topics.discard(topic)
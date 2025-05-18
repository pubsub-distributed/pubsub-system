from collections import defaultdict

class Broker:
    def __init__(self):
        self.subscriptions = defaultdict(set)  # topic -> set of subscribers

    def subscribe(self, topic, subscriber_id):
        self.subscriptions[topic].add(subscriber_id)

    def unsubscribe(self, topic, subscriber_id):
        self.subscriptions[topic].discard(subscriber_id)

    def get_subscribers(self, topic):
        return list(self.subscriptions[topic])
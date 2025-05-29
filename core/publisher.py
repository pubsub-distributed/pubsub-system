# publisher.py
class Publisher:
    def __init__(self, node_id, broker, gossip):
        self.node_id = node_id
        self.broker = broker
        self.gossip = gossip

    async def publish(self, topic, message, fanout = 3):
        msg = {"topic": topic, "content": message}
        # print(f"[{self.node_id}] Publisher: publishing to {peer} topic {topic}")
        await self.gossip.broadcast(msg, fanout=fanout)
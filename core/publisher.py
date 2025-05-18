class Publisher:
    def __init__(self, node_id, broker, gossip):
        self.node_id = node_id
        self.broker = broker
        self.gossip = gossip

    async def publish(self, topic, message):
        msg = {"topic": topic, "content": message}
        await self.gossip.broadcast(msg)
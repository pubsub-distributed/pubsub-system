import asyncio
from core.broker import Broker
from core.publisher import Publisher
from core.subscriber import Subscriber
from core.gossip import GossipAgent

async def simulate():
    broker = Broker()
    peers = ["A", "B", "C", "D"]

    gossip = GossipAgent("A", peers)
    pub = Publisher("A", broker, gossip)

    subs = [Subscriber(id) for id in peers]
    for sub in subs:
        sub.subscribe("news", broker)

    await pub.publish("news", "Breaking: New PubSub system works!")

asyncio.run(simulate())
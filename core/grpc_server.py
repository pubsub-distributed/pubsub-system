import asyncio
import grpc.aio
import gossip_pb2
import gossip_pb2_grpc

class GossipServiceServicer(gossip_pb2_grpc.GossipServiceServicer):
    def __init__(self, node):
        self.node = node

    async def RegisterPublicKey(self, request, context):
        await self.node.register_peer_key(request.sender, request.public_key)
        return gossip_pb2.Ack(success=True)
    
    async def SendMessage(self, request, context):
        print(f"[{self.node.node_id}] SendMessage handler triggered!") 
        msg = {"topic": request.topic, "content": request.content, "sender": request.sender}
        # print(f"[{self.node.node_id}] received: {msg}")
        self.node.receive(msg)
        return gossip_pb2.Ack(success=True)

async def serve(node, port):
    server = grpc.aio.server()
    gossip_pb2_grpc.add_GossipServiceServicer_to_server(GossipServiceServicer(node), server)
    server.add_insecure_port(f"[::]:{port}")
    print(f"[{node.node_id}] gRPC server starting on [::]:{port}")
    await server.start()
    print(f"[{node.node_id}] gRPC server started!")
    await server.wait_for_termination()
# Pub-Sub Distributed System

A scalable, secure, and fault-tolerant **Publish-Subscribe (Pub-Sub) system** implemented in Python. This system enables multiple distributed nodes to publish messages and subscribe to topics of interest, supporting efficient message dissemination using the gossip protocol, with dynamic subscription management and HTTP API controls.

## Features

- **Distributed Pub-Sub:** Nodes act as publishers and/or subscribers for any topic.
- **Gossip Protocol:** Efficient, redundant-minimized message diffusion across the network.
- **Dynamic Subscriptions:** Subscribe/unsubscribe to topics at runtime via HTTP API.
- **Secure Communication:** Each node uses asymmetric encryption to secure messages.
- **Fault Tolerance:** Graceful handling of node failures and network partitions.
- **Easy Control:** Exposes HTTP RESTful endpoints for publishing, subscription management, and status queries.
- **Dockerized:** Easily deploy and manage multiple nodes via Docker Compose.

## Quick Start

### Prerequisites

- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
- (Optional for local dev) Python 3.8+, `pip install -r requirements.txt`

### 1. Clone the Repository

```bash
git clone git@github.com:pubsub-distributed/pubsub-system.git
cd pubsub-system
```

### **2. Build and Launch Nodes**

```
docker-compose up --build
```

This starts multiple nodes (A, B, C, D by default) with REST APIs on ports 8000, 8001, 8002, 8003.

### **3. Publish and Subscribe (via HTTP API)**

**Subscribe node to a topic:**

```
curl -X POST -H "Content-Type: application/json" \
  -d '{"topic": "news"}' \
  http://localhost:8000/subscribe
```

**Publish a message:**

```
curl -X POST -H "Content-Type: application/json" \
  -d '{"topic": "news", "message": "Hello from node A!"}' \
  http://localhost:8000/publish
```

**Check node subscription status:**

```
curl http://localhost:8000/status
```

> Change the port to 8001, 8002, etc., to interact with other nodes.
> 

### **4. Stopping the System**

```
docker-compose down
```

## **System Architecture**

- **Node**: Each node runs a gRPC server for inter-node gossip messaging and an HTTP API server for external control.
- **GossipAgent**: Handles randomized, peer-to-peer gossip-style dissemination of encrypted messages.
- **Broker**: Routes published messages to subscribers.
- **Security**: Asymmetric (public/private key) cryptography secures inter-node communication.

## **HTTP API Endpoints**

| **Endpoint** | **Method** | **Description** | **Example Payload** |
| --- | --- | --- | --- |
| /publish | POST | Publish a message to a topic | { "topic": "news", "message": "..." } |
| /subscribe | POST | Subscribe the node to a topic | { "topic": "news" } |
| /unsubscribe | POST | Unsubscribe the node from a topic | { "topic": "news" } |
| /status | GET | Query current subscriptions/status |  |

## **Configuration**

Edit docker-compose.yml to:

- Set node IDs (NODE_ID)
- Set all node peers (ALL_PEERS)
- Expose different HTTP API ports

## **Code Overview**

- core/node.py – Node logic, HTTP API, subscription management
- core/gossip.py – Gossip protocol logic for message dissemination
- core/grpc_server.py – gRPC server for inter-node comms
- core/publisher.py, core/subscriber.py – Pub-Sub business logic
- security/crypto_utils.py – Cryptography helpers

## **Extending & Testing**

- Easily add more nodes by editing docker-compose.yml.
- Use curl or any HTTP client to interact with nodes.
- For testing, see test/ and sample scripts.

## **License**

MIT License (add your license information here).
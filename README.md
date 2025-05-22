# **Pub-Sub Distributed System**

A scalable, secure, and fault-tolerant **Publish-Subscribe (Pub-Sub) system** implemented in Python. This system enables multiple distributed nodes to publish messages and subscribe to topics of interest, supporting efficient message dissemination using the gossip protocol, with dynamic subscription management and HTTP API controls.

## **Features**

- Distributed Pub-Sub across nodes
- Gossip protocol for efficient, redundant-minimized dissemination
- Dynamic subscription/unsubscription at runtime (HTTP API)
- Secure inter-node messaging with asymmetric cryptography
- Fault-tolerant (handles node failures/network partitions)
- HTTP REST endpoints for easy control
- Dockerized for simple multi-node deployment

---

## **Quick Start**

### **Prerequisites**

- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
- (Optional) Python 3.8+ if running show_subscribers.py locally

### **1. Clone the Repository**

```
git clone git@github.com:pubsub-distributed/pubsub-system.git
cd pubsub-system
```

### **2. Build and Launch Nodes**

```
docker-compose up --build
```

This starts nodes A/B/C/D with REST APIs on ports 8000–8003.

### **3. Interact via HTTP API**

**Subscribe a node to a topic:**

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

### **4. Query All Subscriptions Across Nodes**

A ready-to-use script, **show_subscribers.py**, is included to display all topics and the nodes that subscribe to them.

### **Usage**

Make sure you have requests installed (already in requirements.txt).

Then run:

```
python show_subscribers.py
```

### **Example Output**

```
Topic -> Nodes
news: ['A', 'C', 'D']
chat: ['A', 'B']
sports: ['B', 'D']
```

---

## **HTTP API Endpoints**

| **Endpoint** | **Method** | **Description** | **Example Payload** |
| --- | --- | --- | --- |
| /publish | POST | Publish a message to a topic | { "topic": "news", "message": "..." } |
| /subscribe | POST | Subscribe the node to a topic | { "topic": "news" } |
| /unsubscribe | POST | Unsubscribe the node from a topic | { "topic": "news" } |
| /status | GET | Query node’s current subscriptions |  |

---

## **Configuration**

- Edit docker-compose.yml to set node IDs and ALL_PEERS.
- Each node exposes its API at a different host port (8000, 8001, …).

---

## **Code Overview**

- core/node.py – Node logic, HTTP API, subscription management
- core/gossip.py – Gossip protocol logic
- core/grpc_server.py – gRPC server for node-to-node comms
- core/publisher.py, core/subscriber.py – Pub/Sub business logic
- security/crypto_utils.py – Cryptography utilities
- show_subscribers.py – Lists topics and their subscribers across all nodes

---

## **Extending & Testing**

- Add more nodes by editing docker-compose.yml.
- Use any HTTP client to interact with the system.
- Use show_subscribers.py to check topic subscriptions across the cluster.

---

## **License**

MIT License
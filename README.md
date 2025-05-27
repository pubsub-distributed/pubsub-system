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

This starts nodes A/B/C/D/E/F with REST APIs on ports 8000–8005.

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

## **4. Testing and Automation Scripts**

**All scripts are in the scripts/ directory for convenience!**

| **Script** | **Description** |
| --- | --- |
| scripts/show_subscribers.py | List all topics and nodes subscribed to them across the cluster |
| scripts/subscribe_topic.py | Programmatically subscribe a node to a topic |
| scripts/unsubscribe_topic.py | Programmatically unsubscribe a node from a topic |
| scripts/send_test_messages.py | Send many messages (for throughput/latency testing) |
| scripts/analyze_latency.py | Analyze log files and summarize message delivery latency |

**Example usage:**

```
python scripts/show_subscribers.py
python scripts/subscribe_topic.py <node_letter> <topic>
python scripts/unsubscribe_topic.py <node_letter> <topic>
python scripts/send_test_messages.py <sender> <topic> <message_count>
python scripts/analyze_latency.py
```

> These scripts require requests and (for analyze_latency) re/os (already in requirements.txt).
> 

---

### **Example Output**

```
python scripts/show_subscribers.py

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
- scripts/show_subscribers.py – Lists topics and their subscribers across all nodes
- scripts/subscribe_topic.py / unsubscribe_topic.py – Manage topic subscriptions from script
- scripts/send_test_messages.py – Automated publish message testing
- scripts/analyze_latency.py – Latency/performance analysis tools

---

## **Extending & Testing**

- Add more nodes by editing docker-compose.yml.
- Use any HTTP client to interact with the system.
- Use provided test scripts for cluster introspection and benchmarking.

---

## **License**

MIT License
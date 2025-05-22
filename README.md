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
git clone <your-repo-url>
cd pubsub-system
```

### **2. Clone the Repository**

```
git clone <your-repo-url>
cd pubsub-system
```

### **3. Build and Launch Nodes**

```
docker-compose up --build
```

> This starts nodes (A, B, C, D) with REST APIs on ports 8000, 8001, 8002, 8003.
> 

---

## **Usage**

### **Publish a Message**

```
curl -X POST -H "Content-Type: application/json" \
  -d '{"topic": "chat", "message": "hello world"}' \
  http://localhost:8000/publish
```

### **Subscribe a Node to a Topic**

```
curl -X POST -H "Content-Type: application/json" \
  -d '{"topic": "news"}' \
  http://localhost:8001/subscribe
```

### **Unsubscribe from a Topic**

```
curl -X POST -H "Content-Type: application/json" \
  -d '{"topic": "news"}' \
  http://localhost:8001/unsubscribe
```

### **Query Node Status (subscriptions, etc.)**

```
curl http://localhost:8002/status
```

---

## **Monitor All Subscribers by Topic**

You can see which nodes are subscribed to which topics by running:

```
python show_subscribers.py
```

**Example output:**

```
Topic -> Nodes
chat: ['A', 'B', 'C', 'D']
news: ['B', 'C']
```

---

## **File Structure**

- core/ — Core system modules (node logic, gossip, publisher, subscriber, etc.)
- Dockerfile, docker-compose.yml — Containerization and orchestration
- show_subscribers.py — Utility: Map topics to subscribing nodes

---

## **License**

MIT License (or specify your license here)
# **Distributed Pub/Sub System**

A scalable, fault-tolerant distributed publish-subscribe messaging system supporting both gossip and leader-based modes.

Supports full deployment on local, cloud (AWS EC2), or hybrid clusters.

---

## **Features**

- **Modular Python Architecture:** Node, Broker, Publisher, Subscriber, GossipAgent.
- **Gossip & Leader Modes:** Choose between eventual or strong consistency.
- **Async & Concurrent:** Built with asyncio for high throughput.
- **gRPC Protocol:** Efficient, extensible node communication (optional, if implemented).
- **Secure:** Built-in AES encryption for messages.
- **Cloud-ready:** Orchestration/automation scripts for multi-node clusters (AWS EC2 recommended).
- **Performance Monitoring:** Integrated logging, message tracking, and latency/throughput analysis tools.

---

## **1. Clone the Project**

```
git clone https://github.com/YOUR_GITHUB_USERNAME/pubsub-system.git
cd pubsub-system
```

---

## **2. Environment Setup**

It is recommended to use a **Python virtual environment**:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## **3. Configuration**

Edit peers.json to include all participating nodes.

**Example format:**

```
{
  "A": ["18.217.2.75", 8000],
  "B": ["3.18.108.83", 8001],
  "C": ["18.217.202.61", 8002]
  // Add more nodes as needed
}
```

- **Each node should use the same peers.json file.**

---

## **4. Starting a Node**

On **each node** (local or remote):

```
cd pubsub-system
source venv/bin/activate
python3 start_node.py --node_id <NODE_ID> --port <PORT> --peer_addrs_config peers.json
```

- Replace <NODE_ID> and <PORT> per your configuration.

---

## **5. Running on AWS EC2**

**(Optional)**

If deploying on AWS, launch EC2 instances and set up SSH access (~/.ssh/pubsub-key.pem).

SSH into each instance and follow the steps above for environment setup and node startup.

---

## **6. Using Management and Testing Scripts**

All management and analysis scripts are in the scripts/ and output-analyze/ directories.

### **6.1 Running Utility Scripts**

First, **activate your venv** and switch to the relevant directory:

```
cd pubsub-system
source venv/bin/activate
cd scripts
```

- **send_test_messages.py** — Send N messages from a node.

```
python send_test_messages.py <SENDER> <TOPIC> <MESSAGE> <COUNT>
```

- **concurrent_test.py** — Simulate multiple concurrent senders.

```
python concurrent_test.py <SENDER1> <SENDER2> ... <TOPIC> <MESSAGE> <COUNT>
```

- **subscribe_topic.py / unsubscribe_topic.py / show_subscribers.py / switch_pubsub_mode.py**

> Tip: See in-script help for usage details.
> 

---

### **6.2 Output Analysis Tools**

Switch to the output analysis directory:

```
cd output-analyze
source ../venv/bin/activate
pip install -r requirements.txt
```

- **cleanup_all_nodes.sh**:
    
    Cleans all logs and subscriptions on all nodes (remote via SSH).
    

```
bash cleanup_all_nodes.sh
# Or, make executable: chmod +x cleanup_all_nodes.sh && ./cleanup_all_nodes.sh
```

- **exit_all_nodes.sh**:
    
    Gracefully stops all remote nodes.
    

```
bash exit_all_nodes.sh
```

- **fetch_logs_and_subs.sh**:
    
    Fetches all logs/subscription files from every node via SSH.
    

```
bash fetch_logs_and_subs.sh
```

- **check-message.py**:
    
    Compares sender and receiver logs, validates delivery, outputs detailed correctness report.
    

```
python check-message.py
```

- **analyze_logs.py**:
    
    Analyzes system performance (latency/throughput).
    

```
python analyze_logs.py
```

> All analysis output will be saved to the output-analyze/reports/ directory.
> 

---

## **7. Security**

- By default, nodes use unencrypted connections.
- To enable full security, ensure your configuration uses AES keys and that any secrets/keys are distributed to all participating nodes.

---

## **8. Extending or Contributing**

- Modular design: Easily add new message types, broker strategies, or cloud backends.
- To add a new node:
    - Update peers.json
    - Deploy code & requirements
    - Start the node with correct parameters

---

## **9. Example: Full AWS EC2 Setup**

1. Launch 10 EC2 Ubuntu instances, each with a public IP.
2. SSH into each instance and run setup steps (clone, venv, requirements, configure).
3. Copy the same peers.json to each node.
4. Start each node with its unique --node_id and --port.
5. Use the provided scripts for testing and system analysis.

---

## **10. Troubleshooting**

- Ensure all nodes can communicate (open ports in AWS security groups).
- Use logs/ for troubleshooting system behavior.
- For SSH-based scripts, ensure your local machine has access to the correct key file.

---

## **11. License**

MIT License

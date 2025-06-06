## **Deployment on AWS EC2**

**To access and operate the system on your 10 EC2 instances:**

### **1. SSH into Each Node**

Use your SSH private key ~/.ssh/pubsub-key.pem and the public IP for each node:

```
# Example for node A
ssh -i ~/.ssh/pubsub-key.pem ubuntu@18.217.2.75

# Example for node B
ssh -i ~/.ssh/pubsub-key.pem ubuntu@3.18.108.83

# ...and so on for each node:
# C: 18.217.202.61
# D: 18.116.237.205
# E: 18.191.191.34
# F: 18.224.199.139
# G: 18.217.69.68
# H: 18.217.200.15
# I: 3.19.143.26
# J: 18.222.156.181
```

### **2. Node Startup Example**

Once you are inside a node (e.g. after ssh), run:

```
cd ~/pubsub-system
source venv/bin/activate
python3 start_node.py --node_id A --port 8000 --peer_addrs_config peers.json
```

- Change --node_id and --port according to the node (see your mapping in peers.json).

### **3. Example peers.json**

All nodes must have the same peers.json, e.g.:

```
{
  "A": ["18.217.2.75", 8000],
  "B": ["3.18.108.83", 8001],
  "C": ["18.217.202.61", 8002],
  "D": ["18.116.237.205", 8003],
  "E": ["18.191.191.34", 8004],
  "F": ["18.224.199.139", 8005],
  "G": ["18.217.69.68", 8006],
  "H": ["18.217.200.15", 8007],
  "I": ["3.19.143.26", 8008],
  "J": ["18.222.156.181", 8009]
}
```

### **4. Summary Table (for quick copy-paste)**

| **Node** | **Public IP** | **SSH Command** | **Node ID** | **Port** |
| --- | --- | --- | --- | --- |
| A | 18.217.2.75 | ssh -i ~/.ssh/pubsub-key.pem ubuntu@18.217.2.75 | A | 8000 |
| B | 3.18.108.83 | ssh -i ~/.ssh/pubsub-key.pem ubuntu@3.18.108.83 | B | 8001 |
| C | 18.217.202.61 | ssh -i ~/.ssh/pubsub-key.pem ubuntu@18.217.202.61 | C | 8002 |
| D | 18.116.237.205 | ssh -i ~/.ssh/pubsub-key.pem ubuntu@18.116.237.205 | D | 8003 |
| E | 18.191.191.34 | ssh -i ~/.ssh/pubsub-key.pem ubuntu@18.191.191.34 | E | 8004 |
| F | 18.224.199.139 | ssh -i ~/.ssh/pubsub-key.pem ubuntu@18.224.199.139 | F | 8005 |
| G | 18.217.69.68 | ssh -i ~/.ssh/pubsub-key.pem ubuntu@18.217.69.68 | G | 8006 |
| H | 18.217.200.15 | ssh -i ~/.ssh/pubsub-key.pem ubuntu@18.217.200.15 | H | 8007 |
| I | 3.19.143.26 | ssh -i ~/.ssh/pubsub-key.pem ubuntu@3.19.143.26 | I | 8008 |
| J | 18.222.156.181 | ssh -i ~/.ssh/pubsub-key.pem ubuntu@18.222.156.181 | J | 8009 |

---

## **Using Python Scripts in the scripts/**

This project provides several Python utility scripts to manage, test, and analyze the Pub/Sub system.

**You must run these scripts directly on an AWS node** (not on your local machine).

### **Steps to Run a Script on an AWS Node**

1. **Open a new terminal window (tab).**
2. **Login to the target AWS node via SSH:**

```
ssh -i ~/.ssh/pubsub-key.pem ubuntu@<NODE_PUBLIC_IP>
```

1. Replace <NODE_PUBLIC_IP> with one of:

```
18.217.2.75
3.18.108.83
18.217.202.61
18.116.237.205
18.191.191.34
18.224.199.139
18.217.69.68
18.217.200.15
3.19.143.26
18.222.156.181
```

1. **Activate your Python virtual environment:**

```
cd ./pubsub-system
source venv/bin/activate
cd ./scripts
```

1. **Now, run your desired script as shown below.**

---

### **Overview of Available Scripts**

### **send_test_messages.py**

Send a batch of test messages from a specific node for a given topic.

**Usage:**

```
python send_test_messages.py <SENDER> <TOPIC> <MESSAGE> <COUNT>
```

**Example:**

```
python send_test_messages.py A news 'Hello world!' 10
```

---

### **concurrent_test.py**

Simulate concurrent publishers by sending messages from multiple nodes at once.

**Usage:**

```
python concurrent_test.py <SENDER1> <SENDER2> ... <TOPIC> <MESSAGE> <COUNT>
```

**Example (send from A and B concurrently):**

```
python concurrent_test.py A B news 'Test message' 10
```

- You can add more senders for more concurrency:
    
    python concurrent_test.py A B C D news ‘Hi’ 10
    

---

### **show_subscribers.py**

Display the current subscribers for each topic

**Usage:**

```
python show_subscribers.py
```

---

### **subscribe_topic.py**

Subscribe a node to a topic.

**Usage:**

```
python subscribe_topic.py <NODE_ID> <TOPIC>
```

---

### **unsubscribe_topic.py**

Unsubscribe a node from a topic.

**Usage:**

```
python unsubscribe_topic.py <NODE_ID> <TOPIC>
```

---

### **switch_pubsub_mode.py**

Switch the publish/subscribe mode (e.g., between leader and gossip mode) for a node.

**Usage:**

```
python switch_pubsub_mode.py <MODE>
```

**Example:**

```
python switch_pubsub_mode.py gossip
python switch_pubsub_mode.py leader
```

---

> Note:
> 

> Make sure to activate the venv each time you log in, or open a new SSH session!
> 

---

# **Output Analysis & Management Tools -** output-analyze **— Usage Guide**

## **Setup Python Environment**

> You must use a Python virtual environment before running the tools.
> 

> You must have the correct SSH private key (~/.ssh/pubsub-key.pem) on your local machine, with proper permissions, to access all AWS nodes.
> 

```
cd output-analyze
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## **2.**

## **Cleanup All Nodes**

> Cleans all logs and subscription files on every node.
> 

> Run this before each new test to ensure a fresh start.
> 

```
bash cleanup_all_nodes.sh
```

or (after making the script executable):

```
chmod +x cleanup_all_nodes.sh
./cleanup_all_nodes.sh
```

---

## **Exit (Stop) All Nodes**

> Gracefully stops all running nodes (calls pkill on each AWS instance).
> 

```
bash exit_all_nodes.sh
```

or

```
chmod +x exit_all_nodes.sh
./exit_all_nodes.sh
```

---

## **Fetch Logs and Subscription Files**

> Collects the latest logs and subscription info from all remote nodes and saves them locally to ./logs and ./subs.
> 

```
bash fetch_logs_and_subs.sh
```

or

```
chmod +x fetch_logs_and_subs.sh
./fetch_logs_and_subs.sh
```

---

**Tip:**

If you want to run a shell script directly with ./script_name.sh, you need to give it executable permission first:

```
chmod +x script_name.sh
```

---

## **5.**

## **Analyze Message Delivery Correctness**

> Compares sender logs and receiver logs, based on actual topic subscriptions. Outputs a detailed report for each topic and node.
> 

```
python check-message.py
```

- Output: check-message-report.txt in output-analyze/ reports
- **Purpose:** Find missing, duplicated, and correctly received messages per topic/subscriber.

---

## **6.**

## **Analyze Latency and Throughput**

> Evaluates the performance of your system (average latency, throughput, and percentiles).
> 

```
python analyze_logs.py
```

- Output: analysis_report.txt in output-analyze/ reports
- **Purpose:** Understand delay and performance under various configurations.

---

## **Notes**

- You must have the correct SSH private key (~/.ssh/pubsub-key.pem) on your local machine, with proper permissions, to access all AWS nodes.
- All scripts assume ubuntu user on the nodes.
- Make sure all AWS instances are running before executing these tools.
- Run scripts from the output-analyze directory for correct relative paths.

---

## **Script/Tool Purpose Summary**

| **Script/File** | **Description** |
| --- | --- |
| cleanup_all_nodes.sh | Cleans all logs and subscription files from all nodes |
| exit_all_nodes.sh | Remotely terminates all node processes |
| fetch_logs_and_subs.sh | Downloads all node logs and subscriptions to local folders |
| analyze_logs.py | Analyzes logs for latency/throughput, outputs performance |
| check-message.py | Checks message correctness, detects lost/duplicate per topic |
| requirements.txt | Python dependencies for analysis tools |
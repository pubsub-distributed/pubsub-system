#!/bin/bash

KEY_PATH=~/.ssh/pubsub-key.pem
REMOTE_LOG_PATH=/home/ubuntu/pubsub-system/output/node_latency.log
REMOTE_SENDER_LOG_PATH=/home/ubuntu/pubsub-system/output/sender.log
LOCAL_DIR=./logs

# Fill in your list of node ids and ips
NODE_IDS=("A" "B" "C" "D" "E" "F" "G" "H" "I" "J")
NODE_IPS=("18.217.2.75" "3.18.108.83" "18.217.202.61" "18.116.237.205" "18.191.191.34" "18.224.199.139" "18.217.69.68" "18.217.200.15" "3.19.143.26" "18.222.156.181")

mkdir -p "$LOCAL_DIR"

for i in "${!NODE_IDS[@]}"; do
    id="${NODE_IDS[$i]}"
    ip="${NODE_IPS[$i]}"
    echo "==> Fetching $id ($ip)"
    scp -i "$KEY_PATH" -o StrictHostKeyChecking=no ubuntu@"$ip":"$REMOTE_LOG_PATH" "$LOCAL_DIR/node_${id}.log" || true
    echo "==> Fetching sender.log from $id ($ip)"
    scp -i "$KEY_PATH" -o StrictHostKeyChecking=no ubuntu@"$ip":"$REMOTE_SENDER_LOG_PATH" "$LOCAL_DIR/node_${id}_sender.log" || true
done

echo "All logs have been downloaded"

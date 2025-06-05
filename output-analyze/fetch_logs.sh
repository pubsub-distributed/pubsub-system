#!/bin/bash

KEY_PATH=~/.ssh/pubsub-key.pem
REMOTE_LOG_PATH=/home/ubuntu/pubsub-system/output/node_latency.log
REMOTE_SENDER_LOG_PATH=/home/ubuntu/pubsub-system/output/sender.log
LOCAL_DIR=./logs

# Fill in your list of node ids and ips
NODE_IDS=("A" "B" "C")
NODE_IPS=("18.217.2.75" "3.18.108.83" "18.217.202.61")

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

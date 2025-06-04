#!/bin/bash

KEY_PATH=~/.ssh/pubsub-key.pem
REMOTE_LOG_PATH=/home/ubuntu/pubsub-system/output/node_latency.log
LOCAL_DIR=./logs

# 填写你的节点 id 和 IP 列表
NODE_IDS=("A" "B")
NODE_IPS=("18.217.2.75" "3.18.108.83")

mkdir -p "$LOCAL_DIR"

for i in "${!NODE_IDS[@]}"; do
    id="${NODE_IDS[$i]}"
    ip="${NODE_IPS[$i]}"
    echo "==> Fetching $id ($ip)"
    scp -i "$KEY_PATH" -o StrictHostKeyChecking=no ubuntu@"$ip":"$REMOTE_LOG_PATH" "$LOCAL_DIR/node_${id}.log"
done

echo "所有日志下载完成。"

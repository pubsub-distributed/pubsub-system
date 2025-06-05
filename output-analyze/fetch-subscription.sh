#!/bin/bash

KEY=~/.ssh/pubsub-key.pem
USER=ubuntu
IDS=("A" "B" "C" "D" "E" "F" "G" "H" "I" "J")
NODE=("18.217.2.75" "3.18.108.83" "18.217.202.61" "18.116.237.205" "18.191.191.34" "18.224.199.139" "18.217.69.68" "18.217.200.15" "3.19.143.26" "18.222.156.181")
LOCAL_DIR=./subs  # 本地存放目录

mkdir -p "$LOCAL_DIR"

for i in "${!NODES[@]}"; do
    id="${IDS[$i]}"
    ip="${NODES[$i]}"
    echo "==> Fetching subs_${id}.json from $ip ..."
    scp -i "$KEY" -o StrictHostKeyChecking=no \
      "$USER@$ip:~/subscription/subs_${id}.json" \
      "$LOCAL_DIR/subs_${id}.json" || true
done

echo "All subscription files downloaded."

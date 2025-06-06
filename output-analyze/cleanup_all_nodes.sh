KEY=~/.ssh/pubsub-key.pem
USER=ubuntu
NODES=(18.217.2.75 3.18.108.83 18.217.202.61 18.116.237.205 18.191.191.34 18.224.199.139 18.217.69.68 18.217.200.15 3.19.143.26 18.222.156.181)

CMD='echo "Before:"; ls -lh /home/ubuntu/pubsub-system/output/; rm -vf /home/ubuntu/pubsub-system/*.log /home/ubuntu/pubsub-system/output/*.log /home/ubuntu/pubsub-system/subscription/*.json; echo "After:"; ls -lh /home/ubuntu/pubsub-system/output/'

for ip in "${NODES[@]}"; do
    echo "==> cleaning $ip ..."
    ssh -i "$KEY" -o StrictHostKeyChecking=no "$USER@$ip" "$CMD"
    echo "----- done $ip -----"
done

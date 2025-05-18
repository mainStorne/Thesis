#!/bin/bash
set -e

# Create test filesystem if it doesn't exist
# if [ ! -f /tmp/quotafs.img ]; then
#     echo "Creating quota test filesystem..."
#     dd if=/dev/zero of=/tmp/quotafs.img bs=1GB count=1
#     mkfs.ext4 -F /tmp/quotafs.img
# fi

mount -o loop,usrquota,grpquota /quotafs.img /fs
quotaon -ug /fs

cd /workspace

# run only once
# sudo sh create-registry.sh
# sudo docker stack deploy -c docker-compose.dev.yaml thesis

echo "Quota test environment ready!"

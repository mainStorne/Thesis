#!/bin/bash
set -e

# Create test filesystem if it doesn't exist
# if [ ! -f /tmp/quotafs.img ]; then
#     echo "Creating quota test filesystem..."
#     dd if=/dev/zero of=/tmp/quotafs.img bs=1GB count=1
#     mkfs.ext4 -F /tmp/quotafs.img
# fi

mount -o loop,usrquota,grpquota /test/quotafs.img /test/filesystem/
quotaon -ug /test/filesystem
cd /workspace/utils
sudo docker compose -f docker-compose.students.yaml up -d
echo "Quota test environment ready!"

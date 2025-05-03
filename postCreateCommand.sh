#!/bin/bash
set -e

# Create test filesystem if it doesn't exist
# if [ ! -f /tmp/quotafs.img ]; then
#     echo "Creating quota test filesystem..."
#     dd if=/dev/zero of=/tmp/quotafs.img bs=1M count=200
#     mkfs.ext4 -F /tmp/quotafs.img
# fi

mount -o loop,usrquota,grpquota /test/quotafs.img /test/filesystem/

mount -o loop,usrquota,grpquota /test/students.img /test/filesystem/students/
# Set up mount
# mkdir -p /mnt/quotatest
# mount -o loop,usrquota,grpquota /tmp/quotafs.img /mnt/quotatest || true

# Initialize and enable quota
# quotacheck -cugm /mnt/quotatest
# quotaon -v /mnt/quotatest

# # Create test users
# useradd -m testuser1 || true
# useradd -m testuser2 || true

# # Set quota for test users
# setquota -u testuser1 50000 60000 100 120 /mnt/quotatest
# setquota -u testuser2 100000 120000 200 240 /mnt/quotatest

echo "Quota test environment ready!"

#!/bin/bash
TOTAL_MEM_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
ZRAM_SIZE_KB=$((TOTAL_MEM_KB / 2))

modprobe zram num_devices=1
echo lz4 > /sys/block/zram0/comp_algorithm
echo "${ZRAM_SIZE_KB}K" > /sys/block/zram0/disksize
mkswap /dev/zram0
swapon -p 100 /dev/zram0

echo "zram swap configured: ${ZRAM_SIZE_KB}KB (compressed)"

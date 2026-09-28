#!/bin/bash
# ==============================================================================
# Symbian-X86 LOOX OS Power & Performance Optimization Daemon/Script
# Target: Fujitsu FMV-BIBLO LOOX M/G30 (Intel Atom N450 / NM10 Chipset)
# ==============================================================================

set -e

echo "[LOOX-OPT] Applying hardware power and memory optimizations..."

# 1. CPU Frequency Scaling (ondemand governor with fast down-scaling)
if [ -d /sys/devices/system/cpu/cpu0/cpufreq ]; then
    for cpu in /sys/devices/system/cpu/cpu*/cpufreq; do
        if [ -f "$cpu/scaling_governor" ]; then
            echo ondemand > "$cpu/scaling_governor" 2>/dev/null || true
        fi
    done
    if [ -f /sys/devices/system/cpu/cpufreq/ondemand/up_threshold ]; then
        echo 85 > /sys/devices/system/cpu/cpufreq/ondemand/up_threshold 2>/dev/null || true
    fi
    echo "[LOOX-OPT] CPU Governor configured to ondemand (up_threshold=85)."
fi

# 2. Intel GPU Power Management
if [ -d /sys/class/drm/card0/power ]; then
    echo auto > /sys/class/drm/card0/power/control 2>/dev/null || true
    echo "[LOOX-OPT] GPU dynamic power management enabled."
fi

# 3. SATA Link Power Management (ALPM)
for host in /sys/class/scsi_host/host*/link_power_management_policy; do
    if [ -f "$host" ]; then
        echo med_power_with_dipm > "$host" 2>/dev/null || true
    fi
done

# 4. Audio Codec Power Saving (ALC269)
if [ -f /sys/module/snd_hda_intel/parameters/power_save ]; then
    echo 1 > /sys/module/snd_hda_intel/parameters/power_save 2>/dev/null || true
    echo Y > /sys/module/snd_hda_intel/parameters/power_save_controller 2>/dev/null || true
fi

# 5. Atheros AR9285 Wi-Fi Power Save
if command -v iw >/dev/null 2>&1; then
    for iface in $(iw dev | awk '$1=="Interface"{print $2}'); do
        iw dev "$iface" set power_save on 2>/dev/null || true
    done
fi

# 6. Kernel Virtual Memory Tuning for 1GB RAM (optimized for desktop use)
# Low swappiness: keep apps in RAM, avoid thrashing on 1 GB Atom N450
sysctl -w vm.swappiness=10 >/dev/null 2>&1 || true
# Higher cache pressure: reclaim dentry/inode caches faster when RAM is tight
sysctl -w vm.vfs_cache_pressure=150 >/dev/null 2>&1 || true
# Flush dirty pages quickly so writes don't stall the UI
sysctl -w vm.dirty_background_ratio=3 >/dev/null 2>&1 || true
sysctl -w vm.dirty_ratio=8 >/dev/null 2>&1 || true
# Reduce writeback interval from 500cs → 200cs for snappier FS
sysctl -w vm.dirty_writeback_centisecs=200 >/dev/null 2>&1 || true
# Allow overcommit for small Python/Tkinter apps
sysctl -w vm.overcommit_memory=1 >/dev/null 2>&1 || true
# Minimize time the kernel holds memory for mmap merges
sysctl -w vm.mmap_min_addr=4096 >/dev/null 2>&1 || true

# 7. zram Compressed RAM Swap Setup (50% of physical RAM with lz4 for speed)
if [ -e /dev/zram0 ] || modprobe zram num_devices=1 2>/dev/null; then
    if ! grep -q zram /proc/swaps 2>/dev/null; then
        TOTAL_RAM_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
        ZRAM_SIZE_KB=$(( TOTAL_RAM_KB / 2 ))  # 50% of RAM; lz4 gives ~3x ratio = effective 150%
        # Prefer lz4 (fastest decompression), fall back to lzo or zstd
        echo lz4 > /sys/block/zram0/comp_algorithm 2>/dev/null \
            || echo lzo > /sys/block/zram0/comp_algorithm 2>/dev/null \
            || echo zstd > /sys/block/zram0/comp_algorithm 2>/dev/null || true
        echo "${ZRAM_SIZE_KB}K" > /sys/block/zram0/disksize 2>/dev/null || true
        mkswap /dev/zram0 >/dev/null 2>&1 || true
        swapon -p 100 /dev/zram0 >/dev/null 2>&1 || true
        echo "[LOOX-OPT] zram swap configured (${ZRAM_SIZE_KB}K lz4 compressed)."
    fi
fi

echo "[LOOX-OPT] System power & memory optimization complete."
exit 0

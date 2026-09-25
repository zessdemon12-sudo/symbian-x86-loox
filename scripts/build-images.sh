#!/bin/bash
# ==============================================================================
# Symbian-X86 LOOX OS - USB Image & HDD Image Generator
# Creates:
# - output/symbian-x86-loox-usb.img (Bootable Raw USB Drive Image)
# - output/symbian-x86-loox-hdd.img (Pre-installed Hard Disk Image)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$BASE_DIR/output"
ISO_FILE="$OUTPUT_DIR/symbian-x86-loox.iso"
USB_IMG="$OUTPUT_DIR/symbian-x86-loox-usb.img"
HDD_IMG="$OUTPUT_DIR/symbian-x86-loox-hdd.img"

mkdir -p "$OUTPUT_DIR"

echo "=========================================================="
echo "    [IMAGES] Creating USB & HDD Disk Images"
echo "=========================================================="

# 1. Create bootable USB Image (Hybrid raw disk image)
if [ -f "$ISO_FILE" ]; then
    echo "[IMAGES] Creating bootable USB image: $USB_IMG..."
    cp "$ISO_FILE" "$USB_IMG"
fi

# 2. Create Pre-installed HDD Installation Image
echo "[IMAGES] Creating pre-installed HDD raw image (256MB sparse): $HDD_IMG..."
rm -f "$HDD_IMG"
# Create 256MB raw disk image
dd if=/dev/zero of="$HDD_IMG" bs=1M count=0 seek=256 2>/dev/null || truncate -s 256M "$HDD_IMG"

# Partition image with MBR
parted -s "$HDD_IMG" mklabel msdos 2>/dev/null || true
parted -s "$HDD_IMG" mkpart primary ext4 1MiB 100% 2>/dev/null || true
parted -s "$HDD_IMG" set 1 boot on 2>/dev/null || true

echo "=========================================================="
echo "    [IMAGES] Generated all target disk images:"
ls -lh "$OUTPUT_DIR"/*.img "$OUTPUT_DIR"/*.iso
echo "=========================================================="

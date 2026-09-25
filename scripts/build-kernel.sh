#!/bin/bash
# ==============================================================================
# Symbian-X86 LOOX OS - Kernel & Initramfs Builder
# Target: Intel Atom N450 (i686 32-bit x86)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_BOOT="$BASE_DIR/output/boot"
KERNEL_DIR="$BASE_DIR/kernel"
I686_DIR="$KERNEL_DIR/i686"

mkdir -p "$OUTPUT_BOOT"

echo "=========================================================="
echo "    [KERNEL] Assembling Pure 32-bit i686 Kernel & Initramfs"
echo "=========================================================="

# 1. Use the authentic 32-bit i686 Linux kernel
I686_VMLINUZ="$I686_DIR/kernel_deb/boot/vmlinuz-6.1.0-50-686-pae"
if [ ! -f "$I686_VMLINUZ" ]; then
    echo "[KERNEL] Extracting i686 kernel..."
    mkdir -p "$I686_DIR/kernel_deb"
    cd "$I686_DIR/kernel_deb"
    ar x ../linux-image-6.1.0-50-686-pae_6.1.176-1_i386.deb
    tar -xf data.tar.xz ./boot/
    cd "$BASE_DIR"
fi

cp "$I686_VMLINUZ" "$OUTPUT_BOOT/vmlinuz"
echo "[KERNEL] Staged 32-bit i686 kernel: $OUTPUT_BOOT/vmlinuz"

# 2. Build 32-bit initramfs
bash "$KERNEL_DIR/build-initramfs-i686.sh"

echo "=========================================================="
echo "    [KERNEL] Kernel & Initramfs Assembly Complete:"
ls -lh "$OUTPUT_BOOT"
echo "=========================================================="

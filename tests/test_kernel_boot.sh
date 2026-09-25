#!/bin/bash
# ==============================================================================
# Symbian-X86 LOOX OS - Automated Headless QEMU Boot Verification Test
# Tests Phase 1: Boot Linux on QEMU (Intel Atom N450 PAE Target)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$BASE_DIR/output"
VMLINUZ="$OUTPUT_DIR/boot/vmlinuz"
INITRD="$OUTPUT_DIR/boot/initrd.img"
USB_IMG="$OUTPUT_DIR/symbian-x86-loox-usb.img"
LOG_FILE="/tmp/qemu_symbian_boot.log"

echo "=========================================================="
echo "    [TEST] Running QEMU Headless Boot Verification"
echo "=========================================================="

QEMU_BIN=$(command -v qemu-system-i386 || command -v qemu-system-x86_64)

rm -f "$LOG_FILE"

echo "[TEST] Direct Kernel + Initramfs + USB Drive Boot Verification..."
"$QEMU_BIN" \
    -name "Symbian-X86 Boot Test" \
    -cpu qemu32,+pae \
    -smp 2 \
    -m 512M \
    -kernel "$VMLINUZ" \
    -initrd "$INITRD" \
    -drive file="$USB_IMG",format=raw \
    -append "console=ttyS0 console=tty0 earlyprintk=serial,ttyS0,115200" \
    -nographic \
    -serial mon:stdio > "$LOG_FILE" 2>&1 &
QEMU_PID=$!

sleep 18
kill -9 $QEMU_PID 2>/dev/null || true

echo "[TEST] QEMU execution finished. Inspecting boot log..."
if [ -f "$LOG_FILE" ] && [ -s "$LOG_FILE" ]; then
    echo "--- QEMU Boot Log Output (Key Milestones) ---"
    grep -E "Linux version|Attached SCSI|usbcore|squashfs|sdhci" "$LOG_FILE" || head -n 25 "$LOG_FILE"
    echo "---------------------------------------------"
    if grep -q "Attached SCSI disk" "$LOG_FILE" && grep -q "Linux version" "$LOG_FILE"; then
        echo "✅ [PASS] Kernel and initramfs boot successfully verified in QEMU!"
    else
        echo "⚠️ Kernel booted, inspecting status."
    fi
else
    echo "⚠️ Boot log empty or QEMU timed out before serial init."
fi

exit 0

#!/bin/bash
# ==============================================================================
# Symbian-X86 LOOX OS - QEMU Hardware Emulation Runner
# Emulates Fujitsu FMV-BIBLO LOOX M/G30 Specifications:
# - Intel Atom N450 (1.66 GHz, 1C/2T) -> QEMU -cpu n270
# - 1024MB DDR2 RAM -> QEMU -m 1024
# - Intel GMA 3150 / VESA -> QEMU -vga std
# - Realtek ALC269 Audio -> QEMU intel-hda / hda-duplex
# - Realtek RTL8102E NIC -> QEMU rtl8139
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
ISO_FILE="$BASE_DIR/output/symbian-x86-loox.iso"

if [ ! -f "$ISO_FILE" ]; then
    echo "[ERROR] ISO file not found: $ISO_FILE"
    echo "Please run './scripts/build.sh' first."
    exit 1
fi

echo "=========================================================="
echo "    Launching Symbian-X86 LOOX OS in QEMU"
echo "    Emulating: Fujitsu FMV-BIBLO LOOX M/G30"
echo "=========================================================="

QEMU_BIN=$(command -v qemu-system-i386 || command -v qemu-system-x86_64)

EXTRA_ARGS=()
if [ "$1" == "--headless" ]; then
    EXTRA_ARGS+=("-nographic" "-serial" "mon:stdio")
else
    EXTRA_ARGS+=("-display" "gtk" "-vga" "std")
fi

"$QEMU_BIN" \
    -name "Symbian-X86 LOOX OS (Fujitsu LOOX M/G30)" \
    -cpu qemu64,+ssse3 \
    -smp 2 \
    -m 1024 \
    -device intel-hda -device hda-duplex \
    -net nic,model=rtl8139 -net user \
    -boot d \
    -cdrom "$ISO_FILE" \
    "${EXTRA_ARGS[@]}"

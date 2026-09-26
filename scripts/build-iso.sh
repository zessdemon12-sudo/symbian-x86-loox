#!/bin/bash
# ==============================================================================
# Symbian-X86 LOOX OS - Bootable Hybrid ISO Generator
# Uses Tiny Core Linux 15.x x86 Kernel & Remastered Core
# Generates: output/symbian-x86-loox.iso (Hybrid CD/USB Bootable)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
ISO_STAGING="/tmp/symbian_iso_staging"
OUTPUT_DIR="$BASE_DIR/output"
ISO_FILE="$OUTPUT_DIR/symbian-x86-loox.iso"

echo "=========================================================="
echo "    [ISO] Building Bootable Hybrid ISO for LOOX M/G30"
echo "    Engine: Tiny Core Linux 15.x x86 Remastered"
echo "=========================================================="

rm -rf "$ISO_STAGING"
mkdir -p "$ISO_STAGING"/boot/isolinux

# 1. Copy 32-bit kernel and remastered core.gz
echo "[1/4] Staging kernel and remastered core.gz..."
cp "$OUTPUT_DIR/boot/vmlinuz" "$ISO_STAGING/boot/"
cp "$OUTPUT_DIR/boot/core.gz" "$ISO_STAGING/boot/"

# 2. Setup ISOLINUX Bootloader
echo "[2/4] Setting up ISOLINUX bootloader..."
cp "$BASE_DIR/boot/isolinux"/* "$ISO_STAGING/boot/isolinux/" 2>/dev/null || true

# Stage regular TCZ application packages
if [ -d "$BASE_DIR/kernel/tinycore/tcz_apps" ]; then
    echo "[2.5/4] Staging regular TCZ application packages into ISO..."
    mkdir -p "$ISO_STAGING/cde/optional"
    [ -f "$BASE_DIR/kernel/tinycore/tcz_apps/onboot.lst" ] && cp "$BASE_DIR/kernel/tinycore/tcz_apps/onboot.lst" "$ISO_STAGING/cde/onboot.lst"
    cp -r "$BASE_DIR/kernel/tinycore/tcz_apps"/* "$ISO_STAGING/cde/optional/" 2>/dev/null || true
fi

cat <<'EOF' > "$ISO_STAGING/boot/isolinux/isolinux.cfg"
SERIAL 0 115200
UI menu.c32
PROMPT 1
TIMEOUT 40
DEFAULT live

MENU TITLE Symbian-X86 LOOX OS (Fujitsu LOOX M/G30)
MENU COLOR border       30;44   #40ffffff #a0000000 std
MENU COLOR title        1;36;44 #9033b5e5 #a0000000 std
MENU COLOR sel          7;37;40 #e0ffffff #20ffffff all
MENU COLOR unsel        37;44   #50ffffff #a0000000 std

LABEL live
  MENU LABEL ^1. Symbian-X86 LOOX OS (Tiny Core RAM Desktop)
  KERNEL /boot/vmlinuz
  INITRD /boot/core.gz
  APPEND loglevel=3 quiet waitusb=5 loop.max_loop=256 cde console=ttyS0,115200 console=tty0

LABEL vesa
  MENU LABEL ^2. Symbian-X86 LOOX OS (Safe Graphics - nomodeset/VESA)
  KERNEL /boot/vmlinuz
  INITRD /boot/core.gz
  APPEND loglevel=3 quiet waitusb=5 loop.max_loop=256 xvesa=1024x600x16 nomodeset console=ttyS0,115200 console=tty0

LABEL install
  MENU LABEL ^3. Install Symbian-X86 to Internal HDD/SSD
  KERNEL /boot/vmlinuz
  INITRD /boot/core.gz
  APPEND loglevel=3 quiet waitusb=5 loop.max_loop=256 symbian_installer=1 console=ttyS0,115200 console=tty0

LABEL debug
  MENU LABEL ^4. Symbian-X86 LOOX OS (Verbose Console & Debug Shell)
  KERNEL /boot/vmlinuz
  INITRD /boot/core.gz
  APPEND loglevel=7 debug waitusb=5 loop.max_loop=256 showapps text console=tty0 console=ttyS0,115200
EOF

# 3. Generate ISO with genisoimage
echo "[3/4] Generating ISO image with genisoimage..."
rm -f "$ISO_FILE"
genisoimage -l -J -R -V "SYMBIAN_X86" \
    -no-emul-boot -boot-load-size 4 -boot-info-table \
    -b boot/isolinux/isolinux.bin -c boot/isolinux/boot.cat \
    -o "$ISO_FILE" "$ISO_STAGING" 2>/dev/null

# 4. Make ISO Hybrid (bootable on both CD and USB)
echo "[4/4] Applying isohybrid post-processing..."
isohybrid "$ISO_FILE" 2>/dev/null || true

rm -rf "$ISO_STAGING"

echo "=========================================================="
echo "    [ISO] Successfully generated bootable Hybrid ISO:"
echo "    File: $ISO_FILE ($(du -h "$ISO_FILE" | cut -f1))"
echo "=========================================================="

#!/bin/bash
# ==============================================================================
# Symbian-X86 LOOX OS - Bootable FAT32/Syslinux USB Disk Image Generator
# Optimized for Fujitsu FMV-BIBLO LOOX M/G30 Netbook BIOS
# Produces: output/symbian-x86-loox-usb.img (MBR + FAT32 LBA + Syslinux)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$BASE_DIR/output"
USB_IMG="$OUTPUT_DIR/symbian-x86-loox-usb.img"
PART_IMG="/tmp/symbian_part_fat32.img"

echo "=========================================================="
echo "    [USB-IMG] Building Native FAT32/Syslinux USB Image"
echo "    Target: Fujitsu FMV-BIBLO LOOX M/G30"
echo "=========================================================="

rm -f "$USB_IMG" "$PART_IMG"

# 1. Create a 768 MiB FAT32 partition image (accommodates full firmware & applications)
echo "[1/6] Formatting FAT32 filesystem (768 MiB)..."
truncate -s 768M "$PART_IMG"
mkfs.vfat -F 32 -n "SYMBIAN_X86" "$PART_IMG"

# 2. Copy ALL Syslinux BIOS bootloader modules
echo "[2/6] Staging all Syslinux BIOS bootloader modules (*.c32)..."
mmd -i "$PART_IMG" ::boot 2>/dev/null || true
mmd -i "$PART_IMG" ::boot/syslinux 2>/dev/null || true
mmd -i "$PART_IMG" ::syslinux 2>/dev/null || true

for mod in /usr/lib/syslinux/modules/bios/*.c32; do
    if [ -f "$mod" ]; then
        fname=$(basename "$mod")
        mcopy -o -i "$PART_IMG" "$mod" "::$fname"
        mcopy -o -i "$PART_IMG" "$mod" "::boot/syslinux/$fname"
        mcopy -o -i "$PART_IMG" "$mod" "::syslinux/$fname"
    fi
done

# 3. Create syslinux.cfg boot menu with bulletproof fallback entries & Non-US Keyboards
cat <<'EOF' > /tmp/syslinux.cfg
SERIAL 0 115200
UI menu.c32
PROMPT 1
TIMEOUT 40
DEFAULT live

MENU TITLE Symbian-X86 LOOX OS Boot Menu (Fujitsu LOOX M/G30)
MENU COLOR border       30;44   #40ffffff #a0000000 std
MENU COLOR title        1;36;44 #9033b5e5 #a0000000 std
MENU COLOR sel          7;37;40 #e0ffffff #20ffffff all
MENU COLOR unsel        37;44   #50ffffff #a0000000 std

LABEL live
  MENU LABEL ^1. Symbian-X86 LOOX OS (Tiny Core RAM Desktop - US Keyboard)
  LINUX /boot/vmlinuz
  INITRD /boot/core.gz
  APPEND loglevel=3 quiet waitusb=5 loop.max_loop=256 console=ttyS0,115200 console=tty0

LABEL uk
  MENU LABEL ^2. Symbian-X86 LOOX OS (UK English Keyboard)
  LINUX /boot/vmlinuz
  INITRD /boot/core.gz
  APPEND loglevel=3 quiet waitusb=5 loop.max_loop=256 kmap=qwerty/uk console=ttyS0,115200 console=tty0

LABEL fr
  MENU LABEL ^3. Symbian-X86 LOOX OS (French AZERTY Keyboard)
  LINUX /boot/vmlinuz
  INITRD /boot/core.gz
  APPEND loglevel=3 quiet waitusb=5 loop.max_loop=256 kmap=azerty/fr console=ttyS0,115200 console=tty0

LABEL de
  MENU LABEL ^4. Symbian-X86 LOOX OS (German QWERTZ Keyboard)
  LINUX /boot/vmlinuz
  INITRD /boot/core.gz
  APPEND loglevel=3 quiet waitusb=5 loop.max_loop=256 kmap=qwertz/de console=ttyS0,115200 console=tty0

LABEL es
  MENU LABEL ^5. Symbian-X86 LOOX OS (Spanish Keyboard)
  LINUX /boot/vmlinuz
  INITRD /boot/core.gz
  APPEND loglevel=3 quiet waitusb=5 loop.max_loop=256 kmap=qwerty/es console=ttyS0,115200 console=tty0

LABEL jp
  MENU LABEL ^6. Symbian-X86 LOOX OS (Japanese JP106 Keyboard)
  LINUX /boot/vmlinuz
  INITRD /boot/core.gz
  APPEND loglevel=3 quiet waitusb=5 loop.max_loop=256 kmap=qwerty/jp106 console=ttyS0,115200 console=tty0

LABEL vesa
  MENU LABEL ^7. Safe Graphics (nomodeset/VESA)
  LINUX /boot/vmlinuz
  INITRD /boot/core.gz
  APPEND loglevel=3 quiet waitusb=5 loop.max_loop=256 xvesa=1024x600x16 nomodeset console=ttyS0,115200 console=tty0

LABEL install
  MENU LABEL ^8. Install Symbian-X86 to Internal HDD/SSD
  LINUX /boot/vmlinuz
  INITRD /boot/core.gz
  APPEND loglevel=3 quiet waitusb=5 loop.max_loop=256 symbian_installer=1 console=ttyS0,115200 console=tty0

LABEL debug
  MENU LABEL ^9. Verbose Console & Debug Shell
  LINUX /boot/vmlinuz
  INITRD /boot/core.gz
  APPEND loglevel=7 debug waitusb=5 loop.max_loop=256 showapps text console=ttyS0,115200 console=tty0
EOF

# Copy syslinux.cfg to all standard search locations
mcopy -o -i "$PART_IMG" /tmp/syslinux.cfg ::syslinux.cfg
mcopy -o -i "$PART_IMG" /tmp/syslinux.cfg ::boot/syslinux/syslinux.cfg
mcopy -o -i "$PART_IMG" /tmp/syslinux.cfg ::syslinux/syslinux.cfg

# 4. Copy 32-bit Tiny Core kernel and remastered core.gz
echo "[3/6] Copying 32-bit kernel and remastered core.gz..."
mcopy -o -i "$PART_IMG" "$OUTPUT_DIR/boot/vmlinuz" ::boot/vmlinuz
mcopy -o -i "$PART_IMG" "$OUTPUT_DIR/boot/core.gz" ::boot/core.gz

# Also copy to root of drive as fallback
mcopy -o -i "$PART_IMG" "$OUTPUT_DIR/boot/vmlinuz" ::vmlinuz
mcopy -o -i "$PART_IMG" "$OUTPUT_DIR/boot/core.gz" ::core.gz

# 4.5 Copy regular TCZ application packages and onboot.lst
if [ -d "$BASE_DIR/kernel/tinycore/tcz_apps" ]; then
    echo "[3.5/6] Staging regular TCZ application packages..."
    mmd -i "$PART_IMG" ::tce 2>/dev/null || true
    mmd -i "$PART_IMG" ::tce/optional 2>/dev/null || true
    
    [ -f "$BASE_DIR/kernel/tinycore/tcz_apps/onboot.lst" ] && mcopy -o -i "$PART_IMG" "$BASE_DIR/kernel/tinycore/tcz_apps/onboot.lst" ::tce/onboot.lst
    
    for f in "$BASE_DIR/kernel/tinycore/tcz_apps"/*; do
        if [ -f "$f" ]; then
            fname=$(basename "$f")
            mcopy -o -i "$PART_IMG" "$f" "::tce/optional/$fname" 2>/dev/null || true
        fi
    done
fi

# 5. Install Syslinux boot record to partition
echo "[4/6] Installing Syslinux Volume Boot Record..."
syslinux -i "$PART_IMG"

# 6. Assemble complete MBR disk image (1 MiB alignment)
echo "[5/6] Assembling Master Boot Record and DOS partition table..."
truncate -s 1M "$USB_IMG"
cat "$PART_IMG" >> "$USB_IMG"
rm -f "$PART_IMG"

parted -s "$USB_IMG" mklabel msdos
parted -s "$USB_IMG" mkpart primary fat32 2048s 100%
parted -s "$USB_IMG" set 1 boot on

# Re-inject standard syslinux MBR boot code (440 bytes)
dd if=/usr/lib/syslinux/mbr/mbr.bin of="$USB_IMG" bs=440 count=1 conv=notrunc 2>/dev/null

echo "[6/6] Verifying MBR partition layout:"
fdisk -l "$USB_IMG"

echo "=========================================================="
echo "    [USB-IMG] Built bootable FAT32 USB Image:"
echo "    File: $USB_IMG"
ls -lh "$USB_IMG"
echo "=========================================================="

#!/bin/bash
# ==============================================================================
# Symbian-X86 LOOX OS - Direct USB Flash Drive Creator
# Formats any USB flash drive as standard MBR + FAT32 with Syslinux bootloader
# Target: Fujitsu FMV-BIBLO LOOX M/G30 Netbook
# Usage: sudo ./make-usb.sh /dev/sdX
# ==============================================================================

set -e

USB_DEV="$1"

if [ -z "$USB_DEV" ]; then
    echo "=========================================================="
    echo "  Symbian-X86 LOOX OS - USB Flash Drive Creator"
    echo "=========================================================="
    echo "Usage: sudo ./make-usb.sh /dev/sdX"
    echo ""
    echo "Available removable drives:"
    lsblk -d -o NAME,SIZE,MODEL,TRAN | grep -E "usb|NAME" || true
    echo "=========================================================="
    exit 1
fi

if [ "$EUID" -ne 0 ]; then
    echo "[ERROR] This script must be run as root (use: sudo ./make-usb.sh $USB_DEV)"
    exit 1
fi

if [ ! -b "$USB_DEV" ]; then
    echo "[ERROR] Device '$USB_DEV' is not a valid block device!"
    exit 1
fi

# Safety check: make sure it's not the OS root drive
if mount | grep -q "on / type" && mount | grep "on / type" | grep -q "^$USB_DEV"; then
    echo "[CRITICAL SAFETY ERROR] $USB_DEV contains the currently mounted root system! Aborting."
    exit 1
fi

echo "=========================================================="
echo "  WARNING: ALL DATA ON $USB_DEV WILL BE COMPLETELY ERASED!"
echo "=========================================================="
lsblk "$USB_DEV"
echo -n "Type 'YES' to proceed with formatting $USB_DEV: "
read -r CONFIRM
if [ "$CONFIRM" != "YES" ]; then
    echo "Aborted by user."
    exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/output"

# Unmount any active partitions on the device
echo "[1/6] Unmounting existing partitions on $USB_DEV..."
umount ${USB_DEV}* 2>/dev/null || true

# Partition with MBR
echo "[2/6] Partitioning $USB_DEV with standard MBR..."
parted -s "$USB_DEV" mklabel msdos
parted -s "$USB_DEV" mkpart primary fat32 2048s 100%
parted -s "$USB_DEV" set 1 boot on

PART1="${USB_DEV}1"
if [ ! -b "$PART1" ]; then
    PART1="${USB_DEV}p1"
fi

# Write Syslinux MBR code
echo "[3/6] Installing Syslinux Master Boot Record to LBA 0..."
dd if=/usr/lib/syslinux/mbr/mbr.bin of="$USB_DEV" bs=440 count=1 conv=notrunc 2>/dev/null

# Format as FAT32
echo "[4/6] Formatting partition $PART1 as FAT32 (Label: SYMBIAN_X86)..."
mkfs.vfat -F 32 -n "SYMBIAN_X86" "$PART1"

# Install Syslinux Volume Boot Record
echo "[5/6] Installing Syslinux to partition..."
syslinux -i "$PART1"

# Copy files
echo "[6/6] Copying Symbian-X86 system files and Syslinux modules..."
MOUNT_DIR=$(mktemp -d)
mount "$PART1" "$MOUNT_DIR"

mkdir -p "$MOUNT_DIR/boot/syslinux" "$MOUNT_DIR/syslinux" "$MOUNT_DIR/live"

# Copy all Syslinux modules to root and search paths
for mod in /usr/lib/syslinux/modules/bios/*.c32; do
    if [ -f "$mod" ]; then
        fname=$(basename "$mod")
        cp "$mod" "$MOUNT_DIR/"
        cp "$mod" "$MOUNT_DIR/boot/syslinux/"
        cp "$mod" "$MOUNT_DIR/syslinux/"
    fi
done

cat <<'EOF' > "$MOUNT_DIR/syslinux.cfg"
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
  MENU LABEL ^1. Symbian-X86 LOOX OS (Tiny Core RAM Desktop - Auto KMS)
  LINUX /boot/vmlinuz
  INITRD /boot/core.gz
  APPEND loglevel=3 quiet waitusb=5 tce=c1 console=ttyS0,115200 console=tty0

LABEL vesa
  MENU LABEL ^2. Symbian-X86 LOOX OS (Safe Graphics - nomodeset/VESA)
  LINUX /boot/vmlinuz
  INITRD /boot/core.gz
  APPEND loglevel=3 quiet waitusb=5 xvesa=1024x600x16 nomodeset console=ttyS0,115200 console=tty0

LABEL directroot
  MENU LABEL ^3. Symbian-X86 LOOX OS (Direct Root /vmlinuz)
  LINUX /vmlinuz
  INITRD /core.gz
  APPEND loglevel=3 quiet waitusb=5 console=ttyS0,115200 console=tty0

LABEL kernelmod
  MENU LABEL ^4. Symbian-X86 LOOX OS (KERNEL Direct Mode)
  KERNEL /boot/vmlinuz
  APPEND initrd=/boot/core.gz loglevel=3 quiet waitusb=5 console=ttyS0,115200 console=tty0

LABEL install
  MENU LABEL ^5. Install Symbian-X86 to Internal HDD/SSD
  LINUX /boot/vmlinuz
  INITRD /boot/core.gz
  APPEND loglevel=3 quiet waitusb=5 symbian_installer=1 console=ttyS0,115200 console=tty0

LABEL debug
  MENU LABEL ^6. Symbian-X86 LOOX OS (Verbose Console & Debug Shell)
  LINUX /boot/vmlinuz
  INITRD /boot/core.gz
  APPEND loglevel=7 debug waitusb=5 showapps text console=ttyS0,115200 console=tty0
EOF

cp "$MOUNT_DIR/syslinux.cfg" "$MOUNT_DIR/boot/syslinux/syslinux.cfg"
cp "$MOUNT_DIR/syslinux.cfg" "$MOUNT_DIR/syslinux/syslinux.cfg"

# Copy 32-bit Tiny Core kernel and remastered core.gz
cp "$OUTPUT_DIR/boot/vmlinuz" "$MOUNT_DIR/boot/"
cp "$OUTPUT_DIR/boot/core.gz" "$MOUNT_DIR/boot/"
cp "$OUTPUT_DIR/boot/vmlinuz" "$MOUNT_DIR/"
cp "$OUTPUT_DIR/boot/core.gz" "$MOUNT_DIR/"

sync
umount "$MOUNT_DIR"
rmdir "$MOUNT_DIR"

echo "=========================================================="
echo "  🎉 USB Flash Drive creation completed successfully!"
echo "  Target: $USB_DEV"
echo "  The USB drive is now ready to boot on Fujitsu LOOX M/G30."
echo "=========================================================="

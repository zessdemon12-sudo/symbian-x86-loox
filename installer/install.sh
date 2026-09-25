#!/bin/bash
# ==============================================================================
# Symbian-X86 LOOX OS - Direct Hard Disk Installer
# Target: Fujitsu FMV-BIBLO LOOX M/G30 (160GB / 250GB SATA HDD /dev/sda)
# ==============================================================================

set -e

TARGET_DISK="${1:-/dev/sda}"
MOUNT_POINT="/mnt/symbian_target"

echo "=========================================================="
echo "    Symbian-X86 LOOX OS - Hard Disk Installation"
echo "    Target Drive: ${TARGET_DISK}"
echo "=========================================================="

if [ "$EUID" -ne 0 ]; then
    echo "[ERROR] This installer must be run as root (or inside installer user namespace)."
    exit 1
fi

if [ ! -b "$TARGET_DISK" ]; then
    echo "[ERROR] Target block device $TARGET_DISK not found!"
    exit 1
fi

echo "WARNING: ALL DATA ON $TARGET_DISK WILL BE DESTROYED!"
echo -n "Proceed with installation? (yes/no): "
read -r CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Installation aborted by user."
    exit 0
fi

echo "[1/6] Partitioning disk with MBR (BIOS boot)..."
parted -s "$TARGET_DISK" mklabel msdos
parted -s "$TARGET_DISK" mkpart primary ext4 1MiB 100%
parted -s "$TARGET_DISK" set 1 boot on

PART_ROOT="${TARGET_DISK}1"
if [ ! -b "$PART_ROOT" ]; then
    PART_ROOT="${TARGET_DISK}p1"
fi

echo "[2/6] Formatting root filesystem (ext4 with noatime)..."
mkfs.ext4 -F -O ^metadata_csum,^64bit -L "SYMBIAN_SYS" "$PART_ROOT"

echo "[3/6] Mounting target filesystem..."
mkdir -p "$MOUNT_POINT"
mount "$PART_ROOT" "$MOUNT_POINT"

echo "[4/6] Copying Symbian-X86 system files to hard disk..."
if [ -d "/run/live/medium/live" ] || [ -f "/run/live/medium/live/filesystem.squashfs" ]; then
    unsquashfs -f -d "$MOUNT_POINT" /run/live/medium/live/filesystem.squashfs
else
    # Copy from local rootfs build
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    ROOTFS_DIR="$(dirname "$SCRIPT_DIR")/rootfs/build"
    if [ -d "$ROOTFS_DIR" ]; then
        cp -a "$ROOTFS_DIR"/* "$MOUNT_POINT"/
    else
        rsync -aAXv --exclude={"/dev/*","/proc/*","/sys/*","/tmp/*","/run/*","/mnt/*","/media/*","/lost+found"} / "$MOUNT_POINT"/
    fi
fi

echo "[5/6] Configuring fstab and bootloader..."
UUID_ROOT=$(blkid -s UUID -o value "$PART_ROOT")
cat <<EOF > "$MOUNT_POINT/etc/fstab"
# Symbian-X86 LOOX OS fstab
UUID=$UUID_ROOT  /       ext4    noatime,commit=60,errors=remount-ro 0 1
tmpfs            /tmp    tmpfs   defaults,noatime,mode=1777          0 0
EOF

# Install GRUB to MBR
echo "[6/6] Installing GRUB 2 BIOS bootloader to MBR..."
grub-install --target=i386-pc --boot-directory="$MOUNT_POINT/boot" "$TARGET_DISK" || true

cat <<EOF > "$MOUNT_POINT/boot/grub/grub.cfg"
set default="0"
set timeout=3
menuentry "Symbian-X86 LOOX OS" {
    insmod ext2
    search --no-floppy --fs-uuid --set=root $UUID_ROOT
    linux /boot/vmlinuz root=UUID=$UUID_ROOT ro quiet splash loglevel=3 elevator=deadline intel_idle.max_cstate=4 pcie_aspm=force mitigations=auto,nosmt zswap.enabled=0
    initrd /boot/initrd.img
}
EOF

umount "$MOUNT_POINT"
rmdir "$MOUNT_POINT"

echo "=========================================================="
echo "    Symbian-X86 LOOX OS installation complete!"
echo "    You may now remove your installation media and reboot."
echo "=========================================================="
exit 0

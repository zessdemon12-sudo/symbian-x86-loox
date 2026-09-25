#!/bin/bash
# ==============================================================================
# Symbian-X86 LOOX OS - 32-bit i686 Initramfs Constructor
# Target: Fujitsu FMV-BIBLO LOOX M/G30 (Intel Atom N450 / USB & SATA Live Boot)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
I686_DIR="$SCRIPT_DIR/i686"
STAGING="$I686_DIR/initramfs_staging"
OUTPUT_INITRD="$BASE_DIR/output/boot/initrd.img"
KVER="6.1.0-50-686-pae"
MOD_SRC="$I686_DIR/kernel_deb/lib/modules/$KVER"

echo "=========================================================="
echo "    Building Pure 32-bit i686 Live Boot Initramfs"
echo "    Target Kernel: $KVER"
echo "=========================================================="

rm -rf "$STAGING"
mkdir -p "$STAGING"/{bin,sbin,dev,proc,sys,mnt,run/live/{rofs,cow,medium},newroot,etc,lib/modules/$KVER}

# 1. Install 32-bit static busybox
cp "$I686_DIR/bin/busybox" "$STAGING/bin/busybox"
chmod 755 "$STAGING/bin/busybox"

# Create symlinks
cd "$STAGING/bin"
for applet in sh bash mount umount mkdir rm rmdir ls cat sleep mknod switch_root \
              insmod modprobe depmod rmmod lsmod blkid grep awk sed echo chmod \
              chown find cp mv dmesg mdev readlink dirname basename cut head tail wc; do
    ln -sf busybox "$applet"
done
cd "$SCRIPT_DIR"

# Also symlink sbin tools
cd "$STAGING/sbin"
for applet in mdev modprobe insmod depmod rmmod lsmod; do
    ln -sf ../bin/busybox "$applet"
done
cd "$SCRIPT_DIR"

# 2. Create static device nodes (guarantees early boot console works on all BIOSes)
mkdir -p "$STAGING/dev"
mknod -m 600 "$STAGING/dev/console" c 5 1 2>/dev/null || true
mknod -m 666 "$STAGING/dev/null" c 1 3 2>/dev/null || true
mknod -m 666 "$STAGING/dev/zero" c 1 5 2>/dev/null || true
mknod -m 666 "$STAGING/dev/tty" c 5 0 2>/dev/null || true
mknod -m 666 "$STAGING/dev/tty0" c 4 0 2>/dev/null || true
mknod -m 666 "$STAGING/dev/tty1" c 4 1 2>/dev/null || true
mknod -m 666 "$STAGING/dev/ttyS0" c 4 64 2>/dev/null || true
mknod -m 660 "$STAGING/dev/loop0" b 7 0 2>/dev/null || true
mknod -m 660 "$STAGING/dev/loop1" b 7 1 2>/dev/null || true

# 3. Copy essential kernel driver trees preserving directory hierarchy
echo "[INITRD] Staging modular drivers (Storage, USB, SCSI, SATA, Filesystems, CRC, NLS)..."
MOD_DST="$STAGING/lib/modules/$KVER"

copy_mod_tree() {
    local src_dir="$1"
    if [ -d "$MOD_SRC/$src_dir" ]; then
        mkdir -p "$MOD_DST/$src_dir"
        cp -a "$MOD_SRC/$src_dir"/* "$MOD_DST/$src_dir/" 2>/dev/null || true
    fi
}

copy_mod_tree "kernel/block"
copy_mod_tree "kernel/crypto"
copy_mod_tree "kernel/lib"
copy_mod_tree "kernel/drivers/scsi"
copy_mod_tree "kernel/drivers/cdrom"
copy_mod_tree "kernel/drivers/ata"
copy_mod_tree "kernel/drivers/block"
copy_mod_tree "kernel/drivers/usb"
copy_mod_tree "kernel/drivers/mmc"
copy_mod_tree "kernel/drivers/virtio"
copy_mod_tree "kernel/drivers/hid"
copy_mod_tree "kernel/drivers/input"
copy_mod_tree "kernel/fs"

# Copy builtin and order metadata
cp -f "$MOD_SRC"/modules.* "$MOD_DST/" 2>/dev/null || true

# 4. Run depmod to generate clean modules.dep for the initramfs
echo "[INITRD] Generating module dependency map (depmod)..."
depmod -a -b "$STAGING" "$KVER"

# 5. Create rock-solid /init script
cat <<'INITEOF' > "$STAGING/init"
#!/bin/sh
# Symbian-X86 LOOX OS Live Boot Init Script
# Optimized for Fujitsu FMV-BIBLO LOOX M/G30 Netbook
export PATH=/bin:/sbin

# Ensure console output is directed to screen
exec < /dev/console > /dev/console 2>&1

# Mount virtual filesystems
mount -t devtmpfs devtmpfs /dev 2>/dev/null || true
mount -t proc proc /proc 2>/dev/null || true
mount -t sysfs sysfs /sys 2>/dev/null || true
mount -t tmpfs -o mode=0755 tmpfs /run 2>/dev/null || true

# Recreate essential runtime directories inside fresh /run tmpfs
mkdir -p /run/live/medium /run/live/rofs /run/live/cow /newroot /mnt/check /dev/pts /dev/shm
mount -t devpts devpts /dev/pts 2>/dev/null || true

echo ""
echo "=========================================================="
echo "    Symbian-X86 LOOX OS - Live Boot Loader"
echo "    Target: Fujitsu FMV-BIBLO LOOX M/G30"
echo "=========================================================="

echo "[INIT] Loading storage, USB, SATA, NLS, and filesystem drivers..."
for m in nls_base nls_cp437 nls_iso8859-1 nls_utf8 nls_ascii \
         scsi_mod sd_mod sr_mod cdrom \
         libata libahci ahci ata_piix ata_generic pata_legacy pata_generic \
         virtio virtio_ring virtio_pci virtio_blk virtio_scsi \
         usb-common usbcore ehci-hcd ehci-pci uhci-hcd ohci-hcd xhci-hcd xhci-pci \
         usbhid hid-generic \
         usb-storage uas \
         mmc_core mmc_block sdhci sdhci-pci \
         fat vfat exfat isofs \
         loop squashfs overlay ext4; do
    modprobe -q "$m" 2>/dev/null || true
done

# Rescan hardware after driver loading
mdev -s 2>/dev/null || true
sleep 2
mdev -s 2>/dev/null || true

echo -n "[INIT] Detecting boot medium (USB / SATA / CD / SD)"
FOUND_DEV=""
FOUND_FSTYPE=""

for attempt in $(seq 1 20); do
    echo -n "."
    mdev -s 2>/dev/null || true
    
    # 1. Check all partition block devices in /sys/class/block
    for bpath in /sys/class/block/*; do
        bname=$(basename "$bpath")
        case "$bname" in
            loop*|ram*|dm-*) continue ;;
        esac
        
        dev="/dev/$bname"
        if [ ! -b "$dev" ]; then
            dev_maj_min=$(cat "$bpath/dev" 2>/dev/null || true)
            if [ -n "$dev_maj_min" ]; then
                maj=$(echo "$dev_maj_min" | cut -d: -f1)
                min=$(echo "$dev_maj_min" | cut -d: -f2)
                mknod -m 660 "$dev" b "$maj" "$min" 2>/dev/null || true
            fi
        fi
        
        if [ -b "$dev" ]; then
            for fstype in vfat iso9660 ext4 auto; do
                if [ "$fstype" = "auto" ]; then
                    MNT_OPT="-o ro"
                else
                    MNT_OPT="-t $fstype -o ro"
                fi
                
                if mount $MNT_OPT "$dev" /mnt/check 2>/dev/null; then
                    if [ -f "/mnt/check/live/filesystem.squashfs" ] || [ -f "/mnt/check/filesystem.squashfs" ]; then
                        FOUND_DEV="$dev"
                        FOUND_FSTYPE="$fstype"
                        umount /mnt/check 2>/dev/null || true
                        break 3
                    fi
                    umount /mnt/check 2>/dev/null || true
                fi
            done
        fi
    done
    sleep 1
done

echo ""
if [ -z "$FOUND_DEV" ]; then
    echo "=========================================================="
    echo " [ERROR] Symbian-X86 live medium not found!"
    echo " Available block devices:"
    cat /proc/partitions 2>/dev/null || true
    echo " Dropping to interactive rescue shell..."
    echo "=========================================================="
    while true; do
        /bin/sh
        sleep 1
    done
fi

echo "[INIT] Live medium found on $FOUND_DEV"
echo "[INIT] Mounting live filesystem overlay..."

# Mount device to /run/live/medium
if [ "$FOUND_FSTYPE" = "auto" ]; then
    mount -o ro "$FOUND_DEV" /run/live/medium 2>/dev/null || true
else
    mount -t "$FOUND_FSTYPE" -o ro "$FOUND_DEV" /run/live/medium 2>/dev/null || true
fi

# Mount SquashFS read-only rootfs
SQUASH_FILE="/run/live/medium/live/filesystem.squashfs"
if [ ! -f "$SQUASH_FILE" ]; then
    SQUASH_FILE="/run/live/medium/filesystem.squashfs"
fi

mount -t squashfs -o ro,loop "$SQUASH_FILE" /run/live/rofs

# Create writable tmpfs overlay (COW - Copy On Write)
mount -t tmpfs -o mode=0755 tmpfs /run/live/cow
mkdir -p /run/live/cow/rw /run/live/cow/work /newroot
mount -t overlay overlay -o lowerdir=/run/live/rofs,upperdir=/run/live/cow/rw,workdir=/run/live/cow/work /newroot

# Mount virtual filesystems into new root
mkdir -p /newroot/run/live/medium /newroot/run/live/rofs /newroot/run/live/cow /newroot/dev /newroot/proc /newroot/sys /newroot/run
mount --move /run/live/medium /newroot/run/live/medium 2>/dev/null || true
mount --move /run/live/rofs /newroot/run/live/rofs 2>/dev/null || true
mount --move /run/live/cow /newroot/run/live/cow 2>/dev/null || true
mount --move /dev /newroot/dev 2>/dev/null || true
mount --move /proc /newroot/proc 2>/dev/null || true
mount --move /sys /newroot/sys 2>/dev/null || true
mount --move /run /newroot/run 2>/dev/null || true

echo "[INIT] System ready. Switching to Symbian-X86 Desktop..."
echo "=========================================================="

# Handover execution to init
if [ -x /newroot/sbin/init ]; then
    exec switch_root /newroot /sbin/init
elif [ -x /newroot/bin/busybox ]; then
    exec switch_root /newroot /bin/busybox init
elif [ -x /newroot/bin/sh ]; then
    exec switch_root /newroot /bin/sh
fi

echo "[ERROR] Fallback rescue loop activated."
while true; do
    /bin/sh
    sleep 1
done
INITEOF

chmod 755 "$STAGING/init"

# 6. Pack into CPIO archive
echo "[INITRD] Compressing initramfs into $OUTPUT_INITRD..."
mkdir -p "$(dirname "$OUTPUT_INITRD")"
(cd "$STAGING" && find . | cpio -H newc -o | gzip -9 > "$OUTPUT_INITRD")

echo "=========================================================="
echo "    [INITRD] Built pure 32-bit i686 Initramfs successfully!"
echo "    Output: $OUTPUT_INITRD"
ls -lh "$OUTPUT_INITRD"
echo "=========================================================="

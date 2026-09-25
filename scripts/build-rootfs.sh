#!/bin/bash
# ==============================================================================
# Symbian-X86 LOOX OS - Root Filesystem Assembler & Squashfs Generator
# Desktop Environment: LXQt (Symbian Belle Netbook Edition)
# Target: Fujitsu FMV-BIBLO LOOX M/G30 (Intel Atom N450 / 32-bit i686)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
STAGING="$BASE_DIR/output/rootfs_staging"
OUTPUT_LIVE="$BASE_DIR/output/live"
I686_DIR="$BASE_DIR/kernel/i686"
BUSYBOX_BIN="$I686_DIR/bin/busybox"

echo "=========================================================="
echo "    [ROOTFS] Building LXQt Symbian-X86 Root Filesystem"
echo "    Target: Fujitsu FMV-BIBLO LOOX M/G30 (Atom N450)"
echo "    Desktop Environment: LXQt + Openbox (Symbian Belle Theme)"
echo "=========================================================="

rm -rf "$STAGING"
mkdir -p "$STAGING"/{bin,sbin,etc/init.d,etc/xdg/{lxqt,pcmanfm-qt/lxqt,openbox,autostart},usr/bin,usr/sbin,usr/share/{applications,icons,backgrounds,themes,lxqt/themes/Symbian-Belle},opt/symbian/{bin,sys_drive/sys/bin,rom,packages,resource/apps,system/data/cenrep,private},var/{run,log,lib/alsa},tmp,dev/pts,dev/shm,proc,sys,mnt,media,run,home/symbian/Documents}
mkdir -p "$OUTPUT_LIVE"

# 1. Install Authentic 32-bit Static BusyBox ELF Binary
echo "[1/8] Installing authentic 32-bit BusyBox executable..."
if [ ! -f "$BUSYBOX_BIN" ]; then
    echo "[ERROR] 32-bit BusyBox binary not found at $BUSYBOX_BIN!"
    exit 1
fi
cp "$BUSYBOX_BIN" "$STAGING/bin/busybox"
chmod 755 "$STAGING/bin/busybox"

# Create standard BusyBox applet symlinks
cd "$STAGING/bin"
for applet in sh ash bash mount umount mkdir rm rmdir ls cat sleep mknod switch_root \
              grep egrep fgrep awk sed echo chmod chown find cp mv dmesg mdev ps kill \
              killall top df du free date uname which sync touch more less vi hostname \
              tar gzip gunzip zcat bzcat xzcat clear reset test [ [[ cut head tail wc tr; do
    ln -sf busybox "$applet"
done

cd "$STAGING/sbin"
for applet in init reboot halt poweroff ifconfig route ip blkid getty mdev depmod insmod modprobe rmmod lsmod; do
    ln -sf ../bin/busybox "$applet"
done

cd "$STAGING/usr/bin"
for applet in env time sort uniq wc id whoami tee seq basename dirname; do
    ln -sf ../../bin/busybox "$applet"
done

cd "$STAGING/usr/sbin"
for applet in chroot rfkill; do
    ln -sf ../../bin/busybox "$applet"
done
cd "$SCRIPT_DIR"

# 2. System Init Configuration (/etc/inittab and /etc/init.d/rcS)
echo "[2/8] Creating standard SysV/Busybox init configuration..."
cat <<'EOF' > "$STAGING/etc/inittab"
# /etc/inittab for Symbian-X86 LOOX OS (LXQt Desktop Edition)
::sysinit:/etc/init.d/rcS
::askfirst:/opt/symbian/bin/symbian-session
::ctrlaltdel:/sbin/reboot
::shutdown:/bin/umount -a -r
::restart:/sbin/init
tty1::respawn:/opt/symbian/bin/symbian-session
ttyS0::respawn:/opt/symbian/bin/symbian-session
EOF

cat <<'EOF' > "$STAGING/etc/init.d/rcS"
#!/bin/sh
# Symbian-X86 LOOX OS System Startup Script (LXQt Desktop Edition)
export PATH=/bin:/sbin:/usr/bin:/usr/sbin:/opt/symbian/bin
export HOME=/home/symbian
export USER=symbian
export TERM=linux
export XDG_CURRENT_DESKTOP=LXQt
export QT_QPA_PLATFORMTHEME=lxqt

# 1. Mount virtual and temporary filesystems
mount -t proc proc /proc 2>/dev/null || true
mount -t sysfs sysfs /sys 2>/dev/null || true
mount -t devpts devpts /dev/pts 2>/dev/null || true
mount -t tmpfs -o mode=0777 tmpfs /tmp 2>/dev/null || true
mount -t tmpfs -o mode=0755 tmpfs /run 2>/dev/null || true
mkdir -p /dev/shm /var/run /var/log /home/symbian/.config/lxqt
mount -t tmpfs -o mode=0777 tmpfs /dev/shm 2>/dev/null || true

# 2. Dynamic device population
if [ -f /proc/sys/kernel/hotplug ]; then
    echo /sbin/mdev > /proc/sys/kernel/hotplug 2>/dev/null || true
fi
mdev -s 2>/dev/null || true

# 3. Hostname & Loopback Network
hostname loox-symbian 2>/dev/null || true
ifconfig lo 127.0.0.1 up 2>/dev/null || true

# 4. Atom N450 Power Optimizations
if [ -x /opt/symbian/bin/loox-power-opt.sh ]; then
    /opt/symbian/bin/loox-power-opt.sh 2>/dev/null || true
fi

# 5. Symbian Drives mapping
mkdir -p /home/symbian /media /opt/symbian/rom /opt/symbian/sys_drive/sys/bin
ln -sfn /home/symbian /C: 2>/dev/null || true
ln -sfn /media /D: 2>/dev/null || true
ln -sfn /opt/symbian/rom /Z: 2>/dev/null || true

# Copy default LXQt user configurations if not present
if [ ! -f /home/symbian/.config/lxqt/lxqt.conf ]; then
    mkdir -p /home/symbian/.config/lxqt /home/symbian/.config/pcmanfm-qt/lxqt
    cp -r /etc/xdg/lxqt/* /home/symbian/.config/lxqt/ 2>/dev/null || true
    cp -r /etc/xdg/pcmanfm-qt/* /home/symbian/.config/pcmanfm-qt/ 2>/dev/null || true
    chown -R 1000:1000 /home/symbian 2>/dev/null || true
fi

echo ""
echo "=========================================================="
echo "    Symbian-X86 LOOX OS (LXQt Belle Netbook Edition)"
echo "    Fujitsu FMV-BIBLO LOOX M/G30"
echo "=========================================================="
echo "    Desktop: LXQt + Openbox (Symbian Belle Style)"
echo "    Drives: C: (System/Home), D: (Removable), Z: (ROM)"
echo "    Architecture: 32-bit x86 (i686 PAE Optimized)"
echo "=========================================================="
echo ""
EOF
chmod 755 "$STAGING/etc/init.d/rcS"

# 3. Create Interactive Symbian Session Launcher
cat <<'EOF' > "$STAGING/opt/symbian/bin/symbian-session"
#!/bin/sh
export PATH=/bin:/sbin:/usr/bin:/usr/sbin:/opt/symbian/bin
export HOME=/home/symbian
export USER=symbian
export TERM=linux
export XDG_CURRENT_DESKTOP=LXQt
export QT_QPA_PLATFORMTHEME=lxqt
cd /home/symbian

echo "Welcome to Symbian-X86 LOOX OS (LXQt Edition)!"
echo "Type 'startlxqt' or 'help' to begin."
echo ""

while true; do
    /bin/sh
    sleep 1
done
EOF
chmod 755 "$STAGING/opt/symbian/bin/symbian-session"

# 4. Standard Configuration Files
cat <<EOF > "$STAGING/etc/passwd"
root:x:0:0:root:/home/symbian:/bin/sh
symbian:x:1000:1000:Symbian User:/home/symbian:/bin/sh
EOF

cat <<EOF > "$STAGING/etc/group"
root:x:0:
symbian:x:1000:
audio:x:29:symbian
video:x:44:symbian
EOF

cat <<EOF > "$STAGING/etc/fstab"
proc        /proc           proc    defaults        0   0
sysfs       /sys            sysfs   defaults        0   0
devpts      /dev/pts        devpts  gid=5,mode=620  0   0
tmpfs       /tmp            tmpfs   defaults        0   0
tmpfs       /run            tmpfs   defaults        0   0
tmpfs       /dev/shm        tmpfs   defaults        0   0
EOF

cat <<EOF > "$STAGING/etc/os-release"
NAME="Symbian-X86 LOOX OS"
VERSION="1.0 LTS (Symbian Belle LXQt Edition)"
ID=symbian-x86-loox
ID_LIKE=debian
PRETTY_NAME="Symbian-X86 LOOX OS LXQt (Fujitsu FMV-BIBLO LOOX M/G30)"
VERSION_ID="1.0"
HOME_URL="https://github.com/symbian-x86/loox"
SUPPORT_URL="https://github.com/symbian-x86/loox"
BUG_REPORT_URL="https://github.com/symbian-x86/loox/issues"
EOF

# 5. Installing Hardware Drivers & Power Optimization
echo "[5/8] Installing Hardware Drivers & Power Optimization..."
mkdir -p "$STAGING/etc/X11/xorg.conf.d"
cp "$BASE_DIR/drivers/graphics/20-intel.conf" "$STAGING/etc/X11/xorg.conf.d/" 2>/dev/null || true

mkdir -p "$STAGING/var/lib/alsa"
cp "$BASE_DIR/drivers/audio/asound.state" "$STAGING/var/lib/alsa/" 2>/dev/null || true

cp "$BASE_DIR/drivers/power/loox-power-opt.sh" "$STAGING/opt/symbian/bin/" 2>/dev/null || true
chmod +x "$STAGING/opt/symbian/bin/loox-power-opt.sh" 2>/dev/null || true

# 6. Installing LXQt Desktop Environment, Themes, Icons, and Wallpaper
echo "[6/8] Installing LXQt Desktop (Symbian Belle Theme & Layout)..."
cp "$BASE_DIR/desktop/lxqt/lxqt.conf" "$STAGING/etc/xdg/lxqt/"
cp "$BASE_DIR/desktop/lxqt/session.conf" "$STAGING/etc/xdg/lxqt/"
cp "$BASE_DIR/desktop/lxqt/panel.conf" "$STAGING/etc/xdg/lxqt/"

mkdir -p "$STAGING/etc/xdg/pcmanfm-qt/lxqt"
cp "$BASE_DIR/desktop/lxqt/pcmanfm-qt/lxqt/settings.conf" "$STAGING/etc/xdg/pcmanfm-qt/lxqt/"

# Install LXQt Symbian Belle Theme
mkdir -p "$STAGING/usr/share/lxqt/themes/Symbian-Belle"
cp "$BASE_DIR/desktop/lxqt/themes/Symbian-Belle/lxqt-panel.qss" "$STAGING/usr/share/lxqt/themes/Symbian-Belle/"
cp "$BASE_DIR/desktop/lxqt/themes/Symbian-Belle/lxqt-runner.qss" "$STAGING/usr/share/lxqt/themes/Symbian-Belle/"
cp "$BASE_DIR/desktop/lxqt/themes/Symbian-Belle/lxqt-notificationd.qss" "$STAGING/usr/share/lxqt/themes/Symbian-Belle/"

mkdir -p "$STAGING/usr/share/themes/Symbian-Belle/openbox-3"
cp "$BASE_DIR/desktop/lxqt/themes/Symbian-Belle/openbox-3/themerc" "$STAGING/usr/share/themes/Symbian-Belle/openbox-3/"
mkdir -p "$STAGING/etc/xdg/openbox"
cp "$BASE_DIR/desktop/lxde/openbox/rc.xml" "$STAGING/etc/xdg/openbox/" 2>/dev/null || true

mkdir -p "$STAGING/usr/share/icons/Symbian-Belle/apps"
cp -r "$BASE_DIR/desktop/lxde/icons/Symbian-Belle"/* "$STAGING/usr/share/icons/Symbian-Belle/" 2>/dev/null || true
cp "$BASE_DIR/desktop/lxde/wallpaper/symbian-loox-bg.png" "$STAGING/usr/share/backgrounds/" 2>/dev/null || true

# 7. Installing Symbian Compatibility Framework & Package Tools
echo "[7/8] Installing Symbian Framework & Applications..."
mkdir -p "$STAGING/opt/symbian/lib"
cp -r "$BASE_DIR/symbian" "$STAGING/opt/symbian/" 2>/dev/null || true
cp "$BASE_DIR/symbian/package/sis_installer.py" "$STAGING/usr/bin/symbian-pkg" 2>/dev/null || true
cp "$BASE_DIR/symbian/package/sis_gui.py" "$STAGING/usr/bin/symbian-pkg-gui" 2>/dev/null || true
cp "$BASE_DIR/symbian/package/symbian_run.py" "$STAGING/usr/bin/symbian-run" 2>/dev/null || true
chmod +x "$STAGING/usr/bin/symbian-pkg" "$STAGING/usr/bin/symbian-pkg-gui" "$STAGING/usr/bin/symbian-run" 2>/dev/null || true

cp "$BASE_DIR/applications/notes/notes.py" "$STAGING/usr/bin/symbian-notes" 2>/dev/null || true
cp "$BASE_DIR/applications/calculator/calculator.py" "$STAGING/usr/bin/symbian-calc" 2>/dev/null || true
cp "$BASE_DIR/applications/filebrowser/filebrowser.py" "$STAGING/usr/bin/symbian-filebrowser" 2>/dev/null || true
cp "$BASE_DIR/applications/pkgmanager/appmanager.py" "$STAGING/usr/bin/symbian-appmanager" 2>/dev/null || true
cp "$BASE_DIR/installer/loox-installer-gui.py" "$STAGING/usr/bin/symbian-installer" 2>/dev/null || true
chmod +x "$STAGING/usr/bin/symbian-notes" "$STAGING/usr/bin/symbian-calc" "$STAGING/usr/bin/symbian-filebrowser" "$STAGING/usr/bin/symbian-appmanager" "$STAGING/usr/bin/symbian-installer" 2>/dev/null || true

# Desktop shortcuts
cat <<EOF > "$STAGING/usr/share/applications/symbian-notes.desktop"
[Desktop Entry]
Type=Application
Name=Symbian Notes
Comment=Lightweight Note Taking
Exec=symbian-notes
Icon=/usr/share/icons/Symbian-Belle/apps/notes.png
Terminal=false
Categories=Symbian;Utility;TextEditor;
EOF

cat <<EOF > "$STAGING/usr/share/applications/symbian-calc.desktop"
[Desktop Entry]
Type=Application
Name=Symbian Calculator
Comment=Standard Calculator
Exec=symbian-calc
Icon=/usr/share/icons/Symbian-Belle/apps/calculator.png
Terminal=false
Categories=Symbian;Utility;Calculator;
EOF

cat <<EOF > "$STAGING/usr/share/applications/symbian-files.desktop"
[Desktop Entry]
Type=Application
Name=Symbian File Manager
Comment=Browse C:, D:, E:, Z: Drives
Exec=symbian-filebrowser
Icon=/usr/share/icons/Symbian-Belle/apps/filemanager.png
Terminal=false
Categories=Symbian;System;FileManager;
EOF

cat <<EOF > "$STAGING/usr/share/applications/symbian-pkg-manager.desktop"
[Desktop Entry]
Type=Application
Name=Symbian Software Center
Comment=Manage Symbian SIS Packages & Running Tasks
Exec=symbian-appmanager
Icon=/usr/share/icons/Symbian-Belle/apps/symbian-pkg.png
Terminal=false
Categories=Symbian;System;PackageManager;
EOF

cat <<EOF > "$STAGING/usr/share/applications/symbian-os-installer.desktop"
[Desktop Entry]
Type=Application
Name=Install Symbian-X86 LOOX OS
Comment=Install to Internal Hard Drive
Exec=symbian-installer
Icon=/usr/share/icons/Symbian-Belle/apps/sysmanager.png
Terminal=false
Categories=System;
EOF

# Staging sample packages
cp -r "$BASE_DIR/packages"/* "$STAGING/opt/symbian/packages/" 2>/dev/null || true

# Overlays
if [ -d "$BASE_DIR/rootfs/overlays" ]; then
    cp -r "$BASE_DIR/rootfs/overlays"/* "$STAGING/" 2>/dev/null || true
fi

# 8. Compressing into filesystem.squashfs
echo "[8/8] Compressing into filesystem.squashfs..."
rm -f "$OUTPUT_LIVE/filesystem.squashfs"
mksquashfs "$STAGING" "$OUTPUT_LIVE/filesystem.squashfs" -comp xz -noappend

echo "=========================================================="
echo "    [ROOTFS] Built LXQt filesystem.squashfs successfully!"
ls -lh "$OUTPUT_LIVE/filesystem.squashfs"
echo "=========================================================="

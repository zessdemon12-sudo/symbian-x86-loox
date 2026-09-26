#!/bin/bash
# ==============================================================================
# Symbian-X86 LOOX OS - Tiny Core Linux Remastering Engine
# Re-architects Tiny Core Linux 15.x (x86 32-bit) with:
#  - Symbian API C++ runtime and Python framework
#  - SIS/SISX package management system
#  - Symbian native applications (Notes, Calc, File Browser, App Manager, Installer)
#  - Symbian Belle theme, squircle icons, and wallpaper
#  - LXQt & Openbox desktop environments
#  - Fujitsu FMV-BIBLO LOOX M/G30 Netbook hardware & power optimizations
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
KERNEL_DIR="$BASE_DIR/kernel/tinycore"
OUTPUT_BOOT="$BASE_DIR/output/boot"
STAGING="/tmp/symbian_tinycore_remaster"

echo "=========================================================="
echo "    [REMASTER] Remastering Tiny Core Linux 15.x x86"
echo "    Target: Fujitsu FMV-BIBLO LOOX M/G30 (Intel Atom N450)"
echo "    Desktop: LXQt & Openbox (Symbian Belle Netbook Theme)"
echo "=========================================================="

mkdir -p "$OUTPUT_BOOT"

if [ ! -f "$KERNEL_DIR/core.gz" ] || [ ! -f "$KERNEL_DIR/vmlinuz" ]; then
    echo "[ERROR] Tiny Core Linux base files not found in $KERNEL_DIR!"
    exit 1
fi

# 1. Clean Staging Area
echo "[1/9] Unpacking Tiny Core Linux core.gz rootfs..."
chmod -R u+w "$STAGING" 2>/dev/null || true
rm -rf "$STAGING"
mkdir -p "$STAGING"

cd "$STAGING"
fakeroot sh -c "zcat '$KERNEL_DIR/core.gz' | cpio -idmu" 2>/dev/null
cd "$SCRIPT_DIR"

# Create /dev/loop-control and 256 loop block device nodes
echo "[1.5/9] Creating 256 loop device nodes and loop-control..."
fakeroot sh -c "
    mknod -m 660 '$STAGING/dev/loop-control' c 10 237 2>/dev/null || true
    for i in \$(seq 0 255); do
        mknod -m 660 '$STAGING/dev/loop\$i' b 7 \$i 2>/dev/null || true
    done
    chgrp 50 '$STAGING/dev/loop'* 2>/dev/null || true
"

# Patch tc-config to load loop with max_loop=256 and guarantee loop nodes at boot
sed -i 's/modprobe loop 2>\/dev\/null/modprobe loop max_loop=256 2>\/dev\/null\n[ -c \/dev\/loop-control ] || mknod -m 660 \/dev\/loop-control c 10 237 2>\/dev\/null\nfor i in \$(seq 0 255); do [ -b \/dev\/loop\$i ] || mknod -m 660 \/dev\/loop\$i b 7 \$i 2>\/dev\/null; done\nchgrp staff \/dev\/loop* 2>\/dev\/null\nchmod 660 \/dev\/loop* 2>\/dev\/null/' "$STAGING/etc/init.d/tc-config"

# 2. Unpack Storage & Hardware Kernel Modules
if [ -f "$KERNEL_DIR/modules.gz" ]; then
    echo "[2/9] Integrating storage and filesystem kernel modules..."
    cd "$STAGING"
    fakeroot sh -c "zcat '$KERNEL_DIR/modules.gz' | cpio -idmu" 2>/dev/null || true
    cd "$SCRIPT_DIR"
fi

# 3. Unpack GUI Extensions from Tiny Core ISO
echo "[3/9] Integrating X11 and desktop GUI extensions..."
ISO_TCZ_DIR="/tmp/tc_iso_extract/cde/optional"
if [ ! -d "$ISO_TCZ_DIR" ]; then
    mkdir -p /tmp/tc_iso_extract
    7z x "$KERNEL_DIR/TinyCore-15.0.iso" -o/tmp/tc_iso_extract >/dev/null 2>&1
fi

for tcz in "$ISO_TCZ_DIR"/*.tcz; do
    if [ -f "$tcz" ]; then
        unsquashfs -f -d "$STAGING" "$tcz" >/dev/null 2>&1 || true
    fi
done

# 4. Unpack Python 3.9, Tkinter, Openbox, and Intel Drivers
echo "[4/9] Integrating Python 3.9, Tkinter, Openbox, and Intel graphics..."
for tcz in "$KERNEL_DIR/tcz_base"/*.tcz; do
    if [ -f "$tcz" ]; then
        unsquashfs -f -d "$STAGING" "$tcz" >/dev/null 2>&1 || true
    fi
done

# Extract Python 3.9 files.tar.gz if present
if [ -f "$STAGING/usr/local/share/python3.9/files/files.tar.gz" ]; then
    tar -xzf "$STAGING/usr/local/share/python3.9/files/files.tar.gz" -C "$STAGING" 2>/dev/null || true
fi

# Configure Python search path for Symbian framework
mkdir -p "$STAGING/usr/local/lib/python3.9/site-packages"
echo "/opt" > "$STAGING/usr/local/lib/python3.9/site-packages/symbian.pth"

# Create application symlinks
mkdir -p "$STAGING/usr/bin" "$STAGING/usr/local/bin"
ln -sf /usr/local/bin/python3.9 "$STAGING/usr/bin/python3"
ln -sf /usr/local/bin/python3.9 "$STAGING/usr/bin/python"
ln -sf /usr/local/bin/python3.9 "$STAGING/usr/local/bin/python3"
ln -sf /usr/local/bin/python3.9 "$STAGING/usr/local/bin/python"
[ -f "$STAGING/usr/local/bin/openbox" ] && ln -sf /usr/local/bin/openbox "$STAGING/usr/bin/openbox"
for app in dillo leafpad gpicview flaxpdf lxtask htop lxterminal lxappearance lxrandr fluff flcalc flviewer flburn aterm; do
    [ -f "$STAGING/usr/local/bin/$app" ] && ln -sf "/usr/local/bin/$app" "$STAGING/usr/bin/$app" 2>/dev/null || true
done

# Install TrueType fonts for GUI & Tkinter
mkdir -p "$STAGING/usr/share/fonts/truetype/dejavu" "$STAGING/usr/local/share/fonts" "$STAGING/etc/fonts"
cp /usr/share/fonts/truetype/dejavu/DejaVuSans*.ttf "$STAGING/usr/share/fonts/truetype/dejavu/" 2>/dev/null || true
cp /usr/share/fonts/truetype/dejavu/DejaVuSans*.ttf "$STAGING/usr/local/share/fonts/" 2>/dev/null || true
ln -sf /usr/local/etc/fonts/fonts.conf "$STAGING/etc/fonts/fonts.conf" 2>/dev/null || true

# 5. Integrate Symbian Compatibility Layer
echo "[5/9] Installing Symbian Framework & SIS Package Manager..."
mkdir -p "$STAGING/opt/symbian/lib" "$STAGING/opt/symbian/bin" "$STAGING/opt/symbian/packages" "$STAGING/opt/symbian/rom"
cp -r "$BASE_DIR/symbian"/* "$STAGING/opt/symbian/" 2>/dev/null || true
touch "$STAGING/opt/symbian/__init__.py" "$STAGING/opt/symbian/package/__init__.py" "$STAGING/opt/symbian/api/__init__.py"

# Symbian Package CLI & GUI Tools
cp "$BASE_DIR/symbian/package/sis_installer.py" "$STAGING/usr/bin/symbian-pkg" 2>/dev/null || true
cp "$BASE_DIR/symbian/package/sis_gui.py" "$STAGING/usr/bin/symbian-pkg-gui" 2>/dev/null || true
cp "$BASE_DIR/symbian/package/symbian_run.py" "$STAGING/usr/bin/symbian-run" 2>/dev/null || true
chmod +x "$STAGING/usr/bin/symbian-pkg" "$STAGING/usr/bin/symbian-pkg-gui" "$STAGING/usr/bin/symbian-run" 2>/dev/null || true

# Symbian Native Applications
cp "$BASE_DIR/applications/notes/notes.py" "$STAGING/usr/bin/symbian-notes" 2>/dev/null || true
cp "$BASE_DIR/applications/calculator/calculator.py" "$STAGING/usr/bin/symbian-calc" 2>/dev/null || true
cp "$BASE_DIR/applications/filebrowser/filebrowser.py" "$STAGING/usr/bin/symbian-filebrowser" 2>/dev/null || true
cp "$BASE_DIR/applications/pkgmanager/appmanager.py" "$STAGING/usr/bin/symbian-appmanager" 2>/dev/null || true
cp "$BASE_DIR/installer/loox-installer-gui.py" "$STAGING/usr/bin/symbian-installer" 2>/dev/null || true
chmod +x "$STAGING/usr/bin/symbian-notes" "$STAGING/usr/bin/symbian-calc" "$STAGING/usr/bin/symbian-filebrowser" "$STAGING/usr/bin/symbian-appmanager" "$STAGING/usr/bin/symbian-installer" 2>/dev/null || true

# Copy sample packages
cp -r "$BASE_DIR/packages"/* "$STAGING/opt/symbian/packages/" 2>/dev/null || true

# 6. Install Desktop Environments (LXQt & Openbox) and Symbian Belle Theme
echo "[6/9] Installing LXQt, Openbox, and Symbian Belle Theme..."
mkdir -p "$STAGING/etc/xdg/lxqt" "$STAGING/etc/xdg/pcmanfm-qt/lxqt" "$STAGING/etc/xdg/openbox"
cp "$BASE_DIR/desktop/lxqt/lxqt.conf" "$STAGING/etc/xdg/lxqt/" 2>/dev/null || true
cp "$BASE_DIR/desktop/lxqt/session.conf" "$STAGING/etc/xdg/lxqt/" 2>/dev/null || true
cp "$BASE_DIR/desktop/lxqt/panel.conf" "$STAGING/etc/xdg/lxqt/" 2>/dev/null || true
cp "$BASE_DIR/desktop/lxqt/pcmanfm-qt/lxqt/settings.conf" "$STAGING/etc/xdg/pcmanfm-qt/lxqt/" 2>/dev/null || true
cp "$BASE_DIR/desktop/lxde/openbox/rc.xml" "$STAGING/etc/xdg/openbox/rc.xml" 2>/dev/null || true

# Themes, Icons, and Wallpaper
mkdir -p "$STAGING/usr/share/lxqt/themes/Symbian-Belle"
cp "$BASE_DIR/desktop/lxqt/themes/Symbian-Belle/lxqt-panel.qss" "$STAGING/usr/share/lxqt/themes/Symbian-Belle/" 2>/dev/null || true
cp "$BASE_DIR/desktop/lxqt/themes/Symbian-Belle/lxqt-runner.qss" "$STAGING/usr/share/lxqt/themes/Symbian-Belle/" 2>/dev/null || true
cp "$BASE_DIR/desktop/lxqt/themes/Symbian-Belle/lxqt-notificationd.qss" "$STAGING/usr/share/lxqt/themes/Symbian-Belle/" 2>/dev/null || true

mkdir -p "$STAGING/usr/share/themes/Symbian-Belle/openbox-3"
cp "$BASE_DIR/desktop/lxqt/themes/Symbian-Belle/openbox-3/themerc" "$STAGING/usr/share/themes/Symbian-Belle/openbox-3/" 2>/dev/null || true

mkdir -p "$STAGING/usr/share/icons/Symbian-Belle" "$STAGING/usr/share/backgrounds"
cp -r "$BASE_DIR/desktop/lxde/icons/Symbian-Belle"/* "$STAGING/usr/share/icons/Symbian-Belle/" 2>/dev/null || true
cp "$BASE_DIR/desktop/lxde/wallpaper/symbian-loox-bg.png" "$STAGING/usr/share/backgrounds/" 2>/dev/null || true

# Desktop Entries
mkdir -p "$STAGING/usr/share/applications" "$STAGING/etc/skel/Desktop"
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

cat <<EOF > "$STAGING/usr/share/applications/symbian-browser.desktop"
[Desktop Entry]
Type=Application
Name=Web Browser (Dillo)
Comment=Fast, Lightweight Web Browser
Exec=dillo
Icon=/usr/share/icons/Symbian-Belle/apps/browser.png
Terminal=false
Categories=Network;WebBrowser;
EOF

cat <<EOF > "$STAGING/usr/share/applications/symbian-leafpad.desktop"
[Desktop Entry]
Type=Application
Name=Leafpad Text Editor
Comment=Simple, Lightweight Text Editor
Exec=leafpad
Icon=/usr/share/icons/Symbian-Belle/apps/leafpad.png
Terminal=false
Categories=Utility;TextEditor;
EOF

cat <<EOF > "$STAGING/usr/share/applications/symbian-imageviewer.desktop"
[Desktop Entry]
Type=Application
Name=Image Viewer (GPicView)
Comment=Lightweight Fast Image Viewer
Exec=gpicview
Icon=/usr/share/icons/Symbian-Belle/apps/gpicview.png
Terminal=false
Categories=Graphics;Viewer;
EOF

cat <<EOF > "$STAGING/usr/share/applications/symbian-pdf.desktop"
[Desktop Entry]
Type=Application
Name=PDF Reader (FlaxPDF)
Comment=Lightweight Fast PDF Document Viewer
Exec=flaxpdf
Icon=/usr/share/icons/Symbian-Belle/apps/pdf.png
Terminal=false
Categories=Office;Viewer;
EOF

cat <<EOF > "$STAGING/usr/share/applications/symbian-terminal.desktop"
[Desktop Entry]
Type=Application
Name=Terminal Emulator
Comment=Command Line Terminal
Exec=lxterminal
Icon=/usr/share/icons/Symbian-Belle/apps/terminal.png
Terminal=false
Categories=System;TerminalEmulator;
EOF

cat <<EOF > "$STAGING/usr/share/applications/symbian-taskmanager.desktop"
[Desktop Entry]
Type=Application
Name=Task Manager (LXTask)
Comment=Resource and Process Monitor
Exec=lxtask
Icon=/usr/share/icons/Symbian-Belle/apps/taskmanager.png
Terminal=false
Categories=System;Monitor;
EOF

cat <<EOF > "$STAGING/usr/share/applications/symbian-appearance.desktop"
[Desktop Entry]
Type=Application
Name=Appearance Settings
Comment=Configure GTK Themes and Icons
Exec=lxappearance
Icon=/usr/share/icons/Symbian-Belle/apps/settings.png
Terminal=false
Categories=Settings;DesktopSettings;
EOF

cp "$STAGING/usr/share/applications/symbian-"*.desktop "$STAGING/etc/skel/Desktop/" 2>/dev/null || true

# 7. Hardware, Audio & Netbook Power Optimizations
echo "[7/9] Configuring Fujitsu LOOX M/G30 Netbook hardware..."
mkdir -p "$STAGING/opt/symbian/bin" "$STAGING/etc/X11/xorg.conf.d" "$STAGING/var/lib/alsa"
cp "$BASE_DIR/drivers/power/loox-power-opt.sh" "$STAGING/opt/symbian/bin/" 2>/dev/null || true
chmod +x "$STAGING/opt/symbian/bin/loox-power-opt.sh" 2>/dev/null || true
cp "$BASE_DIR/drivers/graphics/20-intel.conf" "$STAGING/etc/X11/xorg.conf.d/" 2>/dev/null || true
cp "$BASE_DIR/drivers/audio/asound.state" "$STAGING/var/lib/alsa/" 2>/dev/null || true

# Symbian OS Release Identification
cat <<EOF > "$STAGING/etc/os-release"
NAME="Symbian-X86 LOOX OS"
VERSION="1.0 LTS (Symbian Belle Edition on Tiny Core Linux)"
ID=symbian-x86-loox
ID_LIKE="tinycore debian"
PRETTY_NAME="Symbian-X86 LOOX OS (Fujitsu FMV-BIBLO LOOX M/G30)"
VERSION_ID="1.0"
HOME_URL="https://github.com/symbian-x86/loox"
EOF

# 8. Configure Tiny Core System Startup & Symbian Drives
echo "[8/9] Configuring Tiny Core system startup and Symbian drives..."
mkdir -p "$STAGING/opt" "$STAGING/etc/sysconfig"

# Enable serial console ttyS0 for testing & debugging
if ! grep -q "ttyS0" "$STAGING/etc/inittab"; then
    echo "ttyS0::respawn:/sbin/getty -nl /sbin/autologin 38400 ttyS0" >> "$STAGING/etc/inittab"
fi

# Configure autologin to log in as user tc
cat <<'EOF' > "$STAGING/sbin/autologin"
#!/bin/busybox ash
USER="tc"
[ -f /etc/sysconfig/tcuser ] && USER="$(cat /etc/sysconfig/tcuser)"
touch /var/log/autologin
exec login -f "$USER"
EOF
chmod 755 "$STAGING/sbin/autologin"

# Set SUID root on Xvesa and sudo so user tc can start X and run privileged commands
chmod 4755 "$STAGING/usr/local/bin/Xvesa" 2>/dev/null || true
chmod 4755 "$STAGING/usr/bin/sudo" 2>/dev/null || true
chmod u+s "$STAGING/bin/busybox.suid" 2>/dev/null || true

cat <<'EOF' > "$STAGING/opt/bootsync.sh"
#!/bin/sh
# System startup for Symbian-X86 LOOX OS (Tiny Core Linux Base)
/usr/bin/sethostname loox-symbian

# Initialize Symbian Drives
mkdir -p /home/tc /media /opt/symbian/rom /opt/symbian/sys_drive/sys/bin
cp -a /etc/skel/. /home/tc/ 2>/dev/null || true
chown -R tc:staff /home/tc 2>/dev/null || true
ln -sfn /home/tc /C: 2>/dev/null || true
ln -sfn /media /D: 2>/dev/null || true
ln -sfn /opt/symbian/rom /Z: 2>/dev/null || true

# Dynamic library cache
/sbin/ldconfig 2>/dev/null || true

# Run background power & hardware tuning
/opt/bootlocal.sh &
EOF
chmod 755 "$STAGING/opt/bootsync.sh"

cat <<'EOF' > "$STAGING/opt/bootlocal.sh"
#!/bin/sh
# Fujitsu FMV-BIBLO LOOX M/G30 Hardware & Power Optimization
if [ -x /opt/symbian/bin/loox-power-opt.sh ]; then
    /opt/symbian/bin/loox-power-opt.sh 2>/dev/null || true
fi
EOF
chmod 755 "$STAGING/opt/bootlocal.sh"

# Default desktop and Xserver
echo "flwm" > "$STAGING/etc/sysconfig/desktop"
echo "Xvesa" > "$STAGING/etc/sysconfig/Xserver"

# Configure Wbar dock with Symbian Belle icons
cat <<'EOF' > "$STAGING/usr/local/etc/wbar.cfg"
i: /usr/share/icons/Symbian-Belle/symbian-menu.png
c: symbian-appmanager
t: Symbian Apps

i: /usr/share/icons/Symbian-Belle/apps/browser.png
c: dillo
t: Web Browser

i: /usr/share/icons/Symbian-Belle/apps/leafpad.png
c: leafpad
t: Text Editor

i: /usr/share/icons/Symbian-Belle/apps/notes.png
c: symbian-notes
t: Symbian Notes

i: /usr/share/icons/Symbian-Belle/apps/calculator.png
c: symbian-calc
t: Calculator

i: /usr/share/icons/Symbian-Belle/apps/filemanager.png
c: symbian-filebrowser
t: File Browser (C:, D:, Z:)

i: /usr/share/icons/Symbian-Belle/apps/gpicview.png
c: gpicview
t: Image Viewer

i: /usr/share/icons/Symbian-Belle/apps/pdf.png
c: flaxpdf
t: PDF Reader

i: /usr/share/icons/Symbian-Belle/apps/taskmanager.png
c: lxtask
t: Task Manager

i: /usr/share/icons/Symbian-Belle/apps/terminal.png
c: lxterminal
t: Terminal

i: /usr/share/icons/Symbian-Belle/apps/symbian-pkg.png
c: symbian-pkg-gui
t: Package Manager

i: /usr/share/icons/Symbian-Belle/apps/sysmanager.png
c: symbian-installer
t: Install to HDD
EOF
mkdir -p "$STAGING/usr/share/wbar" "$STAGING/etc/skel"
cp "$STAGING/usr/local/etc/wbar.cfg" "$STAGING/usr/share/wbar/dot.wbar" 2>/dev/null || true
cp "$STAGING/usr/local/etc/wbar.cfg" "$STAGING/etc/skel/.wbar" 2>/dev/null || true

# Configure .xsession for user tc
cat <<'EOF' > "$STAGING/etc/skel/.xsession"
#!/bin/sh
export PATH=/home/tc/.local/bin:/usr/local/bin:/usr/bin:/bin:/opt/symbian/bin:$PATH
export PYTHONPATH=/opt:$PYTHONPATH
export LD_LIBRARY_PATH=/usr/local/lib:/opt/symbian/lib:$LD_LIBRARY_PATH
export DISPLAY=:0.0
[ -z "$XAUTHORITY" ] && export XAUTHORITY=$HOME/.Xauthority

# Determine best supported VESA resolution
# Prefer native 1024x600 for Fujitsu LOOX M/G30, fallback to standard VESA 1024x768 or 800x600
RES="1024x768x32"
if Xvesa -listmodes 2>&1 | grep -q "1024x600"; then
    RES="1024x600x32"
elif Xvesa -listmodes 2>&1 | grep -q "1024x768"; then
    RES="1024x768x32"
elif Xvesa -listmodes 2>&1 | grep -q "800x600"; then
    RES="800x600x32"
fi

Xvesa -br -screen "$RES" -shadow -2button -mouse /dev/input/mice,5 -nolisten tcp -I -s 0 -dpms >/tmp/xvesa.log 2>&1 &
export XPID=$!
if ! waitforX 2>/dev/null; then
    kill -9 $XPID 2>/dev/null || true
    Xvesa -br -screen 1024x768x16 -shadow -2button -mouse /dev/input/mice,5 -nolisten tcp -I -s 0 -dpms >/tmp/xvesa.log 2>&1 &
    export XPID=$!
    waitforX || ! echo failed in waitforX || exit
fi

# Symbian Belle Wallpaper (fill screen completely)
if [ -x /usr/local/bin/hsetroot ] && [ -f /usr/share/backgrounds/symbian-loox-bg.png ]; then
    /usr/local/bin/hsetroot -fill /usr/share/backgrounds/symbian-loox-bg.png 2>/dev/null
fi

# Window Manager: flwm or openbox
if [ -x /usr/local/bin/flwm ]; then
    flwm 2>/tmp/wm_errors &
    export WM_PID=$!
elif [ -x /usr/local/bin/openbox ]; then
    openbox --config-file /etc/xdg/openbox/rc.xml 2>/tmp/wm_errors &
    export WM_PID=$!
fi

# Symbian Belle App Dock
if [ -x /usr/local/bin/wbar ]; then
    (sleep 1 && wbar --bpress --above-desk --pos bottom --isize 38 --idist 14 --nanim 3 --nofont --config /usr/local/etc/wbar.cfg) &
fi

# Autostart Standard Desktop Applications & Symbian Notes
cat <<'NOTE' > /tmp/welcome.txt
==========================================================
 Symbian-X86 LOOX OS (Fujitsu LOOX M/G30 Netbook Edition)
 CPU: Intel Atom N450 (32-bit x86) | 1024x600 TFT Display
 Base: Tiny Core Linux 15.x | Desktop: Symbian Belle UI
==========================================================
 Pre-installed Standard Applications:
  * Web Browser: Dillo (Fast, lightweight web browser)
  * Text Editor: Leafpad (GTK2 text editor)
  * Image Viewer: GPicView (Fast image viewer)
  * PDF Reader: FlaxPDF (Lightweight PDF viewer)
  * Task Manager: LXTask (Resource and task monitor)
  * Terminal: LXTerminal (Lightweight tabbed terminal)
  * System Config: LXAppearance & LXRandr
  * Symbian Apps: Notes, Calculator, File Browser (C:, D:, Z:)
==========================================================
NOTE
cp /tmp/welcome.txt /etc/skel/Welcome.txt 2>/dev/null || true
cp /tmp/welcome.txt /home/tc/Welcome.txt 2>/dev/null || true

if [ -x /usr/local/bin/leafpad ]; then
    (sleep 2 && /usr/local/bin/leafpad /tmp/welcome.txt >/tmp/leafpad.log 2>&1) &
elif [ -x /usr/bin/leafpad ]; then
    (sleep 2 && /usr/bin/leafpad /tmp/welcome.txt >/tmp/leafpad.log 2>&1) &
fi

if [ -x /usr/local/bin/lxtask ]; then
    (sleep 3 && /usr/local/bin/lxtask >/tmp/lxtask.log 2>&1) &
elif [ -x /usr/bin/lxtask ]; then
    (sleep 3 && /usr/bin/lxtask >/tmp/lxtask.log 2>&1) &
fi

if [ -x /usr/bin/symbian-notes ]; then
    (sleep 4 && /usr/bin/symbian-notes >/tmp/notes.log 2>&1) &
fi

[ -d "/usr/local/etc/X.d" ] && find "/usr/local/etc/X.d" -type f -o -type l | sort | while read F; do . "$F"; done
[ -d "$HOME/.X.d" ] && find "$HOME/.X.d" -type f -o -type l | sort | while read F; do . "$F"; done

wait $WM_PID
EOF
chmod 755 "$STAGING/etc/skel/.xsession"

# Configure .profile to prevent startx hanging on serial console
cat <<'EOF' > "$STAGING/etc/skel/.profile"
# ~/.profile: Executed by Bourne-compatible login shells.
[ -d "$HOME/.local/bin" ] || mkdir -p "$HOME/.local/bin"
export PATH=$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin:/opt/symbian/bin:$PATH
export PYTHONPATH=/opt:$PYTHONPATH
export LD_LIBRARY_PATH=/usr/local/lib:/opt/symbian/lib:$LD_LIBRARY_PATH

PS1='tc@loox:\w\$ '
PAGER='less -EM'
EDITOR=vi
export PS1 PAGER EDITOR PYTHONPATH LD_LIBRARY_PATH

if [ -f "$HOME/.ashrc" ]; then
   export ENV="$HOME/.ashrc"
   . "$HOME/.ashrc"
fi

TERMTYPE=`/usr/bin/tty 2>/dev/null || echo ""`
case "$TERMTYPE" in
    /dev/tty[1-6])
        if [ -f /etc/sysconfig/Xserver ] && [ ! -f /etc/sysconfig/text ] && [ ! -e /tmp/.X11-unix/X0 ]; then
            startx
        fi
        ;;
    *)
        echo "=========================================================="
        echo "  Welcome to Symbian-X86 LOOX OS (Tiny Core Base)!"
        echo "  Drives: C: (Home), D: (Removable), Z: (ROM)"
        echo "  Native Apps: symbian-notes, symbian-calc, symbian-filebrowser"
        echo "=========================================================="
        ;;
esac
EOF
chmod 644 "$STAGING/etc/skel/.profile"

# 9. Pack Remastered core.gz
echo "[9/9] Repacking remastered core.gz archive..."
rm -f "$OUTPUT_BOOT/core.gz"
cd "$STAGING"
fakeroot sh -c "find . | cpio -o -H newc | gzip -9 > '$OUTPUT_BOOT/core.gz'"
cd "$SCRIPT_DIR"

# Stage vmlinuz
cp "$KERNEL_DIR/vmlinuz" "$OUTPUT_BOOT/vmlinuz"

echo "=========================================================="
echo "    [REMASTER] Successfully Remastered Tiny Core Linux!"
echo "    Kernel:  $OUTPUT_BOOT/vmlinuz ($(du -h "$OUTPUT_BOOT/vmlinuz" | cut -f1))"
echo "    Core:    $OUTPUT_BOOT/core.gz ($(du -h "$OUTPUT_BOOT/core.gz" | cut -f1))"
echo "=========================================================="
